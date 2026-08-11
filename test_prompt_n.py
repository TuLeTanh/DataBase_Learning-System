import requests
import uuid
import os
import time

BASE_URL = "http://127.0.0.1:8000"
SANDBOX_DIR = os.path.join(os.path.dirname(__file__), "backend", "sandbox")

def print_result(name, result, expected):
    print(f"--- Test: {name} ---")
    print(f"Result: {result}")
    if expected in str(result):
        print("[PASS]\n")
    else:
        print("[FAIL]\n")

def run_query(session_id, query):
    res = requests.post(f"{BASE_URL}/api/sandbox/query", json={"session_id": session_id, "query": query})
    if res.status_code == 200:
        return res.json()["result"]
    else:
        return res.json()["detail"]

def create_session():
    res = requests.post(f"{BASE_URL}/api/sessions")
    return res.json()["session_id"]

def delete_session(session_id):
    requests.delete(f"{BASE_URL}/api/sessions/{session_id}")

print("==================== PROMPT N: SANDBOX TESTS ====================")

# 1. Data Isolation & DDL
s1 = create_session()
s2 = create_session()

res = run_query(s1, "CREATE TABLE SinhVien (ID INT PRIMARY KEY, Name TEXT)")
print_result("CREATE TABLE in S1", res, "rows_affected")

res = run_query(s1, "INSERT INTO SinhVien VALUES (1, 'Nguyen Van A')")
print_result("INSERT in S1", res, "rows_affected")

res = run_query(s2, "SELECT * FROM SinhVien")
print_result("SELECT from S2 (Isolation)", res, "no such table: SinhVien")

res = run_query(s1, "SELECT * FROM SinhVien")
print_result("SELECT from S1 (Persistence)", res, "Nguyen Van A")

# 2. DROP TABLE
res = run_query(s1, "DROP TABLE SinhVien")
print_result("DROP TABLE in S1", res, "rows_affected")
res = run_query(s1, "SELECT * FROM SinhVien")
print_result("Verify DROP TABLE", res, "no such table: SinhVien")

# 3. ATTACH DATABASE Block
res = run_query(s1, "ATTACH DATABASE '../chatbot.db' AS prod")
print_result("ATTACH DATABASE Block", res, "Operation not authorized")

# 4. PRAGMA foreign_keys whitelist
res = run_query(s1, "PRAGMA foreign_keys = ON")
print_result("PRAGMA foreign_keys Whitelist", res, "rows_affected")

res = run_query(s1, "PRAGMA journal_mode = WAL")
print_result("PRAGMA journal_mode Block (Not whitelisted)", res, "Operation not authorized")

# 5. Path traversal block
res = run_query("../chatbot.db", "SELECT 1")
print_result("Path traversal block on session_id", res, "Invalid session ID")

# 6. Timeout & Size Limit block (Infinite Loop via Recursive CTE)
res = run_query(s1, """
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x+1 FROM cnt
)
SELECT * FROM cnt;
""")
print_result("Timeout block (Recursive CTE)", res, "timed out")

# 7. Rollback on timeout check
# Create a table, insert one row
run_query(s1, "CREATE TABLE TestRollback (id INT)")
run_query(s1, "INSERT INTO TestRollback VALUES (1)")
# Start a huge insert that times out (wait, sqlite3 auto-commits each statement unless inside BEGIN)
# In python's sqlite3 driver, `execute()` usually auto starts a transaction. Let's do an INSERT with a recursive CTE.
res = run_query(s1, """
INSERT INTO TestRollback 
SELECT count(*) FROM (
    WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM c LIMIT 500)
    SELECT c1.x FROM c c1, c c2, c c3
);
""")
# It can hit size limit or timeout
db_size = os.path.getsize(os.path.join(SANDBOX_DIR, f"{s1}.db"))
if "timed out" in str(res):
    print("--- Test: Timeout-only test (CPU-bound, no disk limit hit) ---")
    print("Result: Blocked by Timeout (> 2s)")
    print(f"Sandbox DB size at block: {db_size} bytes (limit is 5MB)")
    print("[PASS]\n")
else:
    print("--- Test: Timeout-only test (CPU-bound, no disk limit hit) ---")
    print(f"Result: {res}")
    print("[FAIL]\n")

# Verify rollback - it should only have 1 row
res = run_query(s1, "SELECT COUNT(*) as c FROM TestRollback")
print("--- Test: Rollback on timeout check ---")
print(f"Result: {res} (Expected: 1 row, meaning 0 new rows inserted)")
if res == [{'c': 1}]:
    print("[PASS]\n")
else:
    print("[FAIL]\n")

# 8. Lifecycle cleanup check
s3 = create_session()
db_file = os.path.join(SANDBOX_DIR, f"{s3}.db")
run_query(s3, "CREATE TABLE A (id INT)")
if os.path.exists(db_file):
    print(f"--- Test: Lifecycle DB created --- \nResult: Exists\n[PASS]\n")
else:
    print(f"--- Test: Lifecycle DB created --- \nResult: Missing\n[FAIL]\n")

delete_session(s3)
if not os.path.exists(db_file):
    print(f"--- Test: Lifecycle DB deleted on Session Delete --- \nResult: Deleted\n[PASS]\n")
else:
    print(f"--- Test: Lifecycle DB deleted on Session Delete --- \nResult: Still Exists\n[FAIL]\n")

print("=================================================================")
