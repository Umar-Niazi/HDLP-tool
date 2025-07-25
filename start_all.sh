#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# === CONFIG ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/hdlp-venv"
LOG_DIR="$PROJECT_DIR/logs"
ALERT_LOG="$LOG_DIR/alerts_log.txt"

die() { echo "[ERROR] $*" >&2; exit 1; }

# 1. Activate venv
if [ -f "$VENV_DIR/bin/activate" ]; then
  echo "[*] Activating virtualenv…"
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
else
  die "Virtualenv not found—did you run setup_env.sh?"
fi

# 2. Clear old alerts log (but keep other logs)
echo "[*] Resetting alerts log…"
> "$ALERT_LOG"

# 3. Launch services
echo "[*] Starting Flask…"
python3 main.py >> "$LOG_DIR/flask.log" 2>&1 &
FLASK_PID=$!

echo "[*] Starting Watchdog…"
python3 watch_alerts.py >> "$LOG_DIR/watchdog.log" 2>&1 &
WATCHDOG_PID=$!

# 4. Graceful shutdown
trap 'echo "[*] Shutting down…"; kill $FLASK_PID $WATCHDOG_PID; exit 0' SIGINT SIGTERM

echo "[✔] Services running. PIDs: Flask=$FLASK_PID, Watchdog=$WATCHDOG_PID"
echo "    Press Ctrl+C to stop."
wait
