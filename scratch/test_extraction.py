import asyncio
import io
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(r"d:\All Code\New folder\RAG_CSDL")
from backend.app import app
from backend.file_extractor import extract_text_from_file

client = TestClient(app)

def test_manual():
    # 1. Create a dummy pdf
    from reportlab.pdfgen import canvas
    pdf_bytes = io.BytesIO()
    c = canvas.Canvas(pdf_bytes)
    c.drawString(100, 100, "Hello, this is a test PDF document.")
    c.save()
    pdf_data = pdf_bytes.getvalue()
    
    # 2. Extract directly
    extracted = extract_text_from_file(pdf_data, "test.pdf", "application/pdf")
    print("Direct extraction:", repr(extracted))
    
    # 3. Use API
    # Create a session
    res = client.post("/api/sessions")
    session_id = res.json()["session_id"]
    
    # Ask question
    files = {
        "files": ("test.pdf", pdf_data, "application/pdf")
    }
    data = {
        "session_id": session_id,
        "question": "m đọc được file này ko"
    }
    res = client.post("/api/ask", data=data, files=files)
    import json
    with open("api_response.json", "w", encoding="utf-8") as f:
        json.dump(res.json(), f, ensure_ascii=False)
    
test_manual()
