import os
import hashlib
import sqlite3
import time
import shutil
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# === Configuration ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WATCH_DIR = "/home/kali/"
ALLOWED_EXTENSIONS = {'.py', '.txt', '.docx', '.pdf', '.xlsx'}
CACHE_REFRESH_INTERVAL = 5  # seconds
DB_PATH = os.path.join(BASE_DIR, "hash_store.db")

# === Setup Logs ===
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

ALERT_LOG_FILE = os.path.join(LOG_DIR, "alerts_log.txt")
if not os.path.exists(ALERT_LOG_FILE):
    with open(ALERT_LOG_FILE, 'w') as f:
        f.write("")

# === Shared Sensitive Cache ===
sensitive_cache = {}

def refresh_sensitives():
    global sensitive_cache
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT hash_value, allowed_directory FROM sensitive_hashes")
            sensitive_cache = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.close()
            conn.close()
            print("[DEBUG] Sensitive hash DB cache refreshed.")
        except Exception as e:
            print(f"[ERROR] Cache refresh failed: {e}")
        time.sleep(CACHE_REFRESH_INTERVAL)

def sha3_256_of_file(path):
    h = hashlib.sha3_256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def log_alert(filepath, matched_hash, expected_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (
        f"[ALERT] File moved!\n"
        f"Time: {timestamp}\n"
        f"Path: {filepath}\n"
        f"Expected: {expected_path}\n"
        f"Hash: {matched_hash}\n\n"
    )
    try:
        with open(ALERT_LOG_FILE, "a") as f:
            f.write(msg)
        print(f"[ALERT] {filepath} violated expected directory. Logged.")
    except Exception as e:
        print(f"[ERROR] Failed to write alert: {e}")

class DLPHandler(FileSystemEventHandler):
    def is_ignored(self, path):
        abs_path = os.path.abspath(path)
        ignore_dirs = [
            LOG_DIR,
            os.path.join(BASE_DIR, "logs"),
            os.path.expanduser("~/.cache"),
            os.path.expanduser("~/.config"),
            BASE_DIR,
        ]
        return any(abs_path.startswith(d) for d in ignore_dirs)

    def check_file(self, path):
        abs_path = os.path.abspath(path)

        ext = os.path.splitext(abs_path)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            print(f"[DEBUG] Skipped non-sensitive extension: {abs_path}")
            return

        file_hash = sha3_256_of_file(abs_path)
        if not file_hash:
            return

        expected_path = sensitive_cache.get(file_hash)
        if not expected_path:
            return  # Not tracked

        expected_path = os.path.abspath(expected_path)
        real_dir = os.path.dirname(abs_path)
        filename = os.path.basename(abs_path)

        try:
            if not os.path.exists(expected_path):
                log_alert(abs_path, file_hash, expected_path)
            elif not os.path.samefile(real_dir, expected_path):
                log_alert(abs_path, file_hash, expected_path)
                target_path = os.path.join(expected_path, filename)
                if not os.path.exists(target_path):
                    shutil.move(abs_path, target_path)
                    print(f"[AUTO-CORRECT] Moved {filename} back to allowed path.")
                else:
                    os.remove(abs_path)
                    print(f"[AUTO-CORRECT] Duplicate {filename} removed.")
        except Exception as e:
            print(f"[ERROR] Handling file failed: {e}")

    def on_any_event(self, event):
        abs_path = os.path.abspath(
            getattr(event, 'dest_path', getattr(event, 'src_path', str(event)))
        )

        if self.is_ignored(abs_path):
            return

        ext = os.path.splitext(abs_path)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return

        print(f"[EVENT] {event.event_type.upper()}: {abs_path}")
        self.check_file(abs_path)

if __name__ == "__main__":
    print("[*] Watchdog starting...")
    threading.Thread(target=refresh_sensitives, daemon=True).start()
    print("[*] Monitoring started on", WATCH_DIR)

    observer = Observer()
    handler = DLPHandler()
    observer.schedule(handler, WATCH_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
