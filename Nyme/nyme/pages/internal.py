"""Página de Chat Interno para el equipo."""
import reflex as rx
from nyme.state import AppState

def internal_msg_bubble(m: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(m["msg"], size="2", color="white"),
            rx.text(f"@{m['user']} · {m['time']}", size="1", color="#636366"),
            spacing="1", align_items="start",
        ),
        background="#1c1c1e",
        border_radius="8px",
        padding="10px 14px",
        margin_bottom="8px",
        width="fit-content",
    )

def internal_chat_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("💬 Chat Interno de Equipo", size="7", color="white", padding="24px 32px 8px"),
            rx.text("Espacio general para anuncios y coordinación entre agentes.", color="#8e8e93", padding="0 32px 16px"),
            
            rx.divider(color="#2c2c2e"),
            
            # Muro de mensajes
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(AppState.internal_messages.to(list[dict]), internal_msg_bubble),
                    width="100%",
                    spacing="0",
                    padding="24px 32px",
                ),
                height="calc(100vh - 280px)",
                width="100%",
            ),

            # Input
            rx.hstack(
                rx.input(
                    placeholder="Escribe un anuncio para el equipo...",
                    value=AppState.internal_chat_msg,
                    on_change=AppState.set_internal_chat_msg,
                    on_key_down=AppState.handle_internal_key,
                    background="#1c1c1e",
                    border="1px solid #3a3a3c",
                    color="white",
                    flex="1",
                ),
                rx.button(
                    "Publicar",
                    on_click=AppState.send_internal_message,
                    background="#0a84ff",
                    color="white",
                ),
                padding="24px 32px",
                width="100%",
                background="#111",
                border_top="1px solid #2c2c2e",
            ),
            spacing="0",
            width="100%",
        ),
        background="#000",
        min_height="100vh",
        on_mount=AppState.require_auth,
    )
