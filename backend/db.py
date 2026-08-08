import sqlite3
import uuid
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        attachments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
    )
    ''')
    
    # Check if attachments column exists (migration)
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    if "attachments" not in columns:
        cursor.execute("ALTER TABLE messages ADD COLUMN attachments TEXT")
    
    conn.commit()
    conn.close()

def create_session(title="New Chat"):
    session_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (id, title) VALUES (?, ?)", (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def get_all_sessions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at FROM sessions ORDER BY created_at DESC")
    sessions = [{"id": row[0], "title": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return sessions

def get_session_messages(session_id):
    import json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, attachments FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    
    messages = []
    for row in cursor.fetchall():
        msg = {"role": row[0], "text": row[1]}
        if row[2]:
            try:
                msg["attachments"] = json.loads(row[2])
            except:
                pass
        messages.append(msg)
        
    conn.close()
    return messages

def add_message(session_id, role, content, attachments_json=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (session_id, role, content, attachments) VALUES (?, ?, ?, ?)", (session_id, role, content, attachments_json))
    conn.commit()
    conn.close()

def update_session_title(session_id, title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Enable foreign keys for ON DELETE CASCADE
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

# Initialize database
init_db()
