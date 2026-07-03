"""Settings page — admin only."""
import reflex as rx
from nyme.state import AppState

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

    def on_mount_settings(self):
        self.require_auth()
        self._reload_users()
        self._load_core_data()

    def _reload_users(self):
        raw = db.get_all_users()
        self.all_users = [
            {"id": u[0], "username": u[1], "full_name": u[2],
             "role": u[3], "active": bool(u[4])}
            for u in raw
        ]

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
        )
        if ok:
            self.nl_msg = "✅ Línea creada."
            self.nl_name = self.nl_phone_id = self.nl_token = self.nl_welcome = ""
            self._load_core_data()
        else:
            self.nl_msg = f"❌ {err}"

    def toggle_line(self, line_id: int, active: bool):
        db.toggle_line_active(line_id, not active)
        self._load_core_data()

    # ── Usuarios ──────────────────────────────────────────────────────────────
    def set_nu_username(self, v): self.nu_username = v
    def set_nu_fullname(self, v): self.nu_fullname = v
    def set_nu_password(self, v): self.nu_password = v
    def set_nu_role(self, v): self.nu_role = v

    def save_user(self):
        if not self.nu_username or not self.nu_password:
            self.nu_msg = "❌ Usuario y contraseña requeridos."
            return
        ok, err = db.create_user(
            self.nu_username.lower().strip(), self.nu_password,
            self.nu_fullname, self.nu_role,
        )
        if ok:
            self.nu_msg = f"✅ Usuario @{self.nu_username} creado."
            self.nu_username = self.nu_password = self.nu_fullname = ""
            self._reload_users()
        else:
            self.nu_msg = f"❌ {err}"

    def toggle_user(self, user_id: int, active: bool):
        db.toggle_user_active(user_id, not active)
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
        ok, err = db.create_quick_reply(self.qr_shortcut, self.qr_title, self.qr_message)
        if ok:
            self.qr_msg = "✅ Atajo creado."
            self.qr_shortcut = self.qr_title = self.qr_message = ""
            self._load_core_data()
        else:
            self.qr_msg = f"❌ {err}"

    def delete_qr(self, qr_id: int):
        db.delete_quick_reply(qr_id)
        self._load_core_data()


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
    
    return rx.hstack(
        rx.text("@", username, weight="bold", size="2", color="white", width="140px"),
        rx.text(full_name, size="2", color="#8e8e93", flex="1"),
        rx.badge(role, color_scheme="blue"),
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
    return rx.box(
        rx.vstack(
            rx.heading("⚙️ Configuración", size="7", color="white", padding="24px 32px 8px"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("👥 Usuarios", value="users"),
                    rx.tabs.trigger("📱 Líneas", value="lines"),
                    rx.tabs.trigger("⚡ Atajos", value="qr"),
                    rx.tabs.trigger("🛍️ Catálogo", value="catalog"),
                    rx.tabs.trigger("🤖 Gemini AI", value="gemini"),
                    rx.tabs.trigger("🔑 Mi Cuenta", value="account"),
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
                                ),
                                spacing="1",
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
                        rx.text("La API Key se comparte para todos los usuarios.",
                                color="#8e8e93", size="2"),
                        _field("API Key de Gemini", type="password",
                               placeholder="AIza...", on_change=SettingsState.set_gemini_key),
                        rx.button("💾 Guardar", on_click=SettingsState.save_gemini,
                                  color_scheme="blue"),
                        rx.cond(SettingsState.gemini_msg != "",
                                  rx.text(SettingsState.gemini_msg, size="2")),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="gemini", padding="24px 32px",
                ),

                # ── Mi Cuenta ────────────────────────────────────────────
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("🔑 Cambiar contraseña", size="4", color="white"),
                        _field("Nueva contraseña", type="password",
                               on_change=SettingsState.set_pwd_new),
                        _field("Confirmar contraseña", type="password",
                               on_change=SettingsState.set_pwd_confirm),
                        rx.button("Cambiar contraseña", on_click=SettingsState.change_password,
                                  color_scheme="blue"),
                        rx.cond(SettingsState.pwd_msg != "",
                                  rx.text(SettingsState.pwd_msg, size="2")),
                        spacing="4", align_items="start", width="100%",
                    ),
                    value="account", padding="24px 32px",
                ),

                default_value="users",
                width="100%",
            ),
            background="#000000",
            min_height="100vh",
            width="100%",
        ),
        on_mount=SettingsState.on_mount_settings,
    )
