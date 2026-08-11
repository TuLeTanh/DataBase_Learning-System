import requests

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

def create_files():
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("Đây là file TXT test. Trọng số Alpha là 0.75.")
    with open("test.md", "w", encoding="utf-8") as f:
        f.write("# File MD Test\nTrọng số Beta là 0.85.")
    
    with open("empty.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Title (Empty)\n>>\nendobj\n%%EOF")
        
    with open("test.docx", "wb") as f:
        f.write(b"PK\x03\x04") # Fake header just to see if it reads empty or fails

def test_file(filename, content_type, question, out_f):
    session_res = requests.post(SESSION_URL)
    session_id = session_res.json().get("session_id")
    
    with open(filename, "rb") as f:
        file_bytes = f.read()
        
    files = [("files", (filename, file_bytes, content_type))]
    data = {"session_id": session_id, "question": question}
    
    response = requests.post(API_URL, data=data, files=files)
    ans = response.json().get("answer", "")
    
    out_f.write(f"\n[TEST FILE: {filename}]\n")
    out_f.write(f"User: {question}\n")
    out_f.write(f"Bot: {ans}\n")

if __name__ == "__main__":
    create_files()
    with open("audit_attachments_output.txt", "w", encoding="utf-8") as f:
        test_file("test.txt", "text/plain", "Trọng số Alpha là bao nhiêu?", f)
        test_file("test.md", "text/markdown", "Trọng số Beta là bao nhiêu?", f)
        test_file("empty.pdf", "application/pdf", "File này nói về gì?", f)
        test_file("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Trong file có gì?", f)
