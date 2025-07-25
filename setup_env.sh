#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# === CONFIG ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/hdlp-venv"
REQ_FILE="$PROJECT_DIR/requirements.txt"
DB_FILE="$PROJECT_DIR/hash_store.db"
LOG_DIR="$PROJECT_DIR/logs"

# === HELPERS ===
die() { echo "[ERROR] $*" >&2; exit 1; }

# 1. Check for python3
command -v python3 >/dev/null 2>&1 || die "python3 not found."

# 2. Create venv
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
echo "[*] Creating logs directory…"
mkdir -p "$LOG_DIR"

# 5. Create SQLite DB
if [ -f "$DB_FILE" ]; then
  echo "[*] Database already exists at $DB_FILE"
else
  echo "[*] Initializing SQLite DB…"
  python3 - <<EOF
import sqlite3
conn = sqlite3.connect("$DB_FILE")
conn.execute("""
  CREATE TABLE sensitive_hashes (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    hash_value TEXT NOT NULL,
    hash_type TEXT NOT NULL,
    allowed_directory TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
""")
conn.commit()
conn.close()
EOF
  echo "[+] Database created."
fi

echo "[✔] Setup complete! You can now run ./start_services.sh"
