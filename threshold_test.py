import json
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = 'chunks.json'
INDEX_FILE = 'index.npz'
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

def main():
    print("Loading model and index for threshold testing...")
    model = SentenceTransformer(MODEL_NAME)
    data = np.load(INDEX_FILE)
    embeddings = data['embeddings']
    
    def cosine_similarity(a, b):
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b, axis=1)
        dot_products = np.dot(b, a)
        return dot_products / (norm_a * norm_b + 1e-10)

    # 10 questions: 4 in docs, 6 not in docs
    queries = [
        ("Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?", "Có"),
        ("So sánh UNION và UNION ALL trong SQL", "Có"),
        ("Cho ví dụ về vi phạm dạng chuẩn BCNF", "Có"),
        ("Transaction là gì và ACID gồm những gì", "Có"),
        ("asdkjaskjd", "Không"),
        ("làm sao để cài đặt MySQL trên Windows", "Không"),
        ("MongoDB lưu trữ dữ liệu dưới dạng nào?", "Không"),
        ("Làm thế nào để sử dụng phpMyAdmin quản lý database?", "Không"),
        ("Cấu hình Replica Set trong cơ sở dữ liệu phân tán", "Không"),
        ("Giải thích khái niệm Eventual Consistency trong NoSQL", "Không")
    ]
    
    print("\n[BẢNG SO SÁNH THRESHOLD]")
    print(f"{'Câu hỏi':<65} | {'Trong TL':<8} | {'Top-1 Score':<10}")
    print("-" * 90)
    
    for q, in_doc in queries:
        query_vector = model.encode(q)
        similarities = cosine_similarity(query_vector, embeddings)
        
        top_idx = np.argmax(similarities)
        score = similarities[top_idx]
        
        print(f"{q:<65} | {in_doc:<8} | {score:.4f}")

if __name__ == '__main__':
    main()
