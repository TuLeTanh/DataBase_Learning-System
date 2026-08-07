from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot_pipeline import answer_question
import logging

app = FastAPI(title="RAG CSDL Chatbot API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/ask", response_model=ChatResponse)
def ask_question(request: ChatRequest):
    try:
        # answer_question returns (answer_text, no_relevant_context, prompt)
        answer_text, no_relevant_context, _ = answer_question(request.question)
        if answer_text.startswith("ERROR:"):
            raise Exception(answer_text)
        return ChatResponse(answer=answer_text)
    except Exception as e:
        logging.error(f"Error calling LLM: {str(e)}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi kết nối tới LLM. Vui lòng thử lại sau.")
