#!/usr/bin/env bash
# start.sh — Script de inicio para Render (producción)

# Configurar PATH con Node.js portátil instalado en el Build
export PATH="$PWD/node_bin/bin:$PATH"

if [ -z "$PORT" ]; then
  export PORT=10000
fi

echo "[Start] Puerto: $PORT"
echo "[Start] Iniciando Nyme con uvicorn (sin compilacion en caliente)..."

python server.py
