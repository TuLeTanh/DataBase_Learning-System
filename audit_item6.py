import requests
import json
import os

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

exam_file = r"D:\All Code\New folder\test data\2025_2026_HK1_DE THI GIUA KY_CSDL_DE01.md"

questions = [
    "Thời gian làm bài của đề thi CSDL giữa kỳ này là bao nhiêu phút?",
    "Quan hệ CHITIETHD có khóa chính là gì và gồm những thuộc tính nào?",
    "Câu 1 của đề thi yêu cầu sinh viên làm gì với bài toán quản lý tố giác bắt cóc trên không gian mạng?",
    "Ràng buộc về thuộc tính TrangThai trong câu 2a yêu cầu giới hạn những giá trị nào?",
    "Quan hệ LOAIBAOHIEM gồm những thuộc tính gì?"
]

def test_exam():
    if not os.path.exists(exam_file):
        return "File not found."

    session_res = requests.post(SESSION_URL)
    session_id = session_res.json().get("session_id")
    
    with open(exam_file, "rb") as f:
        file_bytes = f.read()

    output = ""
    for idx, q in enumerate(questions):
        output += f"\n--- Câu {idx+1} ---\n"
        output += f"User: {q}\n"
        
        files = [("files", (os.path.basename(exam_file), file_bytes, "text/markdown"))]
        data = {"session_id": session_id, "question": q}
        
        response = requests.post(API_URL, data=data, files=files)
        ans = response.json().get("answer", "")
        output += f"Bot: {ans}\n"
    return output

if __name__ == "__main__":
    out = test_exam()
    with open("audit_item6_output.txt", "w", encoding="utf-8") as f:
        f.write(out)
