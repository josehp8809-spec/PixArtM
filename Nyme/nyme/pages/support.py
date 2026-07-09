"""SaaS support technical chat page (Dual Layout: Admin Ticket Manager vs Client support interface)."""
import reflex as rx
from nyme.state import AppState
from nyme.pages.navbar import navbar


def support_room_row(room: dict) -> rx.Component:
    is_active = (AppState.active_support_room_id == room["id"])
    bg = rx.cond(is_active, "rgba(15, 163, 177, 0.15)", "transparent")
    border = rx.cond(is_active, "1px solid rgba(15, 163, 177, 0.3)", "1px solid rgba(255, 255, 255, 0.08)")
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("🏢", size="4"),
                rx.text(room["tenant_name"], weight="bold", color="white", size="3"),
                rx.spacer(),
                rx.text(room["last_time"], color="#8e8e93", size="1"),
                width="100%",
                align_items="center"
            ),
            rx.text(room["last_message"], color="#8e8e93", size="2", max_width="250px", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
            align_items="start",
            spacing="1"
        ),
        padding="14px 18px",
        background=bg,
        border=border,
        border_radius="12px",
        width="100%",
        cursor="pointer",
        on_click=lambda: AppState.select_support_room(room["id"], room["tenant_name"]),
        _hover={"background": "rgba(255, 255, 255, 0.04)"},
        transition="all 0.2s"
    )


def message_bubble(msg: dict, current_tenant_id: int) -> rx.Component:
    # Determine if message is sent by the current viewer
    is_sent_by_me = (msg["sender_tenant_id"] == current_tenant_id)
    
    bubble_bg = rx.cond(is_sent_by_me, "linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)", "rgba(28, 28, 30, 0.9)")
    align = rx.cond(is_sent_by_me, "end", "start")
    bubble_align = rx.cond(is_sent_by_me, "flex-end", "flex-start")
    text_color = "white"
    
    return rx.vstack(
        rx.box(
            rx.vstack(
                # Sender Label
                rx.hstack(
                    rx.text(f"@{msg['sender_username']}", size="1", color="rgba(255,255,255,0.6)", weight="bold"),
                    rx.spacer(),
                    rx.text(msg["created_at"], size="1", color="rgba(255,255,255,0.5)"),
                    width="100%",
                    spacing="3"
                ),
                rx.text(msg["message"], color=text_color, size="2", line_height="1.4", margin_top="4px"),
                align_items="start",
                spacing="0"
            ),
            padding="12px 16px",
            background=bubble_bg,
            border_radius="14px",
            max_width="450px",
            box_shadow="0 4px 10px rgba(0,0,0,0.2)"
        ),
        align_self=bubble_align,
        align_items=align,
        width="100%",
        spacing="1"
    )


