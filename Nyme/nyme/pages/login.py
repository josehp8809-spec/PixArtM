"""Login page."""
import reflex as rx
from nyme.state import AppState


def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Logo de Nyme (Branding Husky)
            rx.image(
                src="/logo.png",
                width="140px",
                height="auto",
                border_radius="20px",
                box_shadow="0 8px 30px rgba(15, 163, 177, 0.3)",
                margin_bottom="12px",
                _hover={"transform": "scale(1.05)", "transition": "transform 0.3s ease"}
            ),
            rx.heading("Nyme", size="8", color="white", weight="bold", letter_spacing="1px"),
            rx.text(
                "Plataforma de Comunicación Omnicanal",
                color="#0fa3b1",
                weight="medium",
                size="3",
                margin_bottom="6px"
            ),
            rx.text(
                "Conecta WhatsApp, Messenger e Instagram en un solo panel con agentes IA inteligentes.",
                color="#8e8e93",
                size="1",
                text_align="center",
                max_width="290px"
            ),
            rx.divider(color="rgba(255, 255, 255, 0.1)", margin="8px 0"),

            # Formulario Premium
            rx.vstack(
                rx.vstack(
                    rx.text("Usuario", size="1", color="#8e8e93", weight="bold"),
                    rx.input(
                        placeholder="Ingresa tu usuario",
                        on_change=AppState.set_login_username,
                        on_key_down=AppState.handle_login_key,
                        background="rgba(28, 28, 30, 0.8)",
                        border="1px solid rgba(255, 255, 255, 0.15)",
                        color="white",
                        _placeholder={"color": "#636366"},
                        width="100%",
                        height="40px",
                        _focus={"border": "1px solid #0fa3b1", "box_shadow": "0 0 10px rgba(15, 163, 177, 0.2)"}
                    ),
                    spacing="1", width="100%"
                ),
                rx.vstack(
                    rx.text("Contraseña", size="1", color="#8e8e93", weight="bold"),
                    rx.input(
                        placeholder="••••••••",
                        type="password",
                        on_change=AppState.set_login_password,
                        on_key_down=AppState.handle_login_key,
                        background="rgba(28, 28, 30, 0.8)",
                        border="1px solid rgba(255, 255, 255, 0.15)",
                        color="white",
                        _placeholder={"color": "#636366"},
                        width="100%",
                        height="40px",
                        _focus={"border": "1px solid #0fa3b1", "box_shadow": "0 0 10px rgba(15, 163, 177, 0.2)"}
                    ),
                    spacing="1", width="100%"
                ),
                rx.cond(
                    AppState.login_error != "",
                    rx.callout(
                        AppState.login_error,
                        color="red", variant="soft",
                        width="100%",
                    ),
                ),
                rx.button(
                    "Iniciar sesión",
                    on_click=AppState.login,
                    width="100%",
                    background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                    color="white",
                    _hover={"background": "linear-gradient(135deg, #0077b6 0%, #03045e 100%)", "box_shadow": "0 4px 15px rgba(15, 163, 177, 0.4)"},
                    border_radius="10px",
                    height="44px",
                    weight="bold",
                    transition="all 0.3s ease"
                ),
                width="100%",
                spacing="4",
                margin_top="10px"
            ),
            width=["92%", "400px", "360px"],   # responsivo: móvil / tablet / desktop
            padding="40px 32px",
            border="1px solid rgba(15, 163, 177, 0.25)",
            border_radius="20px",
            background="rgba(18, 18, 18, 0.8)",
            backdrop_filter="blur(16px)",
            box_shadow="0 20px 40px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
            spacing="4",
            align_items="center"
        ),
        height="100vh",
        background="radial-gradient(circle at center, #0a1128 0%, #000411 100%)",
    )
