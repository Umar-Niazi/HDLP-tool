import os, time, threading, hashlib, shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import config, db

# Shared cache
_sensitive_cache = {}
_cache_lock = threading.Lock()

def refresh_cache_periodically():
    while True:
        with _cache_lock:
            rows = db.list_sensitives()
            _s = {r['hash_value']: (r['allowed_directory'], r['filename']) for r in rows}
            _sensitive_cache.clear()
            _sensitive_cache.update(_s)
        time.sleep(config.CACHE_REFRESH_SEC)

def hash_file(path):
    h = hashlib.new(config.HASH_TYPE)
    try:
        # Skip symbolic links and special files
        if os.path.islink(path) or not os.path.isfile(path):
            return None
            
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"Hash error: {e}")
        return None

class DLPHandler(FileSystemEventHandler):
    def __init__(self, alert_cb):
        self.alert_cb = alert_cb

    def process(self, path):
        # Skip directories and invalid files
        if not os.path.isfile(path) or os.path.islink(path):
            return
            
        # Skip unsupported extensions
        if os.path.splitext(path)[1].lower() not in config.ALLOWED_EXTENSIONS:
            return

        # Compute file hash
        file_hash = hash_file(path)
        if not file_hash:
            return

        with _cache_lock:
            sensitive_info = _sensitive_cache.get(file_hash)
            
        if not sensitive_info:
            return  # File not in tracking DB

        allowed_dir, original_filename = sensitive_info
        allowed_dir_abs = os.path.abspath(allowed_dir)
        current_dir_abs = os.path.dirname(os.path.abspath(path))
        original_path = os.path.join(allowed_dir_abs, original_filename)

        # Check if file is in allowed location (or subdirectory)
        if current_dir_abs == allowed_dir_abs or current_dir_abs.startswith(allowed_dir_abs + os.sep):
            return  # File is in permitted location
            
        # Check if original still exists
        original_exists = os.path.exists(original_path)
        action = "COPY" if original_exists else "MOVE"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate specific alert message
        alert_msg = (
            f"[{timestamp}] SECURITY ALERT: {original_filename} "
            f"was {action.lower()}ed to {path}. "
            f"Action taken: {'Deleted copy' if action == 'COPY' else 'Restored to secure location'}"
        )
        
        # Log to file
        logfile = os.path.join(config.LOG_DIR, 'alerts_log.txt')
        with open(logfile, 'a') as f:
            f.write(alert_msg + "\n\n")
            
        # Send real-time alert
        self.alert_cb(alert_msg)
        
        # Take appropriate action
        if action == "COPY":
            # Delete unauthorized copy
            try:
                os.remove(path)
            except Exception as e:
                error_msg = f"[{timestamp}] DELETE FAILED: {path} - {str(e)}"
                with open(logfile, 'a') as f:
                    f.write(error_msg + "\n\n")
                self.alert_cb(error_msg)
        else:  # MOVE action
            # Restore with conflict resolution
            restore_path = original_path
            counter = 1
            while os.path.exists(restore_path):
                base, ext = os.path.splitext(original_filename)
                restore_filename = f"{base}_{counter}{ext}"
                restore_path = os.path.join(allowed_dir_abs, restore_filename)
                counter += 1
                
            try:
                shutil.move(path, restore_path)
                
                # Update DB if filename changed
                if counter > 1:
                    db.update_filename(file_hash, os.path.basename(restore_path))
            except Exception as e:
                error_msg = f"[{timestamp}] RESTORE FAILED: {path} → {restore_path} - {str(e)}"
                with open(logfile, 'a') as f:
                    f.write(error_msg + "\n\n")
                self.alert_cb(error_msg)

    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.process(event.dest_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.process(event.src_path)

def start_watcher(alert_callback):
    # Ensure DB & logs exist
    db.init_db()
    os.makedirs(config.LOG_DIR, exist_ok=True)
    open(os.path.join(config.LOG_DIR, 'alerts_log.txt'), 'a').close()

    # Cache refresher
    threading.Thread(target=refresh_cache_periodically, daemon=True).start()

    # Watchdog observer
    obs = Observer()
    obs.schedule(DLPHandler(alert_callback), config.HOME_DIR, recursive=True)
    obs.start()