import reflex as rx
from nyme.state import AppState
from nyme.pages.navbar import navbar

STATUS_ICONS  = {"pending": "⏳", "active": "🟡", "resolved": "✅"}
STATUS_LABELS = {"pending": "Pendiente", "active": "En curso", "resolved": "Resuelto"}

# ─────────────────────────────────────────────────────────────────────────────
# Componentes
# ─────────────────────────────────────────────────────────────────────────────

def template_selector_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.heading("📨 Plantillas de WhatsApp", size="4", color="white"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("✕", variant="ghost", on_click=AppState.toggle_template_modal)
                    ),
                    width="100%", align_items="center"
                ),
                rx.text("Meta requiere usar una plantilla pre-aprobada para abrir conversación si han pasado más de 24 horas.", size="1", color="#8e8e93"),
                rx.divider(color="#2c2c2e", margin_y="12px"),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            AppState.templates,
                            lambda t: rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("📨 " + t["name"].to(str), weight="bold", size="2", color="#0a84ff"),
                                        rx.spacer(),
                                        rx.badge(t["category"].to(str), color_scheme="blue", size="1"),
                                        spacing="2", width="100%"
                                    ),
                                    rx.text(t["body_text"].to(str), size="1", color="white", white_space="pre-wrap"),
                                    rx.button(
                                        "Enviar esta plantilla",
                                        on_click=AppState.send_template(t["body_text"]),
                                        size="1", color_scheme="green", width="100%", margin_top="8px"
                                    ),
                                    align_items="start", spacing="2", width="100%"
                                ),
                                background="#1c1c1e",
                                border="1px solid #3a3a3c",
                                border_radius="10px",
                                padding="12px",
                                width="100%",
                                margin_bottom="8px"
                            )
                        ),
                        width="100%", spacing="1"
                    ),
                    max_height="350px", width="100%"
                ),
                align_items="start", width="100%", spacing="3"
            ),
            background="#111", border="1px solid #2c2c2e", border_radius="12px", max_width="450px"
        ),
        open=AppState.show_template_modal,
    )

def avatar_box(name: rx.Var, size="40px") -> rx.Component:
    initial = name[0]
    return rx.center(
        rx.text(initial, weight="bold", color="white", size="2"),
        width=size, height=size, background="#2c2c2e", border_radius="50%", flex_shrink="0",
        border="1px solid #3a3a3c"
    )

def contact_item(contact: rx.Var) -> rx.Component:
    unread = contact["unread"].to(int)
    status = contact["status"].to(str)
    wa_id = contact["wa_id"].to(str)
    line_id = contact["line_id"].to(int)
    assigned_to = contact["assigned_to"].to(str)
    name = contact["name"].to(str)
    lifecycle = contact["lifecycle_stage"].to(str)
    
    is_selected = (
        (AppState.selected_contact == wa_id)
        & (AppState.selected_line_id == line_id)
    )
    
    display_name = rx.cond(
        name != wa_id,
        name,
        "+" + wa_id
    )

    return rx.box(
        rx.hstack(
            avatar_box(display_name),
            rx.vstack(
                rx.text(display_name, weight="bold", size="2", color="white", line_clamp=1),
                rx.hstack(
                    rx.text(
                        rx.match(
                            status,
                            ("pending", "⏳ Pendiente"),
                            ("active", "🟡 En curso"),
                            ("resolved", "✅ Cerrado"),
                            ("snoozed", "💤 Pospuesto"),
                            "⏳ Pendiente"
                        ),
                        size="1", color="#8e8e93",
                    ),
                    rx.cond(
                        assigned_to != "",
                        rx.badge("👤 " + assigned_to.to(str), color_scheme="blue", size="1", variant="soft", radius="full"),
                    ),
                    rx.badge(lifecycle, color_scheme="gray", size="1", variant="outline", radius="full"),
                    spacing="2", align_items="center"
                ),
                align_items="start", spacing="0", flex="1"
            ),
            rx.cond(unread > 0, rx.badge(unread.to_string(), color_scheme="red", radius="full")),
            width="100%",
            align_items="center"
        ),
        on_click=AppState.select_contact(wa_id, line_id),
        background=rx.cond(is_selected, "#1c1c1e", "transparent"),
        border_radius="10px", padding="12px", cursor="pointer", width="100%",
        border=rx.cond(is_selected, "1px solid #3a3a3c", "1px solid transparent"),
        _hover={"background": "#1c1c1e"},
    )


