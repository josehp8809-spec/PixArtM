"""
server.py — Proxy + Frontend estático para Render con depuración WebSocket.
"""
import os, sys, asyncio
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
import httpx
from starlette.applications import Starlette
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, HTMLResponse, Response
from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

# ── Configuración ──────────────────────────────────────────────────────────────
REFLEX_PORT  = int(os.getenv("REFLEX_BACKEND_PORT", "8000"))
REFLEX_HTTP  = f"http://localhost:{REFLEX_PORT}"
REFLEX_WS    = f"ws://localhost:{REFLEX_PORT}"
BASE         = os.path.dirname(__file__)
BUILD_DIR    = os.path.join(BASE, ".web", "build", "client")

print(f"[Server] Configurado para conectar al backend en: {REFLEX_HTTP}")
print(f"[Server] Configurado para conectar WS en: {REFLEX_WS}")
print(f"[Server] Frontend build: {BUILD_DIR} → existe: {os.path.isdir(BUILD_DIR)}")

# ── 1. Proxy HTTP ─────────────────────────────────────────────────────────────
async def proxy_http(request: Request) -> Response:
    path  = request.url.path
    query = str(request.url.query)
    url   = f"{REFLEX_HTTP}{path}" + (f"?{query}" if query else "")
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "content-length")}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method, url=url,
                headers=headers, content=await request.body(),
            )
            return Response(content=resp.content, status_code=resp.status_code,
                            headers=dict(resp.headers))
    except Exception as e:
        print(f"[HTTP Proxy] Error conectando a {url}: {e}")
        return Response(content=f"Proxy error: {e}", status_code=502)

# ── 2. Proxy WebSocket ────────────────────────────────────────────────────────
async def proxy_websocket(websocket: WebSocket):
    """Reenvía conexiones WebSocket al backend de Reflex de manera robusta."""
    import websockets
    await websocket.accept()

    path  = websocket.url.path
    query = str(websocket.url.query) if websocket.url.query else ""
    ws_url = f"{REFLEX_WS}{path}" + (f"?{query}" if query else "")
    
    print(f"[WS Proxy] Nueva conexion cliente. Reenviando a backend: {ws_url}")

    # No pasar cabeceras de WebSocket del navegador directo para evitar problemas de handshakes
    headers = []
    for k, v in websocket.headers.items():
        k_lower = k.lower()
        if k_lower not in (
            "host", "connection", "upgrade", "sec-websocket-key", 
            "sec-websocket-version", "sec-websocket-extensions", "sec-websocket-protocol"
        ):
            headers.append((k, v))

    try:
        async with websockets.connect(ws_url, additional_headers=headers) as backend:
            print("[WS Proxy] Conexion establecida con el backend de Reflex.")

            async def client_to_backend():
                try:
                    async for msg in websocket.iter_text():
                        await backend.send(msg)
                except WebSocketDisconnect:
                    print("[WS Proxy] Cliente se desconecto (WebSocketDisconnect).")
                except Exception as ex:
                    print(f"[WS Proxy] Error en canal cliente -> backend: {ex}")

            async def backend_to_client():
                try:
                    async for msg in backend:
                        if websocket.client_state == WebSocketState.CONNECTED:
                            text = msg if isinstance(msg, str) else msg.decode("utf-8", errors="replace")
                            await websocket.send_text(text)
                except Exception as ex:
                    print(f"[WS Proxy] Error en canal backend -> cliente: {ex}")

            # Ejecutar ambos bucles en paralelo hasta que uno termine o falle
            await asyncio.gather(client_to_backend(), backend_to_client())
            
    except Exception as e:
        print(f"[WS Proxy] ERROR CONECTANDO AL BACKEND: {e}")
    finally:
        print("[WS Proxy] Cerrando conexion websocket con el cliente.")
        try:
            await websocket.close()
        except Exception:
            pass

# ── 3. Frontend estático ───────────────────────────────────────────────────────
async def serve_page(request: Request) -> Response:
    path = request.path_params.get("path", "").strip("/")
    candidates = []
    if path:
        candidates += [
            os.path.join(BUILD_DIR, path),
            os.path.join(BUILD_DIR, path + ".html"),
            os.path.join(BUILD_DIR, path, "index.html"),
        ]
    candidates += [
        os.path.join(BUILD_DIR, "__spa-fallback.html"),
        os.path.join(BUILD_DIR, "index.html"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return FileResponse(c)
    return HTMLResponse("<h1>Not Found</h1>", status_code=404)

# ── 4. Rutas ────────────────────────────────────────────────────────────────────
routes = [
    Route("/ping",     endpoint=proxy_http, methods=["GET", "HEAD"]),
    Route("/_health",  endpoint=proxy_http, methods=["GET", "HEAD"]),
    Route("/webhook",  endpoint=proxy_http, methods=["GET", "POST"]),
    Route("/upload",   endpoint=proxy_http, methods=["GET", "POST"]),

    WebSocketRoute("/_event",            endpoint=proxy_websocket),
    WebSocketRoute("/_event/{path:path}", endpoint=proxy_websocket),
]

# Assets de Vite
assets_dir = os.path.join(BUILD_DIR, "assets")
if os.path.isdir(assets_dir):
    routes.append(Mount("/assets", app=StaticFiles(directory=assets_dir), name="assets"))

# SPA catch-all
routes += [
    Route("/{path:path}", endpoint=serve_page),
    Route("/",            endpoint=serve_page),
]

combined = Starlette(routes=routes)

# ── 5. Arrancar uvicorn ────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"[Server] Proxy+Frontend listo en puerto público: {port}")
    uvicorn.run(combined, host="0.0.0.0", port=port, log_level="info")
