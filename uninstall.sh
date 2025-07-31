#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# === CONFIG ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$PROJECT_DIR")"
PROJECT_NAME="$(basename "$PROJECT_DIR")"
VENV_DIR="$PROJECT_DIR/dlp-venv"
LOG_DIR="$PROJECT_DIR/logs"
DB_FILE="$PROJECT_DIR/hash_store.db"

# If you pass -y or --yes, skip the final confirmation
FORCE=false
if [[ "${1-:-}" =~ ^(-y|--yes)$ ]]; then
  FORCE=true
fi

echo "=== DLP-Tool Uninstall ==="
echo

# 1) Stop services (no prompt)
PIDS=$(pgrep -f "python3 app\.py|python3 watcher\.py" || true)
if [[ -n "$PIDS" ]]; then
  echo "[*] Stopping running services: $PIDS"
  kill $PIDS
  echo "[✔] Services stopped."
else
  echo "[✔] No running services found."
fi

# 2) Remove venv, logs, DB (no prompts)
if rm -rf "$VENV_DIR"; then
  echo "[✔] Virtualenv removed."
else
  echo "[✔] No virtualenv to remove."
fi

if rm -rf "$LOG_DIR"; then
  echo "[✔] Logs directory removed."
else
  echo "[✔] No logs directory to remove."
fi

if rm -f "$DB_FILE"; then
  echo "[✔] Database file removed."
else
  echo "[✔] No database file to remove."
fi

# 3) Verify we’re in the right folder
echo
echo "[*] Verifying project directory contents..."
for marker in start_services.sh setup_env.sh app.py watcher.py requirements.txt; do
  if [[ ! -e "$PROJECT_DIR/$marker" ]]; then
    echo "[ERROR] Missing expected file: $marker"
    echo "        This doesn’t look like the DLP project root. Aborting."
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
