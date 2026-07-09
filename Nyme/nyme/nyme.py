"""
nyme.py — Punto de entrada principal del app Reflex.
El webhook de Meta se monta como ruta de la API interna de Reflex.
"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import db
db.init_db()

import reflex as rx
from nyme.state import AppState
from nyme.pages.login import login_page
from nyme.pages.chat import chat_page
from nyme.pages.settings import settings_page
from nyme.pages.internal import internal_chat_page
from nyme.pages.contacts import contacts_page
from nyme.pages.orders import orders_page
from nyme.pages.navbar import navbar as premium_navbar
from nyme.pages.landing import landing_page
from nyme.pages.documents import privacy_page, terms_page, data_deletion_page

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
        print(f"[Webhook _verify_sig] Cabecera de firma vacía o formato inválido: {sig_header}")
        return False
    expected = hmac.new(APP_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    result = hmac.compare_digest(expected, sig_header[7:])
    if not result:
        print(f"[Webhook _verify_sig] Mismatch de firma. Esperada: {expected}, Recibida: {sig_header[7:]}")
    return result


async def webhook_get(request: Request):
    params = request.query_params
    mode      = params.get("hub.mode")
    token     = params.get("hub.verify_token")
    challenge = params.get("hub.challenge", "")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

async def run_conversational_flows(wa_id: str, line_id: int, line: dict, body_text: str, tenant_id: int, channel_type: str) -> bool:
    """
    Ejecuta el motor de flujos conversacionales interactivos paso a paso.
    Retorna True si el mensaje fue procesado por un flujo, y False en caso contrario.
    """
    from database import db
    from whatsapp_client import wa_client
    
    state = db.get_flow_state(wa_id)
    flows = db.get_flows(tenant_id)
    
    active_flows = [f for f in flows if f.get("is_active")]
    if not active_flows and not state:
        return False

    flow = None
    if state:
        for f in active_flows:
            if f["id"] == state["flow_id"]:
                flow = f
                break
        if not flow:
            db.delete_flow_state(wa_id)
            return False
    else:
        flow = active_flows[0]
        state = {
            "flow_id": flow["id"],
            "current_step": 0,
            "collected_data": {}
        }
        db.save_flow_state(wa_id, flow["id"], 0, {})
        
        first_step = flow["steps"][0]
        msg_text = first_step["text"]
        
        sent = False
        if channel_type == "whatsapp":
            r = wa_client.send_text_message(line, wa_id, msg_text)
            sent = bool(r)
        else:
            from meta_client import meta_client
            r = meta_client.send_message(line, wa_id, msg_text)
            sent = bool(r)
            
        if sent:
            db.save_message(
                wa_id, "OUTBOUND_REPLY", msg_text,
                agent_username=f"[Flujo: {flow['name']}]",
                line_id=line_id, tenant_id=tenant_id,
                channel_type=channel_type
            )
            return True
        return False

    current_step_idx = state["current_step"]
    steps = flow["steps"]
    
    if current_step_idx >= len(steps):
        db.delete_flow_state(wa_id)
        return False
        
    current_step_def = steps[current_step_idx]
    action = current_step_def.get("action", "none")
    action_val = current_step_def.get("action_value", "")
    collected_data = state["collected_data"] or {}
    
    if action == "ask_name":
        collected_data["name"] = body_text
        db.upsert_contact(wa_id, body_text, collected_data.get("email", ""), "Contacto de Flujo", tenant_id)
    elif action == "ask_email":
        collected_data["email"] = body_text
        contact_name = collected_data.get("name", "Contacto de Flujo")
        db.upsert_contact(wa_id, contact_name, body_text, "Contacto de Flujo", tenant_id)
    elif action == "assign_agent":
        if action_val:
            db.assign_conversation(wa_id, line_id, action_val, tenant_id)
    elif action == "end_flow":
        db.delete_flow_state(wa_id)
        return False

    next_step_idx = current_step_idx + 1
    if next_step_idx < len(steps):
        next_step_def = steps[next_step_idx]
        msg_text = next_step_def["text"]
        
        next_action = next_step_def.get("action", "none")
        next_val = next_step_def.get("action_value", "")
        if next_action == "assign_agent" and next_val:
            db.assign_conversation(wa_id, line_id, next_val, tenant_id)
            
        db.save_flow_state(wa_id, flow["id"], next_step_idx, collected_data)
        
        sent = False
        if channel_type == "whatsapp":
            r = wa_client.send_text_message(line, wa_id, msg_text)
            sent = bool(r)
        else:
            from meta_client import meta_client
            r = meta_client.send_message(line, wa_id, msg_text)
            sent = bool(r)
            
        if sent:
            db.save_message(
                wa_id, "OUTBOUND_REPLY", msg_text,
                agent_username=f"[Flujo: {flow['name']}]",
                line_id=line_id, tenant_id=tenant_id,
                channel_type=channel_type
            )
            if next_action == "end_flow":
                db.delete_flow_state(wa_id)
            return True
    else:
        db.delete_flow_state(wa_id)
        
    return False


async def webhook_post(request: Request):
    from database import db
    from whatsapp_client import wa_client

    raw  = await request.body()
    sig  = request.headers.get("X-Hub-Signature-256", "")
    print(f"[Webhook POST] Solicitud recibida. X-Hub-Signature-256: {sig}")
    if not _verify_sig(raw, sig):
        print(f"[Webhook POST] ❌ Firma SHA256 inválida o rechazada. APP_SECRET configurado: {bool(APP_SECRET)}")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        body = json.loads(raw)
        obj_type = body.get("object")
        print(f"[Webhook POST] Cuerpo decodificado correctamente. object: {obj_type}")
        if obj_type not in ("whatsapp_business_account", "page", "instagram"):
            return JSONResponse({"status": "ignored"})

        # ── Flujo WhatsApp ───────────────────────────────────────────────
        if obj_type == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    phone_id = value.get("metadata", {}).get("phone_number_id")
                    line     = db.get_line_by_phone_id(phone_id) if phone_id else None
                    line_id  = line["id"] if line else None
                    tenant_id = line["tenant_id"] if line else 1

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
                        db.save_message(wa_id, "INBOUND", body_text, line_id=line_id, tenant_id=tenant_id, channel_type="whatsapp")
                        db.mark_conversation_unread(wa_id, line_id)
                        print(f"[Webhook POST] 📩 Mensaje WhatsApp de +{wa_id} guardado para line_id {line_id} (tenant {tenant_id}): {body_text[:60]}")

                        # Disparar respondedor de IA automático y workflows (condicionado a flujos conversacionales)
                        if t == "text" and line_id:
                            async def run_whatsapp_logic():
                                flow_processed = await run_conversational_flows(wa_id, line_id, line, body_text, tenant_id, "whatsapp")
                                if not flow_processed:
                                    await run_ai_agent_responder(wa_id, line_id, line, body_text, tenant_id)
                                    await execute_workflows_for_message(wa_id, line_id, line, body_text, tenant_id)
                            asyncio.create_task(run_whatsapp_logic())

                        if first and line and line.get("welcome_active") and line.get("welcome_message"):
                            r = wa_client.send_text_message(line, wa_id, line["welcome_message"])
                            if r:
                                db.save_message(wa_id, "OUTBOUND_REPLY",
                                                line["welcome_message"],
                                                agent_username="[bienvenida]",
                                                line_id=line_id,
                                                tenant_id=tenant_id,
                                                channel_type="whatsapp")

        # ── Flujo Facebook Messenger o Instagram DMs ───────────────────────
        elif obj_type in ("page", "instagram"):
            prefix = "fb_" if obj_type == "page" else "ig_"
            channel_type = "messenger" if obj_type == "page" else "instagram"

            for entry in body.get("entry", []):
                page_id = entry.get("id")
                channel = db.get_channel_by_page_id(page_id) if page_id else None
                
                if not channel:
                    print(f"[Webhook nyme.py] ⚠️ Canal no registrado para page_id: {page_id}")
                    continue

                line_id = channel["id"]
                tenant_id = channel["tenant_id"]

                for messaging_event in entry.get("messaging", []):
                    if "message" not in messaging_event:
                        continue

                    sender_id = messaging_event["sender"]["id"]
                    contact_wa_id = f"{prefix}{sender_id}"
                    message_data = messaging_event["message"]

                    if message_data.get("is_echo"):
                        continue

                    body_text = message_data.get("text", "")
                    if not body_text:
                        attachments = message_data.get("attachments", [])
                        if attachments:
                            att_type = attachments[0].get("type", "file")
                            body_text = f"[{att_type.capitalize()} adjunto]"
                        else:
                            body_text = "[Mensaje de red social]"

                    # Intentar obtener el nombre real del perfil de Facebook/Instagram
                    import requests
                    sender_name = "Usuario de Facebook" if obj_type == "page" else "Usuario de Instagram"
                    if channel.get("access_token"):
                        try:
                            if obj_type == "page":
                                url = f"https://graph.facebook.com/v19.0/{sender_id}?fields=first_name,last_name&access_token={channel['access_token']}"
                                res = requests.get(url, timeout=5)
                                if res.status_code == 200:
                                    data = res.json()
                                    first_name = data.get("first_name", "")
                                    last_name = data.get("last_name", "")
                                    if first_name or last_name:
                                        sender_name = f"{first_name} {last_name}".strip()
                            else:
                                url = f"https://graph.facebook.com/v19.0/{sender_id}?fields=username&access_token={channel['access_token']}"
                                res = requests.get(url, timeout=5)
                                if res.status_code == 200:
                                    data = res.json()
                                    username = data.get("username", "")
                                    if username:
                                        sender_name = f"@{username}"
                        except Exception as e:
                            print(f"[Webhook Profile Fetch] Error obteniendo perfil de Meta: {e}")

                    db.upsert_contact(contact_wa_id, sender_name, "", "Contacto de Red Social", tenant_id)

                    db.save_message(
                        contact_wa_id, "INBOUND", body_text,
                        line_id=line_id, tenant_id=tenant_id,
                        channel_type=channel_type, sender_name=sender_name
                    )
                    db.mark_conversation_unread(contact_wa_id, line_id)

                    # Disparar IA y Workflows para redes sociales (condicionado a flujos conversacionales)
                    if body_text and not body_text.startswith("["):
                        async def run_social_logic():
                            flow_processed = await run_conversational_flows(contact_wa_id, line_id, channel, body_text, tenant_id, channel_type)
                            if not flow_processed:
                                await run_ai_agent_responder(contact_wa_id, line_id, channel, body_text, tenant_id)
                                await execute_workflows_for_message(contact_wa_id, line_id, channel, body_text, tenant_id)
                        asyncio.create_task(run_social_logic())

                    # Mensaje de bienvenida
                    first = db.is_first_contact(contact_wa_id, line_id)
                    if first and channel.get("welcome_active") and channel.get("welcome_message"):
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
        return JSONResponse({"status": "ok"})
    except Exception as e:
        import traceback
        print(f"[Webhook POST] ❌ Error procesando el webhook: {e}")
        traceback.print_exc()
        return JSONResponse({"status": "error", "detail": str(e)})

async def execute_workflows_for_message(wa_id: str, line_id: int, line: dict, text: str, tenant_id: int):
    """Evalúa y ejecuta flujos de trabajo automáticos en segundo plano basados en palabras clave."""
    from database import db
    from whatsapp_client import wa_client
    import asyncio

    # Pequeña espera para asegurar consistencia en la base de datos
    await asyncio.sleep(1.5)
    
    workflows = db.get_workflows(tenant_id)
    text_lower = text.strip().lower()
    
    for w in workflows:
        if not w.get("is_active", True):
            continue
        if w["trigger_type"] == "message_received" and w["condition_field"] == "body_contains":
            keyword = w["condition_value"].lower()
            if keyword in text_lower:
                action = w["action_type"]
                act_val = w["action_value"]
                
                if action == "reply":
                    if line and line.get("is_active"):
                        r = wa_client.send_text_message(line, wa_id, act_val)
                        if r:
                            db.save_message(
                                wa_id, "OUTBOUND_REPLY", act_val,
                                agent_username="[Regla Auto]",
                                line_id=line_id, tenant_id=tenant_id
                            )
                elif action == "assign":
                    db.assign_conversation(wa_id, line_id, act_val, tenant_id)
                elif action == "set_lifecycle":
                    db.update_contact_lifecycle(wa_id, act_val, tenant_id)

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
    
    # 4. Obtener e inyectar conocimiento del agente (RAG)
    knowledge_list = db.get_agent_knowledge(agent["id"], tenant_id)
    knowledge_context = ""
    if knowledge_list:
        knowledge_context = "\n\n[CONOCIMIENTO OFICIAL DE LA EMPRESA (Usa esto para responder)]\n"
        for k in knowledge_list:
            knowledge_context += f"\n--- Fuente: {k['name']} ---\n{k['content']}\n"
        knowledge_context += "\n------------------------------------------------------\n"
        knowledge_context += "Responde al cliente de forma natural usando únicamente la información de arriba. Si la pregunta no se puede contestar con esa información, indícale de forma muy cortés que lo vas a comunicar con un asesor humano (no inventes información)."
    
    system_prompt = agent["system_prompt"] + knowledge_context

    # 5. Generar respuesta con Gemini
    ai_reply = gemini.generate_agent_reply(system_prompt, history)
    if ai_reply:
        # 6. Enviar la respuesta usando el canal correcto (WhatsApp o Messenger/Instagram)
        channel_type = line.get("channel_type", "whatsapp")
        sent = False
        
        if channel_type == "whatsapp":
            r = wa_client.send_text_message(line, wa_id, ai_reply)
            sent = bool(r)
        else:
            from meta_client import meta_client
            r = meta_client.send_message(line, wa_id, ai_reply)
            sent = bool(r)
            
        if sent:
            # 7. Guardar en BD
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

app.add_page(landing_page,       route="/",          title="Nyme — Inteligencia Omnicanal")
app.add_page(login_page,         route="/login",     title="Nyme — Iniciar Sesión")
app.add_page(privacy_page,       route="/privacy",   title="Nyme — Política de Privacidad")
app.add_page(terms_page,         route="/terms",     title="Nyme — Términos del Servicio")
app.add_page(data_deletion_page, route="/data-deletion", title="Nyme — Eliminación de Datos")
app.add_page(chat_page,          route="/chat",      title="Nyme — WhatsApp")
app.add_page(contacts_page,      route="/contacts",  title="Nyme — Directorio")
app.add_page(internal_chat_page, route="/internal",  title="Nyme — Equipo")
app.add_page(settings_page,      route="/settings",  title="Nyme — Config")
app.add_page(reports_page,       route="/reports",   title="Nyme — Reportes")
app.add_page(orders_page,        route="/orders",    title="Nyme — Ventas")

# Montar webhook dentro del FastAPI/Starlette interno de Reflex
app._api.add_route("/webhook", webhook_get,  methods=["GET"])
app._api.add_route("/webhook", webhook_post, methods=["POST"])

# Endpoints de Chat Web (Fase 3)
async def webchat_widget(request: Request):
    # Genera el JS para inyectar la burbuja de chat
    js_content = """
    (function() {
        // Crear estilos
        var style = document.createElement('style');
        style.innerHTML = `
            #nyme-chat-trigger {
                position: fixed; bottom: 20px; right: 20px;
                width: 60px; height: 60px; border-radius: 50%;
                background: #30d158; color: white; display: flex;
                align-items: center; justify-content: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                cursor: pointer; z-index: 999999; font-size: 28px;
                transition: transform 0.2s ease;
            }
            #nyme-chat-trigger:hover { transform: scale(1.05); }
            #nyme-chat-box {
                position: fixed; bottom: 90px; right: 20px;
                width: 350px; height: 450px; border-radius: 12px;
                background: #111; border: 1px solid #2c2c2e;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);
                display: none; flex-direction: column;
                z-index: 999999; overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            #nyme-chat-header {
                background: #1c1c1e; color: white; padding: 16px;
                font-weight: bold; border-bottom: 1px solid #2c2c2e;
                display: flex; align-items: center; justify-content: space-between;
            }
            #nyme-chat-body {
                flex: 1; padding: 12px; overflow-y: auto;
                background: #000; display: flex; flex-direction: column; gap: 8px;
            }
            .nyme-msg {
                max-width: 80%; padding: 8px 12px; border-radius: 12px;
                font-size: 14px; line-height: 1.4; color: white;
            }
            .nyme-msg-in { background: #2c2c2e; align-self: flex-start; }
            .nyme-msg-out { background: #30d158; align-self: flex-end; }
            #nyme-chat-footer {
                padding: 10px; background: #1c1c1e; border-top: 1px solid #2c2c2e;
                display: flex; gap: 6px;
            }
            #nyme-chat-input {
                flex: 1; background: #2c2c2e; border: 1px solid #3a3a3c;
                border-radius: 6px; padding: 8px; color: white; outline: none; font-size: 14px;
            }
            #nyme-chat-send {
                background: #30d158; border: none; border-radius: 6px;
                padding: 8px 14px; color: white; cursor: pointer; font-weight: bold;
            }
        `;
        document.head.appendChild(style);

        // Identificador del cliente
        var clientWaId = localStorage.getItem('nyme_client_wa_id');
        if (!clientWaId) {
            clientWaId = 'web_' + Math.random().toString(36).substring(2, 10);
            localStorage.setItem('nyme_client_wa_id', clientWaId);
        }
        var clientName = localStorage.getItem('nyme_client_name') || 'Visitante Web';

        // Crear elementos UI
        var trigger = document.createElement('div');
        trigger.id = 'nyme-chat-trigger';
        trigger.innerHTML = '💬';
        document.body.appendChild(trigger);

        var chatBox = document.createElement('div');
        chatBox.id = 'nyme-chat-box';
        chatBox.innerHTML = `
            <div id="nyme-chat-header">
                <span>PixArtM Soporte</span>
                <span id="nyme-chat-close" style="cursor:pointer;">✕</span>
            </div>
            <div id="nyme-chat-body"></div>
            <div id="nyme-chat-footer">
                <input type="text" id="nyme-chat-input" placeholder="Escribe tu duda aquí...">
                <button id="nyme-chat-send">Enviar</button>
            </div>
        `;
        document.body.appendChild(chatBox);

        // Acciones click
        trigger.onclick = function() {
            var display = chatBox.style.display;
            chatBox.style.display = display === 'flex' ? 'none' : 'flex';
            if (chatBox.style.display === 'flex') {
                loadMessages();
            }
        };

        document.getElementById('nyme-chat-close').onclick = function() {
            chatBox.style.display = 'none';
        };

        // Enviar mensaje
        var input = document.getElementById('nyme-chat-input');
        var sendBtn = document.getElementById('nyme-chat-send');
        
        function sendMessage() {
            var text = input.value.trim();
            if (!text) return;
            
            input.value = '';
            
            // Render local de inmediato
            var body = document.getElementById('nyme-chat-body');
            var msgDiv = document.createElement('div');
            msgDiv.className = 'nyme-msg nyme-msg-out';
            msgDiv.innerText = text;
            body.appendChild(msgDiv);
            body.scrollTop = body.scrollHeight;

            fetch('/api/webchat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wa_id: clientWaId, name: clientName, body: text, tenant_id: 1 })
            }).then(() => {
                setTimeout(loadMessages, 500);
            });
        }

        sendBtn.onclick = sendMessage;
        input.onkeypress = function(e) {
            if (e.key === 'Enter') sendMessage();
        };

        // Polling de mensajes
        function loadMessages() {
            if (chatBox.style.display !== 'flex') return;
            fetch('/api/webchat/messages?wa_id=' + clientWaId + '&tenant_id=1')
                .then(r => r.json())
                .then(msgs => {
                    var body = document.getElementById('nyme-chat-body');
                    body.innerHTML = '';
                    msgs.forEach(m => {
                        var msgDiv = document.createElement('div');
                        msgDiv.className = 'nyme-msg ' + (m.type === 'INBOUND' ? 'nyme-msg-out' : 'nyme-msg-in');
                        msgDiv.innerText = m.body;
                        body.appendChild(msgDiv);
                    });
                    body.scrollTop = body.scrollHeight;
                });
        }

        setInterval(loadMessages, 4000);
    })();
    """
    return PlainTextResponse(js_content, media_type="application/javascript")

async def webchat_send(request: Request):
    from database import db
    try:
        data = await request.json()
        wa_id = data.get("wa_id")
        name = data.get("name", "Visitante Web")
        body = data.get("body", "")
        tenant_id = data.get("tenant_id", 1)
        
        if not wa_id or not body:
            return JSONResponse({"status": "error", "message": "Missing arguments"}, status_code=400)
            
        db.upsert_contact(wa_id, name, "", "Origen: Chat Web", tenant_id)
        db.save_message(wa_id, "INBOUND", body, line_id=0, tenant_id=tenant_id)
        db.mark_conversation_unread(wa_id, 0)
        
        # Disparar respondedor de IA automático para chat web
        import asyncio
        asyncio.create_task(
            run_ai_agent_responder(wa_id, 0, {}, body, tenant_id)
        )
        asyncio.create_task(
            execute_workflows_for_message(wa_id, 0, {}, body, tenant_id)
        )
        
        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

async def webchat_messages(request: Request):
    from database import db
    params = request.query_params
    wa_id = params.get("wa_id")
    tenant_id = int(params.get("tenant_id", "1"))
    if not wa_id:
        return JSONResponse([], status_code=400)
    raw = db.get_messages(wa_id, tenant_id)
    msgs = [
        {
            "type": m[0],
            "body": m[1],
            "time": m[2].strftime("%H:%M") if m[2] else "",
            "agent": m[3] or ""
        }
        for m in raw
    ]
    return JSONResponse(msgs)

app._api.add_route("/api/webchat/widget.js", webchat_widget, methods=["GET"])
app._api.add_route("/api/webchat/send", webchat_send, methods=["POST"])
app._api.add_route("/api/webchat/messages", webchat_messages, methods=["GET"])

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
