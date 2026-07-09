"""Legal documents pages for Nyme (Privacy Policy, Terms of Service, Data Deletion Instructions)."""
import reflex as rx
from nyme.state import AppState

DOCS_TEXTS = {
    "es": {
        "nav_home": "Inicio",
        "nav_login": "Iniciar Sesión",
        "contact_info": "Contacto de soporte: soporte@nyme.com",
        "privacy_title": "Política de Privacidad de Nyme",
        "privacy_last_updated": "Última actualización: 9 de Julio de 2026",
        "privacy_p1": "En Nyme, nos tomamos muy en serio la privacidad de tu negocio y la de tus clientes. Esta política explica cómo recopilamos, utilizamos y protegemos la información cuando utilizas nuestra plataforma de comunicación multicanal.",
        "privacy_h1": "1. Información que recopilamos",
        "privacy_p2": "Recopilamos únicamente los datos necesarios para prestar el servicio de chat omnicanal y automatización:",
        "privacy_li1": "Datos de tu cuenta: Nombre, correo electrónico y credenciales cifradas.",
        "privacy_li2": "Datos de canales (Meta API): Identificadores de teléfono (Phone Number ID), identificadores de páginas de Facebook (Page ID) y tokens de acceso necesarios para enviar y recibir mensajes.",
        "privacy_li3": "Datos de conversaciones: Historial de mensajes de texto, imágenes, audios y archivos recibidos a través de los canales conectados, con el único fin de mostrarlos en tu panel y permitir la atención al cliente por parte de tus agentes o de la Inteligencia Artificial.",
        "privacy_h2": "2. Uso de los Datos",
        "privacy_p3": "Los datos recopilados se utilizan exclusivamente para:",
        "privacy_li4": "Proveer, mantener y optimizar el servicio de Nyme.",
        "privacy_li5": "Procesar y enrutar las conversaciones entrantes y salientes de tus clientes.",
        "privacy_li6": "Generar reportes analíticos de rendimiento para tu empresa.",
        "privacy_p4": "Bajo ninguna circunstancia vendemos, alquilamos ni compartimos tus datos ni los de tus clientes con terceros.",
        "privacy_h3": "3. Seguridad de los Datos",
        "privacy_p5": "Implementamos medidas de seguridad técnicas y organizativas para proteger tus datos contra accesos no autorizados, pérdidas o alteraciones. Toda la comunicación viaja cifrada mediante HTTPS/SSL y la base de datos se almacena en servidores seguros con control de acceso restrictivo.",
        
        "terms_title": "Términos del Servicio de Nyme",
        "terms_last_updated": "Última actualización: 9 de Julio de 2026",
        "terms_p1": "Al registrarte y utilizar la plataforma Nyme, aceptas estar sujeto a los siguientes Términos del Servicio. Por favor, léelos atentamente antes de usar nuestro software.",
        "terms_h1": "1. Uso de la Plataforma",
        "terms_p2": "Nyme es una plataforma SaaS de comunicación multiagente. Te comprometes a usar la plataforma únicamente para fines lícitos y de conformidad con las leyes vigentes del país y con las políticas de Meta Platforms Inc.",
        "terms_h2": "2. Cumplimiento de Políticas de WhatsApp y Meta",
        "terms_p3": "Al conectar tus canales de WhatsApp, Facebook e Instagram a Nyme, eres responsable de cumplir las Condiciones de Servicio de Meta, incluyendo la prohibición de enviar SPAM o contenido abusivo. El incumplimiento de estas normas puede resultar en la suspensión de tu cuenta de Meta y de Nyme.",
        "terms_h3": "3. Suscripción y Pagos",
        "terms_p4": "El acceso a ciertas funciones avanzadas requiere una suscripción mensual. Las tarifas son cobradas de forma recurrente y no son reembolsables. Puedes cancelar tu suscripción en cualquier momento desde el panel de control.",
        "terms_h4": "4. Limitación de Responsabilidad",
        "terms_p5": "Nyme no se hace responsable por interrupciones en el servicio causadas por fallos en los servidores externos de Meta, fallos de red ajenos a la plataforma, o suspensiones de cuentas impuestas por Meta debido a malas prácticas del usuario.",
        
        "deletion_title": "Instrucciones de Eliminación de Datos de Nyme",
        "deletion_last_updated": "Última actualización: 9 de Julio de 2026",
        "deletion_p1": "En cumplimiento con las directrices de Meta Developers y los derechos de protección de datos personales, Nyme proporciona un mecanismo claro y sencillo para que los usuarios y clientes eliminen de manera permanente su información de nuestra base de datos.",
        "deletion_h1": "Cómo solicitar o realizar la eliminación de tus datos:",
        "deletion_step1_title": "Opción A: Eliminación automática de canales (Auto-servicio)",
        "deletion_step1_desc": "Si solo deseas eliminar un número de WhatsApp o canal de red social de nuestra plataforma, ve a la sección de Configuración en tu panel de Nyme, busca el canal en la lista y haz clic en el botón de eliminar (papelera 🗑️). Este proceso purga inmediatamente de nuestra base de datos los registros del canal, sus credenciales (Tokens) y todo su historial de mensajes asociados.",
        "deletion_step2_title": "Opción B: Eliminación completa de tu Cuenta de Nyme",
        "deletion_step2_desc": "Si deseas eliminar tu cuenta de Nyme por completo, junto con los datos de tu empresa, agentes, contactos e historial total, envía un correo electrónico a soporte@nyme.com con el asunto 'Solicitud de Eliminación de Datos'. Tu solicitud se procesará en un plazo máximo de 48 horas hábiles, tras el cual se borrará toda tu información de forma definitiva e irrecuperable.",
        "guide_title": "Guía de Uso e Instrucciones de Nyme",
        "guide_last_updated": "Última actualización: 9 de Julio de 2026",
        "guide_p1": "Esta guía práctica explica cómo utilizar las funciones principales de Nyme para centralizar la comunicación de tu negocio y automatizar la atención a tus clientes.",
        "guide_h1": "1. Conexión de Canales y Webhooks",
        "guide_p2": "Para recibir mensajes en tiempo real, debes dar de alta tus canales en el panel:",
        "guide_li1": "Configuración: Ve a Configuración > Canales y registra tu canal ingresando el Phone Number ID o Page ID y tu Access Token.",
        "guide_li2": "Meta Webhooks: Configura el webhook de tu aplicación de Meta apuntando a 'https://nyme-app.onrender.com/webhook' usando el token de verificación asignado, y suscríbete al evento 'messages'.",
        "guide_h2": "2. Bandeja de Entrada y CRM",
        "guide_p3": "Una vez conectados, gestiona tus clientes de forma eficiente:",
        "guide_li3": "Asignación: Asigna conversaciones a asesores específicos haciendo clic en 'Asignarme' o usando el menú desplegable.",
        "guide_li4": "Ciclo de Vida: Clasifica a tus contactos en el panel lateral (Nuevo, Pendiente, etc.) para segmentar tu base de datos.",
        "guide_li5": "Levantamiento de Pedidos: Genera borradores de órdenes registrando productos del catálogo directamente desde la conversación.",
        "guide_h3": "3. Respuestas Rápidas e Inteligencia Artificial",
        "guide_p4": "Ahorra tiempo automatizando respuestas a preguntas frecuentes:",
        "guide_li6": "Atajos de Teclado: Escribe '/' en el campo de texto del chat para abrir la lista de respuestas rápidas y enviarlas en un segundo.",
        "guide_li7": "Agentes IA (RAG): Ve a Configuración > Agentes IA para activar un bot inteligente, y pégale documentos de conocimiento (menús, políticas, precios) para que atienda automáticamente.",
        "footer_guide": "Guía de Uso"
    },
    "en": {
        "nav_home": "Home",
        "nav_login": "Sign In",
        "contact_info": "Support contact: support@nyme.com",
        "privacy_title": "Nyme Privacy Policy",
        "privacy_last_updated": "Last updated: July 9, 2026",
        "privacy_p1": "At Nyme, we take the privacy of your business and your customers very seriously. This policy explains how we collect, use, and safeguard information when you use our multi-channel communication platform.",
        "privacy_h1": "1. Information We Collect",
        "privacy_p2": "We only collect data necessary to provide the omnichannel chat and automation services:",
        "privacy_li1": "Account Data: Name, email address, and encrypted credentials.",
        "privacy_li2": "Channel Data (Meta API): Phone Number IDs, Facebook Page IDs, and access tokens required to send and receive messages.",
        "privacy_li3": "Conversation Data: History of messages, images, audios, and files received through connected channels, solely to display them on your dashboard and enable customer support by your agents or AI.",
        "privacy_h2": "2. How We Use the Data",
        "privacy_p3": "Collected data is used exclusively to:",
        "privacy_li4": "Provide, maintain, and optimize the Nyme service.",
        "privacy_li5": "Process and route incoming and outgoing customer chats.",
        "privacy_li6": "Generate analytical performance reports for your business.",
        "privacy_p4": "Under no circumstances do we sell, rent, or share your data or your customers' data with third parties.",
        "privacy_h3": "3. Data Security",
        "privacy_p5": "We implement technical and organizational security measures to protect your data against unauthorized access, loss, or alteration. All communication is encrypted using HTTPS/SSL, and database records are stored in secure servers with strict access controls.",
        
        "terms_title": "Nyme Terms of Service",
        "terms_last_updated": "Last updated: July 9, 2026",
        "terms_p1": "By registering and using the Nyme platform, you agree to be bound by the following Terms of Service. Please read them carefully before using our software.",
        "terms_h1": "1. Use of the Platform",
        "terms_p2": "Nyme is a multi-agent communication SaaS platform. You agree to use the platform only for lawful purposes and in compliance with local laws and policies of Meta Platforms Inc.",
        "terms_h2": "2. Compliance with WhatsApp & Meta Policies",
        "terms_p3": "By connecting your WhatsApp, Facebook, and Instagram channels to Nyme, you are responsible for complying with Meta's Terms of Service, including the prohibition of sending SPAM or abusive content. Failure to comply may lead to account suspension by Meta and Nyme.",
        "terms_h3": "3. Subscriptions and Billing",
        "terms_p4": "Access to certain premium features requires a monthly subscription. Fees are billed on a recurring basis and are non-refundable. You can cancel your subscription at any time from your billing dashboard.",
        "terms_h4": "4. Limitation of Liability",
        "terms_p5": "Nyme is not liable for service interruptions caused by failures in Meta's external servers, network errors outside the platform, or account suspensions imposed by Meta due to user bad practices.",
        
        "deletion_title": "Nyme Data Deletion Instructions",
        "deletion_last_updated": "Last updated: July 9, 2026",
        "deletion_p1": "In compliance with Meta Developers guidelines and personal data protection regulations, Nyme provides a clear and straightforward mechanism for users and customers to permanently delete their information from our databases.",
        "deletion_h1": "How to request or perform data deletion:",
        "deletion_step1_title": "Option A: Self-service channel removal",
        "deletion_step1_desc": "If you only want to delete a WhatsApp number or social media channel from our platform, navigate to the Settings section in your Nyme dashboard, locate the channel in the list, and click the delete button (trash bin 🗑️). This action immediately purges the channel configurations, security tokens, and all associated message history from our databases.",
        "deletion_step2_title": "Option B: Complete Nyme Account Deletion",
        "deletion_step2_desc": "If you wish to delete your entire Nyme account, along with all business records, agents, contacts, and full chat history, send an email to support@nyme.com with the subject 'Data Deletion Request'. Your request will be processed within 48 business hours, permanently and irreversibly purging all your data.",
        "guide_title": "Nyme User Guide & Instructions",
        "guide_last_updated": "Last updated: July 9, 2026",
        "guide_p1": "This practical guide explains how to use the core features of Nyme to centralize your business communication and automate customer support.",
        "guide_h1": "1. Connecting Channels & Webhooks",
        "guide_p2": "To receive messages in real time, you must link your channels in the dashboard:",
        "guide_li1": "Settings: Go to Settings > Channels and register your channel by entering the Phone Number ID or Page ID and your Access Token.",
        "guide_li2": "Meta Webhooks: Configure your Meta application webhook pointing to 'https://nyme-app.onrender.com/webhook' using the verification token, and subscribe to the 'messages' field.",
        "guide_h2": "2. Omnichannel Inbox & CRM",
        "guide_p3": "Once connected, manage your customers efficiently:",
        "guide_li3": "Assign: Assign chats to specific agents by clicking 'Assign to me' or using the dropdown.",
        "guide_li4": "Lifecycle Stage: Tag your contacts in the sidebar (New Customer, Pending, etc.) to segment your CRM database.",
        "guide_li5": "Order Management: Create order drafts by selecting products from your catalog directly inside the conversation.",
        "guide_h3": "3. Quick Replies & AI Agents",
        "guide_p4": "Save time by automating repetitive responses:",
        "guide_li6": "Keyboard Shortcuts: Type '/' in the chat input box to show the quick replies list and send them in a second.",
        "guide_li7": "AI Agents (RAG): Go to Settings > AI Agents to activate an intelligent assistant, and paste knowledge base documents (menus, policies, pricing) for automatic responses.",
        "footer_guide": "User Guide"
    }
}