def message_bubble(msg: rx.Var) -> rx.Component:
    msg_type = msg["type"].to(str)
    is_note = msg_type == "NOTE"
    is_in = msg["type"] == "INBOUND"
    body_str = msg["body"].to(str)
    media_id_str = msg["media_id"].to(str)
    is_audio = body_str.contains("[🎤 Audio]") | (media_id_str != "")
    
    # Burbuja de Nota Interna
    note_content = rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("📝 NOTA INTERNA", weight="bold", size="1", color="#FFD60A"),
                rx.spacer(),
                rx.text("Solo visible para el equipo", size="1", color="#8e8e93"),
                width="100%", align_items="center"
            ),
            rx.text(body_str, size="2", color="white", white_space="pre-wrap"),
            rx.text("Por: " + msg['agent'].to(str) + " · " + msg['time'].to(str), size="1", color="#8e8e93"),
            spacing="1", align_items="stretch"
        ),
        background="#1c1c1e",
        border="1px solid #FFD60A",
        border_radius="12px",
        padding="12px",
        margin_y="4px",
        width="90%",
        align_self="center", # Se centra en la pantalla
    )

    # Burbuja Normal (Inbound/Outbound)
    normal_content = rx.box(
        rx.vstack(
            rx.cond(
                is_audio & (media_id_str != ""),
                rx.vstack(
                    rx.text("🎤 Mensaje de voz", size="1", color="#8e8e93"),
                    rx.button(
                        "📝 Transcribir con IA",
                        on_click=AppState.transcribe_audio(media_id_str),
                        size="1", variant="soft", color_scheme="blue",
                    ),
                    align_items="start", spacing="2",
                ),
                rx.text(body_str, size="2", color="white", white_space="pre-wrap", class_name="message-body"),
            ),
            rx.text(rx.cond(is_in, "Cliente · ", msg["agent"].to(str) + " · ") + msg["time"].to(str), size="1", color="#636366"),
            align_items=rx.cond(is_in, "start", "end"),
            spacing="1",
        ),
        class_name=rx.cond(is_in, "bubble-in", "bubble-out"),
    )

    return rx.cond(is_note, note_content, normal_content)

def quick_reply_btn(qr: rx.Var) -> rx.Component:
    shortcut = qr["shortcut"].to(str)
    title = qr["title"].to(str)
    message = qr["message"].to(str)
    return rx.button(
        rx.vstack(
            rx.text(shortcut, weight="bold", size="1", color="#0a84ff"),
            rx.text(title, size="1", color="#8e8e93"),
            spacing="0", align_items="start",
        ),
        on_click=AppState.send_quick_reply(message),
        variant="outline", border="1px solid #3a3a3c", background="#1c1c1e",
        border_radius="8px", padding="8px 12px", flex_shrink="0",
    )

# ── Selector de Emojis ───────────────────────────────────────────

def emoji_selector() -> rx.Component:
    return rx.cond(
        AppState.show_emoji_picker,
        rx.box(
            rx.scroll_area(
                rx.grid(
                    rx.foreach(
                        AppState.emoji_list.to(list[str]),
                        lambda e: rx.button(
                            e, on_click=AppState.add_emoji(e),
                            variant="ghost", size="1", font_size="20px",
                            padding="4px",
                        )
                    ),
                    columns="8", spacing="1", padding="8px",
                ),
                height="200px",
            ),
            background="#1c1c1e",
            border="1px solid #3a3a3c",
            border_radius="12px",
            position="absolute",
            bottom="100px",
            left="12px",
            z_index="1000",
            width="280px",
            box_shadow="0 8px 24px rgba(0,0,0,0.5)",
        )
    )

# ─────────────────────────────────────────────────────────────────────────────
# Paneles
# ─────────────────────────────────────────────────────────────────────────────

