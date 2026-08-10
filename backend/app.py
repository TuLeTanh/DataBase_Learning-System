import base64
import json
import io
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from chatbot_pipeline import answer_question
import logging
from backend import db
from backend.file_extractor import extract_text_from_file

app = FastAPI(title="RAG CSDL Chatbot API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatResponse(BaseModel):
    answer: str
    new_title: str | None = None

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/sessions")
def create_session():
    session_id = db.create_session("New Chat")
    return {"session_id": session_id}

@app.get("/api/sessions")
def get_sessions():
    return db.get_all_sessions()

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    messages = db.get_session_messages(session_id)
    return {"session_id": session_id, "messages": messages}

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    db.delete_session(session_id)
    return {"status": "ok"}

def create_thumbnail_base64(file_bytes: bytes) -> str:
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(file_bytes))
        # Convert to RGB to avoid issues with saving some formats (like WebP with alpha) as JPEG
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # Resize to max 200px edge
        img.thumbnail((200, 200))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=70)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        logging.error(f"Thumbnail error: {e}")
        return None

@app.post("/api/ask", response_model=ChatResponse)
async def ask_question_api(
    session_id: str = Form(...),
    question: str = Form(...),
    files: Optional[List[UploadFile]] = File(None)
):
    try:
        # Validate files
        processed_attachments = []
        has_attachments = False
        
        if files:
            has_attachments = True
            if len(files) > 3:
                raise HTTPException(status_code=400, detail="Chỉ được đính kèm tối đa 3 file.")
                
            for file in files:
                # To check size, we need to read it
                file_bytes = await file.read()
                size_mb = len(file_bytes) / (1024 * 1024)
                if size_mb > 10:
                    raise HTTPException(status_code=400, detail=f"File {file.filename} vượt quá 10MB.")
                
                content_type = file.content_type
                filename = file.filename
                
                attachment_info = {
                    "filename": filename,
                    "content_type": content_type,
                    "size": len(file_bytes),
                    "is_image": content_type.startswith("image/")
                }
                
                if attachment_info["is_image"]:
                    # Create thumbnail
                    thumb_b64 = create_thumbnail_base64(file_bytes)
                    if thumb_b64:
                        attachment_info["thumbnail"] = thumb_b64
                else:
                    # Extract text for non-image files
                    extracted_text = extract_text_from_file(file_bytes, filename, content_type)
                    if extracted_text:
                        attachment_info["extracted_text"] = extracted_text
                
                processed_attachments.append(attachment_info)
        
        # Get history from DB
        all_messages = db.get_session_messages(session_id)
        history_for_llm = all_messages[-6:]
        
        # Call RAG pipeline (pass attachments metadata to LLM to acknowledge)
        answer_text, no_relevant_context, _ = answer_question(question, history_for_llm, processed_attachments)
        if answer_text.startswith("ERROR:"):
            raise Exception(answer_text)
            
        # Add messages to DB
        attachments_json = json.dumps(processed_attachments) if processed_attachments else None
        db.add_message(session_id, "user", question, attachments_json)
        db.add_message(session_id, "bot", answer_text)
        
        # Update title if it's the first message
        new_title = None
        if len(all_messages) == 0:
            new_title = question[:45] + ("..." if len(question) > 45 else "")
            if not new_title and has_attachments:
                new_title = f"Gửi {len(processed_attachments)} tệp đính kèm"
            db.update_session_title(session_id, new_title)
            
        return ChatResponse(answer=answer_text, new_title=new_title)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error calling LLM: {str(e)}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi kết nối tới LLM. Vui lòng thử lại sau.")
