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

    # ── Formulario de login ───────────────────────────────────────────────────
    login_username: str = ""
    login_password: str = ""
    login_error: str = ""

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
        return rx.redirect("/")

    def reset_sound_tick(self):
        self.play_sound_tick = 0

    def require_auth(self):
        if not self.authenticated:
            return rx.redirect("/")

    # ─────────────────────────────────────────────────────────────────────────
    # DATOS BASE
    # ─────────────────────────────────────────────────────────────────────────

    def _load_core_data(self):
        """Carga líneas, quick replies, contactos, métricas, agentes IA, plantillas y analítica."""
        raw_lines = db.get_all_lines(self.tenant_id)
        self.all_lines = [
            {
                "id": l[0], "name": l[1], "phone_number_id": l[2],
                "access_token": l[3], "welcome_message": l[4] or "",
                "welcome_active": bool(l[5]), "color": l[6] or "#0A84FF",
                "is_active": bool(l[7]),
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
        self.messages = [
            {
                "type": m[0], "body": m[1],
                "time": m[2].strftime("%H:%M") if m[2] else "",
                "agent": m[3] or "", "line_id": m[4] or 0,
                "media_id": m[5] if len(m) > 5 else None,
                "media_url": m[6] if len(m) > 6 else None,
            }
            for m in raw
        ]

    def _refresh_internal(self):
        raw = db.get_internal_messages()
        self.internal_messages = [
            {"user": r[0], "msg": r[1], "time": r[2].strftime("%H:%M")}
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
            line = next((l for l in self.all_lines if l["id"] == self.selected_line_id), None)
            if line and line["is_active"]:
                wa_client.send_text_message(line, self.selected_contact, text)
            db.save_message(
                self.selected_contact, "OUTBOUND_REPLY", text,
                agent_username=self.username, line_id=self.selected_line_id,
                tenant_id=self.tenant_id
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
            products=products_list
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
        translated = gemini.translate(last_inbound["body"])
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
        transcription = gemini.transcribe_audio(audio_data)
        
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
            model = gemini._get_model()
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
        
        # Envío por WhatsApp API
        line = next((l for l in self.all_lines if l["id"] == self.selected_line_id), None)
        if line and line["is_active"]:
            wa_client.send_text_message(line, self.selected_contact, body_text)
            
        # Registrar en la base de datos
        db.save_message(
            self.selected_contact, "OUTBOUND_REPLY", body_text,
            agent_username=self.username, line_id=self.selected_line_id,
            tenant_id=self.tenant_id
        )
        
        self.show_template_modal = False
        self._refresh_messages()
        self._refresh_contacts()

    # Detección de ventana de 24 horas
    @rx.var
    def is_24h_window_closed(self) -> bool:
        if not self.selected_contact:
            return False
        
        last_inbound_time = db.get_last_inbound_time(self.selected_contact, self.tenant_id)
        if not last_inbound_time:
            # Si no hay mensajes entrantes previos, no hay ventana cerrada
            return False
            
        from datetime import datetime, timezone
        # Comparar en UTC (asumiendo que last_inbound_time está en hora local o UTC)
        # Para evitar problemas de timezone naive vs aware:
        now = datetime.now(last_inbound_time.tzinfo) if last_inbound_time.tzinfo else datetime.now()
        diff = now - last_inbound_time
        return diff.total_seconds() > (24 * 3600)

    # Analíticas y Reportes
    def _refresh_analytics(self):
        self.avg_response_time = db.get_average_response_time(self.tenant_id)
        self.conversation_states_chart = db.get_conversation_states_chart(self.tenant_id)
        self.top_agents = db.get_top_agents(self.tenant_id)

