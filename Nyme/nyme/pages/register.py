"""SaaS business self-registration page."""
import reflex as rx
from nyme.state import AppState

REG_TEXTS = {
    "es": {
        "title": "Solicitud de Registro Nyme",
        "subtitle": "Completa los siguientes datos para pre-registrar tu empresa. Un administrador revisará tu solicitud y te enviará las credenciales por correo electrónico.",
        "company_name": "Nombre de la Empresa *",
        "contact_name": "Nombre de Contacto *",
        "contact_email": "Correo Electrónico de Contacto *",
        "contact_phone": "Teléfono de Contacto",
        "notes": "Notas adicionales (canal de interés, volumen de mensajes, etc.)",
        "submit": "Enviar Solicitud",
        "success": "🎉 ¡Solicitud enviada con éxito!",
        "success_detail": "Tu solicitud ha sido registrada correctamente. Un administrador revisará tus datos y te enviará las credenciales de tu cuenta inicial e instrucciones de inicio por correo en menos de 24 horas hábiles.",
        "back": "Volver al Inicio",
        "error": "Error:"
    },
    "en": {
        "title": "Nyme Account Request",
        "subtitle": "Complete the form below to pre-register your business. An administrator will review your request and email you the login credentials.",
        "company_name": "Company Name *",
        "contact_name": "Contact Name *",
        "contact_email": "Contact Email Address *",
        "contact_phone": "Contact Phone Number",
        "notes": "Additional Notes (preferred channel, monthly message volume, etc.)",
        "submit": "Submit Request",
        "success": "🎉 Request submitted successfully!",
        "success_detail": "Your request has been saved. An administrator will review your application and send an email to your address with your starting login credentials and setup guide within 24 business hours.",
        "back": "Go Back Home",
        "error": "Error:"
    }
}


def t(key: str) -> rx.Var:
    return rx.cond(
        AppState.landing_lang == "es",
        REG_TEXTS["es"].get(key, key),
        REG_TEXTS["en"].get(key, key)
    )


