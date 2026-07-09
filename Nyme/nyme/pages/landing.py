"""Landing page for Nyme SaaS."""
import reflex as rx
from nyme.state import AppState

# Localized texts dictionary
TEXTS = {
    "es": {
        "nav_features": "Características",
        "nav_faq": "Preguntas Frecuentes",
        "nav_login": "Iniciar Sesión",
        "hero_title": "Conecta tu negocio al futuro de la comunicación",
        "hero_subtitle": "Bandeja omnicanal para WhatsApp, Facebook Messenger e Instagram DMs impulsada por Inteligencia Artificial. Centraliza chats, automatiza ventas y organiza tu equipo desde una sola plataforma.",
        "hero_cta": "Comenzar Ahora",
        "hero_demo": "Ver Demo",
        "features_title": "Todo lo que necesitas para escalar tu atención",
        "features_subtitle": "Herramientas diseñadas para aumentar tus ventas y optimizar los tiempos de respuesta de tu equipo.",
        "feat_inbox_title": "📥 Bandeja Omnicanal",
        "feat_inbox_desc": "Centraliza los mensajes de WhatsApp, Facebook Messenger e Instagram en un solo panel colaborativo para tu equipo.",
        "feat_ai_title": "🤖 Agentes IA Avanzados",
        "feat_ai_desc": "Configura chatbots entrenados con la información oficial de tu negocio para responder preguntas frecuentes las 24 horas del día.",
        "feat_crm_title": "📊 CRM y Pedidos en Chat",
        "feat_crm_desc": "Registra las ventas, gestiona el ciclo de vida del cliente y levanta pedidos directamente desde la ventana de conversación.",
        "feat_reports_title": "📈 Reportes y Analíticas",
        "feat_reports_desc": "Visualiza el tiempo promedio de respuesta, chats cerrados y el rendimiento general de tus asesores de ventas.",
        "faq_title": "Preguntas Frecuentes",
        "faq_1_q": "¿Cómo conecto mis canales de WhatsApp y redes sociales?",
        "faq_1_a": "Muy fácil. A través del asistente integrado de Nyme, puedes iniciar sesión con tu cuenta de Facebook, seleccionar tus páginas y números, y el sistema se encargará de enrutarlos automáticamente.",
        "faq_2_q": "¿Los datos y conversaciones de mis clientes están seguros?",
        "faq_2_a": "Sí, la seguridad es nuestra prioridad. Toda la información viaja cifrada mediante protocolos SSL/TLS y se almacena en bases de datos PostgreSQL seguras, cumpliendo rigurosamente con las políticas de privacidad de Meta.",
        "faq_3_q": "¿Puedo solicitar la eliminación total de mis datos?",
        "faq_3_a": "Por supuesto. Puedes eliminar tus canales directamente en la pantalla de configuración de Nyme, lo cual purga los datos del servidor. También puedes enviar una solicitud a soporte@nyme.com para eliminar tu cuenta permanentemente.",
        "footer_rights": "Todos los derechos reservados.",
        "footer_privacy": "Política de Privacidad",
        "footer_terms": "Términos del Servicio",
        "footer_deletion": "Eliminación de Datos",
        "footer_guide": "Guía de Uso",
        "footer_contact": "Contacto: soporte@nyme.com"
    },
    "en": {
        "nav_features": "Features",
        "nav_faq": "FAQ",
        "nav_login": "Sign In",
        "hero_title": "Connect your business to the future of communication",
        "hero_subtitle": "AI-powered omnichannel inbox for WhatsApp, Facebook Messenger, and Instagram DMs. Centralize chats, automate sales, and organize your team from a single, unified platform.",
        "hero_cta": "Get Started",
        "hero_demo": "View Demo",
        "features_title": "Everything you need to scale your support",
        "features_subtitle": "Tools designed to boost your sales and optimize your team's response times.",
        "feat_inbox_title": "📥 Omnichannel Inbox",
        "feat_inbox_desc": "Centralize all messages from WhatsApp, Facebook Messenger, and Instagram into a single collaborative panel for your team.",
        "feat_ai_title": "🤖 Advanced AI Agents",
        "feat_ai_desc": "Deploy custom AI assistants trained on your business's official knowledge base to answer FAQs 24/7.",
        "feat_crm_title": "📊 CRM & Orders in Chat",
        "feat_crm_desc": "Log sales, manage customer lifecycles, and create drafts for client orders directly within the chat window.",
        "feat_reports_title": "📈 Reports & Analytics",
        "feat_reports_desc": "Track key performance metrics such as average response times, active chats, and agent productivity.",
        "faq_title": "Frequently Asked Questions",
        "faq_1_q": "How do I connect my WhatsApp and social media channels?",
        "faq_1_a": "It's simple. Using Nyme's onboarding wizard, you log in with your Facebook account, select your business pages or phone numbers, and the system automatically configures the connection.",
        "faq_2_q": "Are my customers' data and conversations secure?",
        "faq_2_a": "Absolutely. Data security is our top priority. All communications are encrypted using SSL/TLS protocols and stored securely in dedicated PostgreSQL databases, fully complying with Meta policies.",
        "faq_3_q": "Can I request the complete deletion of my data?",
        "faq_3_a": "Yes. You can delete your lines from the Nyme configuration screen to purge their history immediately. You can also contact support at support@nyme.com to request permanent account deletion.",
        "footer_rights": "All rights reserved.",
        "footer_privacy": "Privacy Policy",
        "footer_terms": "Terms of Service",
        "footer_deletion": "Data Deletion Instructions",
        "footer_guide": "User Guide",
        "footer_contact": "Contact: support@nyme.com"
    }
}


