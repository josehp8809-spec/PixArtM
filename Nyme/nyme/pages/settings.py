"""Settings page — admin only."""
import reflex as rx
from nyme.state import AppState
from nyme.pages.navbar import navbar

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database import db
from whatsapp_client import wa_client
from gemini_client import gemini

# ── Funciones Auxiliares de Extracción de Texto para RAG ──
def extract_text_from_pdf(file_path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception as e:
        print(f"[PDF Extract] Error leyendo {file_path}: {e}")
        return ""

def extract_text_from_url(url: str) -> str:
    try:
        import requests
        from bs4 import BeautifulSoup
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Eliminar scripts y estilos que no aportan
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        print(f"[URL Extract] Error leyendo {url}: {e}")
        return ""


class SettingsState(AppState):
    # Variables para Onboarding de Facebook/Instagram (Opción 2)
    fb_discovered_channels: list[dict] = []
    fb_modal_open: bool = False
    fb_loading: bool = False
    fb_status_msg: str = ""

    # Nueva línea/canal
    nl_name: str = ""
    nl_phone_id: str = ""
    nl_token: str = ""
    nl_welcome: str = ""
    nl_welcome_on: bool = True
    nl_color: str = "#0A84FF"
    nl_channel_type: str = "whatsapp"
    nl_page_id: str = ""
    nl_app_id: str = ""
    nl_msg: str = ""
    editing_line_id: int = 0
    nl_tenant_id: int = 0
    selected_line_tenant_name: str = "SaaS Global"

    # Nuevo usuario
    nu_username: str = ""
    nu_fullname: str = ""
    nu_password: str = ""
    nu_role: str = "agent"
    selected_user_tenant_name: str = "SaaS Global"
    nu_msg: str = ""
    all_users: list[dict] = []

    # Gemini
    gemini_key: str = ""
    gemini_msg: str = ""

    @rx.var
    def is_gemini_configured(self) -> bool:
        return gemini.is_configured_for_tenant(self.tenant_id)

    # Quick reply form
    qr_shortcut: str = ""
    qr_title: str = ""
    qr_message: str = ""
    qr_msg: str = ""

    # Nueva empresa (Tenants)
    nt_name: str = ""
    nt_contact_name_1: str = ""
    nt_contact_email_1: str = ""
    nt_contact_phone_1: str = ""
    nt_contact_name_2: str = ""
    nt_contact_email_2: str = ""
    nt_contact_phone_2: str = ""
    nt_msg: str = ""
    all_tenants: list[dict] = []
    
    # Edición de empresa
    et_id: int = 0
    et_name: str = ""
    et_email: str = ""
    et_phone: str = ""
    et_website: str = ""
    et_notes: str = ""
    et_contact_name_1: str = ""
    et_contact_email_1: str = ""
    et_contact_phone_1: str = ""
    et_contact_name_2: str = ""
    et_contact_email_2: str = ""
    et_contact_phone_2: str = ""
    et_msg: str = ""
    et_editing: bool = False
    # Edición de contraseña de usuario
    eu_id: int = 0
    eu_new_password: str = ""
    eu_msg: str = ""
    eu_editing_id: int = 0  # id del usuario cuyo panel de edición está abierto

    # Formularios Fase 2
    selected_ai_line_name: str = "Todas las líneas"
    def set_selected_ai_line_name(self, v): self.selected_ai_line_name = v

    # ── Constructor de Flujos Conversacionales (Flows) ──
    flows: list[dict] = []
    new_flow_name: str = ""
    new_flow_steps: list[dict] = []
    flow_msg: str = ""
    step_text: str = ""
    step_action: str = "none"
    step_action_val: str = ""

    def set_new_flow_name(self, v): self.new_flow_name = v
    def set_step_text(self, v): self.step_text = v
    def set_step_action(self, v): self.step_action = v
    def set_step_action_val(self, v): self.step_action_val = v

    # ── Fuentes de Conocimiento (RAG) ──
    selected_knowledge_agent_id: int = 0
    selected_knowledge_agent_name: str = ""
    new_knowledge_url: str = ""
    agent_knowledge: list[dict] = []
    knowledge_msg: str = ""
    is_knowledge_modal_open: bool = False

    def set_new_knowledge_url(self, v): self.new_knowledge_url = v

    @rx.var
    def line_options_ai(self) -> list[str]:
        return ["Todas las líneas"] + [l["name"] for l in self.all_lines]

    @rx.var
    def tenant_options_for_user(self) -> list[str]:
        return [t["name"] for t in self.all_tenants]

    @rx.var
    def facebook_login_url(self) -> str:
        client_id = os.getenv("META_APP_ID", "")
        redirect_uri = os.getenv("META_REDIRECT_URI", "")
        return f"https://www.facebook.com/v19.0/dialog/oauth?client_id={client_id}&redirect_uri={redirect_uri}&scope=pages_show_list,pages_messaging,instagram_basic,instagram_manage_messages&response_type=code"

    def on_mount_settings(self):
        self.require_auth()
        self.detect_timezone()
        self._reload_users()
        self._load_core_data()
        if self.tenant_id == 1:
            self._reload_tenants()
            self.load_pending_registrations()
        
        # Procesar código de OAuth de Facebook si viene en los parámetros de la URL
        code = self.router.page.params.get("code")
        if code:
            return self.process_facebook_oauth_code(code)

    def process_facebook_oauth_code(self, code: str):
        self.fb_loading = True
        self.fb_status_msg = "Conectando con Facebook..."
        self.fb_modal_open = True
        yield
        
        # Leer credenciales del entorno
        client_id = os.getenv("META_APP_ID")
        client_secret = os.getenv("META_APP_SECRET")
        redirect_uri = os.getenv("META_REDIRECT_URI")
        
        if not client_id or not client_secret or not redirect_uri:
            self.fb_status_msg = "❌ Error: Configuración de Meta App incompleta en el servidor (.env)."
            self.fb_loading = False
            return
            
        from nyme.onboarding import meta_onboarding
        # Intercambiar código por token de larga duración
        user_token = meta_onboarding.exchange_code_for_long_lived_token(
            client_id, client_secret, redirect_uri, code
        )
        
        if not user_token:
            self.fb_status_msg = "❌ Error al autenticar con Facebook. Intente nuevamente."
            self.fb_loading = False
            return
            
        # Obtener páginas de Facebook e Instagram asociadas
        pages = meta_onboarding.get_pages_and_instagrams(user_token)
        if not pages:
            self.fb_status_msg = "⚠️ No se encontraron páginas de Facebook o cuentas de Instagram vinculadas en esta cuenta."
            self.fb_loading = False
            return
            
        self.fb_discovered_channels = pages
        self.fb_status_msg = f"✅ Se encontraron {len(pages)} canales disponibles. Seleccione los que desea activar:"
        self.fb_loading = False

    def activate_discovered_channel(self, channel_data: dict, activate_instagram: bool = False):
        self.fb_loading = True
        self.fb_status_msg = "Suscribiendo canal en Meta..."
        yield
        
        from nyme.onboarding import meta_onboarding
        
        page_id = channel_data["page_id"]
        access_token = channel_data["access_token"]
        name = channel_data["name"]
        
        # Suscribir la app a la página
        subscribed = meta_onboarding.subscribe_app_to_page(page_id, access_token)
        if not subscribed:
            self.fb_status_msg = f"❌ Error al suscribir la app a la página {name}."
            self.fb_loading = False
            return
            
        # Registrar o actualizar en base de datos
        if activate_instagram:
            if not channel_data.get("instagram_id"):
                self.fb_status_msg = "❌ Error: No hay cuenta de Instagram vinculada a esta página."
                self.fb_loading = False
                return
                
            ig_id = channel_data["instagram_id"]
            ig_name = f"{channel_data['instagram_username']} (Instagram)"
            ok, err = db.upsert_facebook_line(
                name=ig_name,
                page_id=ig_id,
                access_token=access_token,
                tenant_id=self.tenant_id,
                channel_type="instagram"
            )
        else:
            ok, err = db.upsert_facebook_line(
                name=f"{name} (Messenger)",
                page_id=page_id,
                access_token=access_token,
                tenant_id=self.tenant_id,
                channel_type="messenger"
            )
            
        if ok:
            self.fb_status_msg = f"✅ Canal '{name}' activado con éxito."
            self._load_core_data()
        else:
            self.fb_status_msg = f"❌ Error guardando el canal: {err}"
            
        self.fb_loading = False

    def close_fb_modal(self):
        self.fb_modal_open = False
        return rx.redirect("/settings")

    def _reload_users(self):
        raw = db.get_users_by_tenant(self.tenant_id)
        self.all_users = [
            {
                "id": u[0], "username": u[1], "full_name": u[2],
                "role": u[3], "active": bool(u[4]),
                "tenant_name": u[6] if len(u) > 6 else "",
                "tenant_id": u[7] if len(u) > 7 else self.tenant_id
            }
            for u in raw
        ]

    def _reload_tenants(self):
        raw = db.get_all_tenants()
        self.all_tenants = [
            {
                "id": t[0], "name": t[1], "active": bool(t[2]),
                "email": t[3] or "", "phone": t[4] or "",
                "website": t[5] or "", "notes": t[6] or "",
                "contact_name_1": t[7] or "" if len(t) > 7 else "",
                "contact_email_1": t[8] or "" if len(t) > 8 else "",
                "contact_phone_1": t[9] or "" if len(t) > 9 else "",
                "contact_name_2": t[10] or "" if len(t) > 10 else "",
                "contact_email_2": t[11] or "" if len(t) > 11 else "",
                "contact_phone_2": t[12] or "" if len(t) > 12 else ""
            }
            for t in raw
        ]

    def set_nt_name(self, v): self.nt_name = v
    def set_nt_contact_name_1(self, v): self.nt_contact_name_1 = v
    def set_nt_contact_email_1(self, v): self.nt_contact_email_1 = v
    def set_nt_contact_phone_1(self, v): self.nt_contact_phone_1 = v
    def set_nt_contact_name_2(self, v): self.nt_contact_name_2 = v
    def set_nt_contact_email_2(self, v): self.nt_contact_email_2 = v
    def set_nt_contact_phone_2(self, v): self.nt_contact_phone_2 = v

    def save_tenant(self):
        if not self.nt_name.strip():
            self.nt_msg = "❌ Nombre de empresa requerido."
            return
        ok, res = db.create_tenant(
            self.nt_name.strip(),
            contact_name_1=self.nt_contact_name_1,
            contact_email_1=self.nt_contact_email_1,
            contact_phone_1=self.nt_contact_phone_1,
            contact_name_2=self.nt_contact_name_2,
            contact_email_2=self.nt_contact_email_2,
            contact_phone_2=self.nt_contact_phone_2
        )
        if ok:
            self.nt_msg = f"✅ Empresa '{self.nt_name.strip()}' creada (ID: {res})."
            admin_uname = f"admin_{self.nt_name.strip().lower().replace(' ', '')[:20]}"
            db.create_user(admin_uname, "Nyme_2026", f"Admin {self.nt_name.strip()}", "admin", res)
            self.nt_name = ""
            self.nt_contact_name_1 = ""
            self.nt_contact_email_1 = ""
            self.nt_contact_phone_1 = ""
            self.nt_contact_name_2 = ""
            self.nt_contact_email_2 = ""
            self.nt_contact_phone_2 = ""
            self._reload_tenants()
        else:
            self.nt_msg = f"❌ {res}"

    def open_tenant_edit(self, t_id: int):
        """Abre el formulario de edición para una empresa."""
        t = next((x for x in self.all_tenants if x["id"] == t_id), None)
        if t:
            self.et_id = t_id
            self.et_name = t["name"]
            self.et_email = t["email"]
            self.et_phone = t["phone"]
            self.et_website = t["website"]
            self.et_notes = t["notes"]
            self.et_contact_name_1 = t.get("contact_name_1", "")
            self.et_contact_email_1 = t.get("contact_email_1", "")
            self.et_contact_phone_1 = t.get("contact_phone_1", "")
            self.et_contact_name_2 = t.get("contact_name_2", "")
            self.et_contact_email_2 = t.get("contact_email_2", "")
            self.et_contact_phone_2 = t.get("contact_phone_2", "")
            self.et_editing = True
            self.et_msg = ""

    def close_tenant_edit(self):
        self.et_editing = False
        self.et_msg = ""

    def set_et_name(self, v): self.et_name = v
    def set_et_email(self, v): self.et_email = v
    def set_et_phone(self, v): self.et_phone = v
    def set_et_website(self, v): self.et_website = v
    def set_et_notes(self, v): self.et_notes = v
    def set_et_contact_name_1(self, v): self.et_contact_name_1 = v
    def set_et_contact_email_1(self, v): self.et_contact_email_1 = v
    def set_et_contact_phone_1(self, v): self.et_contact_phone_1 = v
    def set_et_contact_name_2(self, v): self.et_contact_name_2 = v
    def set_et_contact_email_2(self, v): self.et_contact_email_2 = v
    def set_et_contact_phone_2(self, v): self.et_contact_phone_2 = v

    def save_tenant_edit(self):
        if not self.et_name.strip():
            self.et_msg = "❌ El nombre no puede estar vacío."
            return
        ok, err = db.update_tenant(
            self.et_id, self.et_name.strip(), self.et_email, self.et_phone, self.et_website, self.et_notes,
            self.et_contact_name_1, self.et_contact_email_1, self.et_contact_phone_1,
            self.et_contact_name_2, self.et_contact_email_2, self.et_contact_phone_2
        )
        if ok:
            self.et_msg = "✅ Empresa actualizada."
            self._reload_tenants()
        else:
            self.et_msg = f"❌ {err}"

    def delete_tenant_action(self, t_id: int):
        ok, err = db.delete_tenant(t_id)
        if ok:
            self.nt_msg = "✅ Empresa eliminada."
            self.et_editing = False
            self._reload_tenants()
        else:
            self.nt_msg = f"❌ {err}"

    # ── Líneas ────────────────────────────────────────────────────────────────
    def set_nl_name(self, v): self.nl_name = v
    def set_nl_phone_id(self, v): self.nl_phone_id = v
    def set_nl_token(self, v): self.nl_token = v
    def set_nl_welcome(self, v): self.nl_welcome = v
    def set_nl_welcome_on(self, v): self.nl_welcome_on = v
    def set_nl_color(self, v): self.nl_color = v
    def set_nl_channel_type(self, v): self.nl_channel_type = v
    def set_nl_page_id(self, v): self.nl_page_id = v
    def set_nl_app_id(self, v): self.nl_app_id = v
    def set_selected_line_tenant_name(self, v): self.selected_line_tenant_name = v

    def start_edit_line(self, line: dict):
        self.editing_line_id = line["id"]
        self.nl_name = line["name"]
        self.nl_phone_id = line["phone_number_id"]
        self.nl_token = line["access_token"]
        self.nl_welcome = line["welcome_message"]
        self.nl_welcome_on = line["welcome_active"]
        self.nl_color = line["color"]
        self.nl_channel_type = line["channel_type"]
        self.nl_page_id = line["page_id"]
        self.nl_app_id = line["app_id"]
        
        line_db = db.get_line_by_id(line["id"], self.tenant_id)
        if line_db:
            l_tenant_id = line_db.get("tenant_id", self.tenant_id)
            if self.tenant_id == 1:
                t = next((x for x in self.all_tenants if x["id"] == l_tenant_id), None)
                if t:
                    self.selected_line_tenant_name = t["name"]
                else:
                    self.selected_line_tenant_name = "SaaS Global"
            else:
                self.selected_line_tenant_name = self.tenant_name
        else:
            self.selected_line_tenant_name = self.tenant_name
        self.nl_msg = "✏️ Editando canal."

    def cancel_edit_line(self):
        self.editing_line_id = 0
        self.nl_name = ""
        self.nl_phone_id = ""
        self.nl_token = ""
        self.nl_welcome = ""
        self.nl_welcome_on = True
        self.nl_color = "#0A84FF"
        self.nl_channel_type = "whatsapp"
        self.nl_page_id = ""
        self.nl_app_id = ""
        self.selected_line_tenant_name = self.tenant_name
        self.nl_msg = ""

    def delete_line_action(self, line_id: int):
        ok, err = db.delete_line(line_id)
        if ok:
            self.nl_msg = "🗑️ Canal eliminado."
            if self.editing_line_id == line_id:
                self.cancel_edit_line()
            self._load_core_data()
        else:
            self.nl_msg = f"❌ {err}"

    def save_line(self):
        if not self.nl_name or not self.nl_token:
            self.nl_msg = "❌ Nombre y Token son obligatorios."
            return

        p_id = self.nl_phone_id
        page_id = self.nl_page_id

        if self.nl_channel_type == "whatsapp":
            if not p_id:
                self.nl_msg = "❌ Phone Number ID es obligatorio para WhatsApp."
                return
        else:
            if not page_id:
                self.nl_msg = "❌ ID de Página/Cuenta (Page ID) es obligatorio para redes sociales."
                return
            p_id = ""  # No se usa para Messenger/Instagram

        target_tenant_id = self.tenant_id
        if self.tenant_id == 1 and self.selected_line_tenant_name:
            tenant = next((t for t in self.all_tenants if t["name"] == self.selected_line_tenant_name), None)
            if tenant:
                target_tenant_id = tenant["id"]

        if self.editing_line_id > 0:
            # Edición
            ok, err = db.update_line(
                self.editing_line_id,
                self.nl_name, p_id, self.nl_token,
                self.nl_welcome, self.nl_welcome_on, self.nl_color,
                target_tenant_id, self.nl_channel_type, page_id, self.nl_app_id
            )
            if ok:
                self.nl_msg = "✅ Canal actualizado."
                self.cancel_edit_line()
                self._load_core_data()
            else:
                self.nl_msg = f"❌ {err}"
        else:
            # Creación
            ok, err = db.create_line(
                self.nl_name, p_id, self.nl_token,
                self.nl_welcome, self.nl_welcome_on, self.nl_color,
                target_tenant_id, self.nl_channel_type, page_id, self.nl_app_id
            )
            if ok:
                self.nl_msg = "✅ Canal creado."
                self.cancel_edit_line()
                self._load_core_data()
            else:
                self.nl_msg = f"❌ {err}"

    def toggle_line(self, line_id: int, active: bool):
        db.toggle_line_active(line_id, not active, self.tenant_id)
        self._load_core_data()

    # ── Usuarios ──────────────────────────────────────────────────────────────
    def set_nu_username(self, v): self.nu_username = v
    def set_nu_fullname(self, v): self.nu_fullname = v
    def set_nu_password(self, v): self.nu_password = v
    def set_nu_role(self, v): self.nu_role = v
    def set_selected_user_tenant_name(self, v): self.selected_user_tenant_name = v

    def save_user(self):
        if not self.nu_username or not self.nu_password:
            self.nu_msg = "❌ Usuario y contraseña requeridos."
            return
        
        target_tenant_id = self.tenant_id
        if self.tenant_id == 1:
            tenant = next((t for t in self.all_tenants if t["name"] == self.selected_user_tenant_name), None)
            if tenant:
                target_tenant_id = tenant["id"]
        
        ok, err = db.create_user(
            self.nu_username.lower().strip(), self.nu_password,
            self.nu_fullname, self.nu_role,
            target_tenant_id
        )
        if ok:
            self.nu_msg = f"✅ Usuario @{self.nu_username} creado."
            self.nu_username = self.nu_password = self.nu_fullname = ""
            self._reload_users()
        else:
            self.nu_msg = f"❌ {err}"

    def toggle_user(self, user_id: int, active: bool):
        db.toggle_user_active(user_id, not active, self.tenant_id)
        self._reload_users()

    def delete_user_action(self, user_id: int):
        ok, err = db.delete_user(user_id)
        if ok:
            self.nu_msg = "✅ Usuario eliminado."
            self._reload_users()
        else:
            self.nu_msg = f"❌ {err}"

    def change_user_tenant(self, user_id: int, tenant_name: str):
        t = next((x for x in self.all_tenants if x["name"] == tenant_name), None)
        if t:
            db.update_user_tenant(user_id, t["id"])
            self._reload_users()

    def toggle_edit_user(self, user_id: int):
        self.eu_editing_id = 0 if self.eu_editing_id == user_id else user_id
        self.eu_new_password = ""
        self.eu_msg = ""

    def set_eu_new_password(self, v): self.eu_new_password = v

    def save_user_password(self, user_id: int):
        if len(self.eu_new_password) < 6:
            self.eu_msg = "❌ La contraseña debe tener al menos 6 caracteres."
            return
        ok, err = db.update_user_password(user_id, self.eu_new_password)
        if ok:
            self.eu_msg = "✅ Contraseña actualizada."
            self.eu_new_password = ""
            self.eu_editing_id = 0
        else:
            self.eu_msg = f"❌ {err}"

    # ── Gemini ────────────────────────────────────────────────────────────────
    def set_gemini_key(self, v): self.gemini_key = v

    def save_gemini(self):
        if not self.gemini_key.strip():
            self.gemini_msg = "❌ Ingresa la API Key."
            return
        if self.tenant_id == 1:
            db.set_setting("gemini_api_key", self.gemini_key.strip())
        else:
            db.update_tenant_gemini_key(self.tenant_id, self.gemini_key.strip())
        self.gemini_msg = "✅ API Key guardada."
        self.gemini_key = ""

    # ── Quick Replies ─────────────────────────────────────────────────────────
    def set_qr_shortcut(self, v): self.qr_shortcut = v
    def set_qr_title(self, v): self.qr_title = v
    def set_qr_message(self, v): self.qr_message = v

    def save_qr(self):
        if not self.qr_shortcut.startswith("/"):
            self.qr_msg = "❌ El atajo debe comenzar con /"
            return
        if not self.qr_message:
            self.qr_msg = "❌ Mensaje requerido."
            return
        ok, err = db.create_quick_reply(self.qr_shortcut, self.qr_title, self.qr_message, self.tenant_id)
        if ok:
            self.qr_msg = "✅ Atajo creado."
            self.qr_shortcut = self.qr_title = self.qr_message = ""
            self._load_core_data()
        else:
            self.qr_msg = f"❌ {err}"

    def delete_qr(self, qr_id: int):
        db.delete_quick_reply(qr_id, self.tenant_id)
        self._load_core_data()

    def toggle_knowledge_modal(self, agent_id: int, agent_name: str):
        self.selected_knowledge_agent_id = agent_id
        self.selected_knowledge_agent_name = agent_name
        self.new_knowledge_url = ""
        self.knowledge_msg = ""
        self._refresh_knowledge()
        self.is_knowledge_modal_open = not self.is_knowledge_modal_open

    def close_knowledge_modal(self):
        self.is_knowledge_modal_open = False

    def _refresh_knowledge(self):
        if self.selected_knowledge_agent_id > 0:
            self.agent_knowledge = db.get_agent_knowledge(self.selected_knowledge_agent_id, self.tenant_id)
        else:
            self.agent_knowledge = []

    def delete_knowledge(self, knowledge_id: int):
        if db.delete_agent_knowledge(knowledge_id, self.tenant_id):
            self.knowledge_msg = "🗑️ Fuente eliminada del conocimiento."
            self._refresh_knowledge()
        else:
            self.knowledge_msg = "❌ Error al borrar fuente."

    def add_knowledge_url(self):
        url = self.new_knowledge_url.strip()
        if not url:
            self.knowledge_msg = "❌ URL requerida."
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            self.knowledge_msg = "❌ URL inválida (debe empezar con http/https)."
            return
            
        self.knowledge_msg = "⏳ Extrayendo contenido web..."
        content = extract_text_from_url(url)
        if not content:
            self.knowledge_msg = "❌ No se pudo extraer texto de la URL."
            return
            
        name = url.replace("https://", "").replace("http://", "").split("/")[0] + " (Web)"
        ok, err = db.create_agent_knowledge(self.selected_knowledge_agent_id, "url", name, content, self.tenant_id)
        if ok:
            self.knowledge_msg = "✅ URL agregada con éxito."
            self.new_knowledge_url = ""
            self._refresh_knowledge()
        else:
            self.knowledge_msg = f"❌ Error: {err}"

    async def handle_knowledge_upload(self, files: list[rx.UploadFile]):
        if self.selected_knowledge_agent_id <= 0:
            self.knowledge_msg = "❌ Ningún agente seleccionado."
            return
            
        for file in files:
            content_bytes = await file.read()
            filename = file.filename
            
            temp_path = os.path.join("uploaded_files", filename)
            os.makedirs("uploaded_files", exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(content_bytes)
                
            text = ""
            if filename.lower().endswith(".pdf"):
                self.knowledge_msg = f"⏳ Procesando PDF: {filename}..."
                text = extract_text_from_pdf(temp_path)
            elif filename.lower().endswith(".txt"):
                self.knowledge_msg = f"⏳ Procesando TXT: {filename}..."
                try:
                    text = content_bytes.decode("utf-8")
                except Exception:
                    try:
                        text = content_bytes.decode("latin-1")
                    except Exception:
                        text = ""
                        
            try:
                os.remove(temp_path)
            except Exception:
                pass
                
            if not text.strip():
                self.knowledge_msg = f"❌ No se pudo extraer texto de {filename}."
                continue
                
            ok, err = db.create_agent_knowledge(self.selected_knowledge_agent_id, "file", filename, text, self.tenant_id)
            if ok:
                self.knowledge_msg = f"✅ Archivo {filename} agregado al conocimiento."
            else:
                self.knowledge_msg = f"❌ Error al guardar {filename}: {err}"
                
        self._refresh_knowledge()

    def _refresh_flows(self):
        self.flows = db.get_flows(self.tenant_id)

    def set_new_flow_name(self, v): self.new_flow_name = v
    def set_step_text(self, v): self.step_text = v
    def set_step_action(self, v): self.step_action = v
    def set_step_action_val(self, v): self.step_action_val = v

    def add_step_to_editing(self):
        txt = self.step_text.strip()
        if not txt:
            self.flow_msg = "❌ El mensaje del paso es requerido."
            return
        
        step_id = len(self.new_flow_steps) + 1
        new_step = {
            "id": step_id,
            "text": txt,
            "action": self.step_action,
            "action_value": self.step_action_val.strip() if self.step_action != "none" else ""
        }
        self.new_flow_steps.append(new_step)
        self.step_text = ""
        self.step_action = "none"
        self.step_action_val = ""
        self.flow_msg = "➕ Paso añadido al borrador del flujo."

    def clear_editing_steps(self):
        self.new_flow_steps = []
        self.flow_msg = "🧹 Borrador limpiado."

    def create_conversational_flow(self):
        name = self.new_flow_name.strip()
        if not name:
            self.flow_msg = "❌ El nombre del flujo es obligatorio."
            return
        if not self.new_flow_steps:
            self.flow_msg = "❌ Debes añadir al menos un paso al flujo."
            return
            
        ok, err = db.create_flow(name, self.new_flow_steps, self.tenant_id)
        if ok:
            self.flow_msg = f"✅ Flujo '{name}' creado exitosamente."
            self.new_flow_name = ""
            self.new_flow_steps = []
            self._refresh_flows()
        else:
            self.flow_msg = f"❌ Error: {err}"

    def delete_conversational_flow(self, flow_id: int):
        if db.delete_flow(flow_id, self.tenant_id):
            self.flow_msg = "🗑️ Flujo conversacional eliminado."
            self._refresh_flows()
        else:
            self.flow_msg = "❌ Error al borrar flujo."

    # Gancho on_mount_settings extendido
    def on_mount_settings(self):
        self.require_auth()
        self._reload_users()
        self._load_core_data()
        self._refresh_flows()
        if self.tenant_id == 1:
            self._reload_tenants()
        self.selected_line_tenant_name = self.tenant_name


# ─────────────────────────────────────────────────────────────────────────────
# UI Components
# ─────────────────────────────────────────────────────────────────────────────

def _field(label, **props) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="1", color="#8e8e93"),
        rx.input(
            background="#1c1c1e", border="1px solid #3a3a3c",
            color="white", **props
        ),
        spacing="1", width="100%",
    )


