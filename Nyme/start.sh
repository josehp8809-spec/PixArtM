#!/usr/bin/env bash
# start.sh — Script de inicio nativo para Render
#
# Ahora que usamos NativeFrontendMiddleware en nyme.py,
# no requerimos proxies. Todo corre sobre un único puerto público ($PORT).

export PATH="$PWD/node_bin/bin:$PATH"

if [ -z "$PORT" ]; then
  export PORT=10000
fi

echo "[Start] Iniciando Reflex en puerto único público: $PORT"
echo "[Start] Verificando compilación de producción..."

if [ -d ".web/build/client" ]; then
  echo "[Start] Frontend detectado en .web/build/client/. El middleware nativo lo servirá automáticamente."
else
  echo "[Start] ADVERTENCIA: No se encontró .web/build/client/. El frontend podría no cargar."
fi

# Correr el backend de Reflex en el puerto asignado.
# Como el backend es el que expone el puerto, el WebSocket /_event se conectará de inmediato y de forma nativa.
python -u -m reflex run --backend-only --loglevel info
