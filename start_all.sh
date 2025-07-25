#!/bin/bash

# === Setup ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$HOME/hdlp-env"
LOG_DIR="$PROJECT_DIR/logs"
DB_FILE="$PROJECT_DIR/hash_store.db"
ALERT_LOG="$LOG_DIR/alerts_log.txt"

echo "[*] Activating virtual environment..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "[ERROR] Virtual environment not found at $VENV_DIR"
    exit 1
fi

echo "[*] Cleaning up old logs in $LOG_DIR..."
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR"/*.txt
touch "$ALERT_LOG"
echo "[*] Logs cleaned."

# === Setup SQLite DB if missing ===
if [ ! -f "$DB_FILE" ]; then
    echo "[*] Creating SQLite DB at $DB_FILE..."
    python3 - <<EOF
import sqlite3
conn = sqlite3.connect("$DB_FILE")
cursor = conn.cursor()
cursor.execute(\"""
    CREATE TABLE sensitive_hashes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        hash_value TEXT NOT NULL,
        hash_type TEXT NOT NULL,
        allowed_directory TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
\""\")
conn.commit()
conn.close()
EOF
    echo "[+] SQLite DB initialized."
else
    echo "[*] SQLite DB already exists at $DB_FILE"
fi

# === Start Flask ===
echo "[*] Starting Flask App..."
python3 main.py &
FLASK_PID=$!
echo "[+] Flask started with PID $FLASK_PID"

# === Start Watchdog ===
echo "[*] Starting Watchdog Monitor..."
python3 watch_alerts.py &
WATCHDOG_PID=$!
echo "[+] Watchdog started with PID $WATCHDOG_PID"

# === Graceful shutdown ===
trap 'echo "[*] Shutting down..."; kill $FLASK_PID $WATCHDOG_PID 2>/dev/null; exit 0' SIGINT SIGTERM

echo "[*] System running. Press Ctrl+C to stop both Flask and Watchdog."
wait
