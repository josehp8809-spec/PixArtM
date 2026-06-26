import streamlit as st
import time
from database import db
from whatsapp_client import wa_client
from gemini_client import gemini

# Estado de conversación
STATUS_ICONS  = {"pending": "⏳", "active": "🟡", "resolved": "✅"}
STATUS_LABELS = {"pending": "Pendiente", "active": "En curso", "resolved": "Resuelto"}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _line_badge(line_id, lines_map, short=False):
    """Retorna un string con el nombre e ícono de la línea."""
    line = lines_map.get(line_id)
    if not line:
        return ""
    name = line["name"]
    return f"[{name[:10]}]" if short else f"📱 {name}"


def _load_lines_map():
    """Devuelve dict {line_id: line_dict} para lookup rápido."""
    lines = db.get_all_lines()
    result = {}
    for lid, name, phone_id, token, welcome_msg, welcome_active, color, is_active in lines:
        result[lid] = {
            "id": lid, "name": name, "phone_number_id": phone_id,
            "access_token": token, "welcome_message": welcome_msg,
            "welcome_active": welcome_active, "color": color, "is_active": is_active,
        }
    return result


# ─────────────────────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def render():
    role    = st.session_state.get("role", "agent")
    user_id = st.session_state.get("user_id")
    lines_map = _load_lines_map()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.subheader("📥 Conversaciones")

        auto_ref = st.toggle("🔄 Auto-actualizar (8s)", value=True, key="auto_refresh")

        if len(lines_map) > 1:
            line_filter_options = ["Todas"] + [l["name"] for l in lines_map.values()]
            line_filter = st.selectbox("Línea:", line_filter_options,
                                       label_visibility="collapsed")
        else:
            line_filter = "Todas"

        # (wa_id, last_msg, line_id, status, unread)
        contacts_raw = db.get_contacts_for_user(user_id, role)

        if line_filter != "Todas":
            target_lid = next(
                (lid for lid, l in lines_map.items() if l["name"] == line_filter), None
            )
            contacts_raw = [c for c in contacts_raw if c[2] == target_lid]

        if not contacts_raw:
            st.info("Sin conversaciones.")
            st.session_state.selected_contact = None
            st.session_state.selected_line_id = None
        else:
            labels = []
            for wa_id, _, line_id, status, unread in contacts_raw:
                badge      = _line_badge(line_id, lines_map, short=True)
                unread_str = f" 🔴{unread}" if unread > 0 else ""
                s_icon     = STATUS_ICONS.get(status, "⏳")
                labels.append(f"{s_icon} +{wa_id} {badge}{unread_str}")

            idx = st.radio(
                "Chats:",
                range(len(contacts_raw)),
                format_func=lambda i: labels[i],
                label_visibility="collapsed",
                key="contact_radio",
            )
            st.session_state.selected_contact = contacts_raw[idx][0]
            st.session_state.selected_line_id = contacts_raw[idx][2]

    # ── Auto-refresh polling ──────────────────────────────────────────────────
    if auto_ref:
        time.sleep(8)
        st.rerun()

    # ── Área principal ────────────────────────────────────────────────────────
    contact = st.session_state.get("selected_contact")
    line_id = st.session_state.get("selected_line_id")

    if not contact:
        _empty_state()
    else:
        db.mark_conversation_read(contact, line_id)
        _chat_view(contact, line_id, lines_map)


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO VACÍO
# ─────────────────────────────────────────────────────────────────────────────

