"""Página de Ventas y Administración de Pedidos — Kanban y Gestión."""
import reflex as rx
from nyme.state import AppState
from nyme.pages.navbar import navbar

STATUS_COLORS = {
    "pending": "#ff9f0a",
    "confirmed": "#0a84ff",
    "shipped": "#30d158",
    "delivered": "#5e5ce6",
    "cancelled": "#ff3b30"
}


def order_item_card(order: rx.Var) -> rx.Component:
    """Representa un pedido en el tablero Kanban."""
    
    # Formatear lista de items
    items_text = rx.vstack(
        rx.foreach(
            order["items"].to(list[dict]),
            lambda item: rx.hstack(
                rx.text(item["product"], size="1", color="white", weight="bold", flex="1"),
                rx.text("x", item["quantity"].to_string(), size="1", color="#8e8e93"),
                width="100%"
            )
        ),
        width="100%", spacing="1", padding_top="8px"
    )

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("Pedido #", order["id"].to_string(), weight="bold", size="2", color="white"),
                rx.spacer(),
                rx.text("$", order["total_amount"].to_string(), weight="bold", size="2", color="#30d158"),
                width="100%", align_items="center"
            ),
            rx.divider(color="#2c2c2e"),
            rx.text("Cliente: ", order["contact_name"], size="1", color="#8e8e93"),
            rx.text("WhatsApp: +", order["wa_id"].to_string(), size="1", color="#0a84ff"),
            
            items_text,
            
            rx.divider(color="#2c2c2e"),
            rx.text("Dirección: ", order["shipping_address"], size="1", color="#8e8e93", font_style="italic"),
            
            rx.divider(color="#2c2c2e"),
            rx.hstack(
                rx.text("Estado:", size="1", color="#8e8e93"),
                rx.select(
                    ["pending", "confirmed", "shipped", "delivered", "cancelled"],
                    value=order["status"],
                    on_change=lambda val: AppState.update_order_status(order["id"], val),
                    background="#1c1c1e", color="white", border="1px solid #3a3a3c", size="1", height="24px"
                ),
                width="100%", align_items="center"
            ),
            rx.text("Actualizado: ", order["updated_at"], size="1", color="#636366"),
            spacing="2", align_items="start"
        ),
        padding="16px",
        background="#111",
        border="1px solid #2c2c2e",
        border_radius="12px",
        margin_bottom="12px",
        width="100%",
        box_shadow="0 4px 12px rgba(0,0,0,0.3)"
    )


def kanban_column(status: str, title: str, color: str) -> rx.Component:
    """Columna Kanban que filtra y muestra pedidos según su estado."""
    return rx.vstack(
        rx.hstack(
            rx.box(width="8px", height="8px", background=color, border_radius="50%"),
            rx.heading(title, size="3", color="white"),
            rx.spacer(),
            padding="8px 0", width="100%", align_items="center", border_bottom=f"2px solid {color}"
        ),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(
                    AppState.orders.to(list[dict]),
                    lambda order: rx.cond(
                        order["status"] == status,
                        order_item_card(order)
                    )
                ),
                width="100%", spacing="1", padding_top="12px"
            ),
            height="calc(100vh - 220px)"
        ),
        width="100%", height="100%", spacing="2", padding="0 8px"
    )


def orders_page() -> rx.Component:
    return rx.vstack(
        navbar("/orders"),
        rx.vstack(
            rx.hstack(
                rx.heading("📊 Tablero de Ventas y Pedidos", size="7", color="white"),
                rx.spacer(),
                padding="24px 32px 8px", width="100%"
            ),
            rx.text(
                "Administra los pedidos de los clientes en tiempo real y cambia sus estados para disparar notificaciones SMTP automáticas.",
                color="#8e8e93", padding="0 32px 16px", width="100%"
            ),
            rx.divider(color="#2c2c2e"),
            
            # Tablero Kanban
            rx.grid(
                kanban_column("pending", "Pendiente", STATUS_COLORS["pending"]),
                kanban_column("confirmed", "Preparación", STATUS_COLORS["confirmed"]),
                kanban_column("shipped", "En camino", STATUS_COLORS["shipped"]),
                kanban_column("delivered", "Entregado", STATUS_COLORS["delivered"]),
                kanban_column("cancelled", "Cancelado", STATUS_COLORS["cancelled"]),
                columns="5",
                spacing="4",
                width="100%",
                padding="24px 32px",
                height="calc(100vh - 240px)",
                align_items="stretch"
            ),
            spacing="0", width="100%"
        ),
        background="#000",
        spacing="0",
        min_height="100vh",
        width="100%",
        on_mount=AppState.require_auth
    )
