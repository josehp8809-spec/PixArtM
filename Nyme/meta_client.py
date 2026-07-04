import requests

class MetaClient:
    def __init__(self):
        self.api_version = "v19.0"

    def send_message(self, channel: dict, recipient_id: str, text: str) -> bool:
        """
        Envía un mensaje de texto a través del canal especificado (messenger o instagram).
        Args:
            channel: Diccionario del canal obtenido de la BD (con access_token, channel_type).
            recipient_id: Identificador del destinatario (PSID en Messenger, IGSID en Instagram).
            text: Mensaje de texto a enviar.
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario.
        """
        channel_type = channel.get("channel_type", "whatsapp")
        access_token = channel.get("access_token")

        if not access_token:
            print(f"[MetaClient] Error: Access token faltante para el canal ID {channel.get('id')}")
            return False

        # El ID del destinatario puede venir prefijado por Nyme (ej: "fb_12345" o "ig_54321"). Limpiamos el prefijo si existe.
        clean_recipient_id = recipient_id
        if recipient_id.startswith("fb_"):
            clean_recipient_id = recipient_id[3:]
        elif recipient_id.startswith("ig_"):
            clean_recipient_id = recipient_id[3:]

        # Endpoint de envío de Meta para Messenger e Instagram
        url = f"https://graph.facebook.com/{self.api_version}/me/messages"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "access_token": access_token
        }

        # La estructura del payload es idéntica para texto plano en ambas plataformas
        payload = {
            "recipient": {
                "id": clean_recipient_id
            },
            "message": {
                "text": text
            }
        }

        try:
            print(f"[MetaClient] Enviando mensaje a {channel_type} (ID: {clean_recipient_id})...")
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=10)
            res_data = response.json()
            if response.status_code == 200:
                print(f"[MetaClient] ✅ Mensaje enviado con éxito: {res_data}")
                return True
            else:
                print(f"[MetaClient] ❌ Error enviando mensaje a {channel_type}: {res_data}")
                return False
        except Exception as e:
            print(f"[MetaClient] Exception al enviar mensaje: {e}")
            return False

meta_client = MetaClient()