def line_row(line: rx.Var) -> rx.Component:
    line_id = line["id"].to(int)
    name = line["name"].to(str)
    phone_id = line["phone_number_id"].to(str)
    color = line["color"].to(str)
    is_active = line["is_active"].to(bool)
    channel_type = line["channel_type"].to(str)
    page_id = line["page_id"].to(str)
    
    channel_label = rx.cond(
        channel_type == "messenger",
        "💬 Messenger",
        rx.cond(
            channel_type == "instagram",
            "📸 Instagram",
            "📱 WhatsApp"
        )
    )
    
    channel_badge_color = rx.cond(
        channel_type == "messenger",
        "blue",
        rx.cond(
            channel_type == "instagram",
            "purple",
            "green"
        )
    )

    identifier_text = rx.cond(
        channel_type == "whatsapp",
        "Phone ID: " + phone_id,
        "Page ID: " + page_id
    )

    return rx.hstack(
        rx.box(width="12px", height="12px", background=color, border_radius="50%"),
        rx.vstack(
            rx.hstack(
                rx.text(name, weight="bold", size="2", color="white"),
                rx.badge(channel_label, color_scheme=channel_badge_color, size="1"),
                spacing="2", align_items="center"
            ),
            rx.text(identifier_text, size="1", color="#636366"),
            spacing="0",
        ),
        rx.spacer(),
        rx.badge(
            rx.cond(is_active, "Activo", "Inactivo"),
            color_scheme=rx.cond(is_active, "green", "gray"),
        ),
        rx.button(
            rx.cond(is_active, "Desactivar", "Activar"),
            on_click=SettingsState.toggle_line(line_id, is_active),
            size="1", variant="ghost",
        ),
        rx.button(
            "✏️",
            on_click=SettingsState.start_edit_line(line),
            size="1", variant="ghost",
        ),
        rx.button(
            "🗑️",
            on_click=SettingsState.delete_line_action(line_id),
            size="1", variant="ghost", color="#ff453a",
        ),
        padding="12px",
        border="1px solid #2c2c2e",
        border_radius="10px",
        width="100%",
    )


