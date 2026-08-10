import io
import logging
from docx import Document
from pypdf import PdfReader

MAX_EXTRACT_CHARS = 100000  # Giới hạn 100,000 ký tự cho toàn bộ text trích xuất (~25k tokens)

def extract_text_from_file(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Trích xuất nội dung văn bản từ các định dạng file được hỗ trợ (TXT, MD, DOCX, PDF).
    Bỏ qua (trả về rỗng) đối với các file không phải văn bản (hình ảnh, v.v.).
    """
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    text = ""
    
    try:
        # TXT / MD
        if ext in ['txt', 'md'] or content_type in ['text/plain', 'text/markdown']:
            text = file_bytes.decode('utf-8', errors='ignore')
            
        # DOCX
        elif ext == 'docx' or content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
                    # PDF
        elif ext == 'pdf' or content_type == 'application/pdf':
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages_text.append(page_text.strip())
            text = "\n\n--- Trang tiếp theo ---\n\n".join(pages_text)
            
        else:
            # File không hỗ trợ trích xuất text (ví dụ: ảnh)
            return ""
            
    except Exception as e:
        logging.error(f"Lỗi trích xuất file {filename}: {e}")
        return ""

    # Giới hạn số ký tự
    if len(text) > MAX_EXTRACT_CHARS:
        text = text[:MAX_EXTRACT_CHARS] + "\n\n[...Nội dung đã bị cắt vì quá dài...]"
        
    return text.strip()
