import os

# === Paths & General ===
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
HOME_DIR           = os.path.expanduser("~")
UPLOAD_FOLDER      = os.path.join(BASE_DIR, "uploads")
LOG_DIR            = os.path.join(BASE_DIR, "logs")
DB_PATH            = os.path.join(BASE_DIR, "hash_store.db")

# === Hashing ===
HASH_TYPE          = "sha3_256"
ALLOWED_EXTENSIONS = {'.py','.txt','.docx','.pdf','.xlsx','.jpg','.png','.gif'}

# === Watcher & Polling ===
CACHE_REFRESH_SEC  = 3
ALERT_SSE_ROUTE    = '/alerts/stream'

# === Flask ===
FLASK_DEBUG        = True
FLASK_HOST         = "0.0.0.0"
FLASK_PORT         = 5000

# Ensure dirs exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