def doc_navbar() -> rx.Component:
    return rx.hstack(
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
            rx.button(
                rx.cond(AppState.landing_lang == "es", "🇬🇧 EN", "🇪🇸 ES"),
                on_click=AppState.toggle_landing_lang,
                size="1",
                variant="ghost",
                color="#0fa3b1",
                _hover={"background": "rgba(15, 163, 177, 0.1)"}
            ),
            rx.button(
                "Home",
                on_click=rx.redirect("/"),
                size="1",
                variant="ghost",
                color="#8e8e93"
            ),
            rx.button(
                "Sign In",
                on_click=rx.redirect("/login"),
                size="2",
                background="linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%)",
                color="white",
                weight="bold",
                border_radius="8px"
            ),
            spacing="4",
            align_items="center"
        ),
        padding="16px 5%",
        background="rgba(10, 10, 10, 0.9)",
        backdrop_filter="blur(8px)",
        border_bottom="1px solid rgba(255, 255, 255, 0.08)",
        width="100%",
        position="sticky",
        top="0",
        z_index="999"
    )


def doc_footer() -> rx.Component:
    t = lambda key: DOCS_TEXTS[AppState.landing_lang].get(key, key)
    return rx.vstack(
        rx.divider(color="rgba(255, 255, 255, 0.08)", margin_bottom="24px"),
        rx.hstack(
            rx.text("© 2026 Nyme. All rights reserved.", color="#636366", size="1"),
            rx.spacer(),
            rx.hstack(
                rx.link("Privacy", href="/privacy", color="#8e8e93", size="1", _hover={"color": "#0fa3b1"}),
                rx.link("Terms", href="/terms", color="#8e8e93", size="1", _hover={"color": "#0fa3b1"}),
                rx.link("Data Deletion", href="/data-deletion", color="#8e8e93", size="1", _hover={"color": "#0fa3b1"}),
                rx.link(t("footer_guide"), href="/instructions", color="#8e8e93", size="1", _hover={"color": "#0fa3b1"}),
                spacing="4"
            ),
            width="100%",
            max_width="900px"
        ),
        rx.text(t("contact_info"), color="#636366", size="1", margin_top="16px"),
        padding="32px 5%",
        background="#0a0a0a",
        width="100%",
        align_items="center"
    )


