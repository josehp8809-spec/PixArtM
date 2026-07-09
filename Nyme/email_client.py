import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.zoho.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "activaciones@nymeapp.com")

def send_welcome_email(to_email, company_name, contact_name, username, password, plan_name, billing_frequency, ai_mode):
    # If credentials are not set, log and return False
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[Email Warning] SMTP credentials not set in .env. Skipping email send.")
        return False

    login_url = "https://nymeapp.com/login" # Adjust to production URL

    # Build HTML Content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenido a Nyme</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #000411;
                margin: 0;
                padding: 0;
                color: #ffffff;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #0a1128;
                border: 1px solid rgba(15, 163, 177, 0.2);
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }}
            .header {{
                background: linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%);
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 0.5px;
            }}
            .content {{
                padding: 40px 30px;
                line-height: 1.6;
            }}
            .content h2 {{
                color: #0fa3b1;
                font-size: 20px;
                margin-top: 0;
            }}
            .content p {{
                color: #d1d1d6;
                font-size: 15px;
            }}
            .details-box {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 20px;
                margin: 25px 0;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .label {{
                color: #8e8e93;
                font-weight: bold;
                font-size: 14px;
            }}
            .value {{
                color: #ffffff;
                font-size: 14px;
                font-family: monospace;
            }}
            .cta-button {{
                display: block;
                text-align: center;
                background: linear-gradient(135deg, #0fa3b1 0%, #0077b6 100%);
                color: #ffffff !important;
                text-decoration: none;
                padding: 14px 28px;
                border-radius: 8px;
                font-weight: bold;
                margin: 30px 0;
                box-shadow: 0 4px 15px rgba(15, 163, 177, 0.3);
            }}
            .footer {{
                background-color: rgba(0, 0, 0, 0.4);
                padding: 20px;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .footer p {{
                margin: 0;
                font-size: 12px;
                color: #636366;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Nyme — Inteligencia Omnicanal</h1>
            </div>
            <div class="content">
                <h2>¡Hola, {contact_name}!</h2>
                <p>Tu solicitud de registro para la empresa <strong>{company_name}</strong> ha sido aprobada con éxito por nuestro equipo administrativo.</p>
                <p>A continuación se muestran los detalles de tu cuenta de Administrador para comenzar a operar:</p>
                
                <div class="details-box">
                    <div class="detail-row">
                        <span class="label">Plan Contratado:</span>
                        <span class="value" style="color: #0fa3b1; font-weight: bold;">{plan_name} ({billing_frequency})</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Modalidad de IA:</span>
                        <span class="value">{ai_mode}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Usuario Administrador:</span>
                        <span class="value">{username}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Contraseña Temporal:</span>
                        <span class="value" style="color: #ff9500; font-weight: bold;">{password}</span>
                    </div>
                </div>

                <p>Te recomendamos cambiar tu contraseña una vez que inicies sesión por primera vez desde la sección de Configuración.</p>

                <a href="{login_url}" class="cta-button" target="_blank">Iniciar Sesión en Nyme</a>

                <p style="font-size: 13px; color: #8e8e93; margin-top: 20px;">
                    ¿Tienes dudas sobre cómo conectar tus canales de WhatsApp, Facebook o Instagram? Recuerda que tienes soporte en vivo disponible en tu panel o en la Landing Page oficial.
                </p>
            </div>
            <div class="footer">
                <p>© 2026 Nyme. Todos los derechos reservados.</p>
                <p>Este correo electrónico se envió de forma automática al registrarse.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Build MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✅ Tu cuenta de Nyme para {company_name} está lista"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    # Plain text fallback
    text_fallback = f"""
    ¡Hola, {contact_name}!
    Tu solicitud de registro para {company_name} ha sido aprobada.
    
    Detalles de tu cuenta:
    - Plan: {plan_name} ({billing_frequency})
    - Modalidad IA: {ai_mode}
    - Usuario: {username}
    - Contraseña: {password}
    
    Inicia sesión aquí: {login_url}
    
    © 2026 Nyme.
    """
    msg.attach(MIMEText(text_fallback, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, to_email, msg.as_string())
        server.quit()
        print(f"[Email Success] Welcome email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send welcome email: {e}")
        return False
