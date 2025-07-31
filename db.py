import sqlite3
from contextlib import contextmanager
from config import DB_PATH

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.commit()
    conn.close()

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sensitive_hashes (
          id               INTEGER PRIMARY KEY AUTOINCREMENT,
          filename         TEXT    NOT NULL,
          hash_value       TEXT    UNIQUE NOT NULL,
          hash_type        TEXT    NOT NULL,
          allowed_directory TEXT   NOT NULL,
          created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_hash ON sensitive_hashes(hash_value)
        """)

def add_or_replace_sensitive(filename, hash_value, hash_type, allowed_directory):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO sensitive_hashes
          (filename, hash_value, hash_type, allowed_directory)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(hash_value) DO UPDATE SET
          filename = excluded.filename,
          allowed_directory = excluded.allowed_directory
        """, (filename, hash_value, hash_type, allowed_directory))

def delete_sensitive(id_):
    with get_conn() as conn:
        conn.execute("DELETE FROM sensitive_hashes WHERE id = ?", (id_,))

def list_sensitives():
    with get_conn() as conn:
        return conn.execute("""
          SELECT * FROM sensitive_hashes
          ORDER BY created_at DESC
        """).fetchall()
        
def update_filename(hash_value, new_filename):
    with get_conn() as conn:
        conn.execute("""
        UPDATE sensitive_hashes
        SET filename = ?
        WHERE hash_value = ?
        """, (new_filename, hash_value))