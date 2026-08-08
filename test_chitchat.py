import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

def log_to_file(msg):
    with open('test_report_chitchat.txt', 'a', encoding='utf-8') as f:
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
                log_to_file(f"[System] Rate limited (429). Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json().get("answer", "")
        except requests.exceptions.RequestException as e:
            wait_time = 15 * (attempt + 1)
            log_to_file(f"[System] API Error ({e}). Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            
    return "API ERROR"

def run_tests():
    with open('test_report_chitchat.txt', 'w', encoding='utf-8') as f:
        f.write("")
        
    log_to_file("==================================================")
    log_to_file("PHẦN 1: MỞ RỘNG CHITCHAT BANK (14 CÂU)")
    log_to_file("==================================================")
    
    chitchat_categories = [
        ("1. Troll / Test", ["1+1 bằng mấy", "Mày có thông minh không"]),
        ("2. Than vãn", ["Môn này khó vãi, học dở quá", "Chán học ghê"]),
        ("3. Nghề nghiệp", ["Học CSDL ra làm gì?", "Lương DBA bao nhiêu?"]),
        ("4. Tổ chức lớp", ["Thầy dạy môn này có dễ không?", "Bao giờ thi?"]),
        ("5. Rác", ["asdkjaskjd", "12312 30129"]),
        ("6. Chào / Tạm biệt", ["Cảm ơn nha", "Bye"]),
        ("7. Nhờ giải chung chung", ["Làm bài tập này hộ tao", "Giải giúp cái đề này"])
    ]
    
    for cat_name, queries in chitchat_categories:
        log_to_file(f"\n--- {cat_name} ---")
        for q in queries:
            session_res = requests.post(SESSION_URL)
            session_id = session_res.json().get("session_id")
            
            answer = send_message_with_retry(session_id, q)
            log_to_file(f"User: {q}")
            log_to_file(f"Bot: {answer}\n")
            time.sleep(5)
            
    log_to_file("==================================================")
    log_to_file("PHẦN 2: REGRESSION TEST 6 CÂU NGOÀI PHẠM VI (ACADEMIC)")
    log_to_file("==================================================")
    
    regression_queries = [
        "Làm sao để cài đặt MySQL trên Windows",
        "MongoDB lưu trữ dữ liệu dưới dạng nào?",
        "Làm thế nào để sử dụng phpMyAdmin quản lý database?",
        "Cấu hình Replica Set trong cơ sở dữ liệu phân tán",
        "Giải thích khái niệm Eventual Consistency trong NoSQL",
        "Cách tối ưu hóa index trên PostgreSQL"
    ]
    
    for i, q in enumerate(regression_queries, 1):
        log_to_file(f"\n--- [REGRESSION {i}] ---")
        session_res = requests.post(SESSION_URL)
        session_id = session_res.json().get("session_id")
        
        answer = send_message_with_retry(session_id, q)
        log_to_file(f"User: {q}")
        
        # Check if the bot rejected correctly
        answer_lower = answer.lower()
        if "không đề cập" in answer_lower or "không chứa thông tin" in answer_lower:
            status = "PASS"
        else:
            status = "FAIL (Có thể bị lọt vào Chitchat hoặc ảo giác)"
            
        log_to_file(f"Kết quả: {status}")
        log_to_file(f"Bot: {answer}")
        time.sleep(5)

if __name__ == '__main__':
    run_tests()