def filter_btn(label: str, value: str, current_value: rx.Var, on_click) -> rx.Component:
    is_active = current_value == value
    return rx.button(
        label,
        on_click=on_click,
        size="1",
        variant=rx.cond(is_active, "solid", "surface"),
        color_scheme=rx.cond(is_active, "blue", "gray"),
        border=rx.cond(is_active, "none", "1px solid #2c2c2e"),
        flex="1",
        font_size="10px",
        height="26px",
        padding="2px 4px",
    )

def contacts_panel() -> rx.Component:
    hidden_class = rx.cond(AppState.mobile_view == "chat", "contacts-panel hidden-mobile", "contacts-panel")
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("📥 Conversaciones", weight="bold", color="white", size="3"),
                rx.spacer(),
                padding="14px 12px 8px", width="100%",
            ),
            # Filtros dinámicos al estilo Respond.io
            rx.vstack(
                rx.hstack(
                    filter_btn("Todos", "all", AppState.filter_assignment, AppState.set_filter_assignment("all")),
                    filter_btn("Míos", "mine", AppState.filter_assignment, AppState.set_filter_assignment("mine")),
                    filter_btn("Sin Asignar", "unassigned", AppState.filter_assignment, AppState.set_filter_assignment("unassigned")),
                    width="100%", spacing="1", padding_x="8px"
                ),
                rx.hstack(
                    filter_btn("Abiertos", "open", AppState.filter_status, AppState.set_filter_status("open")),
                    filter_btn("Pospuestos", "snoozed", AppState.filter_status, AppState.set_filter_status("snoozed")),
                    filter_btn("Cerrados", "closed", AppState.filter_status, AppState.set_filter_status("closed")),
                    width="100%", spacing="1", padding_x="8px", padding_bottom="8px"
                ),
                width="100%", spacing="1"
            ),
            rx.divider(color="#2c2c2e"),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(AppState.filtered_contacts.to(list[dict]), contact_item),
                    spacing="1", padding="8px",
                ),
                flex="1", width="100%",
            ),
            background="#111", border_right="1px solid #2c2c2e", spacing="0",
            height="100%",
        ),
        class_name=hidden_class,
        height="100%",
    )

