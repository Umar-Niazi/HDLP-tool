#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# === CONFIG ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/dlp-venv"
LOG_DIR="$PROJECT_DIR/logs"
ALERT_LOG="$LOG_DIR/alerts_log.txt"
FLASK_HOST="0.0.0.0"
FLASK_PORT="5000"

die() { echo "[ERROR] $*" >&2; exit 1; }

# 1. Activate venv
if [ -f "$VENV_DIR/bin/activate" ]; then
  echo "[*] Activating virtualenv…"
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
else
  die "Virtualenv not found—did you run setup_env.sh?"
fi

# 2. Reset alerts log only
echo "[*] Clearing alerts log…"
> "$ALERT_LOG"

# 3. Launch Flask (which now also starts the watcher)
echo "[*] Starting Flask + Watcher…"
python3 app.py >> "$LOG_DIR/flask.log" 2>&1 &
APP_PID=$!

# 3a. Tell user where Flask is hosted
echo "[*] Flask app is now listening on http://${FLASK_HOST}:${FLASK_PORT}/"

# 4. Trap for graceful shutdown
trap 'echo "[*] Shutting down…"; kill $APP_PID; exit 0' SIGINT SIGTERM

echo "[✔] Service running. PID: $APP_PID"
echo "    Press Ctrl+C to stop."
wait