def user_row(u: rx.Var) -> rx.Component:
    user_id = u["id"].to(int)
    username = u["username"].to(str)
    full_name = u["full_name"].to(str)
    role = u["role"].to(str)
    active = u["active"].to(bool)
    tenant_name = u["tenant_name"].to(str)
    is_editing = SettingsState.eu_editing_id == user_id

    return rx.vstack(
        # Fila principal
        rx.hstack(
            rx.vstack(
                rx.text("@" + username, weight="bold", size="2", color="white"),
                rx.text(full_name, size="1", color="#636366"),
                spacing="0",
            ),
            rx.spacer(),
            rx.cond(
                SettingsState.tenant_id == 1,
                rx.badge("🏢 " + tenant_name, color_scheme="purple", size="1"),
            ),
            rx.badge(role, color_scheme="blue", size="1"),
            rx.badge(
                rx.cond(active, "Activo", "Inactivo"),
                color_scheme=rx.cond(active, "green", "gray"),
                size="1",
            ),
            # Botón activar/desactivar
            rx.button(
                rx.cond(active, "⏸ Desactivar", "▶ Activar"),
                on_click=SettingsState.toggle_user(user_id, active),
                size="1", variant="soft",
                color_scheme=rx.cond(active, "orange", "green"),
            ),
            # Botón editar (contraseña + empresa)
            rx.button(
                rx.cond(is_editing, "✕ Cerrar", "✏️ Editar"),
                on_click=SettingsState.toggle_edit_user(user_id),
                size="1", variant="soft", color_scheme="blue",
            ),
            # Botón eliminar
            rx.button(
                "🗑 Eliminar",
                on_click=SettingsState.delete_user_action(user_id),
                size="1", variant="soft", color_scheme="red",
            ),
            padding="10px 14px",
            width="100%",
            align_items="center",
            spacing="2",
        ),
        # Panel de edición expandible
        rx.cond(
            is_editing,
            rx.box(
                rx.vstack(
                    rx.text("Acciones de edición", size="1", color="#8e8e93", weight="bold"),
                    # Cambiar empresa (solo superadmin)
                    rx.cond(
                        SettingsState.tenant_id == 1,
                        rx.hstack(
                            rx.text("Cambiar empresa:", size="1", color="#8e8e93", width="130px"),
                            rx.select(
                                SettingsState.tenant_options_for_user.to(list[str]),
                                value=tenant_name,
                                on_change=lambda v: SettingsState.change_user_tenant(user_id, v),
                                background="#1c1c1e", color="white",
                                border="1px solid #3a3a3c",
                                size="1",
                            ),
                            align_items="center", spacing="2",
                        ),
                    ),
                    # Cambiar contraseña
                    rx.hstack(
                        rx.text("Nueva contraseña:", size="1", color="#8e8e93", width="130px"),
                        rx.input(
                            placeholder="Mínimo 6 caracteres",
                            value=SettingsState.eu_new_password,
                            on_change=SettingsState.set_eu_new_password,
                            type="password",
                            background="#1c1c1e", color="white",
                            border="1px solid #3a3a3c",
                            size="1", flex="1",
                        ),
                        rx.button(
                            "💾 Guardar",
                            on_click=SettingsState.save_user_password(user_id),
                            size="1", color_scheme="blue",
                        ),
                        align_items="center", spacing="2", width="100%",
                    ),
                    rx.cond(
                        SettingsState.eu_msg != "",
                        rx.text(SettingsState.eu_msg, size="1", color="#30d158"),
                    ),
                    spacing="3", padding="12px",
                ),
                background="#111827",
                border_top="1px solid #2c2c2e",
                border_bottom_left_radius="10px",
                border_bottom_right_radius="10px",
                width="100%",
            ),
        ),
        border="1px solid #2c2c2e",
        border_radius="10px",
        width="100%",
        spacing="0",
    )


