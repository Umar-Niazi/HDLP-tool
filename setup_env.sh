#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# === CONFIG ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/dlp-venv"
REQ_FILE="$PROJECT_DIR/requirements.txt"
DB_MODULE="db"
LOG_DIR="$PROJECT_DIR/logs"

die() { echo "[ERROR] $*" >&2; exit 1; }

# 1. Check for python3
command -v python3 >/dev/null 2>&1 || die "python3 not found."

# 2. Create venv if missing
if [ -d "$VENV_DIR" ]; then
  echo "[*] Virtualenv already exists at $VENV_DIR"
else
  echo "[*] Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# 3. Activate and install deps
echo "[*] Activating venv…"
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

if [ -f "$REQ_FILE" ]; then
  echo "[*] Installing dependencies from requirements.txt"
  pip install --upgrade pip
  pip install -r "$REQ_FILE"
else
  die "requirements.txt missing—please create it first."
fi

# 4. Prepare logs folder
echo "[*] Ensuring logs directory exists…"
mkdir -p "$LOG_DIR"

# 5. Initialize SQLite DB via our db module
echo "[*] Initializing database (if needed)…"
python3 - <<EOF
import ${DB_MODULE}
${DB_MODULE}.init_db()
EOF

echo "[✔] Setup complete! You can now run ./start_services.sh"
