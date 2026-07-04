"""
server.py — Servidor de producción para Render.

Monta el frontend estático DIRECTAMENTE sobre el FastAPI de Reflex,
preservando su lifespan y event processor correctamente.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, HTMLResponse
from starlette.requests import Request

# ── 1. Importar la app de Reflex ──────────────────────────────────────────────
#    IMPORTANTE: usar app._api (FastAPI) como app raíz para preservar el
#    lifespan de Reflex que inicializa el event processor y el state manager.
from nyme.nyme import app as reflex_app
fastapi_app = reflex_app._api

# ── 2. Directorio del frontend compilado ──────────────────────────────────────
BASE     = os.path.dirname(__file__)
BUILD_DIR = os.path.join(BASE, ".web", "build", "client")

print(f"[Server] BUILD_DIR = {BUILD_DIR}")
print(f"[Server] BUILD_DIR existe: {os.path.isdir(BUILD_DIR)}")

# ── 3. Montar /assets de Vite sobre la FastAPI de Reflex ──────────────────────
assets_dir = os.path.join(BUILD_DIR, "assets")
if os.path.isdir(assets_dir):
    fastapi_app.mount("/assets", StaticFiles(directory=assets_dir), name="vite_assets")
    print(f"[Server] /assets montado desde {assets_dir}")

# ── 4. Ruta catch-all para servir el SPA ──────────────────────────────────────
@fastapi_app.api_route("/{path:path}", methods=["GET", "HEAD"])
async def spa_catch_all(path: str = ""):
    """Sirve páginas del frontend exportado; fallback a __spa-fallback.html."""
    path = path.strip("/")

    candidates = []
    if path:
        candidates.append(os.path.join(BUILD_DIR, path))            # archivo exacto
        candidates.append(os.path.join(BUILD_DIR, path + ".html"))  # .html directo
        candidates.append(os.path.join(BUILD_DIR, path, "index.html"))

    candidates.append(os.path.join(BUILD_DIR, "__spa-fallback.html"))
    candidates.append(os.path.join(BUILD_DIR, "index.html"))

    for c in candidates:
        if os.path.isfile(c):
            return FileResponse(c)

    return HTMLResponse("<h1>Not Found</h1>", status_code=404)

# ── 5. Arrancar uvicorn con la FastAPI de Reflex (lifespan intacto) ───────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"[Server] Nyme iniciando en http://0.0.0.0:{port}")
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
