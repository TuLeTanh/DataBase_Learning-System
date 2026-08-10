import sys
import requests
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

queries = [
    "Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?",
    "So sánh UNION và UNION ALL trong SQL",
    "Cho ví dụ về vi phạm dạng chuẩn BCNF",
    "Transaction là gì và ACID gồm những gì",
    "asdkjaskjd",
    "làm sao để cài đặt MySQL trên Windows",
    "MongoDB lưu trữ dữ liệu dưới dạng nào?",
    "Làm thế nào để sử dụng phpMyAdmin quản lý database?",
    "Cấu hình Replica Set trong cơ sở dữ liệu phân tán",
    "Giải thích khái niệm Eventual Consistency trong NoSQL."
]

BASE_URL = "http://localhost:8000"

with open("test_report_q3_fix.md", "w", encoding="utf-8") as f:
    f.write("# BÁO CÁO KẾT QUẢ TEST 10 CÂU QUA API\n\n")

for i, q in enumerate(queries):
    print(f"Testing Q{i+1}: {q}")
    res = requests.post(f"{BASE_URL}/api/sessions")
    if res.status_code != 200:
        print("Failed to create session")
        continue
    session_id = res.json()["session_id"]
    
    data = {
        "session_id": session_id,
        "question": q
    }
    # It is multipart/form-data
    res = requests.post(f"{BASE_URL}/api/ask", data=data)
    if res.status_code == 200:
        ans = res.json()["answer"]
    else:
        ans = f"Error: {res.status_code} {res.text}"
    
    print(ans[:50] + "...")
    with open("test_report_q3_fix.md", "a", encoding="utf-8") as f:
        f.write(f"## Câu {i+1}: {q}\n")
        f.write(f"**Kết quả LLM:**\n")
        f.write(ans + "\n\n")
    
    time.sleep(1)

print("Finished!")
