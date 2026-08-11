import sqlite3
import os
import uuid
import time
import logging
from typing import List, Dict, Any, Tuple

SANDBOX_DIR = os.path.join(os.path.dirname(__file__), "sandbox")
if not os.path.exists(SANDBOX_DIR):
    os.makedirs(SANDBOX_DIR)

# Whitelisted PRAGMAs
WHITELISTED_PRAGMAS = {
    "foreign_keys",
    "table_info",
    "index_list",
    "index_info",
    "page_size",
    "max_page_count"
}

def is_valid_session_id(session_id: str) -> bool:
    try:
        val = uuid.UUID(session_id, version=4)
        return True
    except ValueError:
        return False

def get_sandbox_db_path(session_id: str) -> str:
    if not is_valid_session_id(session_id):
        raise ValueError("Invalid session ID format")
    # This prevents any path traversal because we strictly enforce UUID format.
    return os.path.join(SANDBOX_DIR, f"{session_id}.db")

def authorizer_callback(action, arg1, arg2, dbname, source):
    # action codes in sqlite3
    # sqlite3.SQLITE_ATTACH is 24
    # sqlite3.SQLITE_PRAGMA is 19
    if action == 24: # SQLITE_ATTACH
        return sqlite3.SQLITE_DENY
    if action == 19: # SQLITE_PRAGMA
        if arg1.lower() not in WHITELISTED_PRAGMAS:
            return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK

class TimeoutException(Exception):
    pass

def execute_sandbox_query(session_id: str, query: str) -> Tuple[bool, Any]:
    """
    Executes a query in the sandbox DB for the given session_id.
    Returns (success: bool, result_or_error: List[Dict] or str)
    """
    db_path = get_sandbox_db_path(session_id)
    
    # Update modified time if file exists, else it will be created
    if os.path.exists(db_path):
        os.utime(db_path, None)

    conn = sqlite3.connect(db_path)
    
    # 1. Authorizer
    conn.set_authorizer(authorizer_callback)
    
    # 2. Timeout (2 seconds)
    start_time = time.time()
    def progress_handler():
        if time.time() - start_time > 2.0:
            return 1 # Non-zero aborts the operation
        return 0
    
    # Call progress handler every 1000 VM instructions
    conn.set_progress_handler(progress_handler, 1000)

    try:
        cursor = conn.cursor()
        
        # Enforce size limits (5MB = 4096 * 1250)
        cursor.execute("PRAGMA page_size = 4096")
        cursor.execute("PRAGMA max_page_count = 1250")
        
        # Start a transaction so we can rollback if a timeout occurs
        # Note: If the query itself contains COMMIT/ROLLBACK, it might mess with this,
        # but that's standard SQL behavior.
        
        # We don't explicitly BEGIN if the query is DDL, but sqlite3 Python module 
        # normally auto-starts transactions for DML. Let's let the driver handle it,
        # or we just rely on conn.rollback() in the except block.
        
        # Actually, to prevent partial execution if multiple statements are provided,
        # we can execute script, but executescript doesn't return rows.
        # We will split or just let users execute one statement at a time.
        # But SQLite handles multiple statements in execute() if separated by semicolon? No, execute() only allows one statement.
        # Let's use execute() to allow returning rows. Wait, if they want to insert, execute() works.
        # We should allow multiple statements. 
        # Actually, if we use executescript(), we can't get result sets.
        # If we use cursor.execute(), they can only run one statement. 
        # If we want to support multiple statements and return the result of the last one,
        # we need to parse or use SQLite's C API (not easy).
        # Let's just use cursor.execute(). If they want to do multiple, they can do them sequentially from the UI.
        # Wait, if they run `INSERT ...; SELECT ...`, Python's cursor.execute() throws a Warning or Error.
        # Let's use `executescript` if they don't expect rows, but they usually want to see SELECT results.
        # In a sandbox UI, we can split queries by ';' if needed, or just let them run one query at a time.
        
        cursor.execute(query)
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return True, result
        else:
            conn.commit()
            return True, {"rows_affected": cursor.rowcount}
            
    except Exception as e:
        # Rollback on any error, including timeout (OperationalError: interrupted)
        conn.rollback()
        err_msg = str(e)
        if "interrupted" in err_msg.lower():
            return False, "Query execution timed out (> 2s)."
        elif "not authorized" in err_msg.lower():
            return False, "Operation not authorized (Guardrail blocked)."
        return False, err_msg
    finally:
        conn.close()

def delete_sandbox_db(session_id: str):
    try:
        db_path = get_sandbox_db_path(session_id)
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception as e:
        logging.error(f"Failed to delete sandbox DB for {session_id}: {e}")

def cleanup_stale_sandboxes(max_age_days: int = 1):
    """Deletes sandbox DB files older than max_age_days."""
    try:
        now = time.time()
        for filename in os.listdir(SANDBOX_DIR):
            if not filename.endswith(".db"):
                continue
            filepath = os.path.join(SANDBOX_DIR, filename)
            mtime = os.path.getmtime(filepath)
            age_days = (now - mtime) / (24 * 3600)
            if age_days > max_age_days:
                os.remove(filepath)
                logging.info(f"Cleaned up stale sandbox DB: {filename}")
    except Exception as e:
        logging.error(f"Error cleaning up sandboxes: {e}")
