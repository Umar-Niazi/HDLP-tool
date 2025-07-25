from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, os, hashlib, shutil, subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
HASH_TYPE = 'sha3_256'
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
ALERT_LOG_FILE = os.path.join(LOG_DIR, "alerts_log.txt")
HOME_KALI = '/home/kali/'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Create alerts log file if missing ===
if not os.path.exists(ALERT_LOG_FILE):
    with open(ALERT_LOG_FILE, 'w') as f:
        pass

def get_db_connection():
    return sqlite3.connect("hash_store.db")

def generate_file_hash(filepath):
    hasher = hashlib.new(HASH_TYPE)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

@app.route('/delete/<int:hash_id>')
def delete_hash(hash_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sensitive_hashes WHERE id = ?", (hash_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        target_dir = request.form.get('directory')

        if not file or not target_dir:
            return "Missing file or directory", 400

        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        file_hash = generate_file_hash(temp_path)

        # Remove any duplicate files from other directories
        for root, dirs, files in os.walk(HOME_KALI):
            for f in files:
                try:
                    full_path = os.path.join(root, f)
                    if f == filename:
                        existing_hash = generate_file_hash(full_path)
                        if existing_hash == file_hash and not full_path.startswith(target_dir):
                            os.remove(full_path)
                except:
                    continue

        final_path = os.path.join(target_dir, filename)
        shutil.move(temp_path, final_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensitive_hashes WHERE hash_value = ?", (file_hash,))
        exists = cursor.fetchone()[0]

        if not exists:
            cursor.execute("""
                INSERT INTO sensitive_hashes (filename, hash_value, hash_type, allowed_directory)
                VALUES (?, ?, ?, ?)
            """, (filename, file_hash, HASH_TYPE, target_dir))
            conn.commit()

            try:
                subprocess.Popen(["python3", "generate_audit_rules.py"])
            except Exception as e:
                print(f"[ERROR] Failed to regenerate audit rules: {e}")

        else:
            cursor.execute("""
                UPDATE sensitive_hashes
                SET allowed_directory = ?
                WHERE hash_value = ?
            """, (target_dir, file_hash))
            conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sensitive_hashes")
    total_hashes = cursor.fetchone()[0]
    cursor.execute("""
        SELECT id, hash_value, hash_type, filename, allowed_directory, created_at 
        FROM sensitive_hashes ORDER BY created_at DESC
    """)
    hashes = cursor.fetchall()
    cursor.close()
    conn.close()

    dirs = [os.path.join(HOME_KALI, d) for d in os.listdir(HOME_KALI)
            if os.path.isdir(os.path.join(HOME_KALI, d))]

    return render_template('dashboard.html', total_hashes=total_hashes, hashes=hashes, directories=dirs)

@app.route('/get_alerts')
def get_alerts():
    alerts = []
    if os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, 'r') as f:
            alerts = f.read().strip().split("\n\n")
    return jsonify(alerts[::-1])

@app.route('/clear_alerts', methods=['POST'])
def clear_alerts():
    if os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, 'w') as f:
            f.truncate()
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(debug=True)