def register_page() -> rx.Component:
    return rx.vstack(
        # NAVBAR SIMPLE
        rx.hstack(
            rx.hstack(
                rx.image(src="/logo.png", width="32px", height="auto", border_radius="8px"),
                rx.text("Nyme", color="white", weight="bold", size="4"),
                spacing="2",
                align_items="center",
                cursor="pointer",
                on_click=rx.redirect("/")
            ),
            rx.spacer(),
            rx.hstack(
                # Language Switcher
                rx.button(
                    rx.cond(AppState.landing_lang == "es", "🇬🇧 EN", "🇪🇸 ES"),
                    on_click=AppState.toggle_landing_lang,
                    size="1",
                    variant="ghost",
                    color="#0fa3b1",
                    _hover={"background": "rgba(15, 163, 177, 0.1)"}
                ),
                rx.button(
                    t("back"),
                    on_click=rx.redirect("/"),
                    size="1",
                    variant="ghost",
                    color="#8e8e93"
                ),
                spacing="4",
                align_items="center"
            ),
            padding="16px 5%",
            background="rgba(10, 10, 10, 0.9)",
            border_bottom="1px solid rgba(255, 255, 255, 0.08)",
            width="100%"
        ),

        rx.center(
            rx.vstack(
                rx.cond(
                    AppState.reg_success,
                    # TARIETA EXITO
                    rx.vstack(
                        rx.heading(t("success"), size="6", color="#30d158", weight="bold", margin_bottom="12px"),
                        rx.text(t("success_detail"), color="#d1d1d6", size="3", text_align="center", line_height="1.6", margin_bottom="24px"),
                        rx.button(
                            t("back"),
                            on_click=rx.redirect("/"),
                            background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                            color="white",
                            border_radius="10px",
                            size="3",
                            width="100%",
                            weight="bold"
                        ),
                        align_items="center",
                        padding="40px",
                        border="1px solid rgba(48, 209, 88, 0.3)",
                        border_radius="20px",
                        background="rgba(18, 18, 18, 0.8)",
                        backdrop_filter="blur(12px)",
                        box_shadow="0 20px 40px rgba(0,0,0,0.6)",
                        width="100%"
                    ),
                    # FORMULARIO
                    rx.vstack(
                        rx.heading(t("title"), size="7", color="white", weight="bold", margin_bottom="4px", text_align="center"),
                        rx.text(t("subtitle"), color="#8e8e93", size="2", text_align="center", margin_bottom="20px"),
                        
                        # Campos
                        rx.vstack(
                            rx.text(t("company_name"), size="1", color="#8e8e93", weight="bold"),
                            rx.input(
                                placeholder="Ej: Mi Empresa S.A.",
                                on_change=AppState.set_reg_company_name,
                                value=AppState.reg_company_name,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%",
                                height="40px"
                            ),
                            spacing="1", width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text(t("contact_name"), size="1", color="#8e8e93", weight="bold"),
                            rx.input(
                                placeholder="Ej: Juan Pérez",
                                on_change=AppState.set_reg_contact_name,
                                value=AppState.reg_contact_name,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%",
                                height="40px"
                            ),
                            spacing="1", width="100%"
                        ),

                        rx.vstack(
                            rx.text(t("contact_email"), size="1", color="#8e8e93", weight="bold"),
                            rx.input(
                                placeholder="Ej: juan@empresa.com",
                                type="email",
                                on_change=AppState.set_reg_contact_email,
                                value=AppState.reg_contact_email,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%",
                                height="40px"
                            ),
                            spacing="1", width="100%"
                        ),

                        rx.vstack(
                            rx.text(t("contact_phone"), size="1", color="#8e8e93", weight="bold"),
                            rx.input(
                                placeholder="Ej: +52 1 222 333 4455",
                                on_change=AppState.set_reg_contact_phone,
                                value=AppState.reg_contact_phone,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%",
                                height="40px"
                            ),
                            spacing="1", width="100%"
                        ),

                        rx.vstack(
                            rx.text("Plan Seleccionado *", size="1", color="#8e8e93", weight="bold"),
                            rx.select(
                                ["Starter", "Pro", "Enterprise"],
                                value=AppState.reg_selected_plan,
                                on_change=AppState.set_reg_selected_plan,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%"
                            ),
                            spacing="1", width="100%"
                        ),

                        rx.vstack(
                            rx.text("Frecuencia de Pago *", size="1", color="#8e8e93", weight="bold"),
                            rx.select(
                                ["monthly", "semestral", "annual"],
                                value=AppState.reg_billing_frequency,
                                on_change=AppState.set_reg_billing_frequency,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%"
                            ),
                            spacing="1", width="100%"
                        ),

                        rx.vstack(
                            rx.text("Modalidad de IA *", size="1", color="#8e8e93", weight="bold"),
                            rx.select(
                                ["BYOK", "Incluida"],
                                value=AppState.reg_ai_mode,
                                on_change=AppState.set_reg_ai_mode,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%"
                            ),
                            spacing="1", width="100%"
                        ),

                        rx.vstack(
                            rx.text(t("notes"), size="1", color="#8e8e93", weight="bold"),
                            rx.text_area(
                                placeholder="Cuéntanos más de tu negocio...",
                                on_change=AppState.set_reg_notes,
                                value=AppState.reg_notes,
                                background="rgba(28, 28, 30, 0.8)",
                                border="1px solid rgba(255, 255, 255, 0.15)",
                                color="white",
                                width="100%",
                                height="80px"
                            ),
                            spacing="1", width="100%"
                        ),

                        rx.cond(
                            AppState.reg_error != "",
                            rx.callout(
                                AppState.reg_error,
                                color="red", variant="soft",
                                width="100%",
                            ),
                        ),

                        rx.button(
                            t("submit"),
                            on_click=AppState.submit_registration,
                            width="100%",
                            background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                            color="white",
                            _hover={"box_shadow": "0 4px 15px rgba(15, 163, 177, 0.4)"},
                            border_radius="10px",
                            height="44px",
                            weight="bold",
                            margin_top="16px"
                        ),
                        width="100%",
                        spacing="4",
                        padding="40px 32px",
                        border="1px solid rgba(15, 163, 177, 0.25)",
                        border_radius="20px",
                        background="rgba(18, 18, 18, 0.8)",
                        backdrop_filter="blur(16px)",
                        box_shadow="0 20px 40px rgba(0, 0, 0, 0.6)"
                    )
                ),
                width=["92%", "480px", "440px"],
                padding_y="60px"
            ),
            width="100%"
        ),
        background="radial-gradient(circle at center, #0a1128 0%, #000411 100%)",
        min_height="100vh",
        width="100%",
        spacing="0"
    )
