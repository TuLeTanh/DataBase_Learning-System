import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/ask"

def log_to_file(msg):
    with open('test_report_router.txt', 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

def send_message(query):
    payload = {
        "question": query,
        "history": []
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=20)
        response.raise_for_status()
        return response.json().get("answer", "")
    except Exception as e:
        return f"API ERROR: {str(e)}"

def run_tests():
    old_queries = [
        ("Transaction là gì và ACID gồm những gì", True),
        ("asdkjaskjd", False),
        ("làm sao để cài đặt MySQL trên Windows", False),
        ("MongoDB lưu trữ dữ liệu dưới dạng nào?", False),
        ("Làm thế nào để sử dụng phpMyAdmin quản lý database?", False),
        ("Cấu hình Replica Set trong cơ sở dữ liệu phân tán", False),
        ("Giải thích khái niệm Eventual Consistency trong NoSQL", False)
    ]
    
    for i, (q, in_doc) in enumerate(old_queries, 4):
        log_to_file(f"Kết quả: FAIL (Timeout)") # just in case it crashes
        
        # actually, I'll rewrite the previous incomplete line
        # but it's okay, I'll just append
        log_to_file(f"\n--- [TEST CŨ - Tiếp tục] ---")
        log_to_file(f"User: {q}")
        log_to_file(f"Nhóm: {'Trong tài liệu' if in_doc else 'Ngoài tài liệu'}")
        
        answer = send_message(q) 
        
        answer_lower = answer.lower()
        first_part = answer_lower[:100]
        is_reject = "không đề cập" in first_part or "không chứa thông tin" in first_part or "không nhắc đến" in first_part or "không có thông tin" in first_part or "tài liệu môn học hiện tại không đề cập" in first_part
        
        is_pass = False
        if in_doc and not is_reject:
            is_pass = True
        elif not in_doc and is_reject:
            is_pass = True
            
        status = "PASS" if is_pass else "FAIL"
        
        log_to_file(f"Kết quả: {status}")
        log_to_file(f"Bot: {answer}")
        
        time.sleep(1)

if __name__ == '__main__':
    run_tests()
