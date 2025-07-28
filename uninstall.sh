#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# === CONFIG ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$PROJECT_DIR")"
PROJECT_NAME="$(basename "$PROJECT_DIR")"
VENV_DIR="$PROJECT_DIR/hdlp-venv"
LOG_DIR="$PROJECT_DIR/logs"
DB_FILE="$PROJECT_DIR/hash_store.db"

# If you pass -y or --yes, skip the final confirmation
FORCE=false
if [[ "${1-}" =~ ^(-y|--yes)$ ]]; then
  FORCE=true
fi

echo "=== HDLP-Tool Uninstall ==="
echo

# 1) Stop services (no prompt)
PIDS=$(pgrep -f "python3 main\.py|python3 watch_alerts\.py" || true)
if [[ -n "$PIDS" ]]; then
  echo "[*] Stopping running services: $PIDS"
  kill $PIDS
  echo "[✔] Services stopped."
else
  echo "[✔] No running services found."
fi

# 2) Remove venv, logs, DB (no prompts)
rm -rf "$VENV_DIR" && echo "[✔] Virtualenv removed." || echo "[✔] No virtualenv to remove."
rm -rf "$LOG_DIR" && echo "[✔] Logs directory removed." || echo "[✔] No logs directory to remove."
rm -f "$DB_FILE" && echo "[✔] Database file removed." || echo "[✔] No database file to remove."

# 3) Verify we’re really in the right folder
echo
echo "[*] Verifying project directory contents..."
for marker in start_services.sh setup_env.sh main.py watch_alerts.py requirements.txt; do
  if [[ ! -e "$PROJECT_DIR/$marker" ]]; then
    echo "[ERROR] Missing expected file: $marker"
    echo "        This doesn’t look like the HDLP project root. Aborting."
    exit 1
  fi
done
echo "[✔] Marker files OK."

# 4) Final prompt (unless -y or --yes)
if ! $FORCE; then
  echo
  echo "About to permanently delete this entire directory:"
  echo "    $PROJECT_DIR"
  echo
  read -r -p "Proceed? (Y/N): " RESPONSE
  if [[ ! "$RESPONSE" =~ ^[Yy]$ ]]; then
    echo "[!] Aborted—no changes made."
    exit 0
  fi
fi

# 5) Do the delete
echo
echo "[*] Deleting project directory..."
cd "$PARENT_DIR"
rm -rf "$PROJECT_NAME"
echo "[✔] Project directory '$PROJECT_NAME' removed."

exit 0
