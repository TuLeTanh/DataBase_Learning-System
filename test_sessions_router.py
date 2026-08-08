import requests
import json
import time
import os

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

def log_to_file(msg):
    with open('test_report_sessions.txt', 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

def send_message_with_retry(session_id, query, max_retries=5):
    payload = {
        "session_id": session_id,
        "question": query
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json=payload, timeout=60)
            if response.status_code == 429:
                wait_time = 15 * (attempt + 1)
                log_to_file(f"[System] Rate limited (429). Waiting {wait_time}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json().get("answer", "")
        except requests.exceptions.RequestException as e:
            wait_time = 15 * (attempt + 1)
            log_to_file(f"[System] API Error ({e}). Waiting {wait_time}s before retry {attempt+1}/{max_retries}...")
            time.sleep(wait_time)
            
    return "API ERROR: Mức thử lại tối đa đã vượt quá."

def run_tests():
    # Khởi tạo báo cáo
    with open('test_report_sessions.txt', 'w', encoding='utf-8') as f:
        f.write("")
        
    log_to_file("==================================================")
    log_to_file("PHẦN 1: CHẠY LẠI ĐẦY ĐỦ 10 TEST CŨ (VÉT CẠN, CÓ RETRY)")
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
        log_to_file(f"\n--- [TEST CŨ {i}] ---")
        log_to_file(f"User: {q}")
        log_to_file(f"Nhóm: {'Trong tài liệu' if in_doc else 'Ngoài tài liệu'}")
        
        # Tạo session độc lập cho từng câu hỏi test cũ
        session_res = requests.post(SESSION_URL)
        session_id = session_res.json().get("session_id")
        
        answer = send_message_with_retry(session_id, q) 
        
        answer_lower = answer.lower()
        first_part = answer_lower[:100]
        is_reject = "không đề cập" in first_part or "không chứa thông tin" in first_part or "không nhắc đến" in first_part or "không có thông tin" in first_part or "tài liệu môn học hiện tại không đề cập" in first_part or "tài liệu môn học không đề cập" in first_part
        
        is_pass = False
        if in_doc and not is_reject:
            is_pass = True
        elif not in_doc and is_reject:
            is_pass = True
            
        status = "PASS" if is_pass else "FAIL"
        
        log_to_file(f"Kết quả: {status}")
        log_to_file(f"Bot: {answer}")
        
        time.sleep(5) # Delay một chút trước câu tiếp theo

    log_to_file("\n==================================================")
    log_to_file("PHẦN 2: CHITCHAT / KÉM LIÊN QUAN")
    log_to_file("==================================================")
    
    chitchat_queries = [
        "Trời hôm nay nắng hay mưa?",
        "Hãy đếm từ 1 tới 100 cho tôi xem"
    ]
    
    # Tạo 1 session chung cho phần 2
    session_res = requests.post(SESSION_URL)
    session_id = session_res.json().get("session_id")
    
    for i, q in enumerate(chitchat_queries, 1):
        log_to_file(f"\n--- [TEST CHITCHAT {i}] ---")
        log_to_file(f"User: {q}")
        answer = send_message_with_retry(session_id, q)
        log_to_file(f"Bot: {answer}")
        time.sleep(5)
        
    print("Test complete. Báo cáo được lưu tại test_report_sessions.txt")

if __name__ == '__main__':
    run_tests()
