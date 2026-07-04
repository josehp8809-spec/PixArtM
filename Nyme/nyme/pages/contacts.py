"""Página de Directorio — Con Buscador, Avatares y Exportación."""
import reflex as rx
from nyme.state import AppState
from nyme.pages.navbar import navbar

# ── Helper para Avatares ──────────────────────────────────────────

def avatar_box(name: rx.Var, size="40px") -> rx.Component:
    safe_name = rx.cond(name != "", name, "?")
    initial = safe_name[0]
    return rx.center(
        rx.text(initial, weight="bold", color="white", size="2"),
        width=size, height=size,
        background="#2c2c2e",
        border_radius="50%",
        flex_shrink="0",
        border="1px solid #3a3a3c"
    )

# ── Componente Cliente ───────────────────────────────────────────

def contact_card(c: rx.Var) -> rx.Component:
    c_name = c["name"].to(str)
    wa_id = c["wa_id"].to(str)
    notes = c["notes"].to(str)
    lifecycle = c["lifecycle_stage"].to(str)
    avatar_name = rx.cond(c_name != "", c_name, wa_id)
    display_name = rx.cond(c_name != "", c_name, "Sin nombre")

    return rx.box(
        rx.hstack(
            avatar_box(avatar_name),
            rx.vstack(
                rx.hstack(
                    rx.text(display_name, weight="bold", size="3", color="white"),
                    rx.badge(lifecycle, color_scheme="gray", variant="outline", size="1", radius="full"),
                    spacing="2", align_items="center"
                ),
                rx.text("📱 +", wa_id, size="2", color="#0a84ff"),
                align_items="start", spacing="0",
            ),
            rx.spacer(),
            rx.button(
                "💬 Chat",
                on_click=AppState.start_chat_with(wa_id),
                size="2", variant="surface",
            ),
            padding="16px", align_items="center", width="100%",
        ),
        rx.divider(color="#2c2c2e"),
        rx.cond(
            notes != "",
            rx.text(notes, size="1", color="#636366", padding="8px 16px"),
        ),
        background="#111", border="1px solid #2c2c2e", border_radius="12px",
        width="100%", margin_bottom="12px",
    )

# ── Componente Miembro del Equipo ─────────────────────────────────

def team_card(u: rx.Var) -> rx.Component:
    username = u["username"].to(str)
    full_name = u["full_name"].to(str)
    role = u["role"].to(str)
    is_online = u["is_online"].to(bool)
    is_me = (username == AppState.username)

    return rx.box(
        rx.hstack(
            rx.box(
                avatar_box(full_name),
                rx.box( # Indicador de conexión superpuesto
                    width="12px", height="12px",
                    background=rx.cond(is_online, "#30d158", "#3a3a3c"),
                    border="2px solid #111", border_radius="50%",
                    position="absolute", bottom="0", right="0",
                ),
                position="relative",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(full_name, weight="bold", size="3", color="white"),
                    rx.badge(role, color_scheme="blue", size="1"),
                    spacing="2", align_items="center",
                ),
                rx.text(
                    rx.cond(is_online, "En línea", "Desconectado"),
                    size="1", color=rx.cond(is_online, "#30d158", "#8e8e93"),
                ),
                align_items="start", spacing="0",
            ),
            rx.spacer(),
            rx.cond(
                ~is_me,
                rx.button("💬 DM", on_click=AppState.select_room(0, full_name), size="2", variant="soft"),
            ),
            padding="16px", align_items="center", width="100%",
        ),
        background="#111", border="1px solid #2c2c2e", border_radius="12px",
        width="100%", margin_bottom="12px",
    )

# ── Componente Métricas del CRM ────────────────────────────────────

def crm_metric_card(label: str, count_var: rx.Var, icon: str, color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(icon, size="4"),
                rx.text(label, weight="bold", size="2", color="#8e8e93"),
                spacing="2", align_items="center"
            ),
            rx.text(count_var.to_string(), weight="bold", size="6", color=color, margin_top="4px"),
            align_items="start", spacing="0",
        ),
        background="#111",
        border="1px solid #2c2c2e",
        border_radius="12px",
        padding="16px",
        flex="1",
        min_width="160px",
    )

# ── Página Principal ──────────────────────────────────────────────

