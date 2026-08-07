import os
import re
import json
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_DIR = 'data'
CHUNKS_FILE = 'chunks.json'
INDEX_FILE = 'index.npz'
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

# Dictionary for common Vietnamese OCR errors
VN_FIX_DICT = {
    "dữliệu": "dữ liệu", "toànvẹn": "toàn vẹn", "hệthống": "hệ thống",
    "cơsởdữliệu": "cơ sở dữ liệu", "nhấtquán": "nhất quán", "thựcthể": "thực thể",
    "thuộctính": "thuộc tính", "quanhệ": "quan hệ", "phụthuộc": "phụ thuộc",
    "đạisố": "đại số", "khoáchính": "khóa chính", "khoángoại": "khóa ngoại",
    "môhình": "mô hình", "thôngtin": "thông tin", "ứngdụng": "ứng dụng",
    "ràngbuộc": "ràng buộc",
    # Auto-detected stuck words
    "bịchia": "bị chia", "bỏngay": "bỏ ngay", "bộkhông": "bộ không", "bộsẽcó": "bộ sẽ có", "bộthuộc": "bộ thuộc", "bộthứt": "bộ thứ t", "bộtrong": "bộ trong", "bộtrùng": "bộ trùng", "bộđược": "bộ được", "chỉchứa": "chỉ chứa", "chỉcần": "chỉ cần", "chỉkhi": "chỉ khi", "chỉkiểm": "chỉ kiểm", "chỉmục": "chỉ mục", "chỉnếu": "chỉ nếu", "chỉthỏa": "chỉ thỏa", "chỉđược": "chỉ được", "chỉđịnh": "chỉ định", "cốđịnh": "cố định", "cụthểcủa": "cụ thể của", "dụphép": "dụ phép", "giảsửcó": "giả sử có", "giờdạy": "giờ dạy", "giờhọc": "giờ học", "hệngữnghĩa": "hệ ngữ nghĩa", "hệnhanvien": "hệ nhân viên", "hệphải": "hệ phải", "hệquảcủa": "hệ quả của", "hệthành": "hệ thành", "hệtiên": "hệ tiên", "hệtrong": "hệ trong", "hệđược": "hệ được", "khảhợp": "khả hợp", "khảnăng": "khả năng", "kếquan": "kế quan", "kếthừa": "kế thừa", "kỳkhóa": "kỳ khóa", "lệtrong": "lệ trong", "maspchỉ": "masp chỉ", "mởrộng": "mở rộng", "ngữcấp": "ngữ cấp", "ngữnghĩa": "ngữ nghĩa", "ngữrút": "ngữ rút", "ngữđsqh": "ngữ đsqh", "nhỏnhất": "nhỏ nhất", "nhờcác": "nhờ các", "nhờvào": "nhờ vào", "niệmquan": "niệm quan", "phụtrách": "phụ trách", "phủcủa": "phủ của", "phủtối": "phủ tối", "quảcâu": "quả câu", "quảcủa": "quả của", "quảtrung": "quả trung", "quảtruy": "quả truy", "quảtrảvềcủa": "quả trả về của", "quảtrảvềlà": "quả trả về là", "sẻthông": "sẻ thông", "sẽbiết": "sẽ biết", "sẽbịbỏ": "sẽ bị bỏ", "sẽbịcập": "sẽ bị cập", "sẽbịxóa": "sẽ bị xóa", "sẽđược": "sẽ được", "sốbộcủa": "số bộ của", "sốbộluôn": "số bộ luôn", "sốbộtrong": "số bộ trong", "sốdòng": "số dòng", "sốdưới": "số dưới", "sốdạng": "số dạng", "sốkhách": "số khách", "sốkhông": "số không", "sốkiểu": "số kiểu", "sốluật": "số luật", "sốlượng": "số lượng", "sốnguyên": "số nguyên", "sốquan": "số quan", "sốthuộc": "số thuộc", "sốtoán": "số toán", "sốtrong": "số trong", "sốtrên": "số trên", "sốtrừđi": "số trừ đi", "sốtổhợp": "số tổ hợp", "sốxửlý": "số xử lý", "sốđiều": "số điều", "sốđiện": "số điện", "sởgiảng": "sở giảng", "sởđểnhận": "sở để nhận", "sởđểtính": "sở để tính", "sửdụng": "sử dụng", "thoảhai": "thoả hai", "thểchuyển": "thể chuyển", "thểcập": "thể cập", "thểdùng": "thể dùng", "thểgây": "thể gây", "thểhiện": "thể hiện", "thểlồng": "thể lồng", "thểsuy": "thể suy", "thểtham": "thể tham", "thểthiện": "thể thiện", "thểthêm": "thể thêm", "thểthực": "thể thực", "thểtruy": "thể truy", "thểviết": "thể viết", "thểyếu": "thể yếu", "thểđược": "thể được", "thịkết": "thị kết", "thịtrong": "thị trong", "thứtựcác": "thứ tự các", "thứtựgiữa": "thứ tự giữa", "thứtựthực": "thứ tự thực", "trảvềcủa": "trả về của", "trảvềmột": "trả về một", "trịcủa": "trị của", "trịdom": "trị dom", "trịgiá": "trị giá", "trịkhác": "trị khác", "trịmới": "trị mới", "trịnguyên": "trị nguyên", "trịnull": "trị null", "trịphải": "trị phải", "trịrỗng": "trị rỗng", "trịtham": "trị tham", "trịtrong": "trị trong", "trịtương": "trị tương", "trịtại": "trị tại", "trịtừmột": "trị từ một", "trịvới": "trị với", "trịđang": "trị đang", "trởlên": "trở lên", "trừcủa": "trừ của", "trừdòng": "trừ dòng", "trừnhững": "trừ những", "trừtập": "trừ tập", "trữchỉmục": "trữ chỉ mục", "trữthật": "trữ thật", "trữtrong": "trữ trong", "trữtrên": "trữ trên", "trữvật": "trữ vật", "tínhchỉ": "tính chỉ", "tổchức": "tổ chức", "từbảng": "từ bảng", "từkhung": "từ khung", "từkhóa": "từ khóa", "từnhiều": "từ nhiều", "từnhững": "từ những", "tửnhất": "tử nhất", "tựnhiên": "tự nhiên", "vếphải": "vế phải", "đềamstrong": "đề amstrong", "đềfrom": "đề from", "đềgroup": "đề group", "đềhaving": "đề having", "đềselect": "đề select", "đềwhere": "đề where", "đềđược": "đề được", "đểbiến": "để biến", "đểbiểu": "để biểu", "đểchứng": "để chứng", "đểgiải": "để giải", "đểgiữlại": "để giữ lại", "đểhiển": "để hiển", "đểkiểm": "để kiểm", "đểnhận": "để nhận", "đểphân": "để phân", "đểthay": "để thay", "đểthêm": "để thêm", "đểtránh": "để tránh", "đểtrảlời": "để trả lời", "đểtổhợp": "để tổ hợp", "đểđịnh": "để định", "đồcsdl": "đồ csdl", "đồquan": "đồ quan", "đồthịcủa": "đồ thị của", "đồthịphụ": "đồ thị phụ", "đồthịpth": "đồ thị pth", "đồthịvô": "đồ thị vô", "đủbằng": "đủ bằng", "đủtrong": "đủ trong", "ởnhiều": "ở nhiều", "ởnhững": "ở những"
}

