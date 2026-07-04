import reflex as rx
import os

# En producción (Render):
#   REFLEX_BACKEND_PORT = puerto interno donde Reflex escucha (ej. 8080)
#   PORT               = puerto público de Render (ej. 10000)
# En desarrollo: usamos PORT para todo.
_port = int(os.getenv("REFLEX_BACKEND_PORT", os.getenv("PORT", "8080")))

config = rx.Config(
    app_name="nyme",
    backend_port=_port,
    api_url=os.getenv("RENDER_EXTERNAL_URL", f"http://localhost:{_port}"),
)