def contacts_page() -> rx.Component:
    return rx.vstack(
        navbar("/contacts"),
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
            
            # Fila de métricas del CRM tipo Respond.io
            rx.hstack(
                crm_metric_card("New Customer", AppState.lifecycle_counts["New Customer"], "🏆", "white"),
                crm_metric_card("Lead", AppState.lifecycle_counts["Lead"], "🚀", "#30d158"),
                crm_metric_card("Customer", AppState.lifecycle_counts["Customer"], "👥", "#0a84ff"),
                crm_metric_card("Paid", AppState.lifecycle_counts["Paid"], "💳", "#bf5af2"),
                spacing="3",
                padding="8px 32px 16px",
                width="100%",
                flex_wrap="wrap",
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
                                rx.foreach(AppState.filtered_contact_list.to(list[dict]), contact_card),
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
                                rx.foreach(AppState.filtered_team_list.to(list[dict]), team_card),
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
                            # Lado Izquierdo: Creador Individual
                            rx.box(
                                rx.vstack(
                                    rx.heading("➕ Contacto Individual", size="4", color="white"),
                                    rx.text("Registra un nuevo contacto de WhatsApp manualmente.", size="2", color="#8e8e93"),
                                    rx.vstack(
                                        rx.text("WhatsApp ID (Número con código de país) *", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: 5491122334455", on_change=AppState.set_nc_wa_id, value=AppState.nc_wa_id, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                        spacing="1", width="100%"
                                    ),
                                    rx.vstack(
                                        rx.text("Nombre del Cliente", size="1", color="#8e8e93"),
                                        rx.input(placeholder="Ej: Juan Pérez", on_change=SettingsState.set_nc_name, value=AppState.nc_name, background="#1c1c1e", border="1px solid #3a3a3c", color="white", width="100%"),
                                        spacing="1", width="100%"
                                    ),
                                    rx.button("💾 Guardar Contacto", on_click=AppState.save_contact, color_scheme="blue", width="100%"),
                                    rx.cond(AppState.nc_msg != "", rx.text(AppState.nc_msg, color="#30d158", size="2")),
                                    spacing="4", align_items="start", width="100%"
                                ),
                                background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="24px"
                            ),
                            
                            # Lado Derecho: Importación Masiva por CSV
                            rx.box(
                                rx.vstack(
                                    rx.heading("📥 Importación Masiva (CSV)", size="4", color="white"),
                                    rx.text("Sube un archivo CSV con columnas: nombre, telefono, email, notas.", size="2", color="#8e8e93"),
                                    rx.upload(
                                        rx.center(
                                            rx.vstack(
                                                rx.text("📁 Arrastra tu CSV aquí o haz clic para buscar", size="2", color="#8e8e93"),
                                                rx.text("Tamaño máximo 5MB", size="1", color="#636366"),
                                                align_items="center", spacing="1"
                                            ),
                                            padding="24px",
                                            border="2px dashed #3a3a3c",
                                            border_radius="10px",
                                            cursor="pointer",
                                            width="100%",
                                            _hover={"border_color": "#0a84ff"}
                                        ),
                                        id="import_csv",
                                        multiple=False,
                                        accept={
                                            "text/csv": [".csv"]
                                        },
                                        width="100%"
                                    ),
                                    rx.hstack(
                                        rx.button(
                                            "Importar CSV",
                                            on_click=AppState.import_contacts_csv(rx.upload_files(upload_id="import_csv")),
                                            color_scheme="green", size="2"
                                        ),
                                        rx.button(
                                            "Limpiar",
                                            on_click=rx.clear_selected_files("import_csv"),
                                            variant="soft", size="2"
                                        ),
                                        spacing="2"
                                    ),
                                    rx.cond(
                                        AppState.wf_msg != "",
                                        rx.text(AppState.wf_msg, size="2", color="#30d158", weight="bold")
                                    ),
                                    spacing="4", align_items="start", width="100%"
                                ),
                                background="#111", border="1px solid #2c2c2e", border_radius="12px", padding="24px"
                            ),
                            columns="2", spacing="4", width="100%", padding="24px 0"
                        ),
                        width="100%"
                    ),
                    value="new", padding="0 32px",
                ),
                width="100%",
            ),
            spacing="0", width="100%",
        ),
        spacing="0",
        width="100%",
        background="#000",
        min_height="100vh",
        on_mount=AppState.require_auth,
    )
