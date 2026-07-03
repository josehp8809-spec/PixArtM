"""Chat page — Responsivo con Selector de Emojis y Sonido."""
import reflex as rx
from nyme.state import AppState

STATUS_ICONS  = {"pending": "⏳", "active": "🟡", "resolved": "✅"}
STATUS_LABELS = {"pending": "Pendiente", "active": "En curso", "resolved": "Resuelto"}

# ─────────────────────────────────────────────────────────────────────────────
# Componentes
# ─────────────────────────────────────────────────────────────────────────────

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
    
    is_selected = (
        (AppState.selected_contact == wa_id)
        & (AppState.selected_line_id == line_id)
    )
    return rx.box(
        rx.hstack(
            avatar_box(wa_id),
            rx.vstack(
                rx.text("+", wa_id, weight="bold", size="2", color="white"),
                rx.text(
                    rx.match(
                        status,
                        ("pending", "⏳ Pendiente"),
                        ("active", "🟡 En curso"),
                        ("resolved", "✅ Resuelto"),
                        "⏳ Pendiente"
                    ),
                    size="1", color="#8e8e93",
                ),
                align_items="start", spacing="0",
            ),
            rx.spacer(),
            rx.cond(unread > 0, rx.badge(unread.to_string(), color_scheme="red", radius="full")),
            width="100%",
        ),
        on_click=AppState.select_contact(wa_id, line_id),
        background=rx.cond(is_selected, "#1c1c1e", "transparent"),
        border_radius="10px", padding="12px", cursor="pointer", width="100%",
        border=rx.cond(is_selected, "1px solid #3a3a3c", "1px solid transparent"),
        _hover={"background": "#1c1c1e"},
    )

def message_bubble(msg: rx.Var) -> rx.Component:
    is_in = msg["type"] == "INBOUND"
    body_str = msg["body"].to(str)
    media_id_str = msg["media_id"].to(str)
    is_audio = body_str.contains("[🎤 Audio]") | (media_id_str != "")
    
    return rx.box(
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

def contacts_panel() -> rx.Component:
    hidden_class = rx.cond(AppState.mobile_view == "chat", "contacts-panel hidden-mobile", "contacts-panel")
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("📥 Conversaciones", weight="bold", color="white", size="3"),
                rx.spacer(),
                padding="14px 12px 8px", width="100%",
            ),
            rx.divider(color="#2c2c2e"),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(AppState.contacts.to(list[dict]), contact_item),
                    spacing="1", padding="8px",
                ),
                flex="1", width="100%",
            ),
            rx.divider(color="#2c2c2e"),
            rx.hstack(
                rx.link("👥 Clientes",  href="/contacts", color="#8e8e93", size="1"),
                rx.link("🏢 Equipo",    href="/internal", color="#8e8e93", size="1"),
                rx.spacer(),
                rx.button("Salir", on_click=AppState.logout, size="1", variant="ghost", color="#ff453a"),
                padding="8px 12px", width="100%",
            ),
            height="100dvh", width="100%", background="#111", border_right="1px solid #2c2c2e", spacing="0",
        ),
        class_name=hidden_class,
    )

def _active_chat() -> rx.Component:
    return rx.vstack(
        # Header
        rx.hstack(
            rx.button("← Volver", on_click=AppState.go_back, size="1", variant="ghost", color="#0a84ff", class_name="back-btn"),
            rx.vstack(
                rx.text(f"+{AppState.selected_contact}", weight="bold", color="white", size="3"),
                rx.text(AppState.conv_status, size="1", color="#8e8e93"),
                spacing="0",
            ),
            rx.spacer(),
            rx.select(["pending", "active", "resolved"], value=AppState.conv_status, on_change=AppState.set_conv_status, background="#1c1c1e", color="white", border="1px solid #3a3a3c", size="1"),
            padding="12px 16px", border_bottom="1px solid #2c2c2e", background="#111", width="100%", align_items="center",
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
            rx.hstack(
                rx.button(
                    "😊", on_click=AppState.toggle_emoji_picker,
                    variant="ghost", font_size="24px", height="60px",
                ),
                rx.text_area(
                    placeholder="Escribe tu respuesta... (o pega una imagen)",
                    value=AppState.new_message,
                    on_change=AppState.set_new_message,
                    background="#1c1c1e", border="1px solid #3a3a3c", color="white",
                    _placeholder={"color": "#636366"}, resize="none", rows="2", flex="1", font_size="16px",
                ),
                rx.button(
                    rx.text("→", size="5"),
                    on_click=AppState.send_message,
                    background="#0a84ff", color="white", border_radius="12px", height="60px", width="52px",
                ),
                padding="10px 12px", border_top="1px solid #2c2c2e", background="#000", width="100%", align_items="end",
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
                            rx.text(f"${AppState.order_total_amount:.2f}", weight="bold", size="3", color="#30d158"),
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
    return rx.box(
        rx.hstack(
            contacts_panel(), 
            rx.box(rx.cond(AppState.selected_contact != "", _active_chat(), rx.center(rx.vstack(rx.text("💬", size="9"), rx.heading("Nyme", size="7", color="white"), rx.text("Selecciona una conversación", color="#8e8e93")), height="100dvh", background="#000")), flex="1"), 
            rx.cond(AppState.selected_contact != "", orders_sidebar()),
            spacing="0", width="100%", height="100dvh", overflow="hidden"
        ),
        rx.audio(url="https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3", playing=AppState.play_sound_tick > 0, on_ended=AppState.reset_sound_tick, display="none"),
        background="#000", on_mount=[AppState.require_auth, AppState.start_polling],
    )
