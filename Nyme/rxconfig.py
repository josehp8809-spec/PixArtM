import reflex as rx
import os

# En producción (Render), usamos el puerto público provisto en PORT.
# Como el frontend estático ahora se sirve nativamente desde la app de Reflex
# mediante el middleware ASGI, todo corre sobre este mismo puerto.
_port = int(os.getenv("PORT", "10000"))

config = rx.Config(
    app_name="nyme",
    backend_port=_port,
    api_url=os.getenv("RENDER_EXTERNAL_URL", f"http://localhost:{_port}"),
)
