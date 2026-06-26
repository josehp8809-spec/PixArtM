"""Chat page — Responsivo con Selector de Emojis y Sonido."""
import reflex as rx
from nyme.state import AppState

STATUS_ICONS  = {"pending": "⏳", "active": "🟡", "resolved": "✅"}
STATUS_LABELS = {"pending": "Pendiente", "active": "En curso", "resolved": "Resuelto"}

# ─────────────────────────────────────────────────────────────────────────────
# Componentes
# ─────────────────────────────────────────────────────────────────────────────

def avatar_box(name: str, size="40px") -> rx.Component:
    initial = name[0].upper() if name else "?"
    colors = ["#0a84ff", "#30d158", "#ff9f0a", "#5e5ce6", "#ff375f", "#64d2ff"]
    idx = ord(initial) % len(colors)
    return rx.center(
        rx.text(initial, weight="bold", color="white", size="2"),
        width=size, height=size, background=colors[idx], border_radius="50%", flex_shrink="0",
    )

def contact_item(contact: dict) -> rx.Component:
    unread = contact["unread"]
    status = contact["status"]
    is_selected = (
        (AppState.selected_contact == contact["wa_id"])
        & (AppState.selected_line_id == contact["line_id"])
    )
    return rx.box(
        rx.hstack(
            avatar_box(contact["wa_id"]),
            rx.vstack(
                rx.text(f"+{contact['wa_id']}", weight="bold", size="2", color="white"),
                rx.text(
                    STATUS_ICONS.get(status, "⏳") + " " + STATUS_LABELS.get(status, status),
                    size="1", color="#8e8e93",
                ),
                align_items="start", spacing="0",
            ),
            rx.spacer(),
            rx.cond(unread > 0, rx.badge(unread.to_string(), color_scheme="red", radius="full")),
            width="100%",
        ),
        on_click=AppState.select_contact(contact["wa_id"], contact["line_id"]),
        background=rx.cond(is_selected, "#1c1c1e", "transparent"),
        border_radius="10px", padding="12px", cursor="pointer", width="100%",
        border=rx.cond(is_selected, "1px solid #3a3a3c", "1px solid transparent"),
        _hover={"background": "#1c1c1e"},
    )

def message_bubble(msg: dict) -> rx.Component:
    is_in = msg["type"] == "INBOUND"
    is_audio = "[🎤 Audio]" in msg["body"] or msg.get("media_id")
    
    return rx.box(
        rx.vstack(
            rx.cond(
                is_audio & (msg.get("media_id") != None),
                rx.vstack(
                    rx.text("🎤 Mensaje de voz", size="1", color="#8e8e93"),
                    rx.button(
                        "📝 Transcribir con IA",
                        on_click=AppState.transcribe_audio(msg["media_id"]),
                        size="1", variant="soft", color_scheme="blue",
                    ),
                    align_items="start", spacing="2",
                ),
                rx.text(msg["body"], size="2", color="white", white_space="pre-wrap", class_name="message-body"),
            ),
            rx.text(rx.cond(is_in, "Cliente · ", f"@{msg['agent']} · ") + msg["time"], size="1", color="#636366"),
            align_items=rx.cond(is_in, "start", "end"),
            spacing="1",
        ),
        class_name=rx.cond(is_in, "bubble-in", "bubble-out"),
    )

def quick_reply_btn(qr: dict) -> rx.Component:
    return rx.button(
        rx.vstack(
            rx.text(qr["shortcut"], weight="bold", size="1", color="#0a84ff"),
            rx.text(qr["title"], size="1", color="#8e8e93"),
            spacing="0", align_items="start",
        ),
        on_click=AppState.send_quick_reply(qr["message"]),
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
                        AppState.emoji_list,
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
                    rx.foreach(AppState.contacts, contact_item),
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
            rx.vstack(rx.foreach(AppState.messages, message_bubble), spacing="2", align_items="stretch", padding_bottom="8px"),
            class_name="messages-scroll", flex="1", width="100%",
        ),

        # Respuestas rápidas
        rx.cond(AppState.quick_replies.length() > 0, rx.box(rx.hstack(rx.foreach(AppState.quick_replies, quick_reply_btn), spacing="2", padding="8px 12px"), class_name="quick-replies-bar", width="100%", border_top="1px solid #2c2c2e", background="#000")),

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

def chat_page() -> rx.Component:
    return rx.box(
        rx.hstack(contacts_panel(), rx.box(_active_chat() if AppState.selected_contact != "" else rx.center(rx.vstack(rx.text("💬", size="9"), rx.heading("Nyme", size="7", color="white"), rx.text("Selecciona una conversación", color="#8e8e93")), height="100dvh", background="#000"), flex="1"), spacing="0", width="100%", height="100dvh", overflow="hidden"),
        rx.audio(url="https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3", playing=AppState.play_sound_tick > 0, on_ended=AppState.set_play_sound_tick(0), display="none"),
        background="#000", on_mount=[AppState.require_auth, AppState.start_polling],
    )
