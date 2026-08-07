import json
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = 'chunks.json'
INDEX_FILE = 'index.npz'
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

# Load data once
print("Loading model and index...")
model = SentenceTransformer(MODEL_NAME)
with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
    chunks = json.load(f)
    
data = np.load(INDEX_FILE)
embeddings = data['embeddings']

def cosine_similarity(a, b):
    # a is a 1D vector (query), b is a 2D matrix (all chunks)
    # Norms
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b, axis=1)
    
    # Dot product
    dot_products = np.dot(b, a)
    
    # Cosine similarity
    return dot_products / (norm_a * norm_b + 1e-10)

def search(query, top_k=5):
    query_vector = model.encode(query)
    similarities = cosine_similarity(query_vector, embeddings)
    
    # Get top_k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append((chunks[idx], similarities[idx]))
        
    return results

if __name__ == '__main__':
    queries = [
        "Chuẩn hóa 3NF là gì?",
        "Phụ thuộc hàm là gì?",
        "Sự khác nhau giữa DDL và DML?",
        "Ràng buộc toàn vẹn dùng để làm gì?",
        "Đại số quan hệ có những phép toán nào?"
    ]
    
    print("\n--- BẮT ĐẦU KIỂM THỬ ---")
    for q in queries:
        print(f"\n[Câu hỏi]: {q}")
        results = search(q, top_k=3)
        for i, (chunk, score) in enumerate(results):
            section = chunk.get("section_title", "Unknown")
            # Get first 100 chars, replacing newlines with spaces for clean printing
            preview = chunk['text'][:100].replace('\n', ' ')
            print(f"  Top {i+1} (Score: {score:.4f}) - Section: {section}")
            print(f"    Preview: {preview}...")
