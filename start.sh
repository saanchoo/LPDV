#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  🎵  LPDV — La Playlist Del Vago"
echo ""

# ── Backend Flask ──────────────────────────────────────────
source "$ROOT/venv/bin/activate"
echo "  → Backend :  http://127.0.0.1:5000"
python "$ROOT/run.py" &
FLASK_PID=$!

sleep 1   # espera a que Flask esté listo

# ── Frontend Vite ──────────────────────────────────────────
echo "  → Frontend:  http://127.0.0.1:5173"
cd "$ROOT/frontend" && npm run dev &
VITE_PID=$!

echo ""
echo "  Ctrl+C para parar ambos servidores."
echo ""

# Al salir (Ctrl+C o cierre de terminal) mata los dos procesos
trap "echo ''; echo '  Deteniendo servidores...'; kill $FLASK_PID $VITE_PID 2>/dev/null; echo '  Listo.'" EXIT

wait