def clean_text(text, filename):
    is_vn = filename.startswith("Chuong")
    
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line and not is_vn:
            cleaned_lines.append("")
            continue
        elif not line:
            continue
            
        # Remove standalone page numbers
        if line.isdigit() and len(line) < 4:
            continue
            
        # Vấn đề 2: Move HTML tag removal outside is_vn
        line = re.sub(r'<br/?>', ' ', line)
        line = re.sub(r'</?u>', '', line)
        line = re.sub(r'</?b>', '', line)
        line = re.sub(r'</?i>', '', line)
        line = re.sub(r'<.*?>', '', line)
            
        if is_vn:
            if "Khoa HTTT-Đại học CNTT" in line:
                line = line.replace("Khoa HTTT-Đại học CNTT", "").strip()
                line = re.sub(r'\s*\d+\s*$', '', line)
            if line.isdigit() and len(line) < 4:
                continue
            
            # Vấn đề 3: Fix sticked Vietnamese words with comprehensive dict
            line_lower = line.lower()
            for k, v in VN_FIX_DICT.items():
                if k in line_lower:
                    line = re.sub(k, v, line, flags=re.IGNORECASE)
                    
            if not line:
                continue
        else:
            # Ullman specific cleaning
            pass
                
        if line:
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines)

def chunk_vn_slide(text, filename):
    chunks = []
    lines = text.split('\n')
    current_heading = "General"
    current_chunk = []
    
    for line in lines:
        if line.startswith('#'):
            if current_chunk:
                chunks.append({
                    "source": filename,
                    "chapter_title": filename.replace('.md', ''),
                    "section_title": current_heading,
                    "text": current_heading + "\n" + '\n'.join(current_chunk),
                    "n_words": len((current_heading + " " + ' '.join(current_chunk)).split())
                })
            current_heading = line.lstrip('#').strip()
            current_chunk = []
        else:
            current_chunk.append(line)
            
    if current_chunk:
        chunks.append({
            "source": filename,
            "chapter_title": filename.replace('.md', ''),
            "section_title": current_heading,
            "text": current_heading + "\n" + '\n'.join(current_chunk),
            "n_words": len((current_heading + " " + ' '.join(current_chunk)).split())
        })
        
    return chunks

