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
            rx.heading("📊 Reportes y Dashboard Ejecutivo", size="7", color="white", padding="24px 32px 8px"),
            rx.text(
                "Métricas clave del rendimiento del equipo, tiempos de respuesta y volumen de interacciones.",
                color="#8e8e93", padding="0 32px 24px",
            ),
            
            # Fila de KPIs
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("⏱️ Tiempo Promedio de Respuesta", size="1", color="#8e8e93", weight="medium"),
                        rx.hstack(
                            rx.text(AppState.avg_response_time.to_string() + " min", size="6", color="white", weight="bold"),
                            rx.badge("Excelente", color_scheme="green", size="1"),
                            align_items="center", spacing="2"
                        ),
                        spacing="1", align_items="start"
                    ),
                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px"
                ),
                rx.box(
                    rx.vstack(
                        rx.text("🟡 Chats en Curso", size="1", color="#8e8e93", weight="medium"),
                        rx.text(AppState.conversation_states_chart["active"].to_string(), size="6", color="#ffd60a", weight="bold"),
                        spacing="1", align_items="start"
                    ),
                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px"
                ),
                rx.box(
                    rx.vstack(
                        rx.text("⏳ Chats Pendientes", size="1", color="#8e8e93", weight="medium"),
                        rx.text(AppState.conversation_states_chart["pending"].to_string(), size="6", color="#0a84ff", weight="bold"),
                        spacing="1", align_items="start"
                    ),
                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px"
                ),
                rx.box(
                    rx.vstack(
                        rx.text("✅ Chats Cerrados", size="1", color="#8e8e93", weight="medium"),
                        rx.text(AppState.conversation_states_chart["resolved"].to_string(), size="6", color="#30d158", weight="bold"),
                        spacing="1", align_items="start"
                    ),
                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px"
                ),
                columns="4", spacing="4", width="100%", padding="0 32px 24px"
            ),
            
            # Sección Principal: Top Agentes
            rx.grid(
                # Tarjeta Top Agentes
                rx.box(
                    rx.vstack(
                        rx.heading("🏆 Agentes Más Activos (Humano e IA)", size="4", color="white"),
                        rx.text("Ranking de volumen de respuestas enviadas.", color="#8e8e93", size="2"),
                        rx.divider(color="#2c2c2e", margin_y="12px"),
                        rx.cond(
                            AppState.top_agents.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    AppState.top_agents,
                                    lambda tag: rx.hstack(
                                        rx.text(tag["agent"].to(str), weight="bold", size="2", color="white"),
                                        rx.spacer(),
                                        rx.badge(tag["count"].to_string() + " respuestas", color_scheme="blue"),
                                        padding="10px",
                                        border="1px solid #2c2c2e",
                                        border_radius="10px",
                                        width="100%",
                                        background="#1c1c1e"
                                    )
                                ),
                                width="100%", spacing="2"
                            ),
                            rx.text("No hay interacciones registradas en este período.", color="#636366", size="2")
                        ),
                        spacing="3", align_items="start", width="100%"
                    ),
                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="24px", flex="1"
                ),
                # Tarjeta Exportación
                rx.box(
                    rx.vstack(
                        rx.heading("📥 Exportar Datos de Negocio", size="4", color="white"),
                        rx.text("Descarga el historial completo para auditoría y KPIs.", color="#8e8e93", size="2"),
                        rx.divider(color="#2c2c2e", margin_y="12px"),
                        rx.button("📊 Descargar Reporte Completo (Excel)", color_scheme="green", size="3", width="100%", on_click=AppState.export_contacts),
                        rx.text("La exportación incluye datos del CRM, ciclo de vida de clientes, asignaciones y marcas de tiempo de primera respuesta.", size="1", color="#636366"),
                        spacing="4", align_items="start", width="100%"
                    ),
                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="24px"
                ),
                columns="2", spacing="4", width="100%", padding="0 32px"
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

                    # Disparar respondedor de IA automático en segundo plano si es mensaje de texto
                    if t == "text" and line_id:
                        tenant_id = line.get("tenant_id", 1) if line else 1
                        asyncio.create_task(
                            run_ai_agent_responder(wa_id, line_id, line, body_text, tenant_id)
                        )

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

