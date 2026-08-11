import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

regression_queries = [
    "Làm sao để cài đặt MySQL trên Windows",
    "MongoDB lưu trữ dữ liệu dưới dạng nào?",
    "Làm thế nào để sử dụng phpMyAdmin quản lý database?",
    "Cấu hình Replica Set trong cơ sở dữ liệu phân tán",
    "Giải thích khái niệm Eventual Consistency trong NoSQL",
    "Cách tối ưu hóa index trên PostgreSQL"
]

all_pass = True

for q in regression_queries:
    session_res = requests.post(SESSION_URL)
    session_id = session_res.json().get("session_id")
    
    payload = {
        "session_id": session_id,
        "question": q
    }
    response = requests.post(API_URL, data=payload)
    if response.status_code == 200:
        answer = response.json().get("answer", "")
        answer_lower = answer.lower()
        if "không đề cập" in answer_lower or "không chứa thông tin" in answer_lower or "tài liệu môn học" in answer_lower:
            print(f"PASS: {q}")
        else:
            print(f"FAIL: {q}\nAnswer: {answer}")
            all_pass = False
    else:
        print(f"ERROR: {response.status_code} for {q}")
        all_pass = False

if all_pass:
    print("\nALL REGRESSION TESTS PASSED.")
else:
    print("\nSOME REGRESSION TESTS FAILED.")
    sys.exit(1)
