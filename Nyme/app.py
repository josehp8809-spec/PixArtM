import streamlit as st
import os
from dotenv import load_dotenv
from database import db
from whatsapp_client import wa_client
from gemini_client import gemini

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nyme | WhatsApp Platform",
    page_icon="💬",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #000000; color: #f5f5f7; }
section[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 1px solid #2c2c2e;
}
.stButton > button {
    border-radius: 10px; border: 1px solid #3a3a3c;
    background-color: #1c1c1e; color: #f5f5f7;
    font-family: 'Inter', sans-serif; transition: all 0.25s ease;
}
.stButton > button:hover { border-color: #0a84ff; color: #0a84ff; background-color: #0a84ff15; }
.stProgress > div > div { background-color: #0a84ff !important; }
.stForm { background-color: #111111 !important; border: 1px solid #2c2c2e; border-radius: 14px; padding: 24px; }
h1, h2, h3 { font-weight: 600; letter-spacing: -0.5px; }
.stTextInput > div > div > input, .stChatInput textarea {
    background-color: #1c1c1e !important; border: 1px solid #3a3a3c !important;
    color: #f5f5f7 !important; border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE SESIÓN
# ─────────────────────────────────────────────────────────────────────────────
def _init_session():
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": "",
        "full_name": "",
        "role": "",
        "current_page": "chat",
        "selected_contact": None,
        "selected_line_id": None,
        "db_initialized": False,
        "draft_message": None,
        "agent_feedbacks": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _do_login(username, password):
    user = db.verify_user(username, password)
    if user:
        st.session_state.authenticated = True
        st.session_state.user_id   = user["id"]
        st.session_state.username  = user["username"]
        st.session_state.full_name = user["full_name"] or user["username"]
        st.session_state.role      = user["role"]
        st.session_state.current_page = "chat"
        st.rerun()
    else:
        st.error("❌ Usuario o contraseña incorrectos, o cuenta inactiva.")

def _do_logout():
    for k in ["authenticated", "username", "full_name", "role", "current_page", "selected_contact"]:
        st.session_state[k] = "" if isinstance(st.session_state[k], str) else False if isinstance(st.session_state[k], bool) else None
    st.session_state.authenticated = False
    st.rerun()

def _bootstrap_admin():
    """Crea el primer admin desde variables de entorno si la tabla está vacía."""
    if db.user_exists():
        return
    user = os.getenv("ADMIN_USER", "admin")
    pwd  = os.getenv("ADMIN_PASSWORD", "admin123")
    ok, msg = db.create_user(user, pwd, "Administrador", "admin")
    if ok:
        print(f"[Bootstrap] Admin '{user}' creado automáticamente.")
    else:
        print(f"[Bootstrap] No se pudo crear admin: {msg}")

# ─────────────────────────────────────────────────────────────────────────────
# PANTALLA DE LOGIN
# ─────────────────────────────────────────────────────────────────────────────
def _render_login():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/fluency/96/whatsapp.png", width=64)
        st.markdown("## Nyme")
        st.markdown("##### Plataforma de atención al cliente vía WhatsApp")
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Usuario", placeholder="tu_usuario")
            pwd  = st.text_input("Contraseña", type="password", placeholder="••••••••")
            if st.form_submit_button("Iniciar sesión", use_container_width=True):
                _do_login(user.strip().lower(), pwd)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR PRINCIPAL (post-login)
# ─────────────────────────────────────────────────────────────────────────────
def _render_sidebar():
    role = st.session_state.role
    role_icons = {"admin": "👑", "coordinator": "📋", "agent": "💬"}

    with st.sidebar:
        st.markdown(f"### {role_icons.get(role,'👤')} {st.session_state.full_name}")
        st.caption(f"Rol: {role.capitalize()}")
        if st.button("Cerrar sesión", use_container_width=True):
            _do_logout()

        st.markdown("---")

        # Estado de servicios
        if db._check_available():
            st.success("🟢 Base de datos")
        else:
            st.error("🔴 Sin conexión a DB")

        if wa_client.is_configured:
            st.success("🟢 Meta API")
        else:
            st.warning("🟡 Meta API no configurada")

        if gemini.is_configured:
            st.success("🟢 Gemini AI activo")
        else:
            st.warning("🟡 Gemini AI inactivo")

        st.markdown("---")

        # Cuota mensual
        quota = db.get_quota_usage()
        pct   = min(quota / 15, 1.0)
        st.markdown(f"#### 📊 Cuota: {quota}/15")
        st.progress(pct)
        if quota >= 15:
            st.error("⚠️ Cuota agotada")
        elif quota >= 12:
            st.warning(f"Solo quedan {15-quota} mensajes proactivos")

        st.markdown("---")

        # Menú de navegación según rol
        pages = ["💬 Chat"]
        if role in ("admin", "coordinator"):
            pages.append("📊 Reportes")
        if role == "admin":
            pages.append("⚙️ Configuración")

        selected = st.radio("Navegación", pages, label_visibility="collapsed")

        page_map = {
            "💬 Chat":          "chat",
            "📊 Reportes":      "reports",
            "⚙️ Configuración": "settings",
        }
        st.session_state.current_page = page_map.get(selected, "chat")

# ─────────────────────────────────────────────────────────────────────────────
# ROUTER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
_init_session()

# Inicializar DB una sola vez por sesión
if not st.session_state.db_initialized:
    if db.init_db():
        _bootstrap_admin()
        st.session_state.db_initialized = True

# Redirigir a login si no está autenticado
if not st.session_state.authenticated:
    _render_login()
    st.stop()

# Sidebar siempre visible post-login
_render_sidebar()

# Verificar acceso por rol
page = st.session_state.current_page
role = st.session_state.role

if page == "settings" and role != "admin":
    st.error("🚫 Acceso denegado. Solo los administradores pueden acceder a esta sección.")
    st.stop()

if page == "reports" and role not in ("admin", "coordinator"):
    st.error("🚫 Acceso denegado.")
    st.stop()

# Renderizar la página correspondiente
if page == "chat":
    import page_chat
    page_chat.render()

elif page == "reports":
    import page_reports
    page_reports.render()

elif page == "settings":
    import page_settings
    page_settings.render()
