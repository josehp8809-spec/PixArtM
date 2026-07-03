import reflex as rx
import os

# En producción (Render) solo se expone un puerto (variable PORT, por defecto 10000).
# Al usar --backend-only, no debemos definir frontend_port en el rxconfig.
_port = int(os.getenv("PORT", "10000"))

config = rx.Config(
    app_name="nyme",
    backend_port=_port,
    api_url=os.getenv("RENDER_EXTERNAL_URL", f"http://localhost:{_port}"),
)
