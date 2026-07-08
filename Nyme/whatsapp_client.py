import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_VERSION = "v19.0"


class WhatsAppClient:
    """Cliente multi-línea de WhatsApp Cloud API.
    Cada línea tiene su propio token y phone_number_id almacenados en la DB.
    """

    def _build_url(self, phone_number_id):
        return f"https://graph.facebook.com/{API_VERSION}/{phone_number_id}/messages"

    def _headers(self, access_token):
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _clean_number(self, number):
        """Limpia el número de teléfono, especialmente eliminando el '1' para móviles de México (inbound 521 -> outbound 52)."""
        if not number:
            return ""
        # Guardar prefijo fb_ o ig_ si existiera (aunque esto es solo para WhatsApp, por seguridad)
        prefix = ""
        if number.startswith("fb_"):
            prefix = "fb_"
            number = number[3:]
        elif number.startswith("ig_"):
            prefix = "ig_"
            number = number[3:]
            
        cleaned = "".join(c for c in number if c.isdigit())
        if cleaned.startswith("521") and len(cleaned) == 13:
            cleaned = "52" + cleaned[3:]
        return prefix + cleaned

    # ── Media Handling ────────────────────────────────────────────────────────

    def get_media_url(self, line, media_id):
        """Obtiene la URL temporal de descarga de un archivo en Meta."""
        url = f"https://graph.facebook.com/{API_VERSION}/{media_id}"
        headers = {"Authorization": f"Bearer {line['access_token']}"}
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                return r.json().get("url")
        except Exception as e:
            print(f"[WA] Error getting media URL: {e}")
        return None

    def download_media(self, line, media_url):
        """Descarga el contenido binario de un medio de Meta."""
        headers = {"Authorization": f"Bearer {line['access_token']}"}
        try:
            r = requests.get(media_url, headers=headers)
            if r.status_code == 200:
                return r.content
        except Exception as e:
            print(f"[WA] Error downloading media: {e}")
        return None

    def upload_media(self, line, file_path, file_type):
        """Sube un archivo a Meta para poder enviarlo después."""
        url = f"https://graph.facebook.com/{API_VERSION}/{line['phone_number_id']}/media"
        headers = {"Authorization": f"Bearer {line['access_token']}"}
        files = {
            "file": (os.path.basename(file_path), open(file_path, "rb"), file_type),
            "type": (None, file_type),
            "messaging_product": (None, "whatsapp"),
        }
        try:
            r = requests.post(url, headers=headers, files=files)
            if r.status_code == 200:
                return r.json().get("id")
        except Exception as e:
            print(f"[WA] Error uploading media: {e}")
        return None

    # ── Envío por línea (dict) ────────────────────────────────────────────────

    def send_text_message(self, line, recipient_number, message_text):
        """Envía un mensaje usando un dict de línea con phone_number_id y access_token."""
        if not line:
            return None
        recipient_number = self._clean_number(recipient_number)
        url     = self._build_url(line["phone_number_id"])
        headers = self._headers(line["access_token"])
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_number,
            "type": "text",
            "text": {"body": message_text},
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"[WA] HTTP {e.response.status_code}: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[WA] Error de red: {e}")
            return None

    def send_image_message(self, line, recipient_number, media_id, caption=""):
        recipient_number = self._clean_number(recipient_number)
        url     = self._build_url(line["phone_number_id"])
        headers = self._headers(line["access_token"])
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "image",
            "image": {"id": media_id, "caption": caption},
        }
        try:
            r = requests.post(url, headers=headers, json=payload)
            return r.json()
        except Exception: return None

    def send_document_message(self, line, recipient_number, media_id, filename, caption=""):
        recipient_number = self._clean_number(recipient_number)
        url     = self._build_url(line["phone_number_id"])
        headers = self._headers(line["access_token"])
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "document",
            "document": {"id": media_id, "filename": filename, "caption": caption},
        }
        try:
            r = requests.post(url, headers=headers, json=payload)
            return r.json()
        except Exception: return None

    # ── Envío por line_id (busca en DB) ──────────────────────────────────────

    def send_from_line_id(self, line_id, recipient_number, message_text):
        """Carga las credenciales de la DB por line_id y envía el mensaje."""
        from database import db
        line = db.get_line_by_id(line_id)
        if not line or not line["is_active"]:
            print(f"[WA] Línea {line_id} no encontrada o inactiva")
            return None
        return self.send_text_message(line, recipient_number, message_text)

    # ── Prueba de conexión de una línea ───────────────────────────────────────

    def test_line(self, line):
        """Verifica que el token y phone_number_id sean válidos consultando la API."""
        try:
            url  = f"https://graph.facebook.com/{API_VERSION}/{line['phone_number_id']}"
            resp = requests.get(
                url,
                headers=self._headers(line["access_token"]),
                params={"fields": "display_phone_number"},
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
            return True, data.get("display_phone_number", "OK")
        except requests.exceptions.HTTPError as e:
            return False, f"Error {e.response.status_code}: token o Phone ID inválido"
        except Exception as e:
            return False, str(e)

    @property
    def is_configured(self):
        """True si hay al menos una línea activa en la DB."""
        from database import db
        return db.count_lines() > 0


wa_client = WhatsAppClient()
