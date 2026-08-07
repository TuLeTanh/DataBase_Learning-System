import json
import numpy as np
from sentence_transformers import SentenceTransformer
import cohere
import os
import sys

CHUNKS_FILE = 'chunks.json'
INDEX_FILE = 'index.npz'
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
THRESHOLD = 0.45

api_key = os.environ.get('COHERE_API_KEY')
if not api_key:
    print("Lỗi: Không tìm thấy biến môi trường COHERE_API_KEY.")
    sys.exit(1)

print("Loading model and index...")
model = SentenceTransformer(MODEL_NAME)
data = np.load(INDEX_FILE)
embeddings = data['embeddings']

with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

# Khởi tạo Cohere Client v2
client = cohere.ClientV2(api_key=api_key)

def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b, axis=1)
    dot_products = np.dot(b, a)
    return dot_products / (norm_a * norm_b + 1e-10)

def search(query, top_k=5, threshold=THRESHOLD):
    query_vector = model.encode(query)
    similarities = cosine_similarity(query_vector, embeddings)
    
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'chunk': chunks[idx],
            'score': similarities[idx]
        })
        
    if not results or results[0]['score'] < threshold:
        return [], True
        
    return results, False

def build_prompt(query, results):
    context_text = "\n\n".join([f"--- Nguồn: {r['chunk']['source']} ---\n{r['chunk']['text']}" for r in results])
    prompt = f"""Bạn là trợ lý học tập môn Cơ sở dữ liệu. Dưới đây là các đoạn trích từ tài liệu môn học:

[CÁC ĐOẠN TRÍCH TÀI LIỆU]
{context_text}
[KẾT THÚC CÁC ĐOẠN TRÍCH]

Câu hỏi của sinh viên: {query}

Hướng dẫn:
1. Đọc kỹ các đoạn trích trên. Nếu các đoạn trích hoàn toàn không liên quan đến chủ đề câu hỏi (khác khái niệm, khác lĩnh vực, ví dụ hỏi về NoSQL/MongoDB nhưng đoạn trích chỉ nói về SQL quan hệ), hãy trả lời ngay ở đầu câu: "Tài liệu môn học hiện tại không đề cập đến vấn đề này." Tuyệt đối không được cố suy diễn hay chém gió ngoài tài liệu.
2. Nếu các đoạn trích có nói về khái niệm trong câu hỏi, hãy dựa vào định nghĩa, tính chất đã nêu trong đoạn trích để suy luận hợp lý và trả lời trực tiếp câu hỏi (ngay cả khi đoạn trích không chứa câu trả lời y hệt từng chữ). Bạn được phép suy luận trong phạm vi khái niệm đã có trong tài liệu.
3. Chỉ nói "không đề cập" khi context thực sự không có bất kỳ thông tin nào liên quan đến khái niệm được hỏi.
"""
    return prompt

def answer_question(query):
    results, no_relevant_context = search(query)
    
    if no_relevant_context:
        # Nếu không vượt threshold thô, tự động trả lời không cần LLM
        return "Tài liệu môn học hiện tại không đề cập đến vấn đề này.", no_relevant_context, ""
    
    prompt = build_prompt(query, results)
    
    try:
        response = client.chat(
            model="command-r-08-2024",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        # Truy xuất content text từ response (cấu trúc API V2 của Cohere)
        answer_text = response.message.content[0].text
        return answer_text, no_relevant_context, prompt
    except Exception as e:
        return f"ERROR: {str(e)}", no_relevant_context, prompt

def main():
    queries = [
        ("Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?", True),
        ("So sánh UNION và UNION ALL trong SQL", True),
        ("Cho ví dụ về vi phạm dạng chuẩn BCNF", True),
        ("Transaction là gì và ACID gồm những gì", True),
        ("asdkjaskjd", False),
        ("làm sao để cài đặt MySQL trên Windows", False),
        ("MongoDB lưu trữ dữ liệu dưới dạng nào?", False),
        ("Làm thế nào để sử dụng phpMyAdmin quản lý database?", False),
        ("Cấu hình Replica Set trong cơ sở dữ liệu phân tán", False),
        ("Giải thích khái niệm Eventual Consistency trong NoSQL", False)
    ]
    
    with open('llm_test_results.txt', 'w', encoding='utf-8') as f:
        pass_count = 0
        fail_count = 0
        in_doc_pass = 0
        in_doc_fail = 0
        out_doc_pass = 0
        out_doc_fail = 0
        
        for q, in_doc in queries:
            print(f"Testing: {q}")
            answer, no_ctx, prompt = answer_question(q)
            
            # Nếu câu có kết quả trả về bị lỗi Exception từ Cohere, log ra luôn
            if answer.startswith("ERROR:"):
                print(f"[{q}] -> API ERROR: {answer}")
                status = "FAIL (API ERROR)"
                fail_count += 1
                if in_doc: in_doc_fail += 1
                else: out_doc_fail += 1
            else:
                answer_lower = answer.lower()
                # Kiểm tra từ chối trong 100 ký tự đầu tiên để giảm False Negative (ví dụ: trả lời đúng nhưng rào trước/sau)
                first_part = answer_lower[:100]
                is_reject = "không đề cập" in first_part or "không chứa thông tin" in first_part or "không nhắc đến" in first_part or "không có thông tin" in first_part
                
                is_pass = False
                if in_doc and not is_reject:
                    is_pass = True
                elif not in_doc and is_reject:
                    is_pass = True
                    
                status = "PASS" if is_pass else "FAIL"
                if is_pass:
                    pass_count += 1
                    if in_doc: in_doc_pass += 1
                    else: out_doc_pass += 1
                else:
                    fail_count += 1
                    if in_doc: in_doc_fail += 1
                    else: out_doc_fail += 1
            
            with open('llm_test_results.txt', 'a', encoding='utf-8') as f:
                f.write(f"==================================================\n")
                f.write(f"Câu hỏi: {q}\n")
                f.write(f"Nhóm: {'Trong tài liệu' if in_doc else 'Ngoài tài liệu'}\n")
                f.write(f"Vượt threshold thô (0.45): {'Không' if no_ctx else 'Có'}\n")
                f.write(f"Đánh giá: {status}\n")
                f.write(f"--- TRẢ LỜI CỦA LLM ---\n")
                f.write(answer + "\n")
                f.write(f"==================================================\n\n")
                
        summary = f"""
=== TỔNG KẾT ===
Tổng số PASS: {pass_count}/10
Tổng số FAIL: {fail_count}/10

Nhóm TRONG TÀI LIỆU (4 câu):
- PASS: {in_doc_pass}
- FAIL: {in_doc_fail}

Nhóm NGOÀI TÀI LIỆU (6 câu):
- PASS: {out_doc_pass}
- FAIL: {out_doc_fail}
"""
        with open('llm_test_results.txt', 'a', encoding='utf-8') as f:
            f.write(summary)
            print(summary)

if __name__ == '__main__':
    main()