toc_removed_count = 0

def chunk_ullman(text, filename):
    global toc_removed_count
    chunks = []
    lines = text.split('\n')
    
    current_chapter = "Unknown Chapter"
    current_section = "General"
    current_chunk = []
    in_toc = False
    
    def is_toc_lines(chunk_lines):
        if not chunk_lines:
            return False
        table_lines = 0
        for line in chunk_lines:
            if re.search(r'\|.*\d+\|?\s*$', line):
                table_lines += 1
        return (table_lines / len(chunk_lines)) > 0.5
    
    def add_chunk():
        global toc_removed_count
        if in_toc or is_toc_lines(current_chunk):
            if current_chunk:
                toc_removed_count += 1
            return
            
        if current_chunk:
            chunk_text = f"{current_chapter} - {current_section}\n" + '\n'.join(current_chunk)
            n_words = len(chunk_text.split())
            
            if n_words > 350:
                paragraphs = ('\n'.join(current_chunk)).split('\n\n')
                temp_chunk = []
                temp_words = 0
                for p in paragraphs:
                    p_words = len(p.split())
                    if temp_words + p_words > 350 and temp_chunk:
                        txt = f"{current_chapter} - {current_section}\n" + '\n\n'.join(temp_chunk)
                        chunks.append({
                            "source": filename,
                            "chapter_title": current_chapter,
                            "section_title": current_section,
                            "text": txt,
                            "n_words": len(txt.split())
                        })
                        temp_chunk = [p]
                        temp_words = p_words
                    else:
                        temp_chunk.append(p)
                        temp_words += p_words
                if temp_chunk:
                    txt = f"{current_chapter} - {current_section}\n" + '\n\n'.join(temp_chunk)
                    chunks.append({
                        "source": filename,
                        "chapter_title": current_chapter,
                        "section_title": current_section,
                        "text": txt,
                        "n_words": len(txt.split())
                    })
            else:
                chunks.append({
                    "source": filename,
                    "chapter_title": current_chapter,
                    "section_title": current_section,
                    "text": chunk_text,
                    "n_words": n_words
                })
            
    for line in lines:
        if line.startswith('## '):
            add_chunk()
            current_chapter = line.lstrip('#').strip()
            chapter_norm = re.sub(r'[^a-zA-Z]', '', current_chapter).lower()
            in_toc = (chapter_norm == 'tableofcontents')
            current_section = "Introduction"
            current_chunk = []
        elif line.startswith('### '):
            add_chunk()
            current_section = line.lstrip('#').strip()
            section_norm = re.sub(r'[^a-zA-Z]', '', current_section).lower()
            in_toc = in_toc or (section_norm == 'tableofcontents')
            current_chunk = []
        else:
            current_chunk.append(line)
            
    add_chunk()
    return chunks

def process_documents():
    all_chunks = []
    files = os.listdir(DATA_DIR)
    
    for file in files:
        if not file.endswith('.md'): continue
        filepath = os.path.join(DATA_DIR, file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        cleaned_text = clean_text(text, file)
        
        if file.startswith("Chuong"):
            file_chunks = chunk_vn_slide(cleaned_text, file)
        else:
            file_chunks = chunk_ullman(cleaned_text, file)
            
        all_chunks.extend(file_chunks)
        
    final_chunks = []
    chunk_id = 1
    
    stats = {}
    
    for chunk in all_chunks:
        source = chunk['source']
        if source not in stats:
            stats[source] = {"count": 0, "first_chunk_added": False, "words": []}
            
        if chunk['n_words'] >= 15 or not stats[source]["first_chunk_added"]:
            chunk['id'] = chunk_id
            final_chunks.append(chunk)
            chunk_id += 1
            stats[source]["first_chunk_added"] = True
            stats[source]["count"] += 1
            stats[source]["words"].append(chunk['n_words'])
            
    with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_chunks, f, ensure_ascii=False, indent=2)
        
    print("--- CHUNKING STATISTICS ---")
    for source, data in stats.items():
        words = data["words"]
        if words:
            avg_w = sum(words)/len(words)
            max_w = max(words)
            min_w = min(words)
            print(f"{source}: {data['count']} chunks (Avg: {avg_w:.1f}, Min: {min_w}, Max: {max_w} words)")
            
    print(f"\n=> Đã loại bỏ {toc_removed_count} chunk liên quan đến 'Table of Contents'.\n")
        
    return final_chunks

def build_index(chunks):
    print(f"Loading embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    texts = [c['text'] for c in chunks]
    print(f"Encoding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    print(f"Saving embeddings to {INDEX_FILE}...")
    np.savez_compressed(INDEX_FILE, embeddings=embeddings)
    print("Build index complete!")

if __name__ == '__main__':
    chunks = process_documents()
    build_index(chunks)
