import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/ask"

def log_to_file(msg):
    with open('test_report_router.txt', 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

def send_message(session_messages, query):
    history = session_messages[-6:]
    payload = {
        "question": query,
        "history": history
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        answer = response.json().get("answer", "")
        
        session_messages.append({"role": "user", "text": query})
        session_messages.append({"role": "bot", "text": answer})
        
        return answer
    except Exception as e:
        return f"API ERROR: {str(e)}"

def run_tests():
    # Clear file
    with open('test_report_router.txt', 'w', encoding='utf-8') as f:
        f.write("")
        
    log_to_file("==================================================")
    log_to_file("PHẦN 1: MÔ PHỎNG HỘI THOẠI LIÊN TỤC (UI TEST)")
    log_to_file("==================================================")
    
    session_messages = []
    
    chat_queries = [
        "chào",
        "cơ sở dữ liệu là học cái gì",
        "m hãy tạo 1 bảng database và 1 số câu hỏi để t test thử đi",
        "m hãy giải 5 câu trên cho t đi",
        "5 câu m vừa hỏi đấy",
        "m tên là gì",
        "liệt kê các lệnh có trong sql"
    ]
    
    for i, q in enumerate(chat_queries, 1):
        log_to_file(f"\n--- [LƯỢT {i}] ---")
        log_to_file(f"User: {q}")
        
        answer = send_message(session_messages, q)
        
        log_to_file(f"Bot: {answer}")
        
        log_to_file(f"[System] Done Turn {i}. Sleeping for 5s to respect API limits...")
        time.sleep(5)

    log_to_file("\n==================================================")
    log_to_file("PHẦN 2: CHẠY LẠI 10 TEST CŨ (STATELESS - NO HISTORY)")
    log_to_file("==================================================")
    
    old_queries = [
        ("Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?", True),
        ("So sánh UNION và UNION ALL trong SQL", True),
        ("Cho ví dụ về vi phạm dạng chuẩn BCNF", True),
        ("Transaction là gì và ACID gồm những gì", True),
        ("asdkjaskjd", False),
        ("làm sao để cài đặt MySQL trên Windows", False),
        ("MongoDB lưu trữ dữ liệu dưới dạng nào?", False),
        ("Làm thế nào để sử dụng phpMyAdmin quản lý database?", False),
        ("Cấu hình Replica Set trong cơ sở dữ liệu phân tán", False),
        ("Giải thích khái niệm Eventual Consistency trong NoSQL", False)
    ]
    
    for i, (q, in_doc) in enumerate(old_queries, 1):
        log_to_file(f"\n--- [TEST CŨ] ---")
        log_to_file(f"User: {q}")
        log_to_file(f"Nhóm: {'Trong tài liệu' if in_doc else 'Ngoài tài liệu'}")
        
        answer = send_message([], q) 
        
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
        log_to_file(f"[System] Done Old Test {i}. Sleeping for 5s...")
        time.sleep(5)
        
    print("Test complete. Báo cáo được lưu tại test_report_router.txt")

if __name__ == '__main__':
    run_tests()
