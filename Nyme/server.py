"""
server.py — Servidor de producción para Render.

Combina en un solo proceso uvicorn:
  1. El backend de Reflex (WebSocket de estado, API, webhook de Meta)
  2. Los archivos estáticos del frontend compilado en .web/build/
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, HTMLResponse, Response
from starlette.requests import Request

# ── 1. Importar la app de Reflex para obtener las rutas de backend ──────────
from nyme.nyme import app as reflex_app
reflex_routes = list(reflex_app._api.routes)

# ── 2. Directorio del frontend compilado ────────────────────────────────────
BUILD_DIR = os.path.join(os.path.dirname(__file__), ".web", "build")

async def serve_page(request: Request) -> Response:
    """Sirve las páginas SPA del frontend exportado por Reflex."""
    path = request.path_params.get("path", "").strip("/")

    # Buscar archivo exacto (.html, .css, .js, etc.)
    candidates = []
    if path:
        candidates.append(os.path.join(BUILD_DIR, path))           # archivo directo
        candidates.append(os.path.join(BUILD_DIR, path + ".html")) # ruta como .html
        candidates.append(os.path.join(BUILD_DIR, path, "index.html"))

    candidates.append(os.path.join(BUILD_DIR, "index.html"))       # SPA fallback

    for c in candidates:
        if os.path.isfile(c):
            return FileResponse(c)

    return HTMLResponse("<h1>404 — Not Found</h1>", status_code=404)

# ── 3. Construir la app Starlette combinada ──────────────────────────────────
routes = list(reflex_routes)  # Rutas de Reflex (/_event, /ping, /webhook, etc.)

# Assets de Vite (JS, CSS, imágenes)
assets_dir = os.path.join(BUILD_DIR, "assets")
if os.path.isdir(assets_dir):
    routes.append(Mount("/assets", app=StaticFiles(directory=assets_dir), name="assets"))

# Archivos del cliente (chunks de React Router)
client_dir = os.path.join(BUILD_DIR, "client")
if os.path.isdir(client_dir):
    routes.append(Mount("/client", app=StaticFiles(directory=client_dir), name="client"))

# Catch-all: sirve páginas del frontend (SPA)
routes.append(Route("/{path:path}", endpoint=serve_page))
routes.append(Route("/", endpoint=serve_page))

combined = Starlette(routes=routes)

# ── 4. Arrancar uvicorn ──────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"[Server] Nyme iniciando en http://0.0.0.0:{port}")
    print(f"[Server] Frontend en: {BUILD_DIR} — existe: {os.path.isdir(BUILD_DIR)}")
    uvicorn.run(
        combined,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
