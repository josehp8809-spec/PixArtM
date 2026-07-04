"""Settings page — admin only."""
import reflex as rx
from nyme.state import AppState
from nyme.pages.navbar import navbar

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database import db
from whatsapp_client import wa_client
from gemini_client import gemini


class SettingsState(AppState):
    # Nueva línea
    nl_name: str = ""
    nl_phone_id: str = ""
    nl_token: str = ""
    nl_welcome: str = ""
    nl_welcome_on: bool = True
    nl_color: str = "#0A84FF"
    nl_msg: str = ""

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

    # Quick reply form
    qr_shortcut: str = ""
    qr_title: str = ""
    qr_message: str = ""
    qr_msg: str = ""

    # Nueva empresa (Tenants)
    nt_name: str = ""
    nt_msg: str = ""
    all_tenants: list[dict] = []

    # Formularios Fase 2
    selected_ai_line_name: str = "Todas las líneas"
    
    @rx.var
    def line_options_ai(self) -> list[str]:
        return ["Todas las líneas"] + [l["name"] for l in self.all_lines]

    @rx.var
    def tenant_options_for_user(self) -> list[str]:
        return [t["name"] for t in self.all_tenants]

    def on_mount_settings(self):
        self.require_auth()
        self._reload_users()
        self._load_core_data()
        if self.tenant_id == 1:
            self._reload_tenants()

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
            {"id": t[0], "name": t[1], "active": bool(t[2])}
            for t in raw
        ]

    def set_nt_name(self, v): self.nt_name = v

    def save_tenant(self):
        if not self.nt_name.strip():
            self.nt_msg = "❌ Nombre de empresa requerido."
            return
        ok, res = db.create_tenant(self.nt_name.strip())
        if ok:
            self.nt_msg = f"✅ Empresa '{self.nt_name.strip()}' creada (ID: {res})."
            # Auto-crear un administrador por defecto para esa empresa para facilitar el setup
            admin_uname = f"admin_{self.nt_name.strip().lower().replace(' ', '')}"
            db.create_user(admin_uname, "Nyme_2026", f"Admin {self.nt_name.strip()}", "admin", res)
            self.nt_name = ""
            self._reload_tenants()
        else:
            self.nt_msg = f"❌ {res}"

    # ── Líneas ────────────────────────────────────────────────────────────────
    def set_nl_name(self, v): self.nl_name = v
    def set_nl_phone_id(self, v): self.nl_phone_id = v
    def set_nl_token(self, v): self.nl_token = v
    def set_nl_welcome(self, v): self.nl_welcome = v
    def set_nl_welcome_on(self, v): self.nl_welcome_on = v
    def set_nl_color(self, v): self.nl_color = v

    def save_line(self):
        if not self.nl_name or not self.nl_phone_id or not self.nl_token:
            self.nl_msg = "❌ Nombre, Phone ID y Token son obligatorios."
            return
        ok, err = db.create_line(
            self.nl_name, self.nl_phone_id, self.nl_token,
            self.nl_welcome, self.nl_welcome_on, self.nl_color,
            self.tenant_id
        )
        if ok:
            self.nl_msg = "✅ Línea creada."
            self.nl_name = self.nl_phone_id = self.nl_token = self.nl_welcome = ""
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

    # ── Gemini ────────────────────────────────────────────────────────────────
    def set_gemini_key(self, v): self.gemini_key = v

    def save_gemini(self):
        if not self.gemini_key.strip():
            self.gemini_msg = "❌ Ingresa la API Key."
            return
        db.set_setting("gemini_api_key", self.gemini_key.strip())
        gemini.reload()
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

    # ── Fase 2 Agentes IA ──────────────────────────────────────────────
    def set_selected_ai_line_name(self, v): 
        self.selected_ai_line_name = v

    def save_ai_agent_settings(self):
        line_id = 0
        if self.selected_ai_line_name != "Todas las líneas":
            for l in self.all_lines:
                if l["name"] == self.selected_ai_line_name:
                    line_id = l["id"]
                    break
        self.new_agent_line_id = line_id
        self.create_ai_agent()


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
    
    return rx.hstack(
        rx.box(width="12px", height="12px", background=color,
               border_radius="50%"),
        rx.vstack(
            rx.text(name, weight="bold", size="2", color="white"),
            rx.text(phone_id, size="1", color="#636366"),
            spacing="0",
        ),
        rx.spacer(),
        rx.badge(
            rx.cond(is_active, "Activa", "Inactiva"),
            color_scheme=rx.cond(is_active, "green", "gray"),
        ),
        rx.button(
            rx.cond(is_active, "Desactivar", "Activar"),
            on_click=SettingsState.toggle_line(line_id, is_active),
            size="1", variant="ghost",
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
    
    return rx.hstack(
        rx.text("@" + username, weight="bold", size="2", color="white", width="140px"),
        rx.text(full_name, size="2", color="#8e8e93", flex="1"),
        rx.cond(
            SettingsState.tenant_id == 1,
            rx.badge("🏢 " + tenant_name, color_scheme="purple", size="1"),
        ),
        rx.badge(role, color_scheme="blue", size="1"),
        rx.button(
            rx.cond(active, "Desactivar", "Activar"),
            on_click=SettingsState.toggle_user(user_id, active),
            size="1", variant="ghost",
            color=rx.cond(active, "#ff453a", "#30d158"),
        ),
        padding="10px",
        border="1px solid #2c2c2e",
        border_radius="10px",
        width="100%",
        spacing="3",
        align_items="center"
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


def settings_page() -> rx.Component:
    return rx.vstack(
        navbar("/settings"),
        rx.vstack(
            rx.heading("⚙️ Configuración", size="7", color="white", padding="24px 32px 8px"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("👥 Usuarios", value="users"),
                    rx.tabs.trigger("📱 Líneas", value="lines"),
                    rx.tabs.trigger("🤖 Agentes IA", value="ai_agents"),
                    rx.tabs.trigger("📨 Plantillas", value="templates"),
                    rx.tabs.trigger("⚙️ Automatizaciones", value="workflows"),
                    rx.tabs.trigger("⚡ Atajos", value="qr"),
                    rx.tabs.trigger("🛍️ Catálogo", value="catalog"),
                    rx.tabs.trigger("🤖 Gemini AI", value="gemini"),
                    rx.tabs.trigger("🔑 Mi Cuenta", value="account"),
                    rx.cond(
                        SettingsState.tenant_id == 1,
                        rx.tabs.trigger("🏢 Empresas", value="tenants"),
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
                        rx.heading("Usuarios activos", size="4", color="white"),
                        rx.foreach(SettingsState.all_users.to(list[dict]), user_row),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="users", padding="24px 32px",
                ),

                # ── Líneas ───────────────────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Líneas de WhatsApp", size="4", color="white"),
                        rx.foreach(SettingsState.all_lines.to(list[dict]), line_row),
                        rx.divider(color="#2c2c2e"),
                        rx.heading("Agregar línea", size="4", color="white"),
                        rx.grid(
                            _field("Nombre *", placeholder="Ventas / Soporte",
                                   on_change=SettingsState.set_nl_name),
                            _field("Phone Number ID *", on_change=SettingsState.set_nl_phone_id),
                            _field("Access Token *", type="password",
                                   on_change=SettingsState.set_nl_token),
                            _field("Mensaje de bienvenida",
                                   placeholder="¡Hola! ¿En qué te ayudamos?",
                                   on_change=SettingsState.set_nl_welcome),
                            columns="2", spacing="3", width="100%",
                        ),
                        rx.button("💾 Guardar línea", on_click=SettingsState.save_line,
                                  color_scheme="blue"),
                        rx.cond(SettingsState.nl_msg != "",
                                  rx.text(SettingsState.nl_msg, size="2")),
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
                        rx.text("La API Key se comparte para todos los usuarios del tenant.", color="#8e8e93", size="2"),
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
                                rx.button("🤖 Guardar Agente IA", on_click=SettingsState.save_ai_agent_settings, color_scheme="blue", width="200px"),
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

                # ── Automatizaciones (Workflows - Fase 3) ──────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("⚙️ Flujos de Trabajo y Automatizaciones", size="4", color="white"),
                        rx.text("Define reglas automáticas If/Then basadas en palabras clave recibidas en tus chats.", color="#8e8e93", size="2"),
                        
                        # Formulario de Creación
                        rx.box(
                            rx.vstack(
                                rx.heading("Crear Nueva Regla de Automatización", size="3", color="white"),
                                rx.grid(
                                    rx.vstack(
                                        rx.text("Nombre de la Regla", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: Auto-Respuesta Precios", on_change=SettingsState.set_new_wf_name, value=SettingsState.new_wf_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Trigger (Evento)", size="1", color="#8e8e93"),
                                        rx.select(
                                            ["message_received"],
                                            value=SettingsState.new_wf_trigger,
                                            on_change=SettingsState.set_new_wf_trigger,
                                            background="#1c1c1e", color="white", border="1px solid #3a3a3c", width="100%"
                                        ),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Condición", size="1", color="#8e8e93"),
                                        rx.select(
                                            ["body_contains"],
                                            value=SettingsState.new_wf_cond_field,
                                            on_change=SettingsState.set_new_wf_cond_field,
                                            background="#1c1c1e", color="white", border="1px solid #3a3a3c", width="100%"
                                        ),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Palabra Clave", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: precio (en minúsculas)", on_change=SettingsState.set_new_wf_cond_val, value=SettingsState.new_wf_cond_val, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Acción a Ejecutar", size="1", color="#8e8e93"),
                                        rx.select(
                                            ["reply", "assign", "set_lifecycle"],
                                            value=SettingsState.new_wf_action_type,
                                            on_change=SettingsState.set_new_wf_action_type,
                                            background="#1c1c1e", color="white", border="1px solid #3a3a3c", width="100%"
                                        ),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Valor de la Acción", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: El costo es $50 / admin / Lead", on_change=SettingsState.set_new_wf_action_val, value=SettingsState.new_wf_action_val, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                        spacing="1"
                                    ),
                                    columns="3", spacing="3", width="100%"
                                ),
                                rx.button("⚙️ Guardar Regla", on_click=SettingsState.create_workflow, color_scheme="blue", width="200px"),
                                rx.cond(SettingsState.wf_msg != "", rx.text(SettingsState.wf_msg, size="2", color="#30d158")),
                                spacing="3", align_items="start", width="100%"
                            ),
                            background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="20px", width="100%"
                        ),
                        
                        rx.divider(color="#2c2c2e", margin="16px 0"),
                        
                        # Lista de Workflows
                        rx.heading("Automatizaciones activas", size="3", color="white"),
                        rx.cond(
                            SettingsState.workflows.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    SettingsState.workflows,
                                    lambda w: rx.hstack(
                                        rx.vstack(
                                            rx.text("⚙️ " + w["name"].to(str), weight="bold", size="3", color="white"),
                                            rx.text(
                                                rx.match(
                                                    w["action_type"].to(str),
                                                    ("reply", "Si el mensaje contiene '" + w["condition_value"].to(str) + "', responder automáticamente: '" + w["action_value"].to(str) + "'"),
                                                    ("assign", "Si el mensaje contiene '" + w["condition_value"].to(str) + "', asignar chat a: @" + w["action_value"].to(str)),
                                                    ("set_lifecycle", "Si el mensaje contiene '" + w["condition_value"].to(str) + "', cambiar etapa CRM a: " + w["action_value"].to(str)),
                                                    "Acción desconocida"
                                                ),
                                                size="2", color="#8e8e93"
                                            ),
                                            spacing="1", align_items="start"
                                        ),
                                        rx.spacer(),
                                        rx.button("🗑️", on_click=SettingsState.delete_workflow(w["id"].to(int)), size="1", variant="ghost", color="#ff453a"),
                                        padding="14px",
                                        border="1px solid #2c2c2e",
                                        border_radius="10px",
                                        width="100%",
                                        background="#111"
                                    )
                                ),
                                width="100%", spacing="2"
                            ),
                            rx.text("No tienes flujos de trabajo creados.", color="#636366", size="2")
                        ),
                        spacing="4", align_items="start", width="100%"
                    ),
                    value="workflows", padding="24px 32px"
                ),

                # ── Empresas (Solo visible para Súper Tenant ID 1)
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("🏢 Empresas (Tenants)", size="4", color="white"),
                        rx.text("Registra y administra clientes comerciales en la plataforma Nyme.", color="#8e8e93", size="2"),
                        rx.hstack(
                            rx.vstack(
                                rx.text("Nombre de la nueva empresa", size="1", color="#8e8e93"),
                                rx.input(
                                    placeholder="Nombre de la Empresa",
                                    value=SettingsState.nt_name,
                                    on_change=SettingsState.set_nt_name,
                                    background="#1c1c1e", border="1px solid #3a3a3c",
                                    color="white", width="300px"
                                ),
                                spacing="1"
                            ),
                            rx.button("🏢 Registrar Empresa", on_click=SettingsState.save_tenant, color_scheme="green", margin_top="18px"),
                            spacing="3",
                            align_items="end"
                        ),
                        rx.cond(SettingsState.nt_msg != "", rx.text(SettingsState.nt_msg, size="2", color="#30d158")),
                        rx.divider(color="#2c2c2e", margin="16px 0"),
                        rx.heading("Empresas activas", size="3", color="white"),
                        rx.foreach(
                            SettingsState.all_tenants,
                            lambda t: rx.hstack(
                                rx.text(t["name"].to(str), weight="bold", size="2", color="white", flex="1"),
                                rx.badge(rx.cond(t["active"].to(bool), "Activa", "Inactiva"), color_scheme="green"),
                                padding="10px",
                                border="1px solid #2c2c2e",
                                border_radius="10px",
                                width="100%",
                            )
                        ),
                        spacing="4", align_items="start", width="100%"
                    ),
                    value="tenants", padding="24px 32px"
                ),

                default_value="users",
                width="100%",
            ),
            spacing="0",
            width="100%",
        ),
        background="#000000",
        spacing="0",
        min_height="100vh",
        width="100%",
        on_mount=SettingsState.on_mount_settings,
    )
