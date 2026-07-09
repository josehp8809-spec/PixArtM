"""Barra de navegación global premium para Nyme (Branding Husky/Teal)."""
import reflex as rx
from nyme.state import AppState

def navbar(active_page: str = "") -> rx.Component:
    # Helper para dar estilos a los links según estén activos o no (Teal Premium)
    def nav_link(label: str, icon: str, path: str) -> rx.Component:
        is_active = (active_page == path)
        color = rx.cond(is_active, "#0fa3b1", "#8e8e93")
        bg = rx.cond(is_active, "rgba(15, 163, 177, 0.12)", "transparent")
        border = rx.cond(is_active, "1px solid rgba(15, 163, 177, 0.25)", "1px solid transparent")
        
        return rx.link(
            rx.hstack(
                rx.text(icon, size="3"),
                rx.text(label, weight="medium", size="2"),
                spacing="2",
                align_items="center",
                padding="8px 14px",
                border_radius="10px",
                background=bg,
                border=border,
                _hover={"background": "rgba(15, 163, 177, 0.06)", "transform": "translateY(-1px)"},
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
            # Logo de Nyme + Nombre
            rx.link(
                rx.hstack(
                    rx.image(
                        src="/logo.png",
                        width="34px",
                        height="auto",
                        border_radius="6px",
                        box_shadow="0 0 10px rgba(15, 163, 177, 0.4)",
                    ),
                    rx.heading("Nyme", size="5", color="white", weight="bold", letter_spacing="0.5px"),
                    spacing="2",
                    align_items="center",
                    _hover={"opacity": "0.9"},
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
                nav_link("Soporte", "🛠️", "/support"),
                rx.cond(
                    is_admin_or_coord,
                    nav_link("Reportes", "📊", "/reports"),
                ),
                rx.cond(
                    is_admin,
                    nav_link("Configuración", "⚙️", "/settings"),
                ),
                spacing="2",
                align_items="center",
            ),
            
            rx.spacer(),

            # Información del perfil del usuario
            rx.hstack(
                rx.vstack(
                    rx.text(AppState.full_name, color="white", weight="bold", size="2"),
                    rx.text(AppState.role.to(str).capitalize() + " | " + AppState.tenant_name, color="#0fa3b1", size="1", weight="medium"),
                    spacing="0",
                    align_items="end",
                ),
                rx.button(
                    "Salir", 
                    on_click=AppState.logout, 
                    color_scheme="red", 
                    size="1",
                    variant="soft",
                    _hover={"transform": "scale(1.02)"},
                    transition="all 0.2s ease",
                ),
                spacing="3",
                align_items="center",
            ),
            width="100%",
            align_items="center",
            padding="12px 24px",
        ),
        background="rgba(18, 18, 18, 0.8)",
        backdrop_filter="blur(12px)",
        border_bottom="1px solid rgba(15, 163, 177, 0.15)",
        box_shadow="0 4px 20px rgba(0, 0, 0, 0.3)",
        width="100%",
        z_index="999",
    )
