"""Login page."""
import reflex as rx
from nyme.state import AppState


def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Logo + título
            rx.image(
                src="https://img.icons8.com/fluency/96/whatsapp.png",
                width="64px", height="64px",
            ),
            rx.heading("Nyme", size="9", color="white"),
            rx.text(
                "Plataforma de atención al cliente vía WhatsApp",
                color="#8e8e93", size="2",
            ),
            rx.divider(color="#2c2c2e"),

            # Formulario
            rx.vstack(
                rx.input(
                    placeholder="Usuario",
                    on_change=AppState.set_login_username,
                    on_key_down=lambda k: AppState.login() if k == "Enter" else None,
                    background="#1c1c1e",
                    border="1px solid #3a3a3c",
                    color="white",
                    _placeholder={"color": "#636366"},
                    width="100%",
                ),
                rx.input(
                    placeholder="Contraseña",
                    type="password",
                    on_change=AppState.set_login_password,
                    on_key_down=lambda k: AppState.login() if k == "Enter" else None,
                    background="#1c1c1e",
                    border="1px solid #3a3a3c",
                    color="white",
                    _placeholder={"color": "#636366"},
                    width="100%",
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
                    background="#0a84ff",
                    color="white",
                    _hover={"background": "#0060df"},
                    border_radius="10px",
                    height="42px",
                ),
                width="100%",
                spacing="3",
            ),
            width=["90%", "380px", "340px"],   # responsivo: móvil / tablet / desktop
            padding="32px",
            border="1px solid #2c2c2e",
            border_radius="16px",
            background="#111111",
            spacing="4",
        ),
        height="100vh",
        background="#000000",
    )
