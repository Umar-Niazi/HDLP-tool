#!/usr/bin/env python3
# app.py - Data Leak Prevention System

from flask import Flask, render_template, request, redirect, url_for, jsonify, stream_with_context, Response
from werkzeug.utils import secure_filename
import os, time, hashlib, shutil, queue, threading

import config
import db

# In-memory queue for Server-Sent Events
_alert_queue = queue.Queue()

app = Flask(__name__)
app.config.from_object(config)

# Initialize the database (creates tables if needed)
db.init_db()

def generate_file_hash(filepath):
    """Compute the hash of a file, handling errors gracefully."""
    try:
        hasher = hashlib.new(config.HASH_TYPE)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Hashing error on {filepath}: {e}")
        return None

def enqueue_alert(msg):
    """Push alert messages into the SSE queue."""
    _alert_queue.put(msg)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        target = request.form.get('selected_directory', '').strip()
        if not file or not target or not os.path.isdir(target):
            return "Invalid upload or directory", 400

        filename = secure_filename(file.filename)
        temp_path = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(temp_path)

        # Compute hash of uploaded file
        file_hash = generate_file_hash(temp_path)
        if not file_hash:
            os.remove(temp_path)
            return "Failed to hash uploaded file", 500

        final_path = os.path.join(target, filename)

        # Remove duplicates by scanning home directory safely
        for root, dirs, files in os.walk(config.HOME_DIR):
            for f in files:
                full_path = os.path.join(root, f)
                # Skip the temporary file and final destination
                if full_path == temp_path or full_path == final_path:
                    continue
                try:
                    if generate_file_hash(full_path) == file_hash:
                        os.remove(full_path)
                except (FileNotFoundError, PermissionError):
                    continue
                except Exception as e:
                    print(f"Error removing duplicate {full_path}: {e}")

        # Move the file into its allowed directory
        try:
            shutil.move(temp_path, final_path)
        except Exception as e:
            return f"Failed to move file: {e}", 500

        # Verify file exists after move
        if not os.path.exists(final_path):
            return "File save failed", 500

        # Store or update its record in the DB
        db.add_or_replace_sensitive(filename, file_hash, config.HASH_TYPE, target)

        # Give the watcher a moment to pick up changes
        time.sleep(config.CACHE_REFRESH_SEC)

        return redirect(url_for('dashboard'))

    # GET: render the dashboard
    sens = db.list_sensitives()
    return render_template(
        'dashboard.html',
        total_hashes=len(sens),
        hashes=sens,
        home_dir=config.HOME_DIR
    )

@app.route('/delete/<int:id_>')
def delete(id_):
    db.delete_sensitive(id_)
    return redirect(url_for('dashboard'))

@app.route('/get_directory_children')
def get_directory_children():
    path = request.args.get('path', '')
    # Security: Ensure path is within HOME_DIR
    if not os.path.isdir(path) or not os.path.abspath(path).startswith(os.path.abspath(config.HOME_DIR)):
        return jsonify([])
    try:
        children = [
            {"name": e, "path": os.path.join(path, e)}
            for e in os.listdir(path)
            if not e.startswith('.') and os.path.isdir(os.path.join(path, e))
        ]
        return jsonify(children)
    except Exception as e:
        print(f"Directory listing error: {e}")
        return jsonify([])

@app.route('/get_alerts')
def get_alerts():
    log_file = os.path.join(config.LOG_DIR, 'alerts_log.txt')
    if not os.path.exists(log_file):
        return jsonify([])
    with open(log_file) as f:
        blocks = f.read().strip().split("\n\n")
    return jsonify(blocks[::-1])

@app.route('/alerts')
def view_alerts():
    """New endpoint for viewing alerts in a web interface"""
    log_file = os.path.join(config.LOG_DIR, 'alerts_log.txt')
    if not os.path.exists(log_file):
        return render_template('alerts.html', alerts=[])
        
    with open(log_file) as f:
        alerts = [alert.strip() for alert in f.read().split("\n\n") if alert.strip()]
        
    return render_template('alerts.html', alerts=reversed(alerts))

@app.route(config.ALERT_SSE_ROUTE)
def stream_alerts():
    def event_stream():
        while True:
            msg = _alert_queue.get()
            yield f"data: {msg}\n\n"
    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')

@app.route('/clear_alerts', methods=['POST'])
def clear_alerts():
    log_file = os.path.join(config.LOG_DIR, 'alerts_log.txt')
    if os.path.exists(log_file):
        open(log_file, 'w').close()  # Truncate file
    return jsonify({'status': 'success'})

@app.route('/protected_files')
def protected_files():
    """Endpoint to show all protected files in full detail"""
    sens = db.list_sensitives()
    return render_template(
        'protected_files.html',
        total_hashes=len(sens),
        hashes=sens
    )

if __name__ == "__main__":
    from watcher import start_watcher
    # Launch the file watcher in a background thread
    start_watcher(enqueue_alert)
    # Start the Flask application
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )