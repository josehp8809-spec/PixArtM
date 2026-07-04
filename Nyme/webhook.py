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

        obj_type = body.get("object")
        if obj_type not in ("whatsapp_business_account", "page", "instagram"):
            return {"status": "ignored"}

        # ── Flujo WhatsApp ───────────────────────────────────────────────
        if obj_type == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    phone_number_id = value.get("metadata", {}).get("phone_number_id")
                    line    = db.get_line_by_phone_id(phone_number_id) if phone_number_id else None
                    line_id = line["id"] if line else None
                    tenant_id = line["tenant_id"] if line else 1

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

                        first_contact = db.is_first_contact(wa_id, line_id) if line_id else False
                        
                        # Guardar mensaje INBOUND
                        db.save_message(wa_id, "INBOUND", body_text, line_id=line_id, tenant_id=tenant_id, channel_type="whatsapp")
                        db.mark_conversation_unread(wa_id, line_id)
                        print(f"[Webhook] 📩 +{wa_id} (WhatsApp) → {line['name'] if line else 'Línea ?'}: {body_text[:60]}")

                        if first_contact and line and line.get("welcome_active") and line.get("welcome_message"):
                            result = wa_client.send_text_message(line, wa_id, line["welcome_message"])
                            if result:
                                db.save_message(
                                    wa_id, "OUTBOUND_REPLY",
                                    line["welcome_message"],
                                    agent_username="[bienvenida]",
                                    line_id=line_id,
                                    tenant_id=tenant_id,
                                    channel_type="whatsapp"
                                )
                                print(f"[Webhook] 👋 Bienvenida enviada a +{wa_id}")

        # ── Flujo Facebook Messenger o Instagram DMs ───────────────────────
        elif obj_type in ("page", "instagram"):
            prefix = "fb_" if obj_type == "page" else "ig_"
            channel_type = "messenger" if obj_type == "page" else "instagram"

            for entry in body.get("entry", []):
                page_id = entry.get("id")  # FB Page ID o Instagram Account ID
                channel = db.get_channel_by_page_id(page_id) if page_id else None
                
                if not channel:
                    print(f"[Webhook] ⚠️ Canal no registrado para page_id: {page_id}. Ignorando.")
                    continue

                line_id = channel["id"]
                tenant_id = channel["tenant_id"]

                for messaging_event in entry.get("messaging", []):
                    # Ignorar eventos que no son de mensaje (como entregas, lecturas, etc)
                    if "message" not in messaging_event:
                        continue

                    sender_id = messaging_event["sender"]["id"]
                    contact_wa_id = f"{prefix}{sender_id}"
                    message_data = messaging_event["message"]

                    # Saltar si es un mensaje enviado por nuestra propia app/página
                    if message_data.get("is_echo"):
                        continue

                    body_text = message_data.get("text", "")
                    if not body_text:
                        # Si es un adjunto (imagen, etc)
                        attachments = message_data.get("attachments", [])
                        if attachments:
                            att_type = attachments[0].get("type", "file")
                            body_text = f"[{att_type.capitalize()} adjunto]"
                        else:
                            body_text = "[Mensaje de red social]"

                    # Intentar obtener el nombre del contacto (Messenger e Instagram envían datos en algunos casos)
                    sender_name = "Usuario de Facebook" if obj_type == "page" else "Usuario de Instagram"
                    
                    # Registrar contacto en la base de datos si es nuevo
                    db.upsert_contact(contact_wa_id, sender_name, "", "Contacto de Red Social", tenant_id)

                    # Guardar el mensaje entrante
                    db.save_message(
                        contact_wa_id, "INBOUND", body_text, 
                        line_id=line_id, tenant_id=tenant_id, 
                        channel_type=channel_type, sender_name=sender_name
                    )
                    db.mark_conversation_unread(contact_wa_id, line_id)
                    print(f"[Webhook] 📩 {contact_wa_id} ({channel_type}) → {channel['name']}: {body_text[:60]}")

                    # Mensaje de bienvenida del canal
                    first_contact = db.is_first_contact(contact_wa_id, line_id)
                    if first_contact and channel.get("welcome_active") and channel.get("welcome_message"):
                        from meta_client import meta_client
                        success = meta_client.send_message(channel, contact_wa_id, channel["welcome_message"])
                        if success:
                            db.save_message(
                                contact_wa_id, "OUTBOUND_REPLY",
                                channel["welcome_message"],
                                agent_username="[bienvenida]",
                                line_id=line_id,
                                tenant_id=tenant_id,
                                channel_type=channel_type
                            )
                            print(f"[Webhook] 👋 Bienvenida enviada a {contact_wa_id}")

        return {"status": "ok"}

    except Exception as e:
        print(f"[Webhook] Error: {e}")
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
