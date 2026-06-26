"""Página de Directorio — Con Buscador, Avatares y Exportación."""
import reflex as rx
from nyme.state import AppState

# ── Helper para Avatares ──────────────────────────────────────────

def avatar_box(name: str, size="40px") -> rx.Component:
    initial = name[0].upper() if name else "?"
    # Colores consistentes basados en la inicial
    colors = ["#0a84ff", "#30d158", "#ff9f0a", "#5e5ce6", "#ff375f", "#64d2ff"]
    idx = ord(initial) % len(colors)
    return rx.center(
        rx.text(initial, weight="bold", color="white", size="2"),
        width=size, height=size,
        background=colors[idx],
        border_radius="50%",
        flex_shrink="0",
    )

# ── Componente Cliente ───────────────────────────────────────────

def contact_card(c: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            avatar_box(c["name"] or c["wa_id"]),
            rx.vstack(
                rx.text(c["name"] or "Sin nombre", weight="bold", size="3", color="white"),
                rx.text(f"📱 +{c['wa_id']}", size="2", color="#0a84ff"),
                align_items="start", spacing="0",
            ),
            rx.spacer(),
            rx.button(
                "💬 Chat",
                on_click=AppState.start_chat_with(c["wa_id"]),
                size="2", variant="surface",
            ),
            padding="16px", align_items="center", width="100%",
        ),
        rx.divider(color="#2c2c2e"),
        rx.cond(
            c["notes"] != "",
            rx.text(c["notes"], size="1", color="#636366", padding="8px 16px"),
        ),
        background="#111", border="1px solid #2c2c2e", border_radius="12px",
        width="100%", margin_bottom="12px",
    )

# ── Componente Miembro del Equipo ─────────────────────────────────

def team_card(u: dict) -> rx.Component:
    is_me = (u["username"] == AppState.username)
    return rx.box(
        rx.hstack(
            rx.box(
                avatar_box(u["full_name"]),
                rx.box( # Indicador de conexión superpuesto
                    width="12px", height="12px",
                    background=rx.cond(u["is_online"], "#30d158", "#3a3a3c"),
                    border="2px solid #111", border_radius="50%",
                    position="absolute", bottom="0", right="0",
                ),
                position="relative",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(u["full_name"], weight="bold", size="3", color="white"),
                    rx.badge(u["role"], color_scheme="blue", size="1"),
                    spacing="2", align_items="center",
                ),
                rx.text(
                    rx.cond(u["is_online"], "En línea", "Desconectado"),
                    size="1", color=rx.cond(u["is_online"], "#30d158", "#8e8e93"),
                ),
                align_items="start", spacing="0",
            ),
            rx.spacer(),
            rx.cond(
                ~is_me,
                rx.button("💬 DM", on_click=AppState.select_room(0, u["full_name"]), size="2", variant="soft"),
            ),
            padding="16px", align_items="center", width="100%",
        ),
        background="#111", border="1px solid #2c2c2e", border_radius="12px",
        width="100%", margin_bottom="12px",
    )

# ── Página Principal ──────────────────────────────────────────────

def contacts_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("👥 Directorio Nyme", size="7", color="white"),
                rx.spacer(),
                rx.button(
                    "📥 Exportar Excel",
                    on_click=AppState.export_contacts,
                    size="2", variant="outline", color_scheme="green",
                ),
                padding="24px 32px 8px", width="100%",
            ),
            
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("📱 Clientes", value="clients"),
                    rx.tabs.trigger("🏢 Equipo", value="team"),
                    rx.tabs.trigger("➕ Nuevo", value="new"),
                    padding="0 32px",
                ),
                
                # Clientes
                rx.tabs.content(
                    rx.vstack(
                        rx.input(
                            placeholder="🔍 Buscar por nombre, número o notas...",
                            on_change=AppState.set_contact_search,
                            background="#1c1c1e", border="1px solid #3a3a3c",
                            color="white", width="100%", margin_top="16px",
                        ),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(AppState.filtered_contact_list, contact_card),
                                width="100%", padding="16px 0",
                            ),
                            height="calc(100vh - 320px)",
                        ),
                        width="100%",
                    ),
                    value="clients", padding="0 32px",
                ),
                
                # Equipo
                rx.tabs.content(
                    rx.vstack(
                        rx.input(
                            placeholder="🔍 Buscar agente...",
                            on_change=AppState.set_team_search,
                            background="#1c1c1e", border="1px solid #3a3a3c",
                            color="white", width="100%", margin_top="16px",
                        ),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(AppState.filtered_team_list, team_card),
                                width="100%", padding="16px 0",
                            ),
                            height="calc(100vh - 320px)",
                        ),
                        width="100%",
                    ),
                    value="team", padding="0 32px",
                ),
                
                # Registro
                rx.tabs.content(
                    rx.vstack(
                        rx.grid(
                            rx.vstack(
                                rx.text("WhatsApp ID *", size="1", color="#8e8e93"),
                                rx.input(on_change=AppState.set_nc_wa_id, value=AppState.nc_wa_id, background="#1c1c1e", color="white"),
                                spacing="1",
                            ),
                            rx.vstack(
                                rx.text("Nombre Completo", size="1", color="#8e8e93"),
                                rx.input(on_change=AppState.set_nc_name, value=AppState.nc_name, background="#1c1c1e", color="white"),
                                spacing="1",
                            ),
                            columns="2", spacing="4", width="100%",
                        ),
                        rx.button("💾 Guardar Contacto", on_click=AppState.save_contact, color_scheme="blue"),
                        rx.cond(AppState.nc_msg != "", rx.text(AppState.nc_msg, color="green")),
                        spacing="4", padding="24px 0", align_items="start", width="100%",
                    ),
                    value="new", padding="0 32px",
                ),
                width="100%",
            ),
            spacing="0", width="100%",
        ),
        background="#000",
        min_height="100vh",
        on_mount=AppState.require_auth,
    )
