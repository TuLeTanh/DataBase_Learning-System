import sqlite3

def get_stats():
    conn = sqlite3.connect('backend/chatbot.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages")
    messages = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sessions")
    sessions = c.fetchone()[0]
    conn.close()
    return sessions, messages

if __name__ == "__main__":
    s, m = get_stats()
    print(f"Sessions: {s}, Messages: {m}")
