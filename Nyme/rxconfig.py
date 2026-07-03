import reflex as rx
import os

# En producción (Render), el frontend ya fue compilado por build.py.
# El backend corre solo y sirve los archivos estáticos del frontend.
# Render provee el puerto a través de la variable PORT (por defecto 10000).
_port = int(os.getenv("PORT", "8000"))

config = rx.Config(
    app_name="nyme",
    backend_port=_port,
    frontend_port=_port,
    api_url=os.getenv("RENDER_EXTERNAL_URL", f"http://localhost:{_port}"),
)
