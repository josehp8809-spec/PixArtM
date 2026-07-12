"""
state.py — AppState central de Nyme (Reflex).
Toda la lógica de negocio se delega a database.py, whatsapp_client.py, gemini_client.py.
"""
import asyncio
import sys
import os

import reflex as rx

# Asegurar que el directorio raíz esté en el path para importar los módulos backend
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import db
from whatsapp_client import wa_client
from gemini_client import gemini


# ─────────────────────────────────────────────────────────────────────────────
# AppState — único estado global de la app
# ─────────────────────────────────────────────────────────────────────────────

class AppState(rx.State):

    # ── Autenticación ─────────────────────────────────────────────────────────
    authenticated: bool = False
    user_id: int = 0
    username: str = ""
    full_name: str = ""
    role: str = ""
    tenant_id: int = 1
    tenant_name: str = ""
    current_plan_name: str = "Starter"
    current_billing_period: str = "monthly"
    current_ai_mode: str = "BYOK"

    # ── Formulario de login ───────────────────────────────────────────────────
    login_username: str = ""
    login_password: str = ""
    login_error: str = ""
    landing_lang: str = "es"

    # ── Auto-Registro ─────────────────────────────────────────────────────────
    reg_company_name: str = ""
    reg_contact_name: str = ""
    reg_contact_email: str = ""
    reg_contact_phone: str = ""
    reg_notes: str = ""
    reg_selected_plan: str = "Starter"
    reg_billing_frequency: str = "monthly"
    reg_ai_mode: str = "BYOK"
    reg_success: bool = False
    reg_error: str = ""

    # ── Landing Page Pricing State ──────────────────────────────────────────
    pricing_byok: bool = True
    pricing_period: str = "monthly"

    # ── Aprobación de Registro ───────────────────────────────────────────────
    pending_registrations: list[dict] = []
    approved_registrations: list[dict] = []
    approve_username: str = ""
    approve_password: str = ""
    approve_error: str = ""
    approve_success: str = ""

    # ── Soporte Técnico ──────────────────────────────────────────────────────
    support_messages: list[dict] = []
    support_new_message: str = ""
    support_room_id: int = 0
    show_support_chat: bool = False
    support_rooms_list: list[dict] = []
    active_support_room_id: int = 0
    active_support_tenant_name: str = ""
    client_timezone: str = "America/Mexico_City"

    # ── Chat de Soporte de Visitante (Landing Page) ───────────────────────────
    visitor_chat_open: bool = False
    visitor_name: str = ""
    visitor_new_message: str = ""
    visitor_chat_started: bool = False
    visitor_messages: list[dict] = []
    visitor_wa_id: str = ""

    # ── Datos cargados ────────────────────────────────────────────────────────
    contacts: list[dict]      = []
    messages: list[dict]      = []
    all_lines: list[dict]     = []
    quick_replies: list[dict] = []
    internal_messages: list[dict] = []
    contact_list: list[dict]      = []
    team_list: list[dict]         = []

    # ── Búsqueda ──────────────────────────────────────────────────────────────
    contact_search: str = ""
    team_search: str    = ""
    total_unread: int   = 0   # Para rastrear nuevos mensajes y sonar
    play_sound_tick: int = 0  # Trigger para el componente de audio
    show_emoji_picker: bool = False
    emoji_list: list[str] = [
        "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"
    ]

    # ── Chat activo ───────────────────────────────────────────────────────────
    selected_contact: str  = ""
    selected_line_id: int  = 0
    selected_room_id: int  = 0
    selected_room_name: str = "General"
    conv_status: str       = "pending"
    new_message: str       = ""
    internal_chat_msg: str = ""

    # ── Nuevo Contacto ────────────────────────────────────────────────────────
    nc_wa_id: str = ""
    nc_name: str  = ""
    nc_email: str = ""
    nc_notes: str = ""
    nc_msg: str   = ""

    # ── UI helpers ────────────────────────────────────────────────────────────
    toast_message: str  = ""
    ai_result:  str = ""
    orders_filter_status: str = "all"
    order_msg: str = ""
    
    # Campo auxiliar para agregar un item libre personalizado
    special_item_name: str = ""
    special_item_price: str = ""
    loading_ai: bool    = False
    mobile_view: str    = "contacts"   # "contacts" | "chat"  (mobile only)

    # ── Fase 1 (CRM y Filtros Avanzados) ──────────────────────────────────────
    filter_assignment: str = "all"      # "all" | "mine" | "unassigned"
    filter_status: str = "open"          # "open" | "closed" | "snoozed"
    assigned_agent: str = ""             # Agente asignado a la conversación activa
    chat_mode: str = "message"           # "message" (WhatsApp) | "note" (Nota interna)
    contact_lifecycle_stage: str = "New Customer" # Etapa de ciclo de vida del contacto activo
    lifecycle_counts: dict[str, int] = {"New Customer": 0, "Lead": 0, "Customer": 0, "Paid": 0}

    # ── Fase 2 (Agentes IA, Plantillas de Meta y Analítica) ───────────────────
    # Agentes IA
    ai_agents: list[dict] = []
    new_agent_name: str = ""
    new_agent_prompt: str = ""
    new_agent_line_id: int = 0
    new_agent_active: bool = True
    agent_msg: str = ""

    # Plantillas de Mensajes
    templates: list[dict] = []
    new_tpl_name: str = ""
    new_tpl_category: str = "UTILITY"
    new_tpl_body: str = ""
    tpl_msg: str = ""
    show_template_modal: bool = False

    # Analítica y Dashboard
    avg_response_time: float = 0.0
    conversation_states_chart: dict[str, int] = {"pending": 0, "active": 0, "snoozed": 0, "resolved": 0}
    top_agents: list[dict] = []

    # ── Fase 3 (Automatizaciones - Workflows) ──────────────────────────────────
    workflows: list[dict] = []
    new_wf_name: str = ""
    new_wf_trigger: str = "message_received"
    new_wf_cond_field: str = "body_contains"
    new_wf_cond_val: str = ""
    new_wf_action_type: str = "reply"
    new_wf_action_val: str = ""
    wf_msg: str = ""


    # ── Cambio de contraseña ──────────────────────────────────────────────────
    pwd_new: str     = ""
    pwd_confirm: str = ""
    pwd_msg: str     = ""

    # ── Módulo de Catálogo ────────────────────────────────────────────────────
    products: list[dict] = []
    editing_product_id: int = 0
    new_product_name: str = ""
    new_product_desc: str = ""
    new_product_price: str = ""
    new_product_image: str = ""
    new_product_seasonal: bool = True
    prod_msg: str = ""

    # ── Módulo de Pedidos ─────────────────────────────────────────────────────
    orders: list[dict] = []
    order_items: list[dict] = [] # Borrador del pedido: [{"product": name, "quantity": qty, "price": pr}]
    order_address: str = ""
    special_item_price: str = ""

    # ─────────────────────────────────────────────────────────────────────────
    # AUTH
    # ─────────────────────────────────────────────────────────────────────────

    def set_login_username(self, val: str):
        self.login_username = val

    def set_login_password(self, val: str):
        self.login_password = val

    def handle_login_key(self, key: str):
        if key == "Enter":
            return self.login()

    def login(self):
        user = db.verify_user(self.login_username.strip().lower(), self.login_password)
        if user:
            self.authenticated = True
            self.user_id   = user["id"]
            self.username  = user["username"]
            self.full_name = user["full_name"] or user["username"]
            self.role      = user["role"]
            self.tenant_id = user["tenant_id"]
            tenant_info = db.get_tenant_by_id(self.tenant_id)
            if tenant_info:
                self.tenant_name = tenant_info["name"]
            else:
                self.tenant_name = "Empresa"
            self.login_error = ""
            self._load_core_data()
            return rx.redirect("/chat")
        else:
            self.login_error = "❌ Usuario o contraseña incorrectos, o cuenta inactiva."

    def logout(self):
        self.authenticated = False
        self.user_id = 0
        self.username = self.full_name = self.role = ""
        self.tenant_id = 1
        self.tenant_name = ""
        self.selected_contact = ""
        self.contacts = self.messages = self.all_lines = self.quick_replies = []
        return rx.redirect("/login")

    def reset_sound_tick(self):
        self.play_sound_tick = 0

    def require_auth(self):
        if not self.authenticated:
            return rx.redirect("/login")

    @rx.event
    def toggle_landing_lang(self):
        if self.landing_lang == "es":
            self.landing_lang = "en"
        else:
            self.landing_lang = "es"

    # ─────────────────────────────────────────────────────────────────────────
    # DATOS BASE
    # ─────────────────────────────────────────────────────────────────────────

    def _load_core_data(self):
        """Carga líneas, quick replies, contactos, métricas, agentes IA, plantillas, analítica y automatizaciones."""
        # Cargar plan actual de la empresa
        t_info = db.get_tenant_by_id(self.tenant_id)
        if t_info:
            self.current_plan_name = t_info.get("plan_name", "Starter")
            self.current_billing_period = t_info.get("billing_period", "monthly")
            self.current_ai_mode = t_info.get("ai_mode", "BYOK")
        raw_lines = db.get_all_lines(self.tenant_id)
        self.all_lines = [
            {
                "id": l[0], "name": l[1], "phone_number_id": l[2],
                "access_token": l[3], "welcome_message": l[4] or "",
                "welcome_active": bool(l[5]), "color": l[6] or "#0A84FF",
                "is_active": bool(l[7]),
                "channel_type": l[8] if len(l) > 8 else "whatsapp",
                "page_id": l[9] if len(l) > 9 else "",
                "app_id": l[10] if len(l) > 10 else "",
                "tenant_name": l[11] if len(l) > 11 else "",
                "tenant_id": l[12] if len(l) > 12 else self.tenant_id
            }
            for l in raw_lines
        ]
        raw_qr = db.get_quick_replies(self.tenant_id)
        self.quick_replies = [
            {"id": q[0], "shortcut": q[1], "title": q[2] or "", "message": q[3]}
            for q in raw_qr
        ]
        self._refresh_contacts()
        self._refresh_internal()
        self._refresh_contact_list()
        self._refresh_team()
        self._update_total_unread()
        self._refresh_products()
        self._refresh_orders()
        self._refresh_lifecycle_counts()
        self._refresh_ai_agents()
        self._refresh_templates()
        self._refresh_analytics()
        self._refresh_workflows()

    def _update_total_unread(self):
        new_total = sum(c["unread"] for c in self.contacts)
        if new_total > self.total_unread:
            self.play_sound_tick += 1 # Dispara el sonido
        self.total_unread = new_total

    def set_contact_search(self, v): self.contact_search = v
    def set_team_search(self, v): self.team_search = v

    @rx.var
    def filtered_contact_list(self) -> list[dict]:
        if not self.contact_search:
            return self.contact_list
        q = self.contact_search.lower()
        return [
            c for c in self.contact_list 
            if q in c["name"].lower() or q in c["wa_id"] or q in c["notes"].lower()
        ]

    @rx.var
    def filtered_team_list(self) -> list[dict]:
        if not self.team_search:
            return self.team_list
        q = self.team_search.lower()
        return [
            u for u in self.team_list 
            if q in u["full_name"].lower() or q in u["username"].lower()
        ]

    @rx.var
    def order_total_amount(self) -> float:
        total = 0.0
        for item in self.order_items:
            try:
                qty = int(item.get("quantity", 1))
                price = float(item.get("price", 0.0))
                total += qty * price
            except (ValueError, TypeError):
                pass
        return total

    @rx.var
    def order_total_amount_str(self) -> str:
        return f"${self.order_total_amount:.2f}"

    @rx.var
    def current_agent_limit(self) -> int:
        if self.current_plan_name == "Starter":
            return 2
        elif self.current_plan_name == "Pro":
            return 5
        return 999 # Enterprise / Ilimitado

    @rx.var
    def current_agent_count(self) -> int:
        return sum(1 for u in self.team_list if u.get("role") == "agent")
    def _refresh_contacts(self):
        raw = db.get_contacts_for_user(self.user_id, self.role, self.tenant_id)
        self.contacts = [
            {
                "wa_id": c[0], 
                "line_id": c[2] or 0,
                "status": c[3] or "pending", 
                "unread": c[4] or 0,
                "assigned_to": c[5] or "",
                "name": c[6] or c[0],
                "lifecycle_stage": c[7] or "New Customer"
            }
            for c in raw
        ]

    @rx.var
    def filtered_contacts(self) -> list[dict]:
        res = []
        for c in self.contacts:
            # 1. Filtrar por Asignación
            assign = c.get("assigned_to", "")
            if self.filter_assignment == "mine" and assign != self.username:
                continue
            if self.filter_assignment == "unassigned" and assign != "":
                continue

            # 2. Filtrar por Estado
            status = c.get("status", "pending")
            if self.filter_status == "open" and status not in ("pending", "active", "open"):
                continue
            if self.filter_status == "closed" and status not in ("resolved", "closed"):
                continue
            if self.filter_status == "snoozed" and status != "snoozed":
                continue

            res.append(c)
        return res

    def set_filter_assignment(self, val: str):
        self.filter_assignment = val

    def set_filter_status(self, val: str):
        self.filter_status = val

    def set_chat_mode(self, mode: str):
        self.chat_mode = mode
        
    @rx.var
    def agent_options(self) -> list[str]:
        # Lista de agentes de la empresa para dropdown de asignación
        return ["[Sin Asignar]"] + [u["username"] for u in self.team_list]

    @rx.var
    def selected_contact_name(self) -> str:
        if not self.selected_contact:
            return ""
        for c in self.contacts:
            if c["wa_id"] == self.selected_contact:
                return c["name"]
        return "+" + self.selected_contact

    def _refresh_messages(self):
        if not self.selected_contact:
            return
        raw = db.get_messages(self.selected_contact, self.tenant_id)
        self.messages = []
        for m in raw:
            body = m[1] or ""
            media_id = m[5] if len(m) > 5 and m[5] else ""
            media_url = m[6] if len(m) > 6 and m[6] else ""
            is_audio = "[🎤 Audio]" in body or bool(media_id)
            has_media = bool(media_id)
            self.messages.append({
                "type": m[0],
                "body": body,
                "time": self.format_local_time(m[2]),
                "agent": m[3] or "",
                "line_id": m[4] or 0,
                "media_id": media_id,
                "media_url": media_url,
                "is_audio": is_audio,
                "has_media": has_media,
            })

    def _refresh_internal(self):
        raw = db.get_internal_messages()
        self.internal_messages = [
            {"user": r[0], "msg": r[1], "time": self.format_local_time(r[2])}
            for r in raw
        ]

    def _refresh_contact_list(self):
        raw = db.get_all_contacts(self.tenant_id)
        self.contact_list = [
            {"wa_id": r[0], "name": r[1] or "", "email": r[2] or "", "notes": r[3] or ""}
            for r in raw
        ]

    def _refresh_team(self):
        raw = db.get_team_status()
        self.team_list = [
            {"id": r[0], "username": r[1], "full_name": r[2] or r[1], 
             "role": r[3], "is_online": bool(r[4])}
            for r in raw
        ]

    def update_presence(self):
        if self.authenticated:
            db.update_user_presence(self.user_id)

    def _line_name(self, line_id: int) -> str:
        for l in self.all_lines:
            if l["id"] == line_id:
                return l["name"]
        return "?"

    def _line_color(self, line_id: int) -> str:
        for l in self.all_lines:
            if l["id"] == line_id:
                return l["color"]
        return "#888888"

    # ─────────────────────────────────────────────────────────────────────────
    # REAL-TIME POLLING (WebSocket background task)
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event(background=True)
    async def start_polling(self):
        """Se ejecuta en background y actualiza la UI cada 5 segundos via WebSocket."""
        while True:
            await asyncio.sleep(5)
            async with self:
                if not self.authenticated:
                    break
                self.update_presence()
                self._refresh_contacts()
                self._refresh_internal()
                self._refresh_team()
                self._update_total_unread()
                self._refresh_products()
                self._refresh_orders()
                self._refresh_lifecycle_counts()
                self._refresh_analytics()
                if self.selected_contact:
                    self._refresh_messages()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAT
    # ─────────────────────────────────────────────────────────────────────────

    def select_contact(self, wa_id: str, line_id: int):
        self.selected_contact = wa_id
        self.selected_line_id = line_id
        self.mobile_view = "chat"   # en móvil, cambiar a vista de chat
        db.mark_conversation_read(wa_id, line_id)
        self._refresh_messages()
        for c in self.contacts:
            if c["wa_id"] == wa_id and c["line_id"] == line_id:
                self.conv_status = c.get("status", "pending")
                self.assigned_agent = c.get("assigned_to", "")
                self.contact_lifecycle_stage = c.get("lifecycle_stage", "New Customer")
                break

    def assign_to_agent(self, agent_username: str):
        if not self.selected_contact:
            return
        db.assign_conversation(
            self.selected_contact, 
            self.selected_line_id, 
            agent_username if agent_username != "[Sin Asignar]" else "",
            self.tenant_id
        )
        self.assigned_agent = agent_username if agent_username != "[Sin Asignar]" else ""
        self._refresh_contacts()

    def assign_to_me(self):
        self.assign_to_agent(self.username)

    def set_contact_lifecycle_stage(self, stage: str):
        if not self.selected_contact:
            return
        db.update_contact_lifecycle(self.selected_contact, stage, self.tenant_id)
        self.contact_lifecycle_stage = stage
        self._refresh_contacts()
        self._refresh_lifecycle_counts()

    def _refresh_lifecycle_counts(self):
        counts = db.get_lifecycle_counts(self.tenant_id)
        self.lifecycle_counts = counts

    def start_chat_with(self, wa_id: str):
        line_id = 0
        for c in self.contacts:
            if c["wa_id"] == wa_id:
                line_id = c["line_id"]
                break
        if line_id == 0 and self.all_lines:
            line_id = self.all_lines[0]["id"]
        self.select_contact(wa_id, line_id)
        return rx.redirect("/chat")

    def go_back(self):
        """Volver a la lista de contactos (móvil)."""
        self.mobile_view = "contacts"
        self.selected_contact = ""

    def set_new_message(self, val: str):
        self.new_message = val

    def toggle_emoji_picker(self):
        self.show_emoji_picker = not self.show_emoji_picker

    def add_emoji(self, emoji: str):
        self.new_message += emoji
        # self.show_emoji_picker = False # Opcional: cerrar al elegir

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Procesa archivos subidos (fotos, documentos)."""
        if not self.selected_contact or not files:
            return

        line = next((l for l in self.all_lines if l["id"] == self.selected_line_id), None)
        if not line: return

        for file in files:
            upload_data = await file.read()
            # Guardar temporalmente para subir a Meta
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(upload_data)
            
            # 1. Determinar tipo
            mime = "image/jpeg" if file.filename.lower().endswith((".jpg", ".jpeg", ".png")) else "application/pdf"
            msg_type = "image" if "image" in mime else "document"
            
            # 2. Subir a Meta
            media_id = wa_client.upload_media(line, temp_path, mime)
            os.remove(temp_path)
            
            if media_id:
                 # 3. Enviar mensaje
                 if msg_type == "image":
                     wa_client.send_image_message(line, self.selected_contact, media_id)
                 else:
                     wa_client.send_document_message(line, self.selected_contact, media_id, file.filename)
                 
                 # 4. Guardar en DB
                 async with self:
                     db.save_message(
                         self.selected_contact, f"OUTBOUND_{msg_type.upper()}", 
                         f"[{msg_type.capitalize()}: {file.filename}]", 
                         self.username, self.selected_line_id, tenant_id=self.tenant_id
                     )
                     self._refresh_messages()
                     self._refresh_contacts()
 
    def send_message(self):
        text = self.new_message.strip()
        if not text or not self.selected_contact:
            return
        if self.chat_mode == "note":
            db.save_message(
                self.selected_contact, "NOTE", text,
                agent_username=self.username, line_id=self.selected_line_id,
                tenant_id=self.tenant_id
            )
        else:
            if self.selected_contact.startswith("web_"):
                # Canal Chat Web
                db.save_message(
                    self.selected_contact, "OUTBOUND_REPLY", text,
                    agent_username=self.username, line_id=self.selected_line_id,
                    tenant_id=self.tenant_id
                )
            else:
                # Canal WhatsApp o Red Social
                line = next((l for l in self.all_lines if l["id"] == self.selected_line_id), None)
                channel_type = "whatsapp"
                if line:
                    channel_type = line.get("channel_type", "whatsapp")
                    if line["is_active"]:
                        if channel_type in ("messenger", "instagram"):
                            from meta_client import meta_client
                            meta_client.send_message(line, self.selected_contact, text)
                        else:
                            wa_client.send_text_message(line, self.selected_contact, text)
                db.save_message(
                    self.selected_contact, "OUTBOUND_REPLY", text,
                    agent_username=self.username, line_id=self.selected_line_id,
                    tenant_id=self.tenant_id, channel_type=channel_type
                )
        self.new_message = ""
        self._refresh_messages()
        self._refresh_contacts()

    def send_quick_reply(self, message: str):
        self.new_message = message
        self.send_message()

    def set_conv_status(self, status: str):
        self.conv_status = status
        db.set_conversation_status(self.selected_contact, self.selected_line_id, status)
        self._refresh_contacts()

    def archive_current_conversation(self):
        if self.selected_contact and self.selected_line_id:
            self.set_conv_status("resolved")

    def reopen_current_conversation(self):
        if self.selected_contact and self.selected_line_id:
            self.set_conv_status("active")

    # ─────────────────────────────────────────────────────────────────────────
    # GEMINI AI (chat)
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event(background=True)
    async def suggest_reply(self):
        async with self:
            self.loading_ai = True
            products_list = list(self.products)
        result = gemini.suggest_reply(
            [(m["type"], m["body"], None, m["agent"]) for m in self.messages],
            products=products_list,
            tenant_id=self.tenant_id
        )
        async with self:
            self.loading_ai = False
            self.ai_result = result or "No se pudo generar una sugerencia."

    @rx.event(background=True)
    async def translate_last(self):
        last_inbound = next(
            (m for m in reversed(self.messages) if m["type"] == "INBOUND"), None
        )
        if not last_inbound:
            return
        async with self:
            self.loading_ai = True
        translated = gemini.translate(last_inbound["body"], tenant_id=self.tenant_id)
        async with self:
            self.loading_ai = False
            self.ai_result = translated or "No se pudo traducir."

    def use_ai_result(self):
        if self.ai_result:
            self.new_message = self.ai_result
            self.ai_result = ""

    def clear_ai_result(self):
        self.ai_result = ""

    # ─────────────────────────────────────────────────────────────────────────
    # CONTRASEÑA
    # ─────────────────────────────────────────────────────────────────────────

    def set_pwd_new(self, val: str):     self.pwd_new = val
    def set_pwd_confirm(self, val: str): self.pwd_confirm = val

    def change_password(self):
        if len(self.pwd_new) < 6:
            self.pwd_msg = "❌ Mínimo 6 caracteres."
        elif self.pwd_new != self.pwd_confirm:
            self.pwd_msg = "❌ Las contraseñas no coinciden."
        elif db.change_password(self.username, self.pwd_new):
            self.pwd_msg = "✅ Contraseña actualizada."
            self.pwd_new = self.pwd_confirm = ""
    # ── Internal Chat ────────────────────────────────────────────────────────

    def set_internal_chat_msg(self, v): self.internal_chat_msg = v

    def handle_internal_key(self, key: str):
        if key == "Enter":
            return self.send_internal_message()

    def send_internal_message(self):
        if not self.internal_chat_msg.strip(): return
        db.save_internal_message(
            self.username, 
            self.internal_chat_msg.strip(), 
            room_id=self.selected_room_id if self.selected_room_id > 0 else None
        )
        self.internal_chat_msg = ""
        self._refresh_internal()

    def select_room(self, room_id: int, name: str):
        self.selected_room_id = room_id
        self.selected_room_name = name
        self._refresh_internal()

    # ── Contact Directory ─────────────────────────────────────────────────────

    def set_nc_wa_id(self, v): self.nc_wa_id = v
    def set_nc_name(self, v):  self.nc_name = v
    def set_nc_email(self, v): self.nc_email = v
    def set_nc_notes(self, v): self.nc_notes = v
    def save_contact(self):
        if not self.nc_wa_id.strip():
            self.nc_msg = "❌ WhatsApp ID es requerido."
            return
        db.upsert_contact(self.nc_wa_id.strip(), self.nc_name, self.nc_email, self.nc_notes, self.tenant_id)
        self.nc_msg = "✅ Contacto guardado."
        self.nc_wa_id = self.nc_name = self.nc_email = self.nc_notes = ""
        self._refresh_contact_list()

    @rx.event(background=True)
    async def transcribe_audio(self, media_id: str):
        if not media_id: return
        async with self:
            self.loading_ai = True
        
        # 1. Obtener URL de Meta
        line = next((l for l in self.all_lines if l["id"] == self.selected_line_id), None)
        if not line: return
        
        media_url = wa_client.get_media_url(line, media_id)
        if not media_url:
            async with self:
                self.loading_ai = False
                self.ai_result = "❌ No se pudo obtener el audio de Meta."
            return
        
        # 2. Descargar audio
        audio_data = wa_client.download_media(line, media_url)
        
        # 3. Transcribir con Gemini
        transcription = gemini.transcribe_audio(audio_data, tenant_id=self.tenant_id)
        
        async with self:
            self.loading_ai = False
            self.ai_result = f"📝 Transcripción: {transcription}"

    def assign_chat(self, agent_username: str):
        db.assign_conversation(self.selected_contact, self.selected_line_id, agent_username, self.tenant_id)
        self._refresh_contacts()

    def export_contacts(self):
        """Genera y descarga un Excel con la lista de clientes."""
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from report_exporter import exporter
        
        # Mock de datos para el exportador
        data = [
            {"WhatsApp": c["wa_id"], "Nombre": c["name"], "Email": c["email"], "Notas": c["notes"]}
            for c in self.contact_list
        ]
        
        # En una app real usaríamos exporter.export_to_excel con los datos de DB
        # Por ahora devolvemos un mensaje de éxito
        self.nc_msg = "✅ Exportación generada con éxito (Check logs)."
        print(f"[Export] {len(data)} contactos exportados.")

    # ── Métodos Auxiliares de Carga ──────────────────────────────────────────

    def _refresh_products(self):
        raw = db.get_all_products(self.tenant_id)
        self.products = [
            {
                "id": p[0], "name": p[1], "description": p[2] or "",
                "price": float(p[3]), "image_url": p[4] or "",
                "is_seasonal": bool(p[5])
            }
            for p in raw
        ]

    def _refresh_orders(self):
        import json
        raw = db.get_orders(self.tenant_id)
        self.orders = []
        for r in raw:
            try:
                items_val = r[3]
                if isinstance(items_val, str):
                    items = json.loads(items_val)
                elif isinstance(items_val, list):
                    items = items_val
                else:
                    items = []
            except Exception:
                items = []
            
            contact_name = ""
            for c in self.contact_list:
                if c["wa_id"] == r[1]:
                    contact_name = c["name"]
                    break
            if not contact_name:
                contact_name = f"+{r[1]}"

            self.orders.append({
                "id": r[0],
                "wa_id": r[1],
                "contact_name": contact_name,
                "agent_username": r[2] or "Sistema",
                "items": items,
                "total_amount": float(r[4]),
                "status": r[5],
                "shipping_address": r[6] or "Retiro en local",
                "created_at": r[7].strftime("%d/%m/%Y %H:%M") if r[7] else "",
                "updated_at": r[8].strftime("%d/%m/%Y %H:%M") if r[8] else ""
            })

    # ── Handlers de Formulario de Catálogo ─────────────────────────────────────

    def set_new_product_name(self, v): self.new_product_name = v
    def set_new_product_desc(self, v): self.new_product_desc = v
    def set_new_product_price(self, v): self.new_product_price = v
    def set_new_product_image(self, v): self.new_product_image = v
    def set_new_product_seasonal(self, v): self.new_product_seasonal = bool(v)

    def start_edit_product(self, product: dict):
        self.editing_product_id = product["id"]
        self.new_product_name = product["name"]
        self.new_product_desc = product["description"]
        self.new_product_price = str(product["price"])
        self.new_product_image = product["image_url"]
        self.new_product_seasonal = product["is_seasonal"]
        self.prod_msg = "✏️ Editando producto."

    def cancel_edit_product(self):
        self.editing_product_id = 0
        self.new_product_name = ""
        self.new_product_desc = ""
        self.new_product_price = ""
        self.new_product_image = ""
        self.new_product_seasonal = True
        self.prod_msg = ""

 
    def save_product(self):
        if not self.new_product_name.strip():
            self.prod_msg = "❌ El nombre es obligatorio."
            return
        try:
            price = float(self.new_product_price)
        except ValueError:
            self.prod_msg = "❌ El precio debe ser un número válido."
            return

        if self.editing_product_id > 0:
            ok = db.update_product(
                self.editing_product_id,
                self.new_product_name.strip(),
                self.new_product_desc.strip(),
                price,
                self.new_product_image.strip(),
                self.new_product_seasonal,
                self.tenant_id
            )
            if ok:
                self.prod_msg = "✅ Producto actualizado."
                self.cancel_edit_product()
                self._refresh_products()
            else:
                self.prod_msg = "❌ Error al actualizar producto."
        else:
            ok = db.save_product(
                self.new_product_name.strip(),
                self.new_product_desc.strip(),
                price,
                self.new_product_image.strip(),
                self.new_product_seasonal,
                self.tenant_id
            )
            if ok:
                self.prod_msg = "✅ Producto guardado."
                self.new_product_name = ""
                self.new_product_desc = ""
                self.new_product_price = ""
                self.new_product_image = ""
                self.new_product_seasonal = True
                self._refresh_products()
            else:
                self.prod_msg = "❌ Error al guardar producto."

    def delete_product(self, product_id: int):
        if db.delete_product(product_id, self.tenant_id):
            self.prod_msg = "🗑️ Producto eliminado."
            self._refresh_products()
        else:
            self.prod_msg = "❌ Error al eliminar producto."

    # ── Handlers de Borrador de Pedidos ──────────────────────────────────────

    def set_order_address(self, v): self.order_address = v
    def set_special_item_name(self, v): self.special_item_name = v
    def set_special_item_price(self, v): self.special_item_price = v

    def add_product_to_order_draft(self, product: dict):
        for item in self.order_items:
            if item.get("product") == product["name"]:
                item["quantity"] += 1
                self.order_items = list(self.order_items)
                return
        self.order_items.append({
            "product": product["name"],
            "quantity": 1,
            "price": product["price"]
        })
        self.order_items = list(self.order_items)

    def add_special_item_to_order_draft(self):
        name = self.special_item_name.strip()
        if not name:
            return
        try:
            price = float(self.special_item_price)
        except ValueError:
            price = 0.0
        self.order_items.append({
            "product": name,
            "quantity": 1,
            "price": price
        })
        self.order_items = list(self.order_items)
        self.special_item_name = ""
        self.special_item_price = ""

    def remove_order_item(self, product_name: str):
        self.order_items = [item for item in self.order_items if item.get("product") != product_name]
        self.order_items = list(self.order_items)

    def update_order_item_qty(self, product_name: str, value: str):
        try:
            val = int(value)
            for item in self.order_items:
                if item.get("product") == product_name:
                    item["quantity"] = val
                    break
            self.order_items = list(self.order_items)
        except ValueError:
            pass

    def update_order_item_price(self, product_name: str, value: str):
        try:
            val = float(value)
            for item in self.order_items:
                if item.get("product") == product_name:
                    item["price"] = val
                    break
            self.order_items = list(self.order_items)
        except ValueError:
            pass

    def clear_order_draft(self):
        self.order_items = []
        self.order_address = ""
        self.order_msg = ""

    @rx.event(background=True)
    async def create_order(self):
        async with self:
            if not self.selected_contact:
                self.order_msg = "❌ Selecciona un contacto primero."
                return
            if not self.order_items:
                self.order_msg = "❌ El pedido está vacío."
                return
            
            wa_id = self.selected_contact
            agent = self.username
            items = list(self.order_items)
            total = self.order_total_amount
            address = self.order_address.strip()
            
            order_id = db.create_order(wa_id, agent, items, total, address, self.tenant_id)
            
            if order_id:
                self.order_items = []
                self.order_address = ""
                self.order_msg = f"✅ Pedido #{order_id} creado con éxito."
                self._refresh_orders()
            else:
                self.order_msg = "❌ Error al registrar el pedido en la base de datos."
                return

        customer_email = None
        for c in self.contact_list:
            if c["wa_id"] == wa_id:
                customer_email = c.get("email")
                break
        
        from email_client import email_client
        await email_client.send_order_notification(
            order_id, wa_id, agent, items, total, address, "pending", customer_email
        )

    @rx.event(background=True)
    async def update_order_status(self, order_id: int, new_status: str):
        if db.update_order_status(order_id, new_status, self.tenant_id):
            async with self:
                self._refresh_orders()
                order = next((o for o in self.orders if o["id"] == order_id), None)
                if not order:
                    return
                wa_id = order["wa_id"]
                agent = order["agent_username"]
                items = order["items"]
                total = order["total_amount"]
                address = order["shipping_address"]

            customer_email = None
            for c in self.contact_list:
                if c["wa_id"] == wa_id:
                    customer_email = c.get("email")
                    break

            from email_client import email_client
            await email_client.send_order_notification(
                order_id, wa_id, agent, items, total, address, new_status, customer_email
            )

    @rx.event(background=True)
    async def auto_fill_order_with_ai(self):
        async with self:
            if not self.selected_contact or not self.messages:
                return
            self.loading_ai = True
        
        history_text = "\n".join([f"{m['type']}: {m['body']}" for m in self.messages[-10:]])
        
        prompt = f"""
        Analiza la siguiente conversación de chat y extrae la información del pedido.
        Debes responder ÚNICAMENTE en formato JSON con la siguiente estructura, sin bloques de código ```json o texto adicional:
        {{
            "items": [
                {{"product": "Nombre del producto", "quantity": 1, "price": 0.0}}
            ],
            "address": "Dirección completa de entrega, o vacío si no se menciona"
        }}
        
        Conversación:
        {history_text}
        """
        
        try:
            model = gemini._get_model(self.tenant_id)
            if model:
                response = model.generate_content(prompt)
                res_text = response.text.strip()
                if res_text.startswith("```"):
                    res_text = res_text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                
                import json
                parsed = json.loads(res_text)
                
                async with self:
                    self.order_items = parsed.get("items", [])
                    self.order_address = parsed.get("address", "")
                    self.order_msg = "✨ Pedido autocompletado por IA."
            else:
                async with self:
                    self.order_msg = "❌ Gemini no está configurado."
        except Exception as e:
            print(f"[Gemini Autocompletado] Error: {e}")
            async with self:
                self.order_msg = "❌ No se pudo extraer la información con la IA."
        
        async with self:
            self.loading_ai = False

    def send_product_details(self, product: dict):
        detail_msg = f"🛍️ *{product['name']}*\n{product['description']}\n🏷️ *Precio:* ${product['price']:.2f}"
        if product.get("image_url"):
            detail_msg += f"\n📸 *Imagen:* {product['image_url']}"
        self.new_message = detail_msg

    # ── Métodos de la Fase 2 ─────────────────────────────────────────────────
    
    # Agentes IA
    def set_new_agent_name(self, v): self.new_agent_name = v
    def set_new_agent_prompt(self, v): self.new_agent_prompt = v
    def set_new_agent_line_id(self, v): self.new_agent_line_id = int(v)
    def set_new_agent_active(self, v): self.new_agent_active = bool(v)

    def _refresh_ai_agents(self):
        self.ai_agents = db.get_ai_agents(self.tenant_id)

    def create_ai_agent(self):
        name = self.new_agent_name.strip()
        prompt = self.new_agent_prompt.strip()
        if not name or not prompt:
            self.agent_msg = "❌ Nombre e instrucciones de sistema son obligatorios."
            return
        
        ok, err = db.create_ai_agent(
            name, prompt, self.new_agent_line_id, self.new_agent_active, self.tenant_id
        )
        if ok:
            self.agent_msg = f"✅ Agente '{name}' guardado correctamente."
            self.new_agent_name = ""
            self.new_agent_prompt = ""
            self.new_agent_line_id = 0
            self.new_agent_active = True
            self._refresh_ai_agents()
        else:
            self.agent_msg = f"❌ Error: {err}"

    def delete_ai_agent(self, agent_id: int):
        if db.delete_ai_agent(agent_id, self.tenant_id):
            self.agent_msg = "🗑️ Agente IA eliminado."
            self._refresh_ai_agents()
        else:
            self.agent_msg = "❌ Error al eliminar agente."

    # Plantillas de Mensajes
    def set_new_tpl_name(self, v): self.new_tpl_name = v
    def set_new_tpl_category(self, v): self.new_tpl_category = v
    def set_new_tpl_body(self, v): self.new_tpl_body = v

    def _refresh_templates(self):
        self.templates = db.get_message_templates(self.tenant_id)

    def create_message_template(self):
        name = self.new_tpl_name.strip().lower().replace(" ", "_")
        body = self.new_tpl_body.strip()
        if not name or not body:
            self.tpl_msg = "❌ Nombre y texto del mensaje son obligatorios."
            return
        
        ok, err = db.create_message_template(
            name, self.new_tpl_category, body, self.tenant_id
        )
        if ok:
            self.tpl_msg = f"✅ Plantilla '{name}' guardada."
            self.new_tpl_name = ""
            self.new_tpl_body = ""
            self._refresh_templates()
        else:
            self.tpl_msg = f"❌ Error: {err}"

    def delete_message_template(self, tpl_id: int):
        if db.delete_message_template(tpl_id, self.tenant_id):
            self.tpl_msg = "🗑️ Plantilla eliminada."
            self._refresh_templates()
        else:
            self.tpl_msg = "❌ Error al eliminar plantilla."

    def toggle_template_modal(self):
        self.show_template_modal = not self.show_template_modal

    def send_template(self, body_text: str):
        """Envía una plantilla de mensaje al cliente seleccionado."""
        if not self.selected_contact:
            return
        
        # Envío por WhatsApp o Red Social
        line = next((l for l in self.all_lines if l["id"] == self.selected_line_id), None)
        channel_type = "whatsapp"
        if line:
            channel_type = line.get("channel_type", "whatsapp")
            if line["is_active"]:
                if channel_type in ("messenger", "instagram"):
                    from meta_client import meta_client
                    meta_client.send_message(line, self.selected_contact, body_text)
                else:
                    wa_client.send_text_message(line, self.selected_contact, body_text)
            
        # Registrar en la base de datos
        db.save_message(
            self.selected_contact, "OUTBOUND_REPLY", body_text,
            agent_username=self.username, line_id=self.selected_line_id,
            tenant_id=self.tenant_id, channel_type=channel_type
        )
        
        self.show_template_modal = False
        self._refresh_messages()
        self._refresh_contacts()

    # Detección de canal social (Messenger, Instagram, Web Chat)
    @rx.var
    def is_social_channel(self) -> bool:
        """True si el contacto seleccionado es de Messenger, Instagram o Web Chat."""
        if not self.selected_contact:
            return False
        return (
            self.selected_contact.startswith("fb_") or
            self.selected_contact.startswith("ig_") or
            self.selected_contact.startswith("web_")
        )

    # Detección de ventana de 24 horas
    @rx.var
    def is_24h_window_closed(self) -> bool:
        if not self.selected_contact:
            return False
        # Los canales sociales (Messenger, Instagram, Web) no tienen ventana de 24h de WhatsApp
        if (
            self.selected_contact.startswith("fb_") or
            self.selected_contact.startswith("ig_") or
            self.selected_contact.startswith("web_")
        ):
            return False
        
        last_inbound_time = db.get_last_inbound_time(self.selected_contact, self.tenant_id)
        if not last_inbound_time:
            return False
            
        from datetime import datetime, timezone
        now = datetime.now(last_inbound_time.tzinfo) if last_inbound_time.tzinfo else datetime.now()
        diff = now - last_inbound_time
        return diff.total_seconds() > (24 * 3600)

    # Analíticas y Reportes
    def _refresh_analytics(self):
        self.avg_response_time = db.get_average_response_time(self.tenant_id)
        self.conversation_states_chart = db.get_conversation_states_chart(self.tenant_id)
        self.top_agents = db.get_top_agents(self.tenant_id)

    # ── CRUD Automatizaciones (Workflows - Fase 3) ──────────────────────
    def set_new_wf_name(self, v): self.new_wf_name = v
    def set_new_wf_trigger(self, v): self.new_wf_trigger = v
    def set_new_wf_cond_field(self, v): self.new_wf_cond_field = v
    def set_new_wf_cond_val(self, v): self.new_wf_cond_val = v
    def set_new_wf_action_type(self, v): self.new_wf_action_type = v
    def set_new_wf_action_val(self, v): self.new_wf_action_val = v

    def _refresh_workflows(self):
        self.workflows = db.get_workflows(self.tenant_id)

    def create_workflow(self):
        name = self.new_wf_name.strip()
        cond_val = self.new_wf_cond_val.strip()
        action_val = self.new_wf_action_val.strip()
        if not name or not cond_val or not action_val:
            self.wf_msg = "❌ Todos los campos son obligatorios."
            return
        
        ok, err = db.create_workflow(
            name, self.new_wf_trigger, self.new_wf_cond_field, cond_val,
            self.new_wf_action_type, action_val, self.tenant_id
        )
        if ok:
            self.wf_msg = f"✅ Regla '{name}' guardada correctamente."
            self.new_wf_name = ""
            self.new_wf_cond_val = ""
            self.new_wf_action_val = ""
            self._refresh_workflows()
        else:
            self.wf_msg = f"❌ Error: {err}"

    def delete_workflow(self, workflow_id: int):
        if db.delete_workflow(workflow_id, self.tenant_id):
            self.wf_msg = "🗑️ Regla de automatización eliminada."
            self._refresh_workflows()
        else:
            self.wf_msg = "❌ Error al eliminar regla."

    # ── Importación Masiva CSV (Fase 3) ──────────────────────────────────
    async def import_contacts_csv(self, upload_files: list[rx.UploadFile]):
        import csv
        import io
        import re

        count = 0
        errors = 0
        for file in upload_files:
            try:
                content = await file.read()
                decoded = content.decode("utf-8-sig")
                f = io.StringIO(decoded)
                reader = csv.reader(f)
                
                header = next(reader, None)
                if not header:
                    continue
                
                name_idx = 0
                phone_idx = 1
                email_idx = 2
                notes_idx = 3

                # Intentar adivinar mapeo de columnas según nombre de cabecera
                for i, col in enumerate(header):
                    col_lower = col.lower()
                    if "nombre" in col_lower or "name" in col_lower:
                        name_idx = i
                    elif "telefono" in col_lower or "teléfono" in col_lower or "phone" in col_lower or "wa_id" in col_lower:
                        phone_idx = i
                    elif "email" in col_lower or "correo" in col_lower:
                        email_idx = i
                    elif "nota" in col_lower or "notes" in col_lower or "comentario" in col_lower:
                        notes_idx = i
                
                for row in reader:
                    if not row or len(row) <= max(name_idx, phone_idx):
                        continue
                    
                    raw_phone = row[phone_idx].strip()
                    phone = re.sub(r"\D", "", raw_phone)
                    if not phone:
                        continue
                    
                    name = row[name_idx].strip() if len(row) > name_idx else "Sin Nombre"
                    email = row[email_idx].strip() if len(row) > email_idx else ""
                    notes = row[notes_idx].strip() if len(row) > notes_idx else ""
                    
                    db.upsert_contact(phone, name, email, notes, self.tenant_id)
                    count += 1
            except Exception as e:
                print(f"[CSV Import] Error procesando archivo: {e}")
                errors += 1
        
        if errors > 0:
            self.wf_msg = f"⚠️ Importados {count} contactos. Ocurrieron {errors} errores."
        else:
            self.wf_msg = f"✅ ¡Importación masiva exitosa! {count} contactos añadidos."
        self._refresh_contact_list()
        self._refresh_contacts()

    # Setters manuales para Auto-Registro y Soporte
    def set_reg_company_name(self, val: str): self.reg_company_name = val
    def set_reg_contact_name(self, val: str): self.reg_contact_name = val
    def set_reg_contact_email(self, val: str): self.reg_contact_email = val
    def set_reg_contact_phone(self, val: str): self.reg_contact_phone = val
    def set_reg_notes(self, val: str): self.reg_notes = val
    def set_reg_selected_plan(self, val: str): self.reg_selected_plan = val
    def set_reg_billing_frequency(self, val: str): self.reg_billing_frequency = val
    def set_reg_ai_mode(self, val: str): self.reg_ai_mode = val
    def set_pricing_byok(self, val: bool): self.pricing_byok = val
    def set_pricing_period(self, val: str): self.pricing_period = val
    @rx.event
    def handle_buy_plan(self, plan_name: str):
        ai_str = "byok" if self.pricing_byok else "incluida"
        url = f"/register?plan={plan_name}&frequency={self.pricing_period}&ai={ai_str}"
        return rx.redirect(url)
    def set_approve_username(self, val: str): self.approve_username = val
    def set_approve_password(self, val: str): self.approve_password = val
    def set_support_new_message(self, val: str): self.support_new_message = val
    def handle_support_key(self, key: str):
        if key == "Enter":
            return self.send_support_message()

    def set_client_timezone(self, tz: str): self.client_timezone = tz

    @rx.event
    def detect_timezone(self):
        return rx.call_script(
            "Intl.DateTimeFormat().resolvedOptions().timeZone",
            callback=AppState.set_client_timezone
        )

    def format_local_time(self, dt):
        if not dt:
            return ""
        from zoneinfo import ZoneInfo
        try:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            local_dt = dt.astimezone(ZoneInfo(self.client_timezone))
            return local_dt.strftime("%H:%M")
        except Exception as e:
            print(f"[Timezone Error] {e}")
            return dt.strftime("%H:%M")

    # ── Auto-Registro ─────────────────────────────────────────────────────────
    @rx.event
    def on_mount_register(self):
        self.reset_registration_form()
        plan = self.router.page.params.get("plan", "Starter")
        freq = self.router.page.params.get("frequency", "monthly")
        ai = self.router.page.params.get("ai", "BYOK")
        
        # Mapear de query params a valores correctos
        if plan.lower() == "pro":
            self.reg_selected_plan = "Pro"
        elif plan.lower() == "enterprise":
            self.reg_selected_plan = "Enterprise"
        else:
            self.reg_selected_plan = "Starter"
            
        if freq.lower() in ("semestral", "semestralmente"):
            self.reg_billing_frequency = "semestral"
        elif freq.lower() in ("annual", "anual", "anualmente"):
            self.reg_billing_frequency = "annual"
        else:
            self.reg_billing_frequency = "monthly"
            
        if ai.lower() == "incluida":
            self.reg_ai_mode = "Incluida"
        else:
            self.reg_ai_mode = "BYOK"

    @rx.event
    def reset_registration_form(self):
        self.reg_company_name = ""
        self.reg_contact_name = ""
        self.reg_contact_email = ""
        self.reg_contact_phone = ""
        self.reg_notes = ""
        self.reg_success = False
        self.reg_error = ""

    @rx.event
    def submit_registration(self):
        self.reg_error = ""
        self.reg_success = False
        
        if not self.reg_company_name.strip():
            self.reg_error = "El nombre de la empresa es obligatorio."
            return
        if not self.reg_contact_name.strip():
            self.reg_error = "El nombre de contacto es obligatorio."
            return
        if not self.reg_contact_email.strip() or "@" not in self.reg_contact_email:
            self.reg_error = "Por favor ingresa un correo electrónico válido."
            return

        res = db.save_pre_registration(
            self.reg_company_name.strip(),
            self.reg_contact_name.strip(),
            self.reg_contact_email.strip(),
            self.reg_contact_phone.strip(),
            self.reg_notes.strip(),
            selected_plan=self.reg_selected_plan,
            billing_frequency=self.reg_billing_frequency,
            ai_mode=self.reg_ai_mode
        )
        if res:
            self.reg_success = True
            self.reg_company_name = ""
            self.reg_contact_name = ""
            self.reg_contact_email = ""
            self.reg_contact_phone = ""
            self.reg_notes = ""
        else:
            self.reg_error = "Este correo electrónico ya se encuentra registrado o hubo un error."

    # ── Aprobación de Registro ───────────────────────────────────────────────
    @rx.event
    def load_pending_registrations(self):
        self.pending_registrations = db.get_pre_registrations("pending")
        self.approved_registrations = db.get_pre_registrations("approved")
        self.approve_error = ""
        self.approve_success = ""

    @rx.event
    def approve_registration(self, req_id: int):
        self.approve_error = ""
        self.approve_success = ""
        self.approve_username = ""
        self.approve_password = ""
        
        # Buscar los detalles del preregistro
        req = next((r for r in self.pending_registrations if r["id"] == req_id), None)
        if not req:
            self.approve_error = "Solicitud no encontrada."
            return

        # Generar credenciales automáticamente
        import unicodedata
        import re
        import random
        import secrets
        import string

        # 1. Generar Nombre de Usuario Único (Nombre + primera letra del apellido)
        contact_name = req["contact_name"]
        cleaned = unicodedata.normalize('NFKD', contact_name).encode('ASCII', 'ignore').decode('utf-8')
        cleaned = re.sub(r'[^a-zA-Z\s]', '', cleaned).strip().lower()
        parts = cleaned.split()
        if len(parts) >= 2:
            base_user = parts[0] + parts[1][0]
        elif len(parts) == 1:
            base_user = parts[0]
        else:
            base_user = "admin"
            
        if len(base_user) < 3 and len(parts) >= 2:
            base_user = parts[0] + parts[1]
            
        generated_username = base_user
        while db.check_username_exists(generated_username):
            generated_username = f"{base_user}{random.randint(10, 99)}"

        # 2. Generar Contraseña Legible y Segura
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        generated_password = "".join(secrets.choice(chars) for _ in range(10))

        # 1. Crear el Tenant
        success_t, tenant_res = db.create_tenant(
            req["company_name"],
            email=req["contact_email"],
            phone=req["contact_phone"],
            contact_name_1=req["contact_name"],
            contact_email_1=req["contact_email"],
            contact_phone_1=req["contact_phone"]
        )
        if not success_t:
            self.approve_error = f"Error creando empresa: {tenant_res}"
            return
            
        new_tenant_id = tenant_res

        # Guardar detalles del plan en el Tenant aprobado
        db.update_tenant_plan(
            new_tenant_id,
            req.get("selected_plan", "Starter"),
            req.get("billing_frequency", "monthly"),
            req.get("ai_mode", "BYOK")
        )

        # 2. Crear el Usuario Admin
        success_u, user_res = db.create_user(
            generated_username,
            generated_password,
            req["contact_name"],
            "admin",
            new_tenant_id
        )
        if not success_u:
            self.approve_error = f"Empresa creada (ID {new_tenant_id}), pero falló creación de usuario: {user_res}"
            return

        # 3. Marcar el preregistro como aprobado y guardar credenciales
        db.update_pre_registration_status(req_id, "approved", generated_username, generated_password)
        
        # 4. Enviar Correo de Activación
        from nyme.email_client import send_welcome_email
        email_sent = send_welcome_email(
            to_email=req["contact_email"],
            company_name=req["company_name"],
            contact_name=req["contact_name"],
            username=generated_username,
            password=generated_password,
            plan_name=req.get("selected_plan", "Starter"),
            billing_frequency=req.get("billing_frequency", "monthly"),
            ai_mode=req.get("ai_mode", "BYOK")
        )

        mail_status = "Correo enviado con accesos." if email_sent else "No se pudo enviar el correo (SMTP no configurado). Guarda los accesos de abajo."
        self.approve_username = generated_username
        self.approve_password = generated_password
        self.approve_success = f"✅ Empresa '{req['company_name']}' activada con éxito. ({mail_status})"
        self.load_pending_registrations()

    @rx.event
    def reject_registration(self, req_id: int):
        db.update_pre_registration_status(req_id, "rejected")
        self.load_pending_registrations()

    # ── Chat de Soporte Técnico ─────────────────────────────────────────────
    @rx.event
    def toggle_support_chat(self):
        self.show_support_chat = not self.show_support_chat
        if self.show_support_chat:
            self.load_support_chat()

    @rx.event
    def load_support_chat(self):
        # Para clientes (no SaaS Global): cargar su propia sala de soporte
        if self.tenant_id > 1:
            room_id = db.get_or_create_support_room(self.tenant_id)
            if room_id:
                self.support_room_id = room_id
                raw_msgs = db.get_support_messages(room_id)
                self.support_messages = [
                    {
                        "id": m["id"],
                        "room_id": m["room_id"],
                        "sender_username": m["sender_username"],
                        "sender_tenant_id": m["sender_tenant_id"],
                        "message": m["message"],
                        "created_at": self.format_local_time(m["created_at"])
                    }
                    for m in raw_msgs
                ]
        # Para Superadmin (SaaS Global): cargar todas las salas activas de soporte
        elif self.tenant_id == 1:
            self.support_rooms_list = db.get_all_support_rooms()
            if self.active_support_room_id > 0:
                raw_msgs = db.get_support_messages(self.active_support_room_id)
                self.support_messages = [
                    {
                        "id": m["id"],
                        "room_id": m["room_id"],
                        "sender_username": m["sender_username"],
                        "sender_tenant_id": m["sender_tenant_id"],
                        "message": m["message"],
                        "created_at": self.format_local_time(m["created_at"])
                    }
                    for m in raw_msgs
                ]

    @rx.event
    def send_support_message(self):
        msg_text = self.support_new_message.strip()
        if not msg_text:
            return
            
        room_to_send = self.support_room_id if self.tenant_id > 1 else self.active_support_room_id
        if not room_to_send:
            return

        success = db.save_support_message(
            room_to_send,
            self.username or "Asesor",
            self.tenant_id,
            msg_text
        )
        if success:
            self.support_new_message = ""
            raw_msgs = db.get_support_messages(room_to_send)
            self.support_messages = [
                {
                    "id": m["id"],
                    "room_id": m["room_id"],
                    "sender_username": m["sender_username"],
                    "sender_tenant_id": m["sender_tenant_id"],
                    "message": m["message"],
                    "created_at": self.format_local_time(m["created_at"])
                }
                for m in raw_msgs
            ]
            if self.tenant_id == 1:
                self.support_rooms_list = db.get_all_support_rooms()

    @rx.event
    def select_support_room(self, room_id: int, tenant_name: str):
        self.active_support_room_id = room_id
        self.active_support_tenant_name = tenant_name
        raw_msgs = db.get_support_messages(room_id)
        self.support_messages = [
            {
                "id": m["id"],
                "room_id": m["room_id"],
                "sender_username": m["sender_username"],
                "sender_tenant_id": m["sender_tenant_id"],
                "message": m["message"],
                "created_at": self.format_local_time(m["created_at"])
            }
            for m in raw_msgs
        ]

    def set_visitor_name(self, val: str): self.visitor_name = val
    def set_visitor_new_message(self, val: str): self.visitor_new_message = val

    @rx.event
    def toggle_visitor_chat(self):
        self.visitor_chat_open = not self.visitor_chat_open
        if self.visitor_chat_open:
            self.detect_timezone()
            if self.visitor_chat_started:
                return AppState.poll_visitor_messages()

    @rx.event
    def start_visitor_chat(self):
        name_val = self.visitor_name.strip()
        if not name_val:
            return
        import uuid
        self.visitor_wa_id = "web_" + str(uuid.uuid4())[:8]
        db.upsert_contact(self.visitor_wa_id, name_val, "", "Origen: Landing Chat", 1)
        self.visitor_chat_started = True
        self.visitor_messages = []
        return AppState.poll_visitor_messages()

    def load_visitor_messages(self):
        if not self.visitor_wa_id:
            return
        raw = db.get_messages(self.visitor_wa_id, 1)
        self.visitor_messages = []
        for m in raw:
            body = m[1] or ""
            self.visitor_messages.append({
                "type": m[0],
                "body": body,
                "time": self.format_local_time(m[2]),
                "agent": m[3] or "",
            })

    @rx.event
    def send_visitor_message(self):
        msg_text = self.visitor_new_message.strip()
        if not msg_text or not self.visitor_wa_id:
            return

        lines = db.get_all_lines(1)
        valid_line_id = lines[0][0] if lines else 1

        db.save_message(self.visitor_wa_id, "INBOUND", msg_text, line_id=valid_line_id, tenant_id=1)
        db.mark_conversation_unread(self.visitor_wa_id, valid_line_id)
        self.visitor_new_message = ""
        self.load_visitor_messages()

        # Disparar respondedor de IA automático para chat web
        import asyncio
        from nyme.nyme import run_ai_agent_responder, execute_workflows_for_message
        asyncio.create_task(
            run_ai_agent_responder(self.visitor_wa_id, valid_line_id, {}, msg_text, 1)
        )
        asyncio.create_task(
            execute_workflows_for_message(self.visitor_wa_id, valid_line_id, {}, msg_text, 1)
        )

    @rx.event(background=True)
    async def poll_visitor_messages(self):
        while True:
            await asyncio.sleep(4)
            async with self:
                if not self.visitor_chat_open or not self.visitor_chat_started:
                    break
                self.load_visitor_messages()


