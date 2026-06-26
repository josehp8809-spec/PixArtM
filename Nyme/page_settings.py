import streamlit as st
from database import db
from gemini_client import gemini


ROLE_LABELS = {
    "admin":       "🔴 Admin",
    "coordinator": "🟡 Coordinador",
    "agent":       "🟢 Agente",
}
ROLE_LIMITS = {"admin": 2, "coordinator": 3, "agent": 10}


def render():
    st.title("⚙️ Configuración")

    role = st.session_state.get("role", "agent")

    if role == "admin":
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👥 Usuarios", "📱 Líneas WhatsApp",
            "⚡ Respuestas Rápidas", "🤖 Gemini AI", "🔑 Mi Cuenta",
        ])
        with tab1: _user_management()
        with tab2: _lines_management()
        with tab3: _quick_replies()
        with tab4: _gemini_config()
        with tab5: _my_account()
    else:
        # Coordinadores y agentes solo ven Mi Cuenta
        _my_account()


def _my_account():
    st.subheader("🔑 Cambiar contraseña")
    username = st.session_state.get("username", "")
    with st.form("form_pwd"):
        new_pwd  = st.text_input("Nueva contraseña", type="password")
        new_pwd2 = st.text_input("Confirmar nueva contraseña", type="password")
        if st.form_submit_button("💾 Cambiar contraseña", use_container_width=True):
            if not new_pwd or len(new_pwd) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif new_pwd != new_pwd2:
                st.error("Las contraseñas no coinciden.")
            else:
                if db.change_password(username, new_pwd):
                    st.success("✅ Contraseña actualizada correctamente.")
                else:
                    st.error("❌ Error al actualizar la contraseña.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Gestión de Usuarios
# ─────────────────────────────────────────────────────────────────────────────

def _user_management():
    st.subheader("👥 Gestión de Usuarios")

    # ── Capacidad actual ──
    col1, col2, col3 = st.columns(3)
    with col1:
        c = db.count_users_by_role("admin")
        st.metric("🔴 Admins", f"{c} / {ROLE_LIMITS['admin']}")
    with col2:
        c = db.count_users_by_role("coordinator")
        st.metric("🟡 Coordinadores", f"{c} / {ROLE_LIMITS['coordinator']}")
    with col3:
        c = db.count_users_by_role("agent")
        st.metric("🟢 Agentes", f"{c} / {ROLE_LIMITS['agent']}")

    st.markdown("---")

    # ── Lista de usuarios ──
    users = db.get_all_users()

    if not users:
        st.info("No hay usuarios registrados aún.")
    else:
        st.markdown("#### Usuarios registrados")
        for uid, username, full_name, role, is_active, created_at in users:
            # No mostrar el usuario actual para evitar auto-desactivación
            is_self = username == st.session_state.get("username", "")
            status  = "✅ Activo" if is_active else "⛔ Inactivo"
            date_str = created_at.strftime("%d/%m/%Y") if created_at else ""

            c1, c2, c3, c4 = st.columns([2.5, 2, 1.5, 1])
            with c1:
                st.markdown(f"**{full_name or username}**  \n`@{username}`")
            with c2:
                st.markdown(f"{ROLE_LABELS.get(role, role)}  \n{status}")
            with c3:
                if not is_self:
                    lbl = "Desactivar" if is_active else "Activar"
                    btn_type = "secondary" if is_active else "primary"
                    if st.button(lbl, key=f"tog_{uid}", type=btn_type):
                        db.toggle_user_active(uid, not is_active)
                        st.rerun()
                else:
                    st.caption("(tú mismo)")
            with c4:
                st.caption(date_str)
            st.divider()

    # ── Formulario de creación ──
    st.markdown("#### ➕ Crear nuevo usuario")
    with st.form("form_create_user", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Nombre completo *")
            username  = st.text_input("Nombre de usuario * (sin espacios)")
        with c2:
            role     = st.selectbox(
                "Rol *",
                ["agent", "coordinator", "admin"],
                format_func=lambda x: ROLE_LABELS[x],
            )
            password = st.text_input("Contraseña temporal *", type="password")

        submitted = st.form_submit_button("✅ Crear usuario", use_container_width=True)

    if submitted:
        errors = []
        if not full_name.strip():
            errors.append("El nombre completo es obligatorio.")
        if not username.strip() or " " in username:
            errors.append("El usuario no puede estar vacío ni tener espacios.")
        if len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            ok, msg = db.create_user(username.lower().strip(), password, full_name.strip(), role)
            if ok:
                st.success(f"✅ Usuario **@{username}** creado como {ROLE_LABELS[role]}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")


# ───────────────────────────────────────────────────────────────────────────────
# TAB 2 — Líneas WhatsApp
# ───────────────────────────────────────────────────────────────────────────────

def _lines_management():
    from whatsapp_client import wa_client
    st.subheader("📱 Líneas de WhatsApp")
    st.caption(f"Máximo 5 líneas. Activas: {db.count_lines()}/5")

    lines = db.get_all_lines()   # (id, name, phone_number_id, token, welcome_msg, welcome_active, color, is_active)

    # ── Lista de líneas existentes ───────────────────────────────────────────
    if not lines:
        st.info("ℹ️ No hay líneas configuradas. Agrega la primera abajo.")
    else:
        st.markdown("#### Líneas configuradas")
        for lid, name, phone_id, token, welcome_msg, welcome_active, color, is_active in lines:
            masked_token = f"{'•'*20}...{token[-4:]}" if token else "—"
            status_icon  = "✅ Activa" if is_active else "⛔ Inactiva"
            col1, col2, col3, col4 = st.columns([2.5, 2, 1.5, 1])
            with col1:
                st.markdown(f"**{name}**  ")  
                st.caption(f"📱 `{phone_id}`")
            with col2:
                st.caption(f"Token: `{masked_token}`")
                st.caption("👋 Bienvenida activa" if welcome_active else "🔕 Bienvenida inactiva")
            with col3:
                st.markdown(status_icon)
                # Probar conexión
                if st.button("🔍 Probar", key=f"test_{lid}"):
                    line_dict = {"phone_number_id": phone_id, "access_token": token}
                    ok, msg = wa_client.test_line(line_dict)
                    if ok:
                        st.success(f"✅ Conectada: {msg}")
                    else:
                        st.error(f"❌ {msg}")
            with col4:
                if is_active:
                    if st.button("Desactivar", key=f"deact_line_{lid}", type="secondary"):
                        db.toggle_line_active(lid, False); st.rerun()
                else:
                    if st.button("Activar", key=f"act_line_{lid}", type="primary"):
                        db.toggle_line_active(lid, True); st.rerun()

            # Asignación de agentes
            all_users = db.get_all_users()
            agents    = [(u[0], u[1], u[2]) for u in all_users if u[3] == "agent"]
            if agents:
                with st.expander(f"👥 Agentes asignados a {name}"):
                    for uid, username, full_name in agents:
                        assigned_lines = db.get_user_lines(uid)
                        currently = lid in assigned_lines
                        new_val = st.checkbox(
                            f"@{username} — {full_name}",
                            value=currently,
                            key=f"assign_{lid}_{uid}"
                        )
                        if new_val != currently:
                            if new_val:
                                db.assign_user_to_line(uid, lid)
                            else:
                                db.remove_user_from_line(uid, lid)
                            st.rerun()
            st.divider()

    # ── Formulario de nueva línea ────────────────────────────────────────────
    if db.count_lines() < 5:
        st.markdown("#### ➕ Agregar nueva línea")
        with st.form("form_new_line", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                line_name   = st.text_input("Nombre de la línea *", placeholder="Ventas / Soporte")
                phone_id    = st.text_input("Phone Number ID (Meta) *")
                color       = st.color_picker("Color identificador", "#0A84FF")
            with c2:
                token       = st.text_input("Access Token (Meta) *", type="password")
                welcome_msg = st.text_area("Mensaje de bienvenida",
                                           placeholder="¡Hola! Bienvenido a [Empresa]. ¿En qué te ayudamos?")
                welcome_on  = st.checkbox("✅ Activar bienvenida automática", value=True)
            save = st.form_submit_button("💾 Guardar línea", use_container_width=True)

        if save:
            if not line_name or not phone_id or not token:
                st.error("Nombre, Phone ID y Token son obligatorios.")
            else:
                ok, err = db.create_line(line_name, phone_id, token, welcome_msg, welcome_on, color)
                if ok:
                    st.success(f"✅ Línea '{line_name}' creada.")
                    st.rerun()
                else:
                    st.error(f"❌ {err}")
    else:
        st.warning("🚧 Límite de 5 líneas alcanzado.")


# ───────────────────────────────────────────────────────────────────────────────
# TAB 3 — Respuestas Rápidas (compartidas)
# ───────────────────────────────────────────────────────────────────────────────

def _quick_replies():
    st.subheader("⚡ Respuestas Rápidas")
    st.caption("Atajos compartidos para todas las líneas. En el chat, escribe `/` para verlos.")

    qrs = db.get_quick_replies()

    if not qrs:
        st.info("No hay atajos configurados.")
    else:
        st.markdown("#### Atajos actuales")
        for qr_id, shortcut, title, message in qrs:
            c1, c2, c3, c4 = st.columns([1.2, 1.8, 3, 0.8])
            with c1: st.code(shortcut)
            with c2: st.write(title or "—")
            with c3: st.caption(message[:120] + ("..." if len(message) > 120 else ""))
            with c4:
                if st.button("🗑️", key=f"del_qr_{qr_id}", help="Eliminar"):
                    db.delete_quick_reply(qr_id); st.rerun()
        st.divider()

    st.markdown("#### ➕ Nuevo atajo")
    with st.form("form_qr", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            shortcut = st.text_input("Atajo *", placeholder="/hola")
            title    = st.text_input("Título", placeholder="Saludo de bienvenida")
        with c2:
            message  = st.text_area("Mensaje completo *",
                                    placeholder="¡Hola! ¿En qué te puedo ayudar hoy? 😊")
        save = st.form_submit_button("✅ Guardar atajo", use_container_width=True)

    if save:
        if not shortcut.strip() or not message.strip():
            st.error("Atajo y mensaje son obligatorios.")
        elif not shortcut.startswith("/"):
            st.error("El atajo debe comenzar con /")
        else:
            ok, err = db.create_quick_reply(shortcut.strip(), title.strip(), message.strip())
            if ok:
                st.success(f"✅ Atajo `{shortcut}` creado.")
                st.rerun()
            else:
                st.error(f"❌ {err}")


# ───────────────────────────────────────────────────────────────────────────────
# TAB 4 — Gemini AI
# ───────────────────────────────────────────────────────────────────────────────

def _gemini_config():
    st.subheader("🤖 Asistente Gemini AI")
    st.markdown("La API Key es **compartida** para todos los agentes y coordinadores.")

    current_key = db.get_setting("gemini_api_key", "")

    # Estado visual
    if current_key:
        masked = f"{'•' * 28}...{current_key[-4:]}"
        st.success(f"🟢 API Key activa: `{masked}`")
    else:
        st.warning("🟡 Sin API Key — El asistente Gemini está desactivado.")

    st.markdown("---")

    # ── Formulario para guardar/actualizar la key ──
    with st.form("form_gemini_key"):
        new_key = st.text_input(
            "API Key de Gemini",
            type="password",
            placeholder="AIza...",
            help="Obtén tu key gratis en https://aistudio.google.com/app/apikey",
        )
        save_btn = st.form_submit_button("💾 Guardar API Key", use_container_width=True)

    if save_btn:
        if not new_key.strip():
            st.error("La key no puede estar vacía.")
        else:
            db.set_setting("gemini_api_key", new_key.strip())
            st.success("✅ API Key guardada correctamente.")
            st.rerun()

    # ── Prueba de conexión ──
    if current_key:
        st.markdown("---")
        st.markdown("#### 🔍 Probar conexión")
        if st.button("Enviar prueba a Gemini"):
            with st.spinner("Conectando con Gemini..."):
                result = gemini.translate("Hello, this is a connection test.", "español")
            if result:
                st.success(f"✅ Conexión exitosa.  \n**Resultado:** _{result}_")
            else:
                st.error(
                    "❌ No se pudo conectar. Verifica que la API Key sea válida "
                    "y que el paquete `google-generativeai` esté instalado."
                )

    # ── Información de funciones ──
    st.markdown("---")
    st.markdown("#### 🛠️ Funciones disponibles en el chat")
    st.markdown(
        """
| Función | Descripción |
|---|---|
| 🌐 **Traducir** | Detecta el idioma y traduce el mensaje al español |
| ✨ **Sugerir respuesta** | Genera una respuesta basada en el historial del chat |
| ✅ **Mejorar texto** | Corrige ortografía y tono antes de enviar |
        """
    )
