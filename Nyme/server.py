"""
server.py — Servidor de producción para Render.

Combina en un solo proceso uvicorn:
  1. El backend de Reflex (WebSocket de estado, API, webhook de Meta)
  2. Los archivos estáticos del frontend compilado en .web/build/client/
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, HTMLResponse, Response
from starlette.requests import Request

# ── 1. Importar la app de Reflex ─────────────────────────────────────────────
from nyme.nyme import app as reflex_app
reflex_routes = list(reflex_app._api.routes)

# ── 2. Directorio correcto del frontend ──────────────────────────────────────
# Reflex >= 0.9 exporta a .web/build/client/ (no .web/_static/ ni .web/build/)
BASE = os.path.dirname(__file__)
BUILD_DIR = os.path.join(BASE, ".web", "build", "client")

print(f"[Server] BUILD_DIR = {BUILD_DIR}")
print(f"[Server] BUILD_DIR existe: {os.path.isdir(BUILD_DIR)}")
if os.path.isdir(BUILD_DIR):
    print(f"[Server] Contenido BUILD_DIR: {os.listdir(BUILD_DIR)[:10]}")

async def serve_page(request: Request) -> Response:
    """Sirve las páginas del frontend exportado (SPA fallback a index.html)."""
    path = request.path_params.get("path", "").strip("/")

    candidates = []
    if path:
        candidates.append(os.path.join(BUILD_DIR, path))
        candidates.append(os.path.join(BUILD_DIR, path + ".html"))
        candidates.append(os.path.join(BUILD_DIR, path, "index.html"))

    candidates.append(os.path.join(BUILD_DIR, "__spa-fallback.html"))
    candidates.append(os.path.join(BUILD_DIR, "index.html"))

    for c in candidates:
        if os.path.isfile(c):
            return FileResponse(c)

    return HTMLResponse(
        f"<h1>404</h1><p>No se encontró: '{path}'</p><p>BUILD_DIR={BUILD_DIR}</p>",
        status_code=404,
    )

# ── 3. Rutas Starlette combinadas ─────────────────────────────────────────────
routes = list(reflex_routes)  # /ping, /_health, /_event (WS), /webhook

# Assets de Vite (JS, CSS, etc.) — están en BUILD_DIR directamente
if os.path.isdir(BUILD_DIR):
    routes.append(Mount("/assets", app=StaticFiles(directory=os.path.join(BUILD_DIR, "assets")), name="assets"))

# Catch-all para las páginas del SPA
routes.append(Route("/{path:path}", endpoint=serve_page))
routes.append(Route("/", endpoint=serve_page))

combined = Starlette(routes=routes)

# ── 4. Arrancar uvicorn ───────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"[Server] Nyme iniciando en http://0.0.0.0:{port}")
    uvicorn.run(
        combined,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