def feature_card(title: rx.Var, description: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.heading(title, size="4", color="white", margin_bottom="8px"),
        rx.text(description, color="#8e8e93", size="2"),
        padding="28px",
        border="1px solid rgba(15, 163, 177, 0.15)",
        border_radius="16px",
        background="rgba(18, 18, 18, 0.6)",
        backdrop_filter="blur(8px)",
        _hover={
            "border": "1px solid rgba(15, 163, 177, 0.4)",
            "transform": "translateY(-4px)",
            "box_shadow": "0 10px 25px rgba(15, 163, 177, 0.15)"
        },
        transition="all 0.3s ease",
        align_items="start",
        width="100%"
    )


def faq_item(question: rx.Var, answer: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.text(question, color="white", weight="bold", size="3", margin_bottom="6px"),
        rx.text(answer, color="#8e8e93", size="2"),
        padding_y="16px",
        border_bottom="1px solid rgba(255, 255, 255, 0.1)",
        align_items="start",
        width="100%"
    )


def visitor_chat_modal() -> rx.Component:
    # Helper translations
    def vt(es: str, en: str) -> rx.Var:
        return rx.cond(AppState.landing_lang == "es", es, en)

    # Bubble item for visitor chat
    def visitor_bubble(msg: rx.Var) -> rx.Component:
        is_in = msg["type"] == "INBOUND"
        return rx.hstack(
            rx.box(
                rx.vstack(
                    rx.text(msg["body"], size="2", color="white", white_space="pre-wrap"),
                    rx.hstack(
                        rx.text(
                            rx.cond(is_in, rx.cond(AppState.landing_lang == "es", "Tú", "You"), msg["agent"]),
                            color="#8e8e93",
                            size="1"
                        ),
                        rx.text(" · ", color="#8e8e93", size="1"),
                        rx.text(msg["time"], color="#8e8e93", size="1"),
                        spacing="1",
                        align_items="center"
                    ),
                    spacing="1",
                    align_items=rx.cond(is_in, "start", "end"),
                ),
                background=rx.cond(is_in, "#1c1c1e", "#0a3055"),
                border_radius="12px",
                padding="10px 14px",
                max_width="85%",
            ),
            width="100%",
            justify=rx.cond(is_in, "start", "end"),
            padding_x="8px",
            margin_y="2px",
        )

    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.image(src="/logo.png", width="28px", height="auto", border_radius="6px"),
                    rx.vstack(
                        rx.heading(vt("Soporte Nyme", "Nyme Support"), size="3", color="white"),
                        rx.text(vt("Canal de ayuda en línea", "Online help channel"), size="1", color="#8e8e93"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("✕", variant="ghost", on_click=AppState.toggle_visitor_chat, color="white")
                    ),
                    width="100%",
                    align_items="center",
                    border_bottom="1px solid rgba(255,255,255,0.08)",
                    padding_bottom="10px",
                ),

                # Body (Condicional: Registro vs Chat)
                rx.cond(
                    ~AppState.visitor_chat_started,
                    # Pantalla de Bienvenida (Pedir Nombre)
                    rx.vstack(
                        rx.text(
                            vt(
                                "¡Hola! Escribe tu nombre para iniciar una conversación con nuestro equipo de soporte.",
                                "Hello! Enter your name to start a chat with our support team."
                            ),
                            size="2", color="#8e8e93", text_align="center"
                        ),
                        rx.input(
                            placeholder=vt("Tu Nombre Completo", "Your Full Name"),
                            value=AppState.visitor_name,
                            on_change=AppState.set_visitor_name,
                            background="rgba(255,255,255,0.05)",
                            border="1px solid rgba(255,255,255,0.1)",
                            color="white",
                            width="100%",
                            margin_top="8px",
                        ),
                        rx.button(
                            vt("Comenzar Chat", "Start Chat"),
                            on_click=AppState.start_visitor_chat,
                            background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                            color="white",
                            width="100%",
                            margin_top="12px",
                        ),
                        spacing="3",
                        padding_y="16px",
                        width="100%",
                        align_items="stretch",
                    ),
                    # Pantalla de Chat
                    rx.vstack(
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(AppState.visitor_messages, visitor_bubble),
                                spacing="1",
                                align_items="stretch",
                            ),
                            max_height="250px",
                            min_height="180px",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text_area(
                                placeholder=vt("Escribe un mensaje...", "Type a message..."),
                                value=AppState.visitor_new_message,
                                on_change=AppState.set_visitor_new_message,
                                background="rgba(255,255,255,0.05)",
                                border="1px solid rgba(255,255,255,0.1)",
                                color="white",
                                resize="none",
                                rows="1",
                                flex="1",
                            ),
                            rx.button(
                                "→",
                                on_click=AppState.send_visitor_message,
                                background="#0fa3b1",
                                color="white",
                            ),
                            width="100%",
                            align_items="end",
                            padding_top="8px",
                        ),
                        width="100%",
                        spacing="0",
                    ),
                ),
                width="100%",
                spacing="3",
            ),
            background="rgba(10, 10, 10, 0.95)",
            backdrop_filter="blur(16px)",
            border="1px solid rgba(255,255,255,0.1)",
            border_radius="16px",
            max_width="400px",
            padding="16px",
        ),
        open=AppState.visitor_chat_open,
    )