def _empty_state():
    st.markdown("<br>" * 5, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("https://img.icons8.com/fluency/96/whatsapp.png", width=80)
        st.markdown("## Nyme — Panel de Atención")
        st.markdown("Selecciona una conversación del panel izquierdo.")


# ─────────────────────────────────────────────────────────────────────────────
# VISTA DE CHAT
# ─────────────────────────────────────────────────────────────────────────────

def _chat_view(contact, line_id, lines_map):
    line      = lines_map.get(line_id)
    line_name = line["name"] if line else "Línea desconocida"
    line_color = line["color"] if line else "#888"

    # ── Encabezado con badge de línea ──────────────────────────────────────
    col_title, col_status, col_info = st.columns([2.5, 1.5, 1])
    with col_title:
        st.markdown(
            f"## 📱 +{contact} "
            f"<span style='font-size:14px; background:{line_color}22; "
            f"color:{line_color}; border:1px solid {line_color}; "
            f"border-radius:8px; padding:2px 10px;'>📱 {line_name}</span>",
            unsafe_allow_html=True,
        )
    with col_status:
        # Selector de estado de la conversación
        current_statuses = db.get_contacts_for_user(
            st.session_state.get("user_id"), st.session_state.get("role")
        )
        cur_status = next(
            (c[3] for c in current_statuses if c[0] == contact and c[2] == line_id),
            "pending"
        )
        status_options = list(STATUS_LABELS.keys())
        status_idx = status_options.index(cur_status) if cur_status in status_options else 0
        new_status = st.selectbox(
            "Estado:",
            status_options,
            index=status_idx,
            format_func=lambda s: f"{STATUS_ICONS[s]} {STATUS_LABELS[s]}",
            key=f"status_{contact}_{line_id}",
            label_visibility="collapsed",
        )
        if new_status != cur_status:
            db.set_conversation_status(contact, line_id, new_status)
            st.rerun()
    with col_info:
        if gemini.is_configured:
            st.caption("🤖 Gemini activo")
        else:
            st.caption("🤖 Gemini inactivo")

    st.markdown("---")

    # ── Historial de mensajes ──────────────────────────────────────────────
    history = db.get_messages(contact)
    # Cada elemento: (type, body, created_at, agent_username, line_id)

    chat_box = st.container(height=400)
    with chat_box:
        if not history:
            st.info("Aún no hay mensajes en esta conversación.")
        for i, row in enumerate(history):
            msg_type, body, timestamp, agent, msg_line_id = row
            time_str  = timestamp.strftime("%H:%M") if timestamp else ""
            msg_badge = _line_badge(msg_line_id, lines_map, short=True)

            if msg_type == "INBOUND":
                with st.chat_message("user"):
                    st.write(body)
                    # Botón traducir si Gemini está activo
                    if gemini.is_configured:
                        if st.button("🌐 Traducir", key=f"trans_{contact}_{i}"):
                            with st.spinner("Detectando idioma..."):
                                lang = gemini.detect_language(body)
                            if lang != "español":
                                with st.spinner("Traduciendo..."):
                                    translated = gemini.translate(body)
                                if translated:
                                    st.info(f"🌐 **{lang.capitalize()} → Español:** {translated}")
                            else:
                                st.info("ℹ️ El mensaje ya está en español.")
                    st.caption(f"🕐 {time_str}  ·  Cliente  {msg_badge}")
            else:
                with st.chat_message("assistant"):
                    st.write(body)
                    agent_lbl = f"@{agent}" if agent else "Sistema"
                    st.caption(f"🕐 {time_str}  ✓  {agent_lbl}  {msg_badge}")

    # ── Herramientas de IA ────────────────────────────────────────────────
    if gemini.is_configured and history:
        with st.expander("✨ Herramientas de IA", expanded=False):
            g1, g2 = st.columns(2)
            with g1:
                if st.button("✨ Sugerir respuesta", use_container_width=True):
                    with st.spinner("Generando sugerencia..."):
                        suggestion = gemini.suggest_reply(history)
                    if suggestion:
                        st.session_state.draft_message = suggestion
                        st.success(f"💡 _{suggestion}_")
                    else:
                        st.error("No se pudo generar una sugerencia.")
            with g2:
                draft = st.session_state.get("draft_message", "")
                if draft and st.button("✅ Mejorar borrador", use_container_width=True):
                    with st.spinner("Mejorando..."):
                        improved = gemini.improve_text(draft)
                    if improved:
                        st.session_state.draft_message = improved
                        st.success(f"✅ _{improved}_")
                        st.rerun()

    # ── Respuestas rápidas ────────────────────────────────────────────────
    qrs = db.get_quick_replies()   # [(id, shortcut, title, message), ...]
    if qrs:
        with st.expander("⚡ Respuestas rápidas", expanded=False):
            qr_labels = {f"{qr[1]}  —  {qr[2] or qr[3][:40]}": qr[3] for qr in qrs}
            selected_qr = st.selectbox(
                "Selecciona un atajo:",
                ["— Elige un atajo —"] + list(qr_labels.keys()),
                label_visibility="collapsed",
                key=f"qr_select_{contact}",
            )
            if selected_qr != "— Elige un atajo —":
                qr_text = qr_labels[selected_qr]
                st.text_area("Vista previa (editable):", value=qr_text,
                             key=f"qr_preview_{contact}", height=80)
                if st.button("📤 Enviar este atajo", use_container_width=True,
                             key=f"send_qr_{contact}"):
                    _send_message(contact, line_id, line, qr_text)

    # ── Input de mensaje ──────────────────────────────────────────────────
    st.markdown("---")
    msg = st.chat_input("Escribe tu respuesta...")
    if msg:
        _send_message(contact, line_id, line, msg)


# ─────────────────────────────────────────────────────────────────────────────
# ENVÍO DE MENSAJES
# ─────────────────────────────────────────────────────────────────────────────

def _send_message(contact, line_id, line, text):
    """Envía un mensaje por la línea correspondiente y lo guarda en DB."""
    username = st.session_state.get("username")

    if not line or not line.get("is_active"):
        # Sin línea configurada → modo simulación
        db.save_message(contact, "OUTBOUND_REPLY", text,
                        agent_username=username, line_id=line_id)
        st.toast("Guardado en modo simulación (línea no configurada)", icon="⚠️")
        st.rerun()
        return

    with st.spinner("Enviando..."):
        result = wa_client.send_text_message(line, contact, text)

    if result:
        db.save_message(contact, "OUTBOUND_REPLY", text,
                        agent_username=username, line_id=line_id)
        st.rerun()
    else:
        st.error("❌ No se pudo enviar. Verifica el Token y Phone ID de la línea.")
