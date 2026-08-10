# Hệ thống Chatbot Học Cơ Sở Dữ Liệu (RAG Pipeline)

Dự án này là một hệ thống chatbot thông minh (sử dụng kỹ thuật RAG - Retrieval-Augmented Generation) được thiết kế để hỗ trợ sinh viên học môn Cơ sở dữ liệu. Hệ thống giúp giải đáp các thắc mắc lý thuyết dựa trên kho tài liệu bài giảng nội bộ.

Hệ thống được chia làm 2 phần:
- **Backend API**: Xây dựng bằng FastAPI, thực hiện chức năng nhúng (embedding), tìm kiếm ngữ nghĩa (FAISS/numpy) và gọi mô hình LLM (Cohere Command-R) để sinh câu trả lời. Có cấu trúc prompt chặt chẽ chống việc AI "chém gió" kiến thức ngoài lề.
- **Frontend UI**: Xây dựng bằng React (Vite) + Tailwind CSS, cung cấp giao diện chat mượt mà, trực quan.

## Cấu trúc thư mục

```text
├── backend/               # Chứa Backend API
│   └── app.py             # File khởi chạy FastAPI Server
├── frontend/              # Chứa ứng dụng React (Vite)
│   ├── src/
│   │   ├── App.jsx        # Giao diện chat chính
│   │   └── index.css      # Tailwind config
│   └── package.json
├── data.txt               # Link tải bộ dữ liệu (PDF/Markdown bài giảng)
├── chatbot_pipeline.py    # Logic RAG (Tìm kiếm + Gọi LLM Cohere)
├── build_index.py         # Script tiền xử lý dữ liệu và tạo Vector Index
└── ...
```

## Hướng dẫn cài đặt và chạy thử

### 1. Chuẩn bị dữ liệu
Bộ dữ liệu thô (các file `.md` bài giảng) không được đính kèm trong repository này. Hãy mở file `data.txt`, tải thư mục `data` về và đặt vào thư mục gốc của project.
Sau đó, bạn cần tạo index cho dữ liệu (chỉ chạy 1 lần):
```bash
python build_index.py
```
Quá trình này sẽ tạo ra `chunks.json` (dữ liệu văn bản) và `index.npz` (vector embeddings).

### 2. Chạy Backend (FastAPI)
Yêu cầu: Có tài khoản Cohere và API Key (được cấu hình trong file `.env` tại thư mục gốc).
Môi trường Python (venv) đã được tách riêng sang thư mục `D:\csdl-chatbot-venv\venv` để tiết kiệm dung lượng ổ C.

```bash
# Môi trường Windows (Powershell)
$env:PYTHONIOENCODING="utf-8"
& "D:\csdl-chatbot-venv\venv\Scripts\python.exe" -m uvicorn backend.app:app --port 8000 --reload
```
Server sẽ khởi chạy tại `http://localhost:8000`.

### 3. Chạy Frontend (React/Vite)
Mở một tab Terminal khác:
```bash
cd frontend
npm install
npm run dev
```
Truy cập `http://localhost:5173/` để bắt đầu trò chuyện với chatbot!

## Tính năng nổi bật
- Lọc rác tự động bằng Vector Similarity (Threshold 0.45).
- Tích hợp 2 lớp xác thực (Vector Search + LLM System Prompt) giúp chặn hoàn toàn các câu hỏi không thuộc phạm vi bài giảng.
- Giao diện chat theo thời gian thực có báo lỗi kết nối rõ ràng.