async def run_ai_agent_responder(wa_id: str, line_id: int, line: dict, incoming_text: str, tenant_id: int):
    """Genera y envía una respuesta de IA en background si hay un agente activo y no está asignado a un humano."""
    from database import db
    from whatsapp_client import wa_client
    from gemini_client import gemini
    import asyncio

    # Pausa corta para asegurar que el mensaje entrante se asiente en la base de datos
    await asyncio.sleep(1)
    
    # 1. Obtener si hay agente IA activo para esta línea
    agent = db.get_active_agent_for_line(line_id, tenant_id)
    if not agent:
        return

    # 2. Verificar si la conversación está asignada a un humano
    assigned_to = ""
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT assigned_to FROM conversation_status WHERE wa_id = %s AND line_id = %s",
            (wa_id, line_id)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            assigned_to = row[0] or ""
    except Exception:
        pass

    if assigned_to:
        # Ya tiene agente humano asignado, omitimos responder automáticamente
        return

    # 3. Obtener el historial reciente del chat
    history = db.get_messages(wa_id, tenant_id)
    
    # 4. Generar respuesta con Gemini
    ai_reply = gemini.generate_agent_reply(agent["system_prompt"], history)
    if ai_reply:
        # 5. Enviar la respuesta por WhatsApp vía API de Meta
        r = wa_client.send_text_message(line, wa_id, ai_reply)
        if r:
            # 6. Guardar en BD
            db.save_message(
                wa_id, "OUTBOUND_REPLY", ai_reply,
                agent_username=f"[IA] {agent['name']}",
                line_id=line_id, tenant_id=tenant_id
            )



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

# ── 3. Servir frontend estático de forma NATIVA (producción) ──────────────────
# Evita la necesidad de un servidor proxy y soluciona problemas de WebSocket.
BUILD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".web", "build", "client")

if os.path.isdir(BUILD_DIR):
    print(f"[Nyme Native] Detectado compilado de producción en {BUILD_DIR}. Montando middleware de frontend estático...")
    from starlette.staticfiles import StaticFiles
    from starlette.responses import FileResponse
    from starlette.types import ASGIApp, Scope, Receive, Send

    class NativeFrontendMiddleware:
        def __init__(self, asgi_app: ASGIApp):
            self.asgi_app = asgi_app

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] == "http":
                path = scope.get("path", "/")
                # Prefijos de rutas reservados para el backend de Reflex y webhooks
                backend_prefixes = ("/_event", "/ping", "/_health", "/webhook", "/upload", "/backend")
                is_backend = any(path == prefix or path.startswith(prefix + "/") for prefix in backend_prefixes)

                if not is_backend:
                    rel = path.lstrip("/")
                    candidates = []
                    if rel:
                        candidates.append(os.path.join(BUILD_DIR, rel))
                        candidates.append(os.path.join(BUILD_DIR, rel + ".html"))
                        candidates.append(os.path.join(BUILD_DIR, rel, "index.html"))

                    candidates.append(os.path.join(BUILD_DIR, "__spa-fallback.html"))
                    candidates.append(os.path.join(BUILD_DIR, "index.html"))

                    for c in candidates:
                        if os.path.isfile(c):
                            response = FileResponse(c)
                            await response(scope, receive, send)
                            return

            # Para todo lo demás (WebSockets, ping, webhook, uploads) pasamos al backend de Reflex
            await self.asgi_app(scope, receive, send)

    # Registramos el middleware en la Starlette de Reflex
    app._api.add_middleware(NativeFrontendMiddleware)
else:
    print("[Nyme Native] No se detectó compilado de producción (desarrollo local). El frontend se sirve mediante reflex run.")