def product_row(p: rx.Var) -> rx.Component:
    p_id = p["id"].to(int)
    image_url = p["image_url"].to(str)
    name = p["name"].to(str)
    description = p["description"].to(str)
    price = p["price"].to_string()
    is_seasonal = p["is_seasonal"].to(bool)
    
    return rx.hstack(
        rx.cond(
            image_url != "",
            rx.image(src=image_url, width="40px", height="40px", border_radius="6px", object_fit="cover"),
            rx.center(rx.text("🛍️", size="2"), width="40px", height="40px", background="#2c2c2e", border_radius="6px")
        ),
        rx.vstack(
            rx.text(name, weight="bold", size="2", color="white"),
            rx.text(description[:100] + "...", size="1", color="#8e8e93"),
            spacing="0",
        ),
        rx.spacer(),
        rx.text("$", price, weight="bold", size="2", color="#30d158", margin_right="12px"),
        rx.badge(
            rx.cond(is_seasonal, "Temporada", "Regular"),
            color_scheme=rx.cond(is_seasonal, "orange", "blue"),
            margin_right="12px"
        ),
        rx.button("✏️", on_click=SettingsState.start_edit_product(p), size="1", variant="ghost"),
        rx.button("🗑️", on_click=SettingsState.delete_product(p_id), size="1", variant="ghost", color="#ff453a"),
        padding="12px",
        border="1px solid #2c2c2e",
        border_radius="10px",
        width="100%",
    )


def knowledge_base_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.dialog.title("📖 Base de Conocimiento — " + SettingsState.selected_knowledge_agent_name, color="white", size="4"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("✕", variant="ghost", size="1", on_click=SettingsState.close_knowledge_modal)
                    ),
                    width="100%", align_items="center"
                ),
                rx.text("Entrena a tu agente IA agregando PDFs, TXTs o URLs de sitios web. La IA usará esta información para contestar de manera precisa.", color="#8e8e93", size="2"),
                
                rx.divider(color="#2c2c2e", margin_y="8px"),
                
                # Cargar Archivos
                rx.heading("📁 Cargar Archivos (PDF / TXT)", size="2", color="white"),
                rx.upload(
                    rx.vstack(
                        rx.text("Arrastra archivos aquí o haz clic para seleccionar", color="#8e8e93", size="2"),
                        rx.text("(Soporta .pdf, .txt)", color="#636366", size="1"),
                        align_items="center",
                        padding="20px",
                        border="2px dashed #3a3a3c",
                        border_radius="10px",
                        cursor="pointer",
                        width="100%",
                        _hover={"background": "#1c1c1e"}
                    ),
                    id="knowledge_uploader",
                    multiple=True,
                    accept={
                        "application/pdf": [".pdf"],
                        "text/plain": [".txt"]
                    },
                    on_drop=SettingsState.handle_knowledge_upload(rx.upload_files(upload_id="knowledge_uploader")),
                    width="100%"
                ),
                
                # Cargar URL
                rx.heading("🌐 Agregar Sitio Web (URL)", size="2", color="white", margin_top="8px"),
                rx.hstack(
                    rx.input(
                        placeholder="Ej: https://miempresa.com/faq",
                        value=SettingsState.new_knowledge_url,
                        on_change=SettingsState.set_new_knowledge_url,
                        background="#1c1c1e", border="1px solid #3a3a3c", color="white",
                        flex="1"
                    ),
                    rx.button("🔗 Agregar", on_click=SettingsState.add_knowledge_url, color_scheme="blue"),
                    width="100%"
                ),
                
                rx.cond(
                    SettingsState.knowledge_msg != "",
                    rx.text(SettingsState.knowledge_msg, size="2", color="#30d158")
                ),
                
                rx.divider(color="#2c2c2e", margin_y="8px"),
                
                # Lista de fuentes actuales
                rx.heading("Fuentes actuales", size="2", color="white"),
                rx.cond(
                    SettingsState.agent_knowledge.length() > 0,
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                SettingsState.agent_knowledge,
                                lambda k: rx.hstack(
                                    rx.vstack(
                                        rx.text(k["name"].to(str), weight="bold", size="2", color="white"),
                                        rx.text("Tipo: " + k["source_type"].to(str) + " · Creado: " + k["created_at"].to(str), size="1", color="#8e8e93"),
                                        spacing="0", align_items="start"
                                    ),
                                    rx.spacer(),
                                    rx.button("🗑️", on_click=SettingsState.delete_knowledge(k["id"].to(int)), size="1", variant="ghost", color="#ff453a"),
                                    width="100%", padding="8px", border_bottom="1px solid #2c2c2e"
                                )
                            ),
                            width="100%"
                        ),
                        height="200px", width="100%"
                    ),
                    rx.text("El agente no tiene fuentes de conocimiento agregadas.", color="#636366", size="2")
                ),
                
                spacing="3",
                width="100%",
                align_items="stretch"
            ),
            background="#111",
            border="1px solid #2c2c2e",
            border_radius="16px",
            padding="24px",
            max_width="550px"
        ),
        open=SettingsState.is_knowledge_modal_open
    )


def facebook_onboarding_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.heading("🔌 Conectar Canales de Facebook / Instagram", size="4", color="white"),
                    rx.spacer(),
                    rx.button("❌ Cerrar", on_click=SettingsState.close_fb_modal, size="1", variant="ghost"),
                    width="100%", align_items="center"
                ),
                
                rx.text(SettingsState.fb_status_msg, size="2", color="white"),
                
                rx.cond(
                    SettingsState.fb_loading,
                    rx.center(rx.spinner(size="3"), width="100%", padding="20px"),
                    rx.vstack(
                        rx.foreach(
                            SettingsState.fb_discovered_channels,
                            lambda p: rx.hstack(
                                rx.vstack(
                                    rx.text(p["name"].to(str), size="2", weight="bold", color="white"),
                                    rx.cond(
                                        p["has_instagram"],
                                        rx.text("📸 Instagram: @" + p["instagram_username"].to(str), size="1", color="#d62976"),
                                        rx.text("Sin cuenta de Instagram vinculada", size="1", color="#8e8e93")
                                    ),
                                    spacing="0", align_items="start"
                                ),
                                rx.spacer(),
                                rx.hstack(
                                    rx.button(
                                        "Activar Messenger",
                                        on_click=lambda: SettingsState.activate_discovered_channel(p, False),
                                        size="1", color_scheme="blue"
                                    ),
                                    rx.cond(
                                        p["has_instagram"],
                                        rx.button(
                                            "Activar Instagram",
                                            on_click=lambda: SettingsState.activate_discovered_channel(p, True),
                                            size="1", color_scheme="pink"
                                        )
                                    ),
                                    spacing="2"
                                ),
                                width="100%", padding="12px", border_bottom="1px solid #2c2c2e", align_items="center"
                            )
                        ),
                        width="100%", spacing="2"
                    )
                ),
                spacing="4", width="100%"
            ),
            background="#111113", border="1px solid #2c2c2e", max_width="550px", border_radius="12px", padding="24px"
        ),
        open=SettingsState.fb_modal_open,
    )


def pre_registration_row(req: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.heading(req["company_name"], size="3", color="white"),
                        rx.badge(req["selected_plan"], color_scheme="blue", variant="solid"),
                        rx.cond(
                            req["selected_plan"] != "Enterprise",
                            rx.hstack(
                                rx.badge(req["billing_frequency"], color_scheme="green", variant="soft"),
                                rx.badge(req["ai_mode"], color_scheme="purple", variant="soft"),
                                spacing="1"
                            )
                        ),
                        spacing="2",
                        align_items="center"
                    ),
                    rx.text(
                        "Contacto: ", req["contact_name"], " (", req["contact_email"], ") | Tel: ", 
                        rx.cond(req["contact_phone"], req["contact_phone"], "N/A"),
                        color="#8e8e93", size="2"
                    ),
                    spacing="1",
                    align_items="start"
                ),
                rx.spacer(),
                rx.text(req["created_at"], color="#636366", size="1"),
                align_items="center",
                width="100%"
            ),
            rx.cond(
                req["notes"] != "",
                rx.box(
                    rx.text("Notas: ", req["notes"], color="#8e8e93", size="2", italic=True),
                    margin_top="8px",
                    padding="8px 12px",
                    background="rgba(255,255,255,0.03)",
                    border_radius="6px",
                    width="100%"
                )
            ),
            # Formulario de Aprobación en línea
            rx.vstack(
                rx.divider(color="rgba(255, 255, 255, 0.08)", margin="10px 0"),
                rx.text("La aprobación generará automáticamente el usuario administrador (Nombre + primera letra del apellido) y una contraseña temporal segura, notificando al cliente por correo.", size="2", color="#8e8e93"),
                rx.cond(
                    AppState.approve_error != "",
                    rx.callout(AppState.approve_error, color="red", variant="soft", width="100%", margin_top="10px")
                ),
                rx.cond(
                    AppState.approve_success != "",
                    rx.callout(AppState.approve_success, color="green", variant="soft", width="100%", margin_top="10px")
                ),
                rx.hstack(
                    rx.button("Aprobar y Activar Empresa", on_click=lambda: AppState.approve_registration(req["id"]), color_scheme="green", size="2", weight="bold"),
                    rx.button("Rechazar Solicitud", on_click=lambda: AppState.reject_registration(req["id"]), color_scheme="red", size="2", variant="soft"),
                    spacing="3",
                    margin_top="10px"
                ),
                width="100%",
                align_items="start"
            ),
            align_items="start",
            width="100%"
        ),
        padding="20px",
        border="1px solid rgba(15, 163, 177, 0.2)",
        border_radius="12px",
        background="rgba(18, 18, 18, 0.5)",
        width="100%",
        margin_bottom="12px"
    )


