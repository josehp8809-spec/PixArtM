#!/usr/bin/env bash
# start.sh — Render production start script
#
# Arquitectura:
#   1. Reflex backend  → corre internamente en puerto 8080 (event processor, WebSocket, API)
#   2. server.py proxy → corre en $PORT (10000) sirviendo frontend + proxy al backend

export PATH="$PWD/node_bin/bin:$PATH"
export PORT=${PORT:-10000}
export REFLEX_BACKEND_PORT=8000

echo "[Start] Puerto público (Render): $PORT"
echo "[Start] Puerto interno (Reflex):  $REFLEX_BACKEND_PORT"

# ── 1. Iniciar Reflex backend en segundo plano (puerto interno 8080) ──────────
echo "[Start] Iniciando Reflex backend-only en puerto $REFLEX_BACKEND_PORT..."
python -m reflex run --backend-only --loglevel warning &
REFLEX_PID=$!

# ── 2. Esperar a que Reflex esté listo (health check) ────────────────────────
echo "[Start] Esperando que Reflex backend esté listo..."
MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s "http://localhost:$REFLEX_BACKEND_PORT/ping" > /dev/null 2>&1; then
        echo "[Start] Reflex backend listo! (${WAITED}s)"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "[Start] ADVERTENCIA: Reflex no respondió en ${MAX_WAIT}s, iniciando proxy de todas formas..."
fi

# ── 3. Iniciar el proxy + servidor de frontend en $PORT ───────────────────────
echo "[Start] Iniciando proxy+frontend en puerto $PORT..."
python server.py