def superadmin_support_view() -> rx.Component:
    return rx.hstack(
        # Left sidebar: tickets list
        rx.vstack(
            rx.heading("Salas de Soporte", size="4", color="white", margin_bottom="12px"),
            rx.divider(color="rgba(255, 255, 255, 0.08)"),
            rx.vstack(
                rx.foreach(
                    AppState.support_rooms_list,
                    support_room_row
                ),
                spacing="3",
                width="100%",
                overflow_y="auto",
                height="calc(100vh - 200px)"
            ),
            width="320px",
            border_right="1px solid rgba(15, 163, 177, 0.15)",
            padding="24px",
            spacing="4",
            height="100%",
            align_items="stretch"
        ),
        
        # Right pane: chat view
        rx.vstack(
            rx.cond(
                AppState.active_support_room_id > 0,
                # Chat active
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.text("🏢", size="5"),
                        rx.vstack(
                            rx.heading(AppState.active_support_tenant_name, size="4", color="white"),
                            rx.text("Canal de Soporte Técnico Directo", color="#0fa3b1", size="1"),
                            spacing="0",
                            align_items="start"
                        ),
                        width="100%",
                        padding="18px 24px",
                        border_bottom="1px solid rgba(255, 255, 255, 0.08)"
                    ),
                    
                    # Message list
                    rx.vstack(
                        rx.foreach(
                            AppState.support_messages,
                            lambda m: message_bubble(m, 1) # Superadmin tenant_id is 1
                        ),
                        spacing="3",
                        padding="24px",
                        overflow_y="auto",
                        flex="1",
                        width="100%"
                    ),
                    
                    # Footer input
                    rx.hstack(
                        rx.input(
                            placeholder="Escribe tu respuesta aquí...",
                            on_change=AppState.set_support_new_message,
                            value=AppState.support_new_message,
                            on_key_down=AppState.handle_support_key,
                            background="rgba(28, 28, 30, 0.8)",
                            border="1px solid rgba(255, 255, 255, 0.12)",
                            color="white",
                            _focus={"border": "1px solid #0fa3b1"},
                            flex="1",
                            height="44px"
                        ),
                        rx.button(
                            "Enviar",
                            on_click=AppState.send_support_message,
                            background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                            color="white",
                            weight="bold",
                            border_radius="10px",
                            height="44px",
                            padding="0 24px"
                        ),
                        width="100%",
                        padding="16px 24px",
                        border_top="1px solid rgba(255, 255, 255, 0.08)",
                        background="rgba(18, 18, 18, 0.6)",
                        align_items="center"
                    ),
                    width="100%",
                    height="100%",
                    spacing="0"
                ),
                # No active room
                rx.center(
                    rx.vstack(
                        rx.text("💬", size="9", color="#636366"),
                        rx.heading("Centro de Soporte Técnico", size="5", color="white", margin_top="16px"),
                        rx.text("Selecciona una empresa de la lista lateral para iniciar el chat.", color="#8e8e93", size="2"),
                        align_items="center"
                    ),
                    width="100%",
                    height="100%"
                )
            ),
            flex="1",
            height="100%",
            spacing="0"
        ),
        width="100%",
        height="calc(100vh - 70px)",
        spacing="0"
    )


def client_support_view() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Header
            rx.hstack(
                rx.text("🛠️", size="5"),
                rx.vstack(
                    rx.heading("Soporte Técnico Nyme", size="5", color="white"),
                    rx.text("Escríbenos cualquier duda o reporte y te responderemos a la brevedad.", color="#8e8e93", size="1"),
                    spacing="0",
                    align_items="start"
                ),
                width="100%",
                padding="18px 24px",
                border_bottom="1px solid rgba(255, 255, 255, 0.08)"
            ),
            
            # Message list
            rx.vstack(
                rx.foreach(
                    AppState.support_messages,
                    lambda m: message_bubble(m, AppState.tenant_id)
                ),
                spacing="3",
                padding="24px",
                overflow_y="auto",
                flex="1",
                width="100%"
            ),
            
            # Footer input
            rx.hstack(
                rx.input(
                    placeholder="Escribe tu duda o mensaje de soporte aquí...",
                    on_change=AppState.set_support_new_message,
                    value=AppState.support_new_message,
                    on_key_down=AppState.handle_support_key,
                    background="rgba(28, 28, 30, 0.8)",
                    border="1px solid rgba(255, 255, 255, 0.12)",
                    color="white",
                    _focus={"border": "1px solid #0fa3b1"},
                    flex="1",
                    height="44px"
                ),
                rx.button(
                    "Enviar",
                    on_click=AppState.send_support_message,
                    background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                    color="white",
                    weight="bold",
                    border_radius="10px",
                    height="44px",
                    padding="0 24px"
                ),
                width="100%",
                padding="16px 24px",
                border_top="1px solid rgba(255, 255, 255, 0.08)",
                background="rgba(18, 18, 18, 0.6)",
                align_items="center"
            ),
            width="100%",
            max_width="850px",
            height="calc(100vh - 140px)",
            border="1px solid rgba(15, 163, 177, 0.25)",
            border_radius="16px",
            background="rgba(18, 18, 18, 0.5)",
            backdrop_filter="blur(16px)",
            box_shadow="0 12px 30px rgba(0,0,0,0.5)",
            spacing="0",
            margin_top="30px"
        ),
        width="100%",
        height="calc(100vh - 70px)"
    )


def support_page() -> rx.Component:
    return rx.vstack(
        navbar("/support"),
        rx.cond(
            AppState.tenant_id == 1,
            superadmin_support_view(),
            client_support_view()
        ),
        background_color="#000000",
        min_height="100vh",
        spacing="0",
        width="100%",
        on_mount=[AppState.detect_timezone, AppState.load_support_chat]
    )
