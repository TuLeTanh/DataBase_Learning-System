# Nhật Ký Bài Học (Lessons Learned)

*Ghi chú lại các phát hiện và bài học rút ra trong quá trình phát triển hệ thống RAG_CSDL.*

## 1. Ranh Giới An Toàn (Similarity vs Prompt)

**Phát hiện:** Điểm similarity của câu bẫy (out-of-scope) và câu hợp lệ (in-scope) **chồng lấn nhau hoàn toàn**.
- Ví dụ câu bẫy: `phpMyAdmin` (0.6149) và `Eventual Consistency` (0.6285).
- Ví dụ câu hợp lệ: `BCNF` (0.5962) và `Transaction` (0.5190).

**Bài học cốt lõi:**
> "Similarity score không phải ranh giới phân biệt tin cậy giữa câu hỏi trong phạm vi và ngoài phạm vi — hệ thống an toàn hoàn toàn nhờ kỷ luật prompt (Rule 1), không có cơ chế số liệu dự phòng. Mỗi lần sửa Rule 1 trong tương lai đều mang rủi ro tương đương lần này, cần test đủ 6 câu bẫy mỗi lần đụng vào."

Mọi khả năng chặn vi phạm hiện đang phụ thuộc 100% vào việc LLM đọc chunk rồi tuân thủ đúng câu chữ của Rule 1 (tuyệt đối không bịa thêm thông tin ngoài tài liệu).
