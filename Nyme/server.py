"""
server.py — Servidor de producción para Render con depuración detallada.
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

# ── 2. Directorio del frontend ───────────────────────────────────────────────
BUILD_DIR = os.path.join(os.path.dirname(__file__), ".web", "build")

async def serve_page(request: Request) -> Response:
    path = request.path_params.get("path", "").strip("/")
    print(f"[Serve] Petición recibida para ruta: '{path}'")
    
    # Listar contenido de BUILD_DIR para depurar
    try:
        if os.path.isdir(BUILD_DIR):
            files = os.listdir(BUILD_DIR)
            print(f"[Serve] Contenido de {BUILD_DIR}: {files}")
        else:
            print(f"[Serve] ERROR: {BUILD_DIR} no es un directorio válido")
    except Exception as ex:
        print(f"[Serve] Error listando directorio: {ex}")

    candidates = []
    if path:
        candidates.append(os.path.join(BUILD_DIR, path))
        candidates.append(os.path.join(BUILD_DIR, path + ".html"))
        candidates.append(os.path.join(BUILD_DIR, path, "index.html"))

    candidates.append(os.path.join(BUILD_DIR, "index.html"))

    for c in candidates:
        exists = os.path.isfile(c)
        print(f"[Serve] Probando candidato: {c} -> Existe: {exists}")
        if exists:
            return FileResponse(c)

    return HTMLResponse(f"<h1>404 — Not Found</h1><p>Buscando ruta: '{path}' en {BUILD_DIR}</p>", status_code=404)

# ── 3. Rutas Starlette ────────────────────────────────────────────────────────
routes = list(reflex_routes)

# Servir assets y client si existen
assets_dir = os.path.join(BUILD_DIR, "assets")
if os.path.isdir(assets_dir):
    print("[Server] Registrando /assets de frontend")
    routes.append(Mount("/assets", app=StaticFiles(directory=assets_dir), name="assets"))

client_dir = os.path.join(BUILD_DIR, "client")
if os.path.isdir(client_dir):
    print("[Server] Registrando /client de frontend")
    routes.append(Mount("/client", app=StaticFiles(directory=client_dir), name="client"))

# Catch-all
routes.append(Route("/{path:path}", endpoint=serve_page))
routes.append(Route("/", endpoint=serve_page))

combined = Starlette(routes=routes)

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
