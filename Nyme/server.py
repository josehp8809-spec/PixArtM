"""
server.py — Punto de entrada de producción para Render.

Arranca el backend de Reflex directamente con Uvicorn, sin compilar
el frontend en caliente. El frontend ya fue compilado en la fase de Build.
"""
import os
import sys

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn

# Importar la app de Reflex (esto carga el estado, páginas, etc.)
from nyme.nyme import app

# Obtener la aplicación ASGI interna de Reflex (FastAPI + Websockets)
fastapi_app = app._api

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"[Server] Iniciando Nyme en puerto {port}...")
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