def _active_chat() -> rx.Component:
    return rx.vstack(
        # Header
        rx.hstack(
            rx.button("← Volver", on_click=AppState.go_back, size="1", variant="ghost", color="#0a84ff", class_name="back-btn"),
            rx.vstack(
                rx.hstack(
                    rx.text(AppState.selected_contact_name, weight="bold", color="white", size="3", line_clamp=1),
                    rx.cond(
                        AppState.selected_contact.startswith("web_"),
                        rx.badge("🌐 Webchat", color_scheme="blue", size="1"),
                        rx.badge("📱 WhatsApp", color_scheme="green", size="1")
                    ),
                    spacing="2", align_items="center"
                ),
                rx.cond(
                    AppState.selected_contact.startswith("web_"),
                    rx.text("ID: " + AppState.selected_contact, size="1", color="#8e8e93"),
                    rx.text("+" + AppState.selected_contact, size="1", color="#8e8e93")
                ),
                spacing="0",
                max_width="220px"
            ),
            rx.spacer(),
            # Asignación de Agentes
            rx.hstack(
                rx.text("👤 Agente:", size="1", color="#8e8e93"),
                rx.select(
                    AppState.agent_options.to(list[str]),
                    value=AppState.assigned_agent,
                    on_change=AppState.assign_to_agent,
                    background="#1c1c1e", color="white", border="1px solid #3a3a3c", size="1"
                ),
                rx.cond(
                    AppState.assigned_agent == "",
                    rx.button("Asignarme", on_click=AppState.assign_to_me, size="1", color_scheme="blue", variant="soft")
                ),
                align_items="center", spacing="1"
            ),
            # Ciclo de Vida (CRM)
            rx.hstack(
                rx.text("📈 CRM:", size="1", color="#8e8e93"),
                rx.select(
                    ["New Customer", "Lead", "Customer", "Paid"],
                    value=AppState.contact_lifecycle_stage,
                    on_change=AppState.set_contact_lifecycle_stage,
                    background="#1c1c1e", color="white", border="1px solid #3a3a3c", size="1"
                ),
                align_items="center", spacing="1"
            ),
            # Estado de Conversación
            rx.select(
                ["pending", "active", "snoozed", "resolved"],
                value=AppState.conv_status,
                on_change=AppState.set_conv_status,
                background="#1c1c1e", color="white", border="1px solid #3a3a3c", size="1"
            ),
            padding="12px 16px", border_bottom="1px solid #2c2c2e", background="#111", width="100%", align_items="center", spacing="3"
        ),

        # Mensajes
        rx.scroll_area(
            rx.vstack(rx.foreach(AppState.messages.to(list[dict]), message_bubble), spacing="2", align_items="stretch", padding_bottom="8px"),
            class_name="messages-scroll", flex="1", width="100%",
        ),

        # Respuestas rápidas
        rx.cond(AppState.quick_replies.length() > 0, rx.box(rx.hstack(rx.foreach(AppState.quick_replies.to(list[dict]), quick_reply_btn), spacing="2", padding="8px 12px"), class_name="quick-replies-bar", width="100%", border_top="1px solid #2c2c2e", background="#000")),

        # IA Tools
        rx.cond(AppState.ai_result != "", rx.hstack(rx.callout(AppState.ai_result, color="blue", variant="soft", size="1", flex="1"), rx.vstack(rx.button("✅ Usar", size="1", on_click=AppState.use_ai_result, color_scheme="blue"), rx.button("✕", size="1", on_click=AppState.clear_ai_result, variant="ghost"), spacing="1"), padding="8px 12px", width="100%")),
        rx.hstack(
            rx.button("🌐 Traducir", on_click=AppState.translate_last, size="1", variant="ghost", color="#0a84ff", loading=AppState.loading_ai),
            rx.button("✨ Sugerir", on_click=AppState.suggest_reply, size="1", variant="ghost", color="#30d158", loading=AppState.loading_ai),
            rx.spacer(),
            # Upload invisible pero disparado por el clip
            rx.upload(
                rx.button("📎", variant="ghost", font_size="20px", color="#8e8e93"),
                id="upload_files",
                multiple=True,
                accept={
                    "image/*": [".jpg", ".jpeg", ".png"],
                    "application/pdf": [".pdf"],
                },
                on_drop=AppState.handle_upload(rx.upload_files(upload_id="upload_files")),
                border="none",
                padding="0",
            ),
            padding="4px 12px", spacing="2", background="#000", width="100%",
        ),

        # Input Row
        rx.box(
            emoji_selector(),
            template_selector_modal(),
            
            # Condicionar por ventana de 24 horas y modo (las notas no están bloqueadas)
            rx.cond(
                AppState.is_24h_window_closed & (AppState.chat_mode == "message") & (~AppState.selected_contact.startswith("web_")),
                # Banner de Ventana de 24 horas cerrada
                rx.center(
                    rx.vstack(
                        rx.text("⚠️ Ventana de 24 horas cerrada", weight="bold", color="#ff453a", size="3"),
                        rx.text("Meta requiere el uso de plantillas pre-aprobadas para reabrir el chat con este cliente.", color="#8e8e93", size="2", text_align="center"),
                        rx.button("📨 Seleccionar y Enviar Plantilla", on_click=AppState.toggle_template_modal, color_scheme="green", size="2", margin_top="4px"),
                        spacing="2",
                        align_items="center",
                        padding="24px 16px",
                        width="100%",
                    ),
                    background="#111",
                    border_top="1px solid #ff453a",
                    width="100%",
                ),
                # Caja de Entrada normal de Mensaje / Nota
                rx.vstack(
                    # Selector de modo de chat (Mensaje vs Nota Interna)
                    rx.hstack(
                        rx.button(
                            "💬 Mensaje",
                            on_click=lambda: AppState.set_chat_mode("message"),
                            size="1",
                            variant=rx.cond(AppState.chat_mode == "message", "solid", "ghost"),
                            color_scheme=rx.cond(AppState.chat_mode == "message", "blue", "gray"),
                            font_size="12px",
                            height="28px",
                        ),
                        rx.button(
                            "📝 Nota Interna",
                            on_click=lambda: AppState.set_chat_mode("note"),
                            size="1",
                            variant=rx.cond(AppState.chat_mode == "note", "solid", "ghost"),
                            color_scheme=rx.cond(AppState.chat_mode == "note", "yellow", "gray"),
                            font_size="12px",
                            height="28px",
                        ),
                        spacing="2",
                        padding_x="12px",
                        padding_top="6px",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "😊", on_click=AppState.toggle_emoji_picker,
                            variant="ghost", font_size="24px", height="60px",
                        ),
                        rx.text_area(
                            placeholder=rx.cond(
                                AppState.chat_mode == "note",
                                "Escribe una nota interna para tu equipo... (No se envía al cliente)",
                                "Escribe tu respuesta... (o pega una imagen)"
                            ),
                            value=AppState.new_message,
                            on_change=AppState.set_new_message,
                            background="#1c1c1e",
                            border=rx.cond(
                                AppState.chat_mode == "note",
                                "1px solid #FFD60A",
                                "1px solid #3a3a3c"
                            ),
                            color="white",
                            _placeholder={"color": "#636366"}, resize="none", rows="2", flex="1", font_size="16px",
                        ),
                        rx.button(
                            rx.text("→", size="5"),
                            on_click=AppState.send_message,
                            background=rx.cond(
                                AppState.chat_mode == "note",
                                "#FFD60A",
                                "#0a84ff"
                            ),
                            color=rx.cond(
                                AppState.chat_mode == "note",
                                "black",
                                "white"
                            ),
                            border_radius="12px", height="60px", width="52px",
                        ),
                        padding="6px 12px 10px", width="100%", align_items="end",
                    ),
                    width="100%",
                    spacing="0",
                ),
            ),
            width="100%", position="relative", class_name="input-row",
        ),

        background="#000", width="100%", height="100dvh", spacing="0", overflow="hidden",
    )