def privacy_page() -> rx.Component:
    t = lambda key: DOCS_TEXTS[AppState.landing_lang][key]
    
    return rx.vstack(
        doc_navbar(),
        rx.center(
            rx.vstack(
                rx.heading(t("privacy_title"), size="7", color="white", weight="bold", margin_bottom="4px"),
                rx.text(t("privacy_last_updated"), color="#0fa3b1", size="2", margin_bottom="24px"),
                
                rx.text(t("privacy_p1"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("privacy_h1"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("privacy_p2"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="12px"),
                rx.vstack(
                    rx.text(f"• {t('privacy_li1')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('privacy_li2')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('privacy_li3')}", color="#8e8e93", size="2"),
                    align_items="start",
                    padding_left="16px",
                    margin_bottom="24px",
                    spacing="2"
                ),
                
                rx.heading(t("privacy_h2"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("privacy_p3"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="12px"),
                rx.vstack(
                    rx.text(f"• {t('privacy_li4')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('privacy_li5')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('privacy_li6')}", color="#8e8e93", size="2"),
                    align_items="start",
                    padding_left="16px",
                    margin_bottom="16px",
                    spacing="2"
                ),
                rx.text(t("privacy_p4"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("privacy_h3"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("privacy_p5"), color="#d1d1d6", size="3", line_height="1.6"),
                
                align_items="start",
                max_width="800px",
                width="100%",
                padding="64px 24px"
            ),
            width="100%"
        ),
        doc_footer(),
        background_color="#000000",
        min_height="100vh",
        spacing="0",
        width="100%"
    )


def terms_page() -> rx.Component:
    t = lambda key: DOCS_TEXTS[AppState.landing_lang][key]
    
    return rx.vstack(
        doc_navbar(),
        rx.center(
            rx.vstack(
                rx.heading(t("terms_title"), size="7", color="white", weight="bold", margin_bottom="4px"),
                rx.text(t("terms_last_updated"), color="#0fa3b1", size="2", margin_bottom="24px"),
                
                rx.text(t("terms_p1"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("terms_h1"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("terms_p2"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("terms_h2"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("terms_p3"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("terms_h3"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("terms_p4"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("terms_h4"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("terms_p5"), color="#d1d1d6", size="3", line_height="1.6"),
                
                align_items="start",
                max_width="800px",
                width="100%",
                padding="64px 24px"
            ),
            width="100%"
        ),
        doc_footer(),
        background_color="#000000",
        min_height="100vh",
        spacing="0",
        width="100%"
    )


def data_deletion_page() -> rx.Component:
    t = lambda key: DOCS_TEXTS[AppState.landing_lang][key]
    
    return rx.vstack(
        doc_navbar(),
        rx.center(
            rx.vstack(
                rx.heading(t("deletion_title"), size="7", color="white", weight="bold", margin_bottom="4px"),
                rx.text(t("deletion_last_updated"), color="#0fa3b1", size="2", margin_bottom="24px"),
                
                rx.text(t("deletion_p1"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("deletion_h1"), size="5", color="white", margin_bottom="20px"),
                
                rx.vstack(
                    rx.heading(t("deletion_step1_title"), size="4", color="#0fa3b1", margin_bottom="8px"),
                    rx.text(t("deletion_step1_desc"), color="#d1d1d6", size="3", line_height="1.6"),
                    padding="24px",
                    border="1px solid rgba(15, 163, 177, 0.2)",
                    border_radius="12px",
                    background="rgba(15, 163, 177, 0.05)",
                    width="100%",
                    align_items="start",
                    margin_bottom="24px"
                ),
                
                rx.vstack(
                    rx.heading(t("deletion_step2_title"), size="4", color="#0a84ff", margin_bottom="8px"),
                    rx.text(t("deletion_step2_desc"), color="#d1d1d6", size="3", line_height="1.6"),
                    padding="24px",
                    border="1px solid rgba(10, 132, 255, 0.2)",
                    border_radius="12px",
                    background="rgba(10, 132, 255, 0.05)",
                    width="100%",
                    align_items="start"
                ),
                
                align_items="start",
                max_width="800px",
                width="100%",
                padding="64px 24px"
            ),
            width="100%"
        ),
        doc_footer(),
        background_color="#000000",
        min_height="100vh",
        spacing="0",
        width="100%"
    )


def instructions_page() -> rx.Component:
    t = lambda key: DOCS_TEXTS[AppState.landing_lang][key]
    
    return rx.vstack(
        doc_navbar(),
        rx.center(
            rx.vstack(
                rx.heading(t("guide_title"), size="7", color="white", weight="bold", margin_bottom="4px"),
                rx.text(t("guide_last_updated"), color="#0fa3b1", size="2", margin_bottom="24px"),
                
                rx.text(t("guide_p1"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="24px"),
                
                rx.heading(t("guide_h1"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("guide_p2"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="12px"),
                rx.vstack(
                    rx.text(f"• {t('guide_li1')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('guide_li2')}", color="#8e8e93", size="2"),
                    align_items="start",
                    padding_left="16px",
                    margin_bottom="24px",
                    spacing="2"
                ),
                
                rx.heading(t("guide_h2"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("guide_p3"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="12px"),
                rx.vstack(
                    rx.text(f"• {t('guide_li3')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('guide_li4')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('guide_li5')}", color="#8e8e93", size="2"),
                    align_items="start",
                    padding_left="16px",
                    margin_bottom="24px",
                    spacing="2"
                ),
                
                rx.heading(t("guide_h3"), size="4", color="white", margin_bottom="12px"),
                rx.text(t("guide_p4"), color="#d1d1d6", size="3", line_height="1.6", margin_bottom="12px"),
                rx.vstack(
                    rx.text(f"• {t('guide_li6')}", color="#8e8e93", size="2"),
                    rx.text(f"• {t('guide_li7')}", color="#8e8e93", size="2"),
                    align_items="start",
                    padding_left="16px",
                    spacing="2"
                ),
                
                align_items="start",
                max_width="800px",
                width="100%",
                padding="64px 24px"
            ),
            width="100%"
        ),
        doc_footer(),
        background_color="#000000",
        min_height="100vh",
        spacing="0",
        width="100%"
    )