def landing_page() -> rx.Component:
    # Read dynamic localized string based on AppState.landing_lang via rx.cond
    def t(key: str) -> rx.Var:
        return rx.cond(
            AppState.landing_lang == "es",
            TEXTS["es"][key],
            TEXTS["en"][key]
        )

    return rx.vstack(
        # 1. NAVBAR
        rx.hstack(
            rx.hstack(
                rx.image(src="/logo.png", width="36px", height="auto", border_radius="8px"),
                rx.heading("Nyme", size="5", color="white", weight="bold", letter_spacing="0.5px"),
                spacing="2",
                align_items="center"
            ),
            rx.spacer(),
            rx.hstack(
                # Language Switcher Toggle
                rx.button(
                    rx.cond(AppState.landing_lang == "es", "🇬🇧 EN", "🇪🇸 ES"),
                    on_click=AppState.toggle_landing_lang,
                    size="1",
                    variant="ghost",
                    color="#0fa3b1",
                    _hover={"background": "rgba(15, 163, 177, 0.1)"}
                ),
                rx.button(
                    rx.cond(AppState.landing_lang == "es", "💬 Ayuda", "💬 Help"),
                    on_click=AppState.toggle_visitor_chat,
                    size="2",
                    variant="ghost",
                    color="#0fa3b1",
                    _hover={"background": "rgba(15, 163, 177, 0.1)"}
                ),
                rx.button(
                    t("nav_login"),
                    on_click=rx.redirect("/login"),
                    size="2",
                    background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                    color="white",
                    weight="bold",
                    border_radius="8px",
                    _hover={"box_shadow": "0 4px 15px rgba(15, 163, 177, 0.3)"}
                ),
                spacing="4",
                align_items="center"
            ),
            padding="16px 5%",
            background="rgba(0, 0, 0, 0.8)",
            backdrop_filter="blur(12px)",
            border_bottom="1px solid rgba(255, 255, 255, 0.08)",
            width="100%",
            position="sticky",
            top="0",
            z_index="999"
        ),

        # 2. HERO SECTION
        rx.center(
            rx.vstack(
                rx.heading(
                    t("hero_title"),
                    size="9",
                    color="white",
                    weight="bold",
                    text_align="center",
                    max_width="850px",
                    line_height="1.2",
                    background="linear-gradient(to right, #ffffff, #0fa3b1)",
                    background_clip="text",
                    # text_fill_color is represented as custom style properties in Reflex if needed, but linear gradient color is fine
                ),
                rx.text(
                    t("hero_subtitle"),
                    color="#8e8e93",
                    size="4",
                    text_align="center",
                    max_width="650px",
                    margin_top="16px"
                ),
                rx.hstack(
                    rx.button(
                        t("hero_cta"),
                        on_click=rx.redirect("/register"),
                        size="3",
                        background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                        color="white",
                        weight="bold",
                        border_radius="10px",
                        padding="12px 28px",
                        _hover={"transform": "scale(1.03)", "box_shadow": "0 6px 20px rgba(15, 163, 177, 0.4)"},
                        transition="all 0.2s ease"
                    ),
                    spacing="4",
                    margin_top="28px"
                ),
                align_items="center",
                padding="90px 20px",
                width="100%"
            ),
            width="100%",
            background="radial-gradient(circle at top, #0a1329 0%, #000000 70%)"
        ),

        # 3. FEATURES SECTION
        rx.vstack(
            rx.center(
                rx.vstack(
                    rx.heading(t("features_title"), size="7", color="white", weight="bold", text_align="center"),
                    rx.text(t("features_subtitle"), color="#8e8e93", size="3", text_align="center", max_width="500px"),
                    spacing="2",
                    align_items="center",
                    margin_bottom="48px"
                )
            ),
            # Features Grid
            rx.grid(
                feature_card(t("feat_inbox_title"), t("feat_inbox_desc")),
                feature_card(t("feat_ai_title"), t("feat_ai_desc")),
                feature_card(t("feat_crm_title"), t("feat_crm_desc")),
                feature_card(t("feat_reports_title"), t("feat_reports_desc")),
                columns="2", # Reflex auto handles responsiveness via mobile, but simple 2 columns is clean
                spacing="6",
                width="100%",
                max_width="1000px"
            ),
            padding="64px 5%",
            width="100%",
            align_items="center"
        ),

        # 4. FAQ SECTION
        rx.center(
            rx.vstack(
                rx.heading(t("faq_title"), size="6", color="white", weight="bold", margin_bottom="32px"),
                rx.vstack(
                    faq_item(t("faq_1_q"), t("faq_1_a")),
                    faq_item(t("faq_2_q"), t("faq_2_a")),
                    faq_item(t("faq_3_q"), t("faq_3_a")),
                    width="100%",
                    max_width="750px",
                    spacing="3"
                ),
                align_items="center",
                width="100%"
            ),
            padding="64px 5% 90px",
            width="100%"
        ),

        # 5. FOOTER
        rx.vstack(
            rx.divider(color="rgba(255, 255, 255, 0.08)", margin_bottom="32px"),
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.image(src="/logo.png", width="28px", height="auto", border_radius="6px"),
                        rx.text("Nyme", color="white", weight="bold", size="3"),
                        spacing="2",
                        align_items="center"
                    ),
                    rx.text(f"© 2026 Nyme. {t('footer_rights')}", color="#636366", size="1", margin_top="8px"),
                    align_items="start"
                ),
                rx.spacer(),
                rx.vstack(
                    rx.link(t("footer_privacy"), href="/privacy", color="#8e8e93", size="2", _hover={"color": "#0fa3b1"}),
                    rx.link(t("footer_terms"), href="/terms", color="#8e8e93", size="2", _hover={"color": "#0fa3b1"}),
                    rx.link(t("footer_deletion"), href="/data-deletion", color="#8e8e93", size="2", _hover={"color": "#0fa3b1"}),
                    rx.link(t("footer_guide"), href="/instructions", color="#8e8e93", size="2", _hover={"color": "#0fa3b1"}),
                    align_items="end",
                    spacing="2"
                ),
                width="100%",
                max_width="1000px"
            ),
            rx.text(t("footer_contact"), color="#636366", size="1", margin_top="20px"),
            padding="48px 5%",
            background="rgba(10, 10, 10, 0.9)",
            width="100%",
            align_items="center"
        ),
        visitor_chat_modal(),
        background_color="#000000",
        min_height="100vh",
        spacing="0",
        width="100%"
    )
