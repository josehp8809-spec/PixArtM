"""Barra de navegación global premium para Nyme."""
import reflex as rx
from nyme.state import AppState

def navbar(active_page: str = "") -> rx.Component:
    # Helper para dar estilos a los links según estén activos o no
    def nav_link(label: str, icon: str, path: str) -> rx.Component:
        is_active = (active_page == path)
        color = rx.cond(is_active, "#30d158", "#8e8e93")
        bg = rx.cond(is_active, "rgba(48, 209, 88, 0.1)", "transparent")
        
        return rx.link(
            rx.hstack(
                rx.text(icon, size="3"),
                rx.text(label, weight="medium", size="2"),
                spacing="2",
                align_items="center",
                padding="8px 12px",
                border_radius="8px",
                background=bg,
                _hover={"background": "rgba(255,255,255,0.05)"},
                transition="all 0.2s ease",
            ),
            href=path,
            color=color,
            text_decoration="none",
        )

    # Rol del usuario reactivo
    is_admin = (AppState.role == "admin")
    is_admin_or_coord = (AppState.role == "admin") | (AppState.role == "coordinator")

    return rx.box(
        rx.hstack(
            # Logo + Nombre
            rx.link(
                rx.hstack(
                    rx.image(
                        src="https://img.icons8.com/fluency/48/whatsapp.png",
                        width="28px", height="28px",
                    ),
                    rx.heading("Nyme", size="5", color="white", weight="bold"),
                    spacing="2",
                    align_items="center",
                ),
                href="/chat",
                text_decoration="none",
            ),
            rx.spacer(),
            
            # Enlaces principales
            rx.hstack(
                nav_link("Chats", "💬", "/chat"),
                nav_link("Directorio", "👥", "/contacts"),
                nav_link("Equipo", "🏢", "/internal"),
                nav_link("Ventas", "🛍️", "/orders"),
                # Mostrar reportes solo a admin o coordinador
                rx.cond(
                    is_admin_or_coord,
                    nav_link("Reportes", "📊", "/reports"),
                ),
                # Mostrar configuraciones solo a admin
                rx.cond(
                    is_admin,
                    nav_link("Configuración", "⚙️", "/settings"),
                ),
                spacing="2",
                align_items="center",
            ),
            
            rx.spacer(),

            # Perfil usuario + Logout
            rx.hstack(
                rx.vstack(
                    rx.text(AppState.full_name, color="white", weight="bold", size="2"),
                    rx.text(AppState.role.to(str).capitalize(), color="#8e8e93", size="1"),
                    spacing="0",
                    align_items="end",
                ),
                rx.button(
                    "Salir", 
                    on_click=AppState.logout, 
                    color_scheme="red", 
                    size="1",
                    variant="soft",
                ),
                spacing="3",
                align_items="center",
            ),
            width="100%",
            align_items="center",
            padding="12px 24px",
        ),
        background="#111111",
        border_bottom="1px solid #2c2c2e",
        width="100%",
        z_index="999",
    )
