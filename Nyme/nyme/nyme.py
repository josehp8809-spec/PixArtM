"""
nyme.py — Punto de entrada principal del app Reflex.
El webhook de Meta se monta como ruta de la API interna de Reflex.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import reflex as rx
from nyme.state import AppState
from nyme.pages.login import login_page
from nyme.pages.chat import chat_page
from nyme.pages.settings import settings_page
from nyme.pages.internal import internal_chat_page
from nyme.pages.contacts import contacts_page
from nyme.pages.orders import orders_page
from nyme.pages.navbar import navbar as premium_navbar

# ─────────────────────────────────────────────────────────────────────────────
# Navbar compartida
# ─────────────────────────────────────────────────────────────────────────────

def navbar() -> rx.Component:
    return rx.hstack(
        rx.text("📱 Nyme", weight="bold", color="white", size="3"),
        rx.spacer(),
        rx.link("💬 WhatsApp",  href="/chat",     color="#8e8e93", size="2"),
        rx.link("👥 Clientes",  href="/contacts", color="#8e8e93", size="2"),
        rx.link("🏢 Equipo",    href="/internal", color="#8e8e93", size="2"),
        rx.cond(
            (AppState.role == "admin") | (AppState.role == "coordinator"),
            rx.hstack(
                rx.link("📊 Ventas",   href="/orders",  color="#8e8e93", size="2"),
                rx.link("📊 Reportes", href="/reports", color="#8e8e93", size="2"),
                spacing="4"
            )
        ),
        rx.cond(
            AppState.role == "admin",
            rx.link("⚙️ Config", href="/settings",  color="#8e8e93", size="2"),
        ),
        rx.button(
            f"@{AppState.username}",
            on_click=AppState.logout,
            size="1", variant="ghost", color="#ff453a",
        ),
        padding="12px 24px",
        background="#111111",
        border_bottom="1px solid #2c2c2e",
        width="100%",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Página de reportes (wrapper simple — la lógica pesada en report_exporter)
# ─────────────────────────────────────────────────────────────────────────────

def reports_page() -> rx.Component:
    return rx.vstack(
        premium_navbar("/reports"),
        rx.vstack(
            rx.heading("📊 Reportes", size="7", color="white", padding="24px 32px 8px"),
            rx.text(
                "El módulo de reportes está disponible. Integración completa con SLA, "
                "análisis de sentimientos y exportación a Excel/PDF.",
                color="#8e8e93", padding="0 32px",
            ),
            rx.callout(
                "Módulo de reportes avanzado — conecta desde el panel de reportes exportando "
                "Excel y PDF desde report_exporter.py",
                color="blue", variant="soft", margin="32px",
            ),
            spacing="0",
            width="100%",
        ),
        background="#000000",
        spacing="0",
        min_height="100vh",
        width="100%",
        on_mount=AppState.require_auth,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Webhook Meta — montado en app.api de Reflex
# ─────────────────────────────────────────────────────────────────────────────

import hmac
import hashlib
import json
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "nyme_verify_2024")
APP_SECRET   = os.getenv("META_APP_SECRET", "")


def _verify_sig(payload: bytes, sig_header: str) -> bool:
    if not APP_SECRET:
        return True
    if not sig_header or not sig_header.startswith("sha256="):
        return False
    expected = hmac.new(APP_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header[7:])


async def webhook_get(request: Request):
    params = request.query_params
    mode      = params.get("hub.mode")
    token     = params.get("hub.verify_token")
    challenge = params.get("hub.challenge", "")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


async def webhook_post(request: Request):
    from database import db
    from whatsapp_client import wa_client

    raw  = await request.body()
    sig  = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_sig(raw, sig):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        body = json.loads(raw)
        if body.get("object") != "whatsapp_business_account":
            return {"status": "ignored"}

        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                phone_id = value.get("metadata", {}).get("phone_number_id")
                line     = db.get_line_by_phone_id(phone_id) if phone_id else None
                line_id  = line["id"] if line else None

                for msg in value.get("messages", []):
                    wa_id = msg["from"]
                    t = msg["type"]
                    if t == "text":
                        body_text = msg["text"]["body"]
                    elif t == "image":
                        body_text = f"[📷 Imagen]"
                    elif t == "audio":
                        body_text = "[🎤 Audio]"
                    elif t == "document":
                        body_text = f"[📎 {msg.get('document',{}).get('filename','Documento')}]"
                    elif t == "location":
                        loc = msg.get("location", {})
                        body_text = f"[📍 {loc.get('name','')} {loc.get('address','')}]"
                    else:
                        body_text = f"[{t}]"

                    first = db.is_first_contact(wa_id, line_id) if line_id else False
                    db.save_message(wa_id, "INBOUND", body_text, line_id=line_id)
                    db.mark_conversation_unread(wa_id, line_id)

                    if first and line and line.get("welcome_active") and line.get("welcome_message"):
                        r = wa_client.send_text_message(line, wa_id, line["welcome_message"])
                        if r:
                            db.save_message(wa_id, "OUTBOUND_REPLY",
                                            line["welcome_message"],
                                            agent_username="[bienvenida]",
                                            line_id=line_id)
        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)})


# ─────────────────────────────────────────────────────────────────────────────
# App Reflex
# ─────────────────────────────────────────────────────────────────────────────

app = rx.App(
    style={
        "font_family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        "background_color": "#000000",
    },
)

app.add_page(login_page,         route="/",         title="Nyme — Login")
app.add_page(chat_page,          route="/chat",      title="Nyme — WhatsApp")
app.add_page(contacts_page,      route="/contacts",  title="Nyme — Directorio")
app.add_page(internal_chat_page, route="/internal",  title="Nyme — Equipo")
app.add_page(settings_page,      route="/settings",  title="Nyme — Config")
app.add_page(reports_page,       route="/reports",   title="Nyme — Reportes")
app.add_page(orders_page,        route="/orders",    title="Nyme — Ventas")

# Montar webhook dentro del FastAPI/Starlette interno de Reflex
app._api.add_route("/webhook", webhook_get,  methods=["GET"])
app._api.add_route("/webhook", webhook_post, methods=["POST"])
