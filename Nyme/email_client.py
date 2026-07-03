"""
email_client.py — Cliente para enviar correos de notificación (SMTP) en segundo plano.
"""
import os
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailClient:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER", "")
        self.password = os.getenv("SMTP_PASS", "")
        self.notif_email = os.getenv("NOTIFICATION_EMAIL", "")

    @property
    def is_configured(self):
        return bool(self.host and self.user and self.password)

    def _send_email_sync(self, to_email: str, subject: str, html_body: str):
        """Envía el correo de forma síncrona usando smtplib."""
        if not self.is_configured:
            print("[Email] Error: Cliente SMTP no configurado en .env")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.user
            msg["To"] = to_email

            part = MIMEText(html_body, "html")
            msg.attach(part)

            # Conexión SMTP
            server = smtplib.SMTP(self.host, self.port, timeout=10)
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, to_email, msg.as_string())
            server.quit()
            print(f"[Email] ✅ Correo enviado con éxito a {to_email}")
            return True
        except Exception as e:
            print(f"[Email] ❌ Error enviando correo: {e}")
            return False

    async def send_email(self, to_email: str, subject: str, html_body: str):
        """Ejecuta el envío de correo en un hilo de fondo para no bloquear el Event Loop."""
        if not to_email:
            return False
        return await asyncio.to_thread(self._send_email_sync, to_email, subject, html_body)

    async def send_order_notification(self, order_id, contact_wa_id, agent_username, items, total_amount, address, status, customer_email=None):
        """Notifica al administrador y al cliente (si tiene correo) sobre un cambio en su pedido."""
        status_labels = {
            "pending": "Pendiente de Confirmación",
            "confirmed": "Confirmado / En Preparación",
            "shipped": "Enviado / En camino",
            "delivered": "Entregado",
            "cancelled": "Cancelado"
        }
        status_colors = {
            "pending": "#ff9f0a",
            "confirmed": "#0a84ff",
            "shipped": "#30d158",
            "delivered": "#5e5ce6",
            "cancelled": "#ff3b30"
        }

        # Formatear items para el cuerpo HTML
        items_html = ""
        for item in items:
            p_name = item.get("product", "Producto Especial")
            qty = item.get("quantity", 1)
            price = item.get("price", 0.0)
            items_html += f"<tr><td style='padding: 8px; border-bottom: 1px solid #333;'>{p_name}</td><td style='padding: 8px; border-bottom: 1px solid #333; text-align: center;'>{qty}</td><td style='padding: 8px; border-bottom: 1px solid #333; text-align: right;'>${price:.2f}</td></tr>"

        subject = f"Nyme: Estado de Pedido #{order_id} actualizado a {status_labels.get(status, status)}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #111; color: #f5f5f7; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1c1c1e; border: 1px solid #2c2c2e; border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
                <h2 style="color: #0a84ff; border-bottom: 1px solid #2c2c2e; padding-bottom: 10px; margin-top: 0;">📱 Nyme — Actualización de Pedido</h2>
                <p>Hola,</p>
                <p>El pedido <strong>#{order_id}</strong> del cliente con WhatsApp <strong>+{contact_wa_id}</strong> ha cambiado de estado:</p>
                <div style="background-color: {status_colors.get(status, '#333')}22; border: 1px solid {status_colors.get(status, '#333')}; border-radius: 8px; padding: 12px; text-align: center; margin: 20px 0;">
                    <span style="font-size: 18px; font-weight: bold; color: {status_colors.get(status, '#FFF')};">{status_labels.get(status, status.upper())}</span>
                </div>
                <h4 style="color: #FFF; margin-bottom: 8px;">Detalles del Pedido:</h4>
                <table style="width: 100%; border-collapse: collapse; color: #ccc;">
                    <thead>
                        <tr style="background-color: #2c2c2e; color: #FFF;">
                            <th style="padding: 8px; text-align: left;">Producto</th>
                            <th style="padding: 8px; text-align: center; width: 60px;">Cant.</th>
                            <th style="padding: 8px; text-align: right; width: 100px;">Precio</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                <p style="text-align: right; font-size: 16px; font-weight: bold; color: #FFF; margin-top: 15px;">Total: ${total_amount:.2f}</p>
                <p style="margin-top: 15px; font-size: 13px; color: #888;">
                    <strong>Dirección de entrega:</strong> {address or 'Retiro en local'}<br>
                    <strong>Agente asignado:</strong> @{agent_username or 'Sistema'}
                </p>
                <div style="border-top: 1px solid #2c2c2e; padding-top: 15px; margin-top: 24px; text-align: center; font-size: 11px; color: #666;">
                    Nyme WhatsApp Customer Platform. Todos los derechos reservados.
                </div>
            </div>
        </body>
        </html>
        """

        # Enviar al correo de notificaciones del negocio
        if self.notif_email:
            await self.send_email(self.notif_email, f"[ADMIN] {subject}", html_body)

        # Enviar al cliente si tiene correo electrónico registrado
        if customer_email:
            await self.send_email(customer_email, subject, html_body)


email_client = EmailClient()