def settings_page() -> rx.Component:
    return rx.vstack(
        navbar("/settings"),
        rx.vstack(
            rx.heading("⚙️ Configuración", size="7", color="white", padding="24px 32px 8px"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("👥 Usuarios", value="users"),
                    rx.tabs.trigger("📡 Canales", value="lines"),
                    rx.tabs.trigger("🤖 Agentes IA", value="ai_agents"),
                    rx.tabs.trigger("📨 Plantillas", value="templates"),
                    rx.tabs.trigger("⚙️ Automatizaciones", value="workflows"),
                    rx.tabs.trigger("⚡ Atajos", value="qr"),
                    rx.tabs.trigger("🛍️ Catálogo", value="catalog"),
                    rx.cond(
                        SettingsState.role == "admin",
                        rx.tabs.trigger("🤖 Gemini AI", value="gemini"),
                    ),
                    rx.tabs.trigger("🔑 Mi Cuenta", value="account"),
                    rx.cond(
                        SettingsState.tenant_id == 1,
                        rx.tabs.trigger("🏢 Empresas", value="tenants"),
                    ),
                    rx.cond(
                        SettingsState.tenant_id == 1,
                        rx.tabs.trigger("📝 Solicitudes", value="pre_registrations"),
                    ),
                    border_bottom="1px solid #2c2c2e",
                    padding="0 32px",
                ),

                # ── Usuarios ─────────────────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Crear usuario", size="4", color="white"),
                        rx.grid(
                            _field("Usuario *", placeholder="@usuario", on_change=SettingsState.set_nu_username),
                            _field("Nombre completo", placeholder="Juan Pérez", on_change=SettingsState.set_nu_fullname),
                            _field("Contraseña *", type="password", on_change=SettingsState.set_nu_password),
                            rx.vstack(
                                rx.text("Rol", size="1", color="#8e8e93"),
                                rx.select(
                                    ["agent", "coordinator", "admin"],
                                    default_value="agent",
                                    on_change=SettingsState.set_nu_role,
                                    background="#1c1c1e", color="white",
                                    border="1px solid #3a3a3c",
                                    width="100%"
                                ),
                                spacing="1",
                                width="100%"
                            ),
                            rx.cond(
                                SettingsState.tenant_id == 1,
                                rx.vstack(
                                    rx.text("Asociar a Empresa (Tenant)", size="1", color="#8e8e93"),
                                    rx.select(
                                        SettingsState.tenant_options_for_user.to(list[str]),
                                        value=SettingsState.selected_user_tenant_name,
                                        on_change=SettingsState.set_selected_user_tenant_name,
                                        background="#1c1c1e", color="white",
                                        border="1px solid #3a3a3c",
                                        width="100%"
                                    ),
                                    spacing="1",
                                    width="100%"
                                )
                            ),
                            columns="2", spacing="3", width="100%",
                        ),
                        rx.button("Crear usuario", on_click=SettingsState.save_user,
                                  color_scheme="blue"),
                        rx.cond(SettingsState.nu_msg != "",
                                  rx.text(SettingsState.nu_msg, size="2")),
                        rx.divider(color="#2c2c2e"),
                        rx.box(
                            rx.hstack(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("📋 Plan Contratado: ", size="2", color="#8e8e93"),
                                        rx.badge(SettingsState.current_plan_name, color_scheme="blue", variant="solid"),
                                        spacing="2", align_items="center"
                                    ),
                                    rx.hstack(
                                        rx.text("🤖 Modo de IA: ", size="2", color="#8e8e93"),
                                        rx.badge(SettingsState.current_ai_mode, color_scheme="purple", variant="soft"),
                                        spacing="2", align_items="center"
                                    ),
                                    spacing="1", align_items="start"
                                ),
                                rx.spacer(),
                                rx.vstack(
                                    rx.text("Agentes humanos creados", size="1", color="#8e8e93"),
                                    rx.hstack(
                                        rx.heading(SettingsState.current_agent_count.to(str), size="6", color="white"),
                                        rx.text("/", color="#636366"),
                                        rx.heading(
                                            rx.cond(SettingsState.current_plan_name == "Enterprise", "Ilimitado", SettingsState.current_agent_limit.to(str)),
                                            size="6", color="#0fa3b1"
                                        ),
                                        align_items="baseline", spacing="1"
                                    ),
                                    align_items="end"
                                ),
                                width="100%", align_items="center"
                            ),
                            background="#1c1c1e", border="1px solid #2c2c2e", border_radius="12px", padding="16px", width="100%", margin_bottom="12px"
                        ),
                        rx.heading("Usuarios activos", size="4", color="white"),
                        rx.foreach(SettingsState.all_users.to(list[dict]), user_row),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="users", padding="24px 32px",
                ),

                # ── Canales (WhatsApp / FB / Instagram) ──────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Canales de Comunicación Activos", size="4", color="white"),
                        rx.text("Configura múltiples líneas de WhatsApp o cuentas de Facebook e Instagram para esta empresa.", size="2", color="#8e8e93"),
                        
                        # Bloque premium de conexión autogestionada (Opción 2)
                        rx.box(
                            rx.hstack(
                                rx.vstack(
                                    rx.text("🔗 Conectar Facebook e Instagram automáticamente", size="3", weight="bold", color="white"),
                                    rx.text("Inicia sesión con tu cuenta de Facebook para vincular tus páginas de Messenger o Instagram Business sin configuraciones manuales.", size="2", color="#8e8e93"),
                                    spacing="1", align_items="start"
                                ),
                                rx.spacer(),
                                rx.link(
                                    rx.button(
                                        "🔌 Conectar Facebook", 
                                        color_scheme="blue", 
                                        variant="solid",
                                        cursor="pointer"
                                    ),
                                    href=SettingsState.facebook_login_url,
                                    is_external=True
                                ),
                                width="100%", align_items="center", spacing="4"
                            ),
                            background="#1c1c1e", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%", margin_bottom="12px", margin_top="8px"
                        ),

                        rx.foreach(SettingsState.all_lines.to(list[dict]), line_row),
                        
                        rx.divider(color="#2c2c2e"),
                        
                        rx.heading(
                            rx.cond(
                                SettingsState.editing_line_id.to(int) > 0,
                                "✏️ Editar canal",
                                "➕ Agregar nuevo canal"
                            ),
                            size="4", color="white"
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text("Tipo de Canal *", size="1", color="#8e8e93"),
                                rx.select(
                                    ["whatsapp", "messenger", "instagram"],
                                    value=SettingsState.nl_channel_type,
                                    on_change=SettingsState.set_nl_channel_type,
                                    background="#1c1c1e", color="white",
                                    border="1px solid #3a3a3c", width="100%"
                                ),
                                spacing="1", width="100%"
                            ),
                            _field("Nombre del Canal *", placeholder="Ventas FB / WhatsApp Principal / IG Soporte", value=SettingsState.nl_name, on_change=SettingsState.set_nl_name),
                            
                            # Campo condicional de ID de teléfono (solo para whatsapp)
                            rx.cond(
                                SettingsState.nl_channel_type == "whatsapp",
                                _field("Phone Number ID *", placeholder="Ej: 109283748293748", value=SettingsState.nl_phone_id, on_change=SettingsState.set_nl_phone_id)
                            ),
                            
                            # Campo condicional de ID de Página (para facebook/instagram)
                            rx.cond(
                                SettingsState.nl_channel_type != "whatsapp",
                                _field("ID de Página o Cuenta de Instagram (Page ID) *", placeholder="Ej: 109283748293748", value=SettingsState.nl_page_id, on_change=SettingsState.set_nl_page_id)
                            ),

                            _field("Access Token * (Page Token o Permanent Token)", type="password", value=SettingsState.nl_token, on_change=SettingsState.set_nl_token),
                            _field("Meta App ID (Opcional)", placeholder="Ej: 123456789012345", value=SettingsState.nl_app_id, on_change=SettingsState.set_nl_app_id),
                            
                            _field("Mensaje de bienvenida", placeholder="¡Hola! Bienvenido a nuestro canal oficial. ¿En qué te ayudamos?", value=SettingsState.nl_welcome, on_change=SettingsState.set_nl_welcome),
                            
                            rx.cond(
                                SettingsState.tenant_id == 1,
                                rx.vstack(
                                    rx.text("Asociar a Empresa (Tenant)", size="1", color="#8e8e93"),
                                    rx.select(
                                        SettingsState.tenant_options_for_user.to(list[str]),
                                        value=SettingsState.selected_line_tenant_name,
                                        on_change=SettingsState.set_selected_line_tenant_name,
                                        background="#1c1c1e", color="white",
                                        border="1px solid #3a3a3c",
                                        width="100%"
                                    ),
                                    spacing="1",
                                    width="100%"
                                )
                            ),
                            
                            columns="2", spacing="3", width="100%",
                        ),
                        
                        # Panel de ayuda visual de Meta Developers
                        rx.box(
                            rx.vstack(
                                rx.text("💡 ¿Cómo obtener los datos de Meta?", size="2", weight="bold", color="#0A84FF"),
                                rx.text("1. Ingresa a developers.facebook.com y crea una aplicación tipo 'Negocios' (Business).", size="1", color="#8e8e93"),
                                rx.text("2. Añade los productos 'WhatsApp', 'Messenger' o 'Instagram' según los canales que desees usar.", size="1", color="#8e8e93"),
                                rx.text("3. Genera un token de acceso a la página de Facebook vinculada a tu cuenta de Instagram o tu chat de Messenger.", size="1", color="#8e8e93"),
                                rx.text("4. Copia el ID de la Página (FB Page ID) o el ID de la cuenta de Instagram para enlazarlos aquí.", size="1", color="#8e8e93"),
                                spacing="1", align_items="start"
                            ),
                            background="#1c1c1e", border="1px solid #3a3a3c", border_radius="10px", padding="14px", width="100%"
                        ),

                        rx.hstack(
                            rx.button(
                                rx.cond(
                                    SettingsState.editing_line_id.to(int) > 0,
                                    "💾 Actualizar Canal",
                                    "💾 Guardar Canal"
                                ),
                                on_click=SettingsState.save_line,
                                color_scheme="blue"
                            ),
                            rx.cond(
                                SettingsState.editing_line_id.to(int) > 0,
                                rx.button(
                                    "✕ Cancelar",
                                    on_click=SettingsState.cancel_edit_line,
                                    color_scheme="gray",
                                    variant="soft"
                                )
                            ),
                            spacing="2"
                        ),
                        rx.cond(SettingsState.nl_msg != "", rx.text(SettingsState.nl_msg, size="2")),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="lines", padding="24px 32px",
                ),

                # ── Atajos ───────────────────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Respuestas rápidas", size="4", color="white"),
                        rx.foreach(
                            SettingsState.quick_replies.to(list[dict]),
                            lambda q: rx.hstack(
                                rx.badge(q["shortcut"], color_scheme="blue"),
                                rx.text(q["title"], size="2", color="#8e8e93"),
                                rx.spacer(),
                                rx.button(
                                    "🗑", size="1", variant="ghost", color="#ff453a",
                                    on_click=SettingsState.delete_qr(q["id"]),
                                ),
                                padding="8px 12px",
                                border="1px solid #2c2c2e",
                                border_radius="8px",
                                width="100%",
                            ),
                        ),
                        rx.divider(color="#2c2c2e"),
                        rx.heading("Nuevo atajo", size="4", color="white"),
                        rx.grid(
                            _field("Atajo *", placeholder="/hola",
                                   on_change=SettingsState.set_qr_shortcut),
                            _field("Título", placeholder="Saludo de bienvenida",
                                   on_change=SettingsState.set_qr_title),
                            columns="2", spacing="3", width="100%",
                        ),
                        rx.vstack(
                            rx.text("Mensaje completo *", size="1", color="#8e8e93"),
                            rx.text_area(
                                placeholder="¡Hola! ¿En qué te puedo ayudar? 😊",
                                on_change=SettingsState.set_qr_message,
                                background="#1c1c1e", border="1px solid #3a3a3c",
                                color="white", width="100%",
                            ),
                            spacing="1", width="100%",
                        ),
                        rx.button("✅ Guardar atajo", on_click=SettingsState.save_qr,
                                  color_scheme="blue"),
                        rx.cond(SettingsState.qr_msg != "",
                                  rx.text(SettingsState.qr_msg, size="2")),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="qr", padding="24px 32px",
                ),

                # ── Catálogo de Temporada ─────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Gestionar Catálogo de Productos", size="4", color="white"),
                        rx.text("Administra los productos de temporada y ofertas disponibles para los agentes.", color="#8e8e93", size="2"),
                        
                        rx.box(
                            rx.vstack(
                                rx.heading(
                                    rx.cond(SettingsState.editing_product_id > 0, "✏️ Editar Producto", "➕ Agregar Producto"),
                                    size="3", color="white"
                                ),
                                rx.grid(
                                    _field("Nombre del Producto *", placeholder="Zapatillas Nike Sport", value=SettingsState.new_product_name, on_change=SettingsState.set_new_product_name),
                                    _field("Precio ($) *", placeholder="59.99", value=SettingsState.new_product_price, on_change=SettingsState.set_new_product_price),
                                    _field("Imagen URL (Opcional)", placeholder="https://example.com/image.jpg", value=SettingsState.new_product_image, on_change=SettingsState.set_new_product_image),
                                    rx.vstack(
                                        rx.text("Tipo de Oferta", size="1", color="#8e8e93"),
                                        rx.checkbox(
                                            "Producto de Temporada / Oferta",
                                            checked=SettingsState.new_product_seasonal,
                                            on_change=SettingsState.set_new_product_seasonal,
                                            color_scheme="orange"
                                        ),
                                        align_items="start",
                                        justify_content="center",
                                        height="100%"
                                    ),
                                    columns="2", spacing="3", width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Descripción del Producto", size="1", color="#8e8e93"),
                                    rx.text_area(
                                        placeholder="Descripción corta, beneficios, tallas, etc.",
                                        value=SettingsState.new_product_desc,
                                        on_change=SettingsState.set_new_product_desc,
                                        background="#1c1c1e", border="1px solid #3a3a3c",
                                        color="white", width="100%",
                                    ),
                                    spacing="1", width="100%",
                                ),
                                rx.hstack(
                                    rx.button(
                                        rx.cond(SettingsState.editing_product_id > 0, "💾 Actualizar Producto", "💾 Guardar Producto"),
                                        on_click=SettingsState.save_product,
                                        color_scheme="blue"
                                    ),
                                    rx.cond(
                                        SettingsState.editing_product_id > 0,
                                        rx.button("Cancelar", on_click=SettingsState.cancel_edit_product, variant="soft"),
                                    ),
                                    spacing="2"
                                ),
                                rx.cond(SettingsState.prod_msg != "", rx.text(SettingsState.prod_msg, size="2", color="#30d158")),
                                spacing="3", width="100%", padding="16px", background="#111", border="1px solid #2c2c2e", border_radius="12px"
                            ),
                            width="100%"
                        ),
                        
                        rx.divider(color="#2c2c2e"),
                        rx.heading("Catálogo registrado", size="3", color="white"),
                        rx.foreach(SettingsState.products.to(list[dict]), product_row),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="catalog", padding="24px 32px",
                ),

                # ── Gemini ───────────────────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("🤖 Gemini AI", size="4", color="white"),
                        rx.text("Configura la API Key de Gemini dedicada para tu empresa. Si no se configura, el sistema usará la del SaaS Global por defecto.", color="#8e8e93", size="2"),
                        rx.hstack(
                            rx.text("Estado de configuración: ", color="#8e8e93", size="2"),
                            rx.cond(
                                SettingsState.is_gemini_configured,
                                rx.badge("Activa", color_scheme="green"),
                                rx.badge("No configurada (Usando Global)", color_scheme="gray")
                            ),
                            align_items="center"
                        ),
                        _field("API Key de Gemini", type="password", placeholder="AIza...", on_change=SettingsState.set_gemini_key),
                        rx.button("💾 Guardar", on_click=SettingsState.save_gemini, color_scheme="blue"),
                        rx.cond(SettingsState.gemini_msg != "", rx.text(SettingsState.gemini_msg, size="2")),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="gemini", padding="24px 32px",
                ),

                # ── Mi Cuenta ────────────────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("🔑 Cambiar contraseña", size="4", color="white"),
                        _field("Nueva contraseña", type="password", on_change=SettingsState.set_pwd_new),
                        _field("Confirmar contraseña", type="password", on_change=SettingsState.set_pwd_confirm),
                        rx.button("Cambiar contraseña", on_click=SettingsState.change_password, color_scheme="blue"),
                        rx.cond(SettingsState.pwd_msg != "", rx.text(SettingsState.pwd_msg, size="2")),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="account", padding="24px 32px",
                ),

                # ── Agentes IA (Fase 2) ──────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("🤖 Configuración de Agentes IA", size="4", color="white"),
                        rx.text("Configura respondedores automáticos basados en Gemini AI por línea de WhatsApp.", color="#8e8e93", size="2"),
                        
                        # Formulario de Creación
                        rx.box(
                            rx.vstack(
                                rx.heading("Crear Nuevo Agente", size="3", color="white"),
                                rx.hstack(
                                    rx.vstack(
                                        rx.text("Nombre del Agente", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: Sophia (Ventas)", on_change=SettingsState.set_new_agent_name, value=SettingsState.new_agent_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="250px"),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Asociar a Línea", size="1", color="#8e8e93"),
                                        rx.select(
                                            SettingsState.line_options_ai.to(list[str]),
                                            value=SettingsState.selected_ai_line_name,
                                            on_change=SettingsState.set_selected_ai_line_name,
                                            background="#1c1c1e", color="white", border="1px solid #3a3a3c"
                                        ),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Estado inicial", size="1", color="#8e8e93"),
                                        rx.hstack(
                                            rx.switch(is_checked=SettingsState.new_agent_active, on_change=SettingsState.set_new_agent_active),
                                            rx.text("Activo", size="2", color="white"),
                                            spacing="2", align_items="center"
                                        ),
                                        spacing="1", padding_top="8px"
                                    ),
                                    spacing="4", align_items="end"
                                ),
                                rx.vstack(
                                    rx.text("Instrucciones del Sistema (System Prompt)", size="1", color="#8e8e93"),
                                    rx.text_area(
                                        placeholder="Define la personalidad, reglas y cómo debe contestar el agente de IA. Ej: Eres un asistente amigable de PixArtM, debes contestar dudas sobre los productos y guiar al cliente a agendar una cita...",
                                        value=SettingsState.new_agent_prompt,
                                        on_change=SettingsState.set_new_agent_prompt,
                                        background="#1c1c1e", border="1px solid #3a3a3c", color="white",
                                        resize="vertical", rows="4", width="100%"
                                    ),
                                    spacing="1", width="100%"
                                ),
                                rx.button("🤖 Guardar Agente IA", on_click=SettingsState.create_ai_agent, color_scheme="blue", width="200px"),
                                rx.cond(SettingsState.agent_msg != "", rx.text(SettingsState.agent_msg, size="2", color="#30d158")),
                                spacing="3", align_items="start", width="100%"
                            ),
                            background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%"
                        ),
                        
                        rx.divider(color="#2c2c2e", margin="16px 0"),
                        
                        # Lista de Agentes Creados
                        rx.heading("Agentes IA configurados", size="3", color="white"),
                        rx.cond(
                            SettingsState.ai_agents.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    SettingsState.ai_agents,
                                    lambda a: rx.hstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text("🤖 " + a["name"].to(str), weight="bold", size="3", color="white"),
                                                rx.badge(rx.cond(a["is_active"].to(bool), "Activo", "Inactivo"), color_scheme=rx.cond(a["is_active"].to(bool), "green", "gray")),
                                                spacing="2"
                                            ),
                                            rx.text("Instrucciones: " + a["system_prompt"].to(str), size="1", color="#8e8e93", line_clamp=2),
                                            spacing="1", align_items="start"
                                        ),
                                        rx.spacer(),
                                        rx.button(
                                            "📖 Fuentes de Conocimiento",
                                            on_click=SettingsState.toggle_knowledge_modal(a["id"].to(int), a["name"].to(str)),
                                            size="1",
                                            variant="soft",
                                            color_scheme="blue"
                                        ),
                                        rx.button("🗑️", on_click=SettingsState.delete_ai_agent(a["id"].to(int)), size="1", variant="ghost", color="#ff453a"),
                                        padding="14px",
                                        border="1px solid #2c2c2e",
                                        border_radius="10px",
                                        width="100%",
                                        background="#111"
                                    )
                                ),
                                width="100%", spacing="2"
                            ),
                            rx.text("No tienes agentes IA creados. Agrega uno arriba.", color="#636366", size="2")
                        ),
                        spacing="4", align_items="start", width="100%"
                    ),
                    value="ai_agents", padding="24px 32px"
                ),

                # ── Plantillas de WhatsApp (Fase 2) ──────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("📨 Plantillas de WhatsApp (Meta)", size="4", color="white"),
                        rx.text("Crea y guarda las plantillas de mensaje para enviar a clientes fuera de la ventana de 24 horas.", color="#8e8e93", size="2"),
                        
                        # Formulario de Creación
                        rx.box(
                            rx.vstack(
                                rx.heading("Registrar Nueva Plantilla", size="3", color="white"),
                                rx.hstack(
                                    rx.vstack(
                                        rx.text("Nombre de la Plantilla", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: recordatorio_pago (sin espacios)", on_change=SettingsState.set_new_tpl_name, value=SettingsState.new_tpl_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="250px"),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Categoría", size="1", color="#8e8e93"),
                                        rx.select(
                                            ["UTILITY", "MARKETING", "AUTHENTICATION"],
                                            value=SettingsState.new_tpl_category,
                                            on_change=SettingsState.set_new_tpl_category,
                                            background="#1c1c1e", color="white", border="1px solid #3a3a3c"
                                        ),
                                        spacing="1"
                                    ),
                                    spacing="4", align_items="end"
                                ),
                                rx.vstack(
                                    rx.text("Cuerpo del Mensaje", size="1", color="#8e8e93"),
                                    rx.text_area(
                                        placeholder="Escribe el texto de la plantilla. Ej: Hola {{1}}, te recordamos que tu pago de {{2}} está listo para procesar. Saludos!",
                                        value=SettingsState.new_tpl_body,
                                        on_change=SettingsState.set_new_tpl_body,
                                        background="#1c1c1e", border="1px solid #3a3a3c", color="white",
                                        resize="vertical", rows="3", width="100%"
                                    ),
                                    spacing="1", width="100%"
                                ),
                                rx.button("📨 Guardar Plantilla", on_click=SettingsState.create_message_template, color_scheme="blue", width="200px"),
                                rx.cond(SettingsState.tpl_msg != "", rx.text(SettingsState.tpl_msg, size="2", color="#30d158")),
                                spacing="3", align_items="start", width="100%"
                            ),
                            background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%"
                        ),
                        
                        rx.divider(color="#2c2c2e", margin="16px 0"),
                        
                        # Lista de Plantillas
                        rx.heading("Plantillas guardadas", size="3", color="white"),
                        rx.cond(
                            SettingsState.templates.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    SettingsState.templates,
                                    lambda t: rx.hstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text("📨 " + t["name"].to(str), weight="bold", size="3", color="white"),
                                                rx.badge(t["category"].to(str), color_scheme="blue"),
                                                spacing="2"
                                            ),
                                            rx.text(t["body_text"].to(str), size="2", color="#8e8e93", white_space="pre-wrap"),
                                            spacing="1", align_items="start"
                                        ),
                                        rx.spacer(),
                                        rx.button("🗑️", on_click=SettingsState.delete_message_template(t["id"].to(int)), size="1", variant="ghost", color="#ff453a"),
                                        padding="14px",
                                        border="1px solid #2c2c2e",
                                        border_radius="10px",
                                        width="100%",
                                        background="#111"
                                    )
                                ),
                                width="100%", spacing="2"
                            ),
                            rx.text("No tienes plantillas de mensaje creadas.", color="#636366", size="2")
                        ),
                        spacing="4", align_items="start", width="100%"
                    ),
                    value="templates", padding="24px 32px"
                ),

                # ── Automatizaciones y Constructor de Flujos (Fase 3) ────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("⚙️ Flujos de Trabajo y Automatizaciones", size="4", color="white"),
                        rx.text("Automatiza tus canales de mensajería creando reglas rápidas o flujos conversacionales interactivos paso a paso al estilo de Respond.io.", color="#8e8e93", size="2"),
                        
                        rx.grid(
                            # LADO IZQUIERDO: Reglas de Automatización Lineales
                            rx.vstack(
                                rx.box(
                                    rx.vstack(
                                        rx.heading("1. Reglas Rápidas (If/Then)", size="3", color="white"),
                                        rx.text("Respuestas o acciones automáticas cuando un mensaje contiene palabras clave.", color="#8e8e93", size="1"),
                                        rx.vstack(
                                            rx.text("Nombre de la Regla", size="1", color="#8e8e93"),
                                            rx.input(placeholder="Ej: Auto-Respuesta Precios", on_change=SettingsState.set_new_wf_name, value=SettingsState.new_wf_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                            spacing="1", width="100%"
                                        ),
                                        rx.grid(
                                            rx.vstack(
                                                rx.text("Palabra Clave", size="1", color="#8e8e93"),
                                                rx.input(placeholder="Ej: precio", on_change=SettingsState.set_new_wf_cond_val, value=SettingsState.new_wf_cond_val, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                                spacing="1"
                                            ),
                                            rx.vstack(
                                                rx.text("Acción", size="1", color="#8e8e93"),
                                                rx.select(
                                                    ["reply", "assign", "set_lifecycle"],
                                                    value=SettingsState.new_wf_action_type,
                                                    on_change=SettingsState.set_new_wf_action_type,
                                                    background="#1c1c1e", color="white", border="1px solid #3a3a3c", width="100%"
                                                ),
                                                spacing="1"
                                            ),
                                            columns="2", spacing="2", width="100%"
                                        ),
                                        rx.vstack(
                                            rx.text("Valor de la Acción", size="1", color="#8e8e93"),
                                            rx.input(placeholder="Ej: El costo es $50 / admin / Lead", on_change=SettingsState.set_new_wf_action_val, value=SettingsState.new_wf_action_val, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                            spacing="1", width="100%"
                                        ),
                                        rx.button("⚙️ Guardar Regla", on_click=SettingsState.create_workflow, color_scheme="blue", width="100%"),
                                        rx.cond(SettingsState.wf_msg != "", rx.text(SettingsState.wf_msg, size="2", color="#30d158")),
                                        spacing="3", align_items="stretch", width="100%"
                                    ),
                                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%"
                                ),
                                spacing="3", width="100%"
                            ),
                            
                            # LADO DERECHO: Constructor de Flujos Conversacionales Secuenciales
                            rx.vstack(
                                rx.box(
                                    rx.vstack(
                                        rx.heading("2. Flujos Conversacionales Paso a Paso", size="3", color="white"),
                                        rx.text("Guía y califica a tus clientes de forma secuencial al iniciar el chat.", color="#8e8e93", size="1"),
                                        rx.vstack(
                                            rx.text("Nombre del Flujo", size="1", color="#8e8e93"),
                                            rx.input(placeholder="Ej: Bienvenida y Calificación", value=SettingsState.new_flow_name, on_change=SettingsState.set_new_flow_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                            spacing="1", width="100%"
                                        ),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("Añadir paso al borrador", weight="bold", size="2", color="#0a84ff"),
                                                rx.text("Mensaje a enviar:", size="1", color="#8e8e93"),
                                                rx.text_area(placeholder="Ej: ¡Hola! ¿Cuál es tu nombre completo?", value=SettingsState.step_text, on_change=SettingsState.set_step_text, background="#1a1a1c", border="1px solid #3a3a3c", color="white", rows="2", width="100%"),
                                                rx.grid(
                                                    rx.vstack(
                                                        rx.text("Acción al responder", size="1", color="#8e8e93"),
                                                        rx.select(
                                                            ["none", "ask_name", "ask_email", "assign_agent", "end_flow"],
                                                            value=SettingsState.step_action,
                                                            on_change=SettingsState.set_step_action,
                                                            background="#1a1a1c", color="white", border="1px solid #3a3a3c", width="100%"
                                                        ),
                                                        spacing="1"
                                                    ),
                                                    rx.vstack(
                                                        rx.text("Valor Acción (opcional)", size="1", color="#8e8e93"),
                                                        rx.input(placeholder="Ej: admin / agente1", value=SettingsState.step_action_val, on_change=SettingsState.set_step_action_val, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                        spacing="1"
                                                    ),
                                                    columns="2", spacing="2", width="100%"
                                                ),
                                                rx.hstack(
                                                    rx.button("➕ Añadir Paso", on_click=SettingsState.add_step_to_editing, color_scheme="green", size="1"),
                                                    rx.button("🧹 Limpiar", on_click=SettingsState.clear_editing_steps, variant="outline", size="1"),
                                                    spacing="2"
                                                ),
                                                spacing="2", width="100%"
                                            ),
                                            background="#1c1c1e", border="1px solid #3a3a3c", border_radius="10px", padding="12px", width="100%"
                                        ),
                                        # Vista previa de pasos
                                        rx.text("Pasos del flujo actual:", size="1", color="#8e8e93"),
                                        rx.cond(
                                            SettingsState.new_flow_steps.length() > 0,
                                            rx.vstack(
                                                rx.foreach(
                                                    SettingsState.new_flow_steps,
                                                    lambda s: rx.hstack(
                                                        rx.badge(s["id"].to_string(), color_scheme="blue", radius="full"),
                                                        rx.vstack(
                                                            rx.text(s["text"].to(str), size="2", color="white", line_clamp=1),
                                                            rx.text("Acción: " + s["action"].to(str) + rx.cond(s["action_value"].to(str) != "", " (" + s["action_value"].to(str) + ")", ""), size="1", color="#8e8e93"),
                                                            spacing="0", align_items="start"
                                                        ),
                                                        width="100%", padding="4px", border_bottom="1px solid #2c2c2e"
                                                    )
                                                ),
                                                width="100%"
                                            ),
                                            rx.text("Borrador vacío. Agrega pasos arriba.", color="#636366", size="1")
                                        ),
                                        rx.button("🚀 Guardar y Publicar Flujo", on_click=SettingsState.create_conversational_flow, color_scheme="blue", width="100%"),
                                        rx.cond(SettingsState.flow_msg != "", rx.text(SettingsState.flow_msg, size="2", color="#30d158")),
                                        spacing="3", align_items="stretch", width="100%"
                                    ),
                                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%"
                                ),
                                spacing="3", width="100%"
                            ),
                            columns="2", spacing="4", width="100%"
                        ),
                        
                        rx.divider(color="#2c2c2e", margin="16px 0"),
                        
                        # Lista de Automatizaciones y Flujos Activos
                        rx.grid(
                            rx.vstack(
                                rx.heading("Automatizaciones lineales activas", size="3", color="white"),
                                rx.cond(
                                    SettingsState.workflows.length() > 0,
                                    rx.vstack(
                                        rx.foreach(
                                            SettingsState.workflows,
                                            lambda w: rx.hstack(
                                                rx.vstack(
                                                    rx.text("⚙️ " + w["name"].to(str), weight="bold", size="2", color="white"),
                                                    rx.text(
                                                        rx.match(
                                                            w["action_type"].to(str),
                                                            ("reply", "Si contiene '" + w["condition_value"].to(str) + "', responder: '" + w["action_value"].to(str) + "'"),
                                                            ("assign", "Si contiene '" + w["condition_value"].to(str) + "', asignar a: @" + w["action_value"].to(str)),
                                                            ("set_lifecycle", "Si contiene '" + w["condition_value"].to(str) + "', etapa CRM: " + w["action_value"].to(str)),
                                                            "Acción desconocida"
                                                        ),
                                                        size="1", color="#8e8e93"
                                                    ),
                                                    spacing="0", align_items="start"
                                                ),
                                                rx.spacer(),
                                                rx.button("🗑️", on_click=SettingsState.delete_workflow(w["id"].to(int)), size="1", variant="ghost", color="#ff453a"),
                                                padding="10px", border="1px solid #2c2c2e", border_radius="8px", width="100%", background="#111"
                                            )
                                        ),
                                        width="100%", spacing="2"
                                    ),
                                    rx.text("No tienes reglas lineales creadas.", color="#636366", size="2")
                                ),
                                width="100%", spacing="3"
                            ),
                            rx.vstack(
                                rx.heading("Flujos paso a paso activos", size="3", color="white"),
                                rx.cond(
                                    SettingsState.flows.length() > 0,
                                    rx.vstack(
                                        rx.foreach(
                                            SettingsState.flows,
                                            lambda f: rx.hstack(
                                                rx.vstack(
                                                    rx.text("🚀 " + f["name"].to(str), weight="bold", size="2", color="white"),
                                                    rx.text("Pasos totales: " + f["steps"].to(list).length().to(str), size="1", color="#8e8e93"),
                                                    spacing="0", align_items="start"
                                                ),
                                                rx.spacer(),
                                                rx.button("🗑️", on_click=SettingsState.delete_conversational_flow(f["id"].to(int)), size="1", variant="ghost", color="#ff453a"),
                                                padding="10px", border="1px solid #2c2c2e", border_radius="8px", width="100%", background="#111"
                                            )
                                        ),
                                        width="100%", spacing="2"
                                    ),
                                    rx.text("No tienes flujos paso a paso creados.", color="#636366", size="2")
                                ),
                                width="100%", spacing="3"
                            ),
                            columns="2", spacing="4", width="100%"
                        ),
                        spacing="4", align_items="start", width="100%"
                    ),
                    value="workflows", padding="24px 32px"
                ),

                # ── Empresas (Solo visible para Súper Tenant ID 1)
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("🏢 Gestión de Empresas (Tenants)", size="4", color="white"),
                        rx.text("Registra y administra clientes comerciales, administradores y parámetros de contacto de cada Tenant.", color="#8e8e93", size="2"),
                        
                        rx.grid(
                            # Formulario Nueva Empresa
                            rx.box(
                                rx.vstack(
                                    rx.heading("➕ Nueva Empresa", size="3", color="white"),
                                    rx.text("Registra los datos generales de la empresa cliente.", color="#8e8e93", size="1"),
                                    rx.vstack(
                                        rx.text("Nombre de la Empresa *", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: SubliArtM & Andili", value=SettingsState.nt_name, on_change=SettingsState.set_nt_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                        spacing="1", width="100%"
                                    ),
                                    # Contacto Principal
                                    rx.box(
                                        rx.vstack(
                                            rx.text("👤 Contacto Principal (Requerido)", weight="bold", size="2", color="#0fa3b1"),
                                            rx.grid(
                                                rx.vstack(
                                                    rx.text("Nombre Completo", size="1", color="#8e8e93"),
                                                    rx.input(placeholder="Juan Pérez", value=SettingsState.nt_contact_name_1, on_change=SettingsState.set_nt_contact_name_1, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                    spacing="1"
                                                ),
                                                rx.vstack(
                                                    rx.text("Correo Electrónico", size="1", color="#8e8e93"),
                                                    rx.input(placeholder="juan@empresa.com", value=SettingsState.nt_contact_email_1, on_change=SettingsState.set_nt_contact_email_1, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                    spacing="1"
                                                ),
                                                rx.vstack(
                                                    rx.text("Teléfono de Contacto", size="1", color="#8e8e93"),
                                                    rx.input(placeholder="+52 55 1234 5678", value=SettingsState.nt_contact_phone_1, on_change=SettingsState.set_nt_contact_phone_1, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                    spacing="1"
                                                ),
                                                columns="3", spacing="2", width="100%"
                                            ),
                                            spacing="2", width="100%"
                                        ),
                                        background="#19191b", border="1px solid #2c2c2e", border_radius="10px", padding="12px", width="100%"
                                    ),
                                    # Contacto Secundario (Opcional)
                                    rx.box(
                                        rx.vstack(
                                            rx.text("👥 Contacto Secundario (Opcional)", weight="bold", size="2", color="#8e8e93"),
                                            rx.grid(
                                                rx.vstack(
                                                    rx.text("Nombre Completo", size="1", color="#8e8e93"),
                                                    rx.input(placeholder="María Gómez", value=SettingsState.nt_contact_name_2, on_change=SettingsState.set_nt_contact_name_2, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                    spacing="1"
                                                ),
                                                rx.vstack(
                                                    rx.text("Correo Electrónico", size="1", color="#8e8e93"),
                                                    rx.input(placeholder="maria@empresa.com", value=SettingsState.nt_contact_email_2, on_change=SettingsState.set_nt_contact_email_2, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                    spacing="1"
                                                ),
                                                rx.vstack(
                                                    rx.text("Teléfono de Contacto", size="1", color="#8e8e93"),
                                                    rx.input(placeholder="+52 55 8765 4321", value=SettingsState.nt_contact_phone_2, on_change=SettingsState.set_nt_contact_phone_2, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                    spacing="1"
                                                ),
                                                columns="3", spacing="2", width="100%"
                                            ),
                                            spacing="2", width="100%"
                                        ),
                                        background="#19191b", border="1px solid #2c2c2e", border_radius="10px", padding="12px", width="100%"
                                    ),
                                    rx.button("🏢 Registrar Empresa", on_click=SettingsState.save_tenant, color_scheme="blue", width="100%"),
                                    rx.cond(SettingsState.nt_msg != "", rx.text(SettingsState.nt_msg, size="2", color="#30d158")),
                                    spacing="3", align_items="stretch", width="100%"
                                ),
                                background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%"
                            ),
                            
                            # Panel de Edición (se muestra condicionalmente)
                            rx.cond(
                                SettingsState.et_editing,
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.heading("✏️ Editar Empresa", size="3", color="white"),
                                            rx.spacer(),
                                            rx.button("✕ Cerrar", on_click=SettingsState.close_tenant_edit, size="1", variant="ghost", color="#8e8e93"),
                                        ),
                                        rx.vstack(
                                            rx.text("Nombre de la Empresa", size="1", color="#8e8e93"),
                                            rx.input(value=SettingsState.et_name, on_change=SettingsState.set_et_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                            spacing="1", width="100%"
                                        ),
                                        # Contacto Principal
                                        rx.box(
                                            rx.vstack(
                                                rx.text("👤 Contacto Principal", weight="bold", size="2", color="#0fa3b1"),
                                                rx.grid(
                                                    rx.vstack(
                                                        rx.text("Nombre", size="1", color="#8e8e93"),
                                                        rx.input(value=SettingsState.et_contact_name_1, on_change=SettingsState.set_et_contact_name_1, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                        spacing="1"
                                                    ),
                                                    rx.vstack(
                                                        rx.text("Correo", size="1", color="#8e8e93"),
                                                        rx.input(value=SettingsState.et_contact_email_1, on_change=SettingsState.set_et_contact_email_1, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                        spacing="1"
                                                    ),
                                                    rx.vstack(
                                                        rx.text("Teléfono", size="1", color="#8e8e93"),
                                                        rx.input(value=SettingsState.et_contact_phone_1, on_change=SettingsState.set_et_contact_phone_1, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                        spacing="1"
                                                    ),
                                                    columns="3", spacing="2", width="100%"
                                                ),
                                                spacing="2", width="100%"
                                            ),
                                            background="#19191b", border="1px solid #2c2c2e", border_radius="10px", padding="12px", width="100%"
                                        ),
                                        # Contacto Secundario
                                        rx.box(
                                            rx.vstack(
                                                rx.text("👥 Contacto Secundario", weight="bold", size="2", color="#8e8e93"),
                                                rx.grid(
                                                    rx.vstack(
                                                        rx.text("Nombre", size="1", color="#8e8e93"),
                                                        rx.input(value=SettingsState.et_contact_name_2, on_change=SettingsState.set_et_contact_name_2, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                        spacing="1"
                                                    ),
                                                    rx.vstack(
                                                        rx.text("Correo", size="1", color="#8e8e93"),
                                                        rx.input(value=SettingsState.et_contact_email_2, on_change=SettingsState.set_et_contact_email_2, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                        spacing="1"
                                                    ),
                                                    rx.vstack(
                                                        rx.text("Teléfono", size="1", color="#8e8e93"),
                                                        rx.input(value=SettingsState.et_contact_phone_2, on_change=SettingsState.set_et_contact_phone_2, background="#1a1a1c", border="1px solid #3a3a3c", color="white", width="100%"),
                                                        spacing="1"
                                                    ),
                                                    columns="3", spacing="2", width="100%"
                                                ),
                                                spacing="2", width="100%"
                                            ),
                                            background="#19191b", border="1px solid #2c2c2e", border_radius="10px", padding="12px", width="100%"
                                        ),
                                        rx.hstack(
                                            rx.button("💾 Guardar Cambios", on_click=SettingsState.save_tenant_edit, color_scheme="blue"),
                                            rx.button("🗑️ Eliminar", on_click=SettingsState.delete_tenant_action(SettingsState.et_id), color_scheme="red", variant="soft"),
                                            spacing="3", width="100%"
                                        ),
                                        rx.cond(SettingsState.et_msg != "", rx.text(SettingsState.et_msg, size="2", color="#30d158")),
                                        spacing="3", align_items="stretch", width="100%"
                                    ),
                                    background="#0d1117", border="1px solid #0fa3b1", border_radius="12px", padding="20px", width="100%"
                                ),
                                rx.box(
                                    rx.center(
                                        rx.text("Selecciona una empresa para editar sus datos de contacto y parámetros.", color="#636366", size="2"),
                                        height="100%"
                                    ),
                                    background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%"
                                )
                            ),
                            columns="2", spacing="4", width="100%"
                        ),
                        
                        rx.divider(color="#2c2c2e", margin="16px 0"),
                        
                        # Listado de Empresas
                        rx.heading("Empresas registradas", size="3", color="white"),
                        rx.cond(
                            SettingsState.all_tenants.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    SettingsState.all_tenants,
                                    lambda t: rx.hstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text("🏢 " + t["name"].to(str), weight="bold", size="3", color="white"),
                                                rx.badge(rx.cond(t["active"].to(bool), "Activa", "Inactiva"), color_scheme=rx.cond(t["active"].to(bool), "green", "gray")),
                                                spacing="2", align_items="center"
                                            ),
                                            rx.grid(
                                                rx.cond(
                                                    t["contact_name_1"].to(str) != "",
                                                    rx.vstack(
                                                        rx.text("Contacto Principal:", size="1", color="#0fa3b1", weight="bold"),
                                                        rx.text("👤 " + t["contact_name_1"].to(str), size="1", color="white"),
                                                        rx.text("📧 " + t["contact_email_1"].to(str) + " · 📞 " + t["contact_phone_1"].to(str), size="1", color="#8e8e93"),
                                                        spacing="0", align_items="start"
                                                    ),
                                                    rx.text("Sin contacto principal", size="1", color="#636366")
                                                ),
                                                rx.cond(
                                                    t["contact_name_2"].to(str) != "",
                                                    rx.vstack(
                                                        rx.text("Contacto Secundario:", size="1", color="#8e8e93", weight="bold"),
                                                        rx.text("👤 " + t["contact_name_2"].to(str), size="1", color="white"),
                                                        rx.text("📧 " + t["contact_email_2"].to(str) + " · 📞 " + t["contact_phone_2"].to(str), size="1", color="#8e8e93"),
                                                        spacing="0", align_items="start"
                                                    ),
                                                    rx.text("Sin contacto secundario", size="1", color="#636366")
                                                ),
                                                columns="2", spacing="4", width="100%", margin_top="4px"
                                            ),
                                            spacing="1", align_items="start", flex="1"
                                        ),
                                        rx.hstack(
                                            rx.button("✏️ Editar", on_click=SettingsState.open_tenant_edit(t["id"].to(int)), size="1", variant="soft", color_scheme="blue"),
                                            rx.cond(
                                                t["id"].to(int) != 1,
                                                rx.button("🗑️", on_click=SettingsState.delete_tenant_action(t["id"].to(int)), size="1", variant="ghost", color="#ff453a"),
                                            ),
                                            spacing="2", align_items="center"
                                        ),
                                        padding="16px", border="1px solid #2c2c2e", border_radius="10px", width="100%", background="#111"
                                    )
                                ),
                                width="100%", spacing="2"
                            ),
                            rx.text("No hay empresas registradas.", color="#636366", size="2")
                        ),

                        spacing="4", align_items="start", width="100%",
                    ),
                    value="tenants", padding="24px 32px",
                ),

                # ── Pre-registros (SaaS) ──────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Solicitudes de Registro Pendientes", size="5", color="white", margin_bottom="16px"),
                        rx.cond(
                            AppState.pending_registrations,
                            rx.vstack(
                                rx.foreach(
                                    AppState.pending_registrations,
                                    pre_registration_row
                                ),
                                spacing="4",
                                width="100%"
                            ),
                            rx.text("No hay solicitudes de registro pendientes.", color="#636366", size="2")
                        ),
                        spacing="4", align_items="start", width="100%"
                    ),
                    value="pre_registrations", padding="24px 32px",
                ),

                default_value="users",
                width="100%",
            ),
            spacing="0",
            width="100%",
        ),
        knowledge_base_modal(),
        facebook_onboarding_modal(),
        background="#000000",
        spacing="0",
        min_height="100vh",
        width="100%",
        on_mount=SettingsState.on_mount_settings,
    )
