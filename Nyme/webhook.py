from fastapi import FastAPI, Request, HTTPException, Query
from database import db
from whatsapp_client import wa_client
import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN   = os.getenv("META_VERIFY_TOKEN", "nyme_verify_2024")
APP_SECRET     = os.getenv("META_APP_SECRET", "")   # App Secret del portal de Meta


# ─────────────────────────────────────────────────────────────────────────────
# SEGURIDAD — Validación de firma SHA256
# ─────────────────────────────────────────────────────────────────────────────

def _verify_signature(payload: bytes, signature_header: str) -> bool:
    """Valida que el mensaje viene realmente de Meta usando HMAC-SHA256."""
    if not APP_SECRET:
        # Si no se configuró el App Secret, omitir validación (solo en desarrollo)
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        APP_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    received = signature_header[7:]   # Quita "sha256="
    return hmac.compare_digest(expected, received)


# ─────────────────────────────────────────────────────────────────────────────
# VERIFICACIÓN DEL WEBHOOK (GET)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/webhook")
async def verify_webhook(
    mode:      str = Query(None, alias="hub.mode"),
    token:     str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta llama a este endpoint para verificar que el webhook es nuestro."""
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[Webhook] ✅ Verificado por Meta.")
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


# ─────────────────────────────────────────────────────────────────────────────
# RECEPCIÓN DE MENSAJES (POST)
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/webhook")
async def receive_message(request: Request):
    """Recibe mensajes de Meta — valida firma SHA256 y procesa multi-línea."""
    raw_body = await request.body()

    # Validar firma de Meta
    sig_header = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_signature(raw_body, sig_header):
        print("[Webhook] ❌ Firma SHA256 inválida — solicitud rechazada.")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        body = await request.json() if not raw_body else __import__("json").loads(raw_body)

        if body.get("object") != "whatsapp_business_account":
            return {"status": "ignored"}

        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # ── Detectar línea por phone_number_id ────────────────────
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                line    = db.get_line_by_phone_id(phone_number_id) if phone_number_id else None
                line_id = line["id"] if line else None

                # ── Procesar mensajes entrantes ────────────────────────────
                for message in value.get("messages", []):
                    wa_id = message["from"]

                    if message["type"] == "text":
                        body_text = message["text"]["body"]
                    elif message["type"] == "image":
                        body_text = f"[📷 Imagen: {message.get('image',{}).get('caption','sin descripción')}]"
                    elif message["type"] == "document":
                        body_text = f"[📎 Documento: {message.get('document',{}).get('filename','archivo')}]"
                    elif message["type"] == "audio":
                        body_text = "[🎤 Mensaje de voz]"
                    elif message["type"] == "video":
                        body_text = "[🎬 Video]"
                    elif message["type"] == "location":
                        loc = message.get("location", {})
                        body_text = f"[📍 Ubicación: {loc.get('name','')} {loc.get('address','')}]"
                    else:
                        body_text = f"[Mensaje tipo: {message['type']}]"

                    # Verificar primer contacto en esta línea
                    first_contact = db.is_first_contact(wa_id, line_id) if line_id else False

                    # Guardar mensaje INBOUND
                    db.save_message(wa_id, "INBOUND", body_text, line_id=line_id)
                    db.mark_conversation_unread(wa_id, line_id)
                    print(f"[Webhook] 📩 +{wa_id} → {line['name'] if line else 'Línea ?'}: {body_text[:60]}")

                    # Enviar bienvenida automática
                    if (
                        first_contact and line
                        and line.get("welcome_active")
                        and line.get("welcome_message")
                    ):
                        result = wa_client.send_text_message(line, wa_id, line["welcome_message"])
                        if result:
                            db.save_message(
                                wa_id, "OUTBOUND_REPLY",
                                line["welcome_message"],
                                agent_username="[bienvenida]",
                                line_id=line_id,
                            )
                            print(f"[Webhook] 👋 Bienvenida enviada a +{wa_id}")

        return {"status": "ok"}

    except Exception as e:
        print(f"[Webhook] Error: {e}")
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
