import sys
import json
sys.path.append(r"d:\All Code\New folder\RAG_CSDL")
from chatbot_pipeline import search

q3 = "Cho ví dụ về vi phạm dạng chuẩn BCNF"
results, no_relevant_context = search(q3)

context_text = "\n\n".join([f"--- Nguồn: {r['chunk']['source']} ---\n{r['chunk']['text']}" for r in results])

rule_1 = '1. Đọc kỹ các đoạn trích trên. Nếu các đoạn trích hoàn toàn không liên quan đến chủ đề câu hỏi (khác khái niệm, khác lĩnh vực, ví dụ hỏi về NoSQL/MongoDB nhưng đoạn trích chỉ nói về SQL quan hệ), hãy trả lời ngay ở đầu câu: "Tài liệu môn học hiện tại không đề cập đến vấn đề này." Nếu đoạn trích chứa đúng khái niệm cốt lõi được hỏi (không chỉ liên quan mơ hồ), bạn được phép diễn giải, tổng hợp, hoặc tạo ví dụ minh hoạ dựa trên chính nội dung trong đoạn trích đó — không được thêm thông tin, ví dụ, hay khái niệm nào không xuất phát từ đoạn trích. Nếu đoạn trích không đủ để tạo ví dụ cụ thể, hãy nói rõ giới hạn đó thay vì tự bịa thêm.'

prompt = f"""Bạn là trợ lý học tập môn Cơ sở dữ liệu. Dưới đây là các đoạn trích từ tài liệu môn học:

[CÁC ĐOẠN TRÍCH TÀI LIỆU]
{context_text}
[KẾT THÚC CÁC ĐOẠN TRÍCH]

Làm theo các quy tắc sau:
{rule_1}
2. Nếu câu hỏi yêu cầu giải thích, hãy giải thích dễ hiểu, sử dụng ví dụ trong tài liệu nếu có.
3. Nếu có mã SQL/Relational Algebra, hãy format trong markdown block.
4. KHÔNG ĐƯỢC trả lời bằng tiếng Anh, luôn trả lời bằng tiếng Việt. Nếu tài liệu tiếng Anh, hãy dịch sang tiếng Việt một cách tự nhiên.

Câu hỏi của sinh viên: {q3}
"""

with open("final_prompt_q3.txt", "w", encoding="utf-8") as f:
    f.write(prompt)

print("Saved prompt to final_prompt_q3.txt")
