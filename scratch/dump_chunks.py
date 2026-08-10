import sys
sys.path.append(r"d:\All Code\New folder\RAG_CSDL")
from chatbot_pipeline import search

with open("chunks_q1_q3.md", "w", encoding="utf-8") as f:
    f.write("# Bằng Chứng Chunks (Câu 1 và Câu 3)\n\n")
    
    q1 = "Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?"
    r1, _ = search(q1)
    f.write(f"## Câu 1: {q1}\n")
    f.write(f"- Top-K: {len(r1)} chunks\n\n")
    for i, chunk in enumerate(r1):
        c = chunk['chunk']
        f.write(f"### Chunk {i+1} (Score: {chunk['score']:.4f})\n")
        f.write(f"- Nguồn: `{c['source']}`\n")
        f.write("```text\n")
        f.write(c['text'] + "\n")
        f.write("```\n\n")
        
    q3 = "Cho ví dụ về vi phạm dạng chuẩn BCNF"
    r3, _ = search(q3)
    f.write(f"## Câu 3: {q3}\n")
    f.write(f"- Top-K: {len(r3)} chunks\n\n")
    for i, chunk in enumerate(r3):
        c = chunk['chunk']
        f.write(f"### Chunk {i+1} (Score: {chunk['score']:.4f})\n")
        f.write(f"- Nguồn: `{c['source']}`\n")
        f.write("```text\n")
        f.write(c['text'] + "\n")
        f.write("```\n\n")
