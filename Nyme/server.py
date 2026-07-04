"""
server.py — Servidor de producción para Render.

Usa un middleware ASGI que envuelve la app de Reflex sin modificarla,
preservando su lifespan y event processor, mientras sirve el frontend
estático compilado para todas las rutas no-Reflex.
"""
import os, sys, mimetypes
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import FileResponse, Response

# ── 1. Importar la app de Reflex (preserva lifespan + event processor) ────────
from nyme.nyme import app as reflex_app
reflex_asgi = reflex_app._api

# ── 2. Directorio del frontend compilado ──────────────────────────────────────
BASE      = os.path.dirname(__file__)
BUILD_DIR = os.path.join(BASE, ".web", "build", "client")

print(f"[Server] BUILD_DIR = {BUILD_DIR}")
print(f"[Server] BUILD_DIR existe: {os.path.isdir(BUILD_DIR)}")

# Rutas internas de Reflex que deben pasarse directamente al backend
REFLEX_PREFIXES = ("/ping", "/_health", "/_event", "/webhook", "/backend", "/upload")

# ── 3. Middleware ASGI que sirve el frontend estático ─────────────────────────
class FrontendMiddleware:
    """
    Middleware ASGI que:
    - Rutas de Reflex  → pasan directo al backend de Reflex
    - WebSocket        → pasan directo al backend de Reflex
    - Todo lo demás    → sirve archivos estáticos del frontend compilado
    """

    def __init__(self, app: ASGIApp, build_dir: str) -> None:
        self.app = app
        self.build_dir = build_dir

    def _is_reflex_route(self, path: str) -> bool:
        for prefix in REFLEX_PREFIXES:
            if path == prefix or path.startswith(prefix + "/"):
                return True
        return False

    async def _serve_static(self, path: str, scope: Scope, receive: Receive, send: Send) -> bool:
        """Intenta servir un archivo estático. Retorna True si lo sirvió."""
        rel = path.lstrip("/")
        candidates = []
        if rel:
            candidates.append(os.path.join(self.build_dir, rel))
            candidates.append(os.path.join(self.build_dir, rel + ".html"))
            candidates.append(os.path.join(self.build_dir, rel, "index.html"))

        # Fallback SPA
        candidates.append(os.path.join(self.build_dir, "__spa-fallback.html"))
        candidates.append(os.path.join(self.build_dir, "index.html"))

        for c in candidates:
            if os.path.isfile(c):
                response = FileResponse(c)
                await response(scope, receive, send)
                return True
        return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            # WebSocket siempre va al backend de Reflex
            await self.app(scope, receive, send)
            return

        if scope["type"] == "http":
            path = scope.get("path", "/")

            # Rutas internas de Reflex → backend
            if self._is_reflex_route(path):
                await self.app(scope, receive, send)
                return

            # Todo lo demás → intentar servir frontend estático
            served = await self._serve_static(path, scope, receive, send)
            if not served:
                # Último recurso: dejar que Reflex responda (dará 404 interno)
                await self.app(scope, receive, send)
            return

        # Otros tipos (lifespan, etc.) → Reflex los maneja
        await self.app(scope, receive, send)

# ── 4. Construir la app final ─────────────────────────────────────────────────
final_app = FrontendMiddleware(reflex_asgi, BUILD_DIR)

# ── 5. Arrancar uvicorn ───────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"[Server] Nyme iniciando en http://0.0.0.0:{port}")
    uvicorn.run(
        final_app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
