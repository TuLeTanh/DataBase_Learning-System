import requests
import json
import time
import os

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

def log_to_file(msg):
    with open('test_report_attachments.txt', 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

def send_message_with_retry(session_id, query, files=None, max_retries=5):
    data = {
        "session_id": session_id,
        "question": query
    }
    
    # files is a list of tuples: [("files", (filename, file_bytes, content_type))]
    
    for attempt in range(max_retries):
        try:
            if files:
                # We need to recreate the file objects for each retry so they can be read again if needed
                files_payload = []
                for f_name, f_bytes, f_type in files:
                    files_payload.append(("files", (f_name, f_bytes, f_type)))
                response = requests.post(API_URL, data=data, files=files_payload, timeout=60)
            else:
                response = requests.post(API_URL, data=data, timeout=60)
                
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

def create_dummy_files():
    # 1. Create a dummy image
    with open("dummy_image.jpg", "wb") as f:
        # 1x1 white pixel jpeg
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x00\xff\xd9')
    
    # 2. Create a dummy PDF
    with open("de_bai.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Title (De bai SQL)\n>>\nendobj\n%%EOF")

def run_tests():
    create_dummy_files()
    
    with open('test_report_attachments.txt', 'w', encoding='utf-8') as f:
        f.write("")
        
    log_to_file("==================================================")
    log_to_file("TEST 1: ĐÍNH KÈM 1 ẢNH (KHÔNG HỎI HOẶC CHUNG CHUNG)")
    log_to_file("==================================================")
    session_res = requests.post(SESSION_URL)
    session_id = session_res.json().get("session_id")
    
    with open("dummy_image.jpg", "rb") as f:
        img_bytes = f.read()
    
    files = [("dummy_image.jpg", img_bytes, "image/jpeg")]
    q1 = "Xem giúp mình ảnh này với"
    log_to_file(f"User: {q1} (Kèm file: dummy_image.jpg)")
    ans1 = send_message_with_retry(session_id, q1, files)
    log_to_file(f"Bot: {ans1}\n")
    
    
    log_to_file("==================================================")
    log_to_file("TEST 2: ĐÍNH KÈM PDF VÀ HỎI KÈM THEO")
    log_to_file("==================================================")
    with open("de_bai.pdf", "rb") as f:
        pdf_bytes = f.read()
        
    files = [("de_bai.pdf", pdf_bytes, "application/pdf")]
    q2 = "Giải giúp tao bài trong PDF này. Tiện thể Khóa chính là gì?"
    log_to_file(f"User: {q2} (Kèm file: de_bai.pdf)")
    ans2 = send_message_with_retry(session_id, q2, files)
    log_to_file(f"Bot: {ans2}\n")
    
    
    log_to_file("==================================================")
    log_to_file("TEST 5: KHÔNG HỞ LỖ HỔNG (REGRESSION)")
    log_to_file("==================================================")
    regression_queries = [
        "MongoDB lưu trữ dữ liệu dưới dạng nào?",
        "Cấu hình Replica Set trong cơ sở dữ liệu phân tán"
    ]
    
    for i, q in enumerate(regression_queries, 1):
        log_to_file(f"\n--- [REGRESSION {i}] ---")
        log_to_file(f"User: {q}")
        ans = send_message_with_retry(session_id, q, None)
        log_to_file(f"Bot: {ans}")
        time.sleep(2)
        
if __name__ == '__main__':
    run_tests()
