#!/usr/bin/env bash
# start.sh — Script de inicio para Render

# Configurar PATH con Node.js instalado durante el Build
export PATH="$PWD/node_bin/bin:$PATH"

if [ -z "$PORT" ]; then
  export PORT=10000
fi

echo "[Start] Puerto: $PORT"
echo "[Start] Verificando frontend compilado..."

if [ -d ".web/build/client" ]; then
  echo "[Start] Frontend encontrado en .web/build/client/ OK"
  ls .web/build/client/ | head -5
else
  echo "[Start] ADVERTENCIA: .web/build/client/ no existe"
fi

echo "[Start] Iniciando Reflex backend-only..."
python -m reflex run --backend-only --loglevel info
