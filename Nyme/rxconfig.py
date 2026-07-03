import reflex as rx
import os

# En producción (Render) solo se expone un puerto (variable PORT, por defecto 10000).
# frontend_port == backend_port es OBLIGATORIO para que Reflex arranque en prod.
_port = int(os.getenv("PORT", "10000"))

config = rx.Config(
    app_name="nyme",
    backend_port=_port,
    frontend_port=_port,
    api_url=os.getenv("RENDER_EXTERNAL_URL", f"http://localhost:{_port}"),
)