def order_draft_item(item: dict) -> rx.Component:
    return rx.hstack(
        rx.text(item["product"], weight="bold", size="1", color="white", flex="1"),
        rx.input(
            value=item["quantity"].to_string(),
            on_change=lambda val: AppState.update_order_item_qty(item["product"], val),
            width="45px", height="24px", background="#1c1c1e", color="white", border="1px solid #3a3a3c", size="1"
        ),
        rx.text("x", size="1", color="#8e8e93"),
        rx.input(
            value=item["price"].to_string(),
            on_change=lambda val: AppState.update_order_item_price(item["product"], val),
            width="65px", height="24px", background="#1c1c1e", color="white", border="1px solid #3a3a3c", size="1"
        ),
        rx.button("🗑️", on_click=AppState.remove_order_item(item["product"]), size="1", variant="ghost", color="#ff453a"),
        align_items="center", spacing="1", width="100%"
    )


def orders_sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("📦 Pedidos", value="draft"),
                    rx.tabs.trigger("🛍️ Catálogo", value="catalog"),
                    width="100%",
                ),
                
                # Tab 1: Pedidos / Borrador
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Borrador del Pedido", size="2", color="white", margin_top="8px"),
                        rx.cond(
                            AppState.order_items.length() == 0,
                            rx.text("El borrador está vacío. Añade productos desde el catálogo o agrega uno especial abajo.", size="1", color="#636366"),
                            rx.vstack(
                                rx.foreach(
                                    AppState.order_items.to(list[dict]),
                                    order_draft_item
                                ),
                                width="100%", spacing="2"
                            )
                        ),
                        rx.divider(color="#2c2c2e"),
                        
                        # Agregar producto especial / personalizado
                        rx.heading("Agregar Item Especial", size="1", color="#8e8e93"),
                        rx.hstack(
                            rx.input(
                                placeholder="Nombre (ej: Envoltura)",
                                value=AppState.special_item_name,
                                on_change=AppState.set_special_item_name,
                                background="#1c1c1e", border="1px solid #3a3a3c", color="white", size="1", flex="1", height="28px"
                            ),
                            rx.input(
                                placeholder="Precio",
                                value=AppState.special_item_price,
                                on_change=AppState.set_special_item_price,
                                background="#1c1c1e", border="1px solid #3a3a3c", color="white", size="1", width="60px", height="28px"
                            ),
                            rx.button("➕", on_click=AppState.add_special_item_to_order_draft, size="1", color_scheme="blue", height="28px"),
                            width="100%", spacing="1", align_items="center"
                        ),
                        rx.divider(color="#2c2c2e"),
                        
                        # Datos finales
                        rx.vstack(
                            rx.text("Dirección de Envío", size="1", color="#8e8e93"),
                            rx.text_area(
                                placeholder="Dirección completa del cliente",
                                value=AppState.order_address,
                                on_change=AppState.set_order_address,
                                background="#1c1c1e", border="1px solid #3a3a3c", color="white", resize="none", rows="2", font_size="12px", width="100%"
                            ),
                            spacing="1", width="100%"
                        ),
                        
                        rx.hstack(
                            rx.text("Total:", weight="bold", size="2", color="white"),
                            rx.spacer(),
                            rx.text(AppState.order_total_amount_str, weight="bold", size="3", color="#30d158"),
                            width="100%"
                        ),
                        
                        rx.grid(
                            rx.button("💾 Guardar", on_click=AppState.create_order, color_scheme="green", size="1"),
                            rx.button("✨ IA Rellenar", on_click=AppState.auto_fill_order_with_ai, color_scheme="blue", size="1", loading=AppState.loading_ai),
                            rx.button("🗑️ Vaciar", on_click=AppState.clear_order_draft, variant="soft", color_scheme="red", size="1"),
                            columns="3", spacing="2", width="100%"
                        ),
                        rx.cond(AppState.order_msg != "", rx.text(AppState.order_msg, size="1", color="#30d158")),
                        spacing="3", width="100%", align_items="stretch"
                    ),
                    value="draft"
                ),
                
                # Tab 2: Catálogo de temporada
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Productos de Temporada", size="2", color="white", margin_top="8px"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    AppState.products.to(list[dict]),
                                    lambda p: rx.box(
                                        rx.hstack(
                                            rx.cond(
                                                p["image_url"] != "",
                                                rx.image(src=p["image_url"], width="30px", height="30px", border_radius="4px", object_fit="cover"),
                                                rx.center(rx.text("🛍️", size="1"), width="30px", height="30px", background="#2c2c2e", border_radius="4px")
                                            ),
                                            rx.vstack(
                                                rx.text(p["name"], weight="bold", size="1", color="white"),
                                                rx.text("$", p["price"].to_string(), size="1", color="#30d158"),
                                                spacing="0", align_items="start"
                                            ),
                                            rx.spacer(),
                                            rx.button("➕", on_click=AppState.add_product_to_order_draft(p), size="1", variant="soft", color_scheme="blue"),
                                            rx.button("📄 Info", on_click=AppState.send_product_details(p), size="1", variant="ghost", color_scheme="gray"),
                                            align_items="center", spacing="1", width="100%"
                                        ),
                                        rx.text(p["description"].to(str)[:60] + "...", size="1", color="#8e8e93", padding_top="4px"),
                                        padding="8px", background="#1c1c1e", border_radius="8px", border="1px solid #2c2c2e", margin_bottom="8px", width="100%"
                                    )
                                ),
                                spacing="1", width="100%"
                            ),
                            height="calc(100vh - 120px)"
                        ),
                        width="100%", spacing="2"
                    ),
                    value="catalog"
                ),
                default_value="draft",
                width="100%"
            ),
            spacing="3", padding="12px", width="300px", height="100dvh", background="#111", border_left="1px solid #2c2c2e"
        ),
        class_name="hidden-mobile"
    )


def chat_page() -> rx.Component:
    return rx.vstack(
        navbar("/chat"),
        rx.hstack(
            contacts_panel(), 
            rx.box(rx.cond(AppState.selected_contact != "", _active_chat(), rx.center(rx.vstack(rx.text("💬", size="9"), rx.heading("Nyme", size="7", color="white"), rx.text("Selecciona una conversación", color="#8e8e93")), height="100%", background="#000")), flex="1", height="100%"), 
            rx.cond(AppState.selected_contact != "", orders_sidebar()),
            spacing="0", width="100%", height="100%", overflow="hidden"
        ),
        rx.audio(url="https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3", playing=AppState.play_sound_tick > 0, on_ended=AppState.reset_sound_tick, display="none"),
        background="#000",
        spacing="0",
        width="100%",
        height="100dvh",
        overflow="hidden",
        on_mount=[AppState.require_auth, AppState.start_polling],
    )
