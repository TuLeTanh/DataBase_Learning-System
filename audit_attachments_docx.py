import requests
from docx import Document

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

def create_files():
    # DOCX
    doc = Document()
    doc.add_paragraph("Đây là file DOCX test. Điểm số Gamma là 0.95.")
    doc.save("test.docx")

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
    with open("audit_attachments_docx_output.txt", "w", encoding="utf-8") as f:
        test_file("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Điểm số Gamma là bao nhiêu?", f)
