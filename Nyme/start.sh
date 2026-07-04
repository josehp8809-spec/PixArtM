#!/usr/bin/env bash
# start.sh — Script de inicio para Render

# 1. Configurar el PATH para Node.js portátil
export PATH="$PWD/node_bin/bin:$PATH"

# Validar puerto
if [ -z "$PORT" ]; then
  export PORT=10000
fi

echo "[Start] Puerto detectado: $PORT"
echo "[Start] Iniciando backend de Reflex con --backend-only..."

# 2. Ejecutar únicamente el backend de Reflex en producción
python -m reflex run --backend-only --loglevel info
