import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = 'chunks.json'
INDEX_FILE = 'index.npz'
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

def main():
    with open('test_report_raw.txt', 'w', encoding='utf-8') as out:
        out.write("=== PHẦN 1: VERIFY 3 VẤN ĐỀ ===\n")
        
        with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        # 1. Table of Contents
        out.write("\n[1. Kiểm tra Table of Contents]\n")
        toc_chunks = []
        for c in chunks:
            title = c.get('chapter_title', '').lower()
            text = c.get('text', '').lower()
            if 'table of contents' in title or 'table of contents' in text:
                toc_chunks.append(c)
                
        out.write(f"Số lượng chunk chứa 'table of contents': {len(toc_chunks)}\n")
        for c in toc_chunks:
            out.write(f"\n--- Chunk ID: {c['id']} ---\n")
            out.write(c['text'] + "\n")
            
        # 2. Thẻ HTML
        out.write("\n[2. Kiểm tra Thẻ HTML]\n")
        html_pattern = re.compile(r'<br/?>|</?u>|</?b>|</?i>', re.IGNORECASE)
        html_chunks = []
        for c in chunks:
            if html_pattern.search(c['text']):
                html_chunks.append(c)
                
        out.write(f"Số lượng chunk chứa thẻ HTML: {len(html_chunks)}\n")
        for c in html_chunks:
            out.write(f"- Chunk ID: {c['id']}\n")
            
        # 3. Lỗi dính chữ tiếng Việt
        out.write("\n[3. Kiểm tra lỗi dính chữ]\n")
        vn_diacritics = "áàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ"
        vn_diacritics += vn_diacritics.upper()
        
        word_pattern = re.compile(r'[A-Za-z' + vn_diacritics + r']{16,}')
        
        suspicious_words = []
        for c in chunks:
            text = c['text']
            words = word_pattern.findall(text)
            for w in words:
                if any(char in vn_diacritics for char in w):
                    suspicious_words.append((w, c['id']))
                    
        out.write(f"Số lượng từ nghi ngờ dính chữ (>15 ký tự, có dấu tiếng Việt): {len(suspicious_words)}\n")
        for w, cid in suspicious_words:
            out.write(f"- Từ: '{w}' (Chunk ID: {cid})\n")


        out.write("\n=== PHẦN 2: TEST RETRIEVAL VỚI CÂU HỎI MỚI ===\n")
        
        # Load index and model
        out.write("Loading model and index for retrieval...\n")
        model = SentenceTransformer(MODEL_NAME)
        data = np.load(INDEX_FILE)
        embeddings = data['embeddings']
        
        def cosine_similarity(a, b):
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b, axis=1)
            dot_products = np.dot(b, a)
            return dot_products / (norm_a * norm_b + 1e-10)

        queries = [
            "Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?",
            "So sánh UNION và UNION ALL trong SQL",
            "Cho ví dụ về vi phạm dạng chuẩn BCNF",
            "Transaction là gì và ACID gồm những gì",
            "asdkjaskjd",
            "làm sao để cài đặt MySQL trên Windows"
        ]
        
        top1_scores = {}
        
        for q in queries:
            out.write(f"\n==========================================\n")
            out.write(f"[Câu hỏi]: {q}\n")
            out.write(f"==========================================\n")
            query_vector = model.encode(q)
            similarities = cosine_similarity(query_vector, embeddings)
            
            top_indices = np.argsort(similarities)[-5:][::-1]
            
            if top_indices.size > 0:
                top1_scores[q] = similarities[top_indices[0]]
                
            for i, idx in enumerate(top_indices):
                c = chunks[idx]
                score = similarities[idx]
                out.write(f"\n--- Top {i+1} (Score: {score:.4f}) | ID: {c['id']} | Source: {c['source']} | Section: {c['section_title']} ---\n")
                out.write(c['text'] + "\n")
                out.write("-" * 50 + "\n")


        out.write("\n=== PHẦN 3: THỐNG KÊ TỔNG THỂ ===\n")
        
        out.write("\n[Thống kê số lượng chunk theo file]\n")
        stats = {}
        for c in chunks:
            src = c['source']
            stats[src] = stats.get(src, 0) + 1
            
        for src, count in stats.items():
            out.write(f"- {src}: {count} chunks\n")
        total = len(chunks)
        out.write(f"Tổng số chunk mới: {total} (So với trước là 1793, chênh lệch: {total - 1793})\n")
        
        out.write("\n[Phân bố Similarity Score của Top-1 cho 6 câu hỏi]\n")
        out.write(f"{'Câu hỏi':<65} | {'Top-1 Score':<10}\n")
        out.write("-" * 80 + "\n")
        for q in queries:
            out.write(f"{q:<65} | {top1_scores[q]:.4f}\n")

if __name__ == '__main__':
    main()
