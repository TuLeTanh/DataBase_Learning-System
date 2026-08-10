import sys
import traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r"d:\All Code\New folder\RAG_CSDL")

try:
    from chatbot_pipeline import answer_question

    queries = [
        "Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?",
        "So sánh UNION và UNION ALL trong SQL",
        "Cho ví dụ về vi phạm dạng chuẩn BCNF",
        "Transaction là gì và ACID gồm những gì",
        "asdkjaskjd",
        "làm sao để cài đặt MySQL trên Windows",
        "MongoDB lưu trữ dữ liệu dưới dạng nào?",
        "Làm thế nào để sử dụng phpMyAdmin quản lý database?",
        "Cấu hình Replica Set trong cơ sở dữ liệu phân tán",
        "Giải thích khái niệm Eventual Consistency trong NoSQL."
    ]

    print("BẮT ĐẦU TEST...")
    with open('test_report_q3_fix.md', 'w', encoding='utf-8') as f:
        f.write("# BÁO CÁO KẾT QUẢ TEST LẠI 10 CÂU HỎI SAU KHI SỬA RULE 4\n\n")

    for i, q in enumerate(queries):
        print(f"Đang test câu {i+1}...")
        ans, no_rel, prompt = answer_question(q, [], None)
        with open('test_report_q3_fix.md', 'a', encoding='utf-8') as f:
            f.write(f"## Câu {i+1}: {q}\n")
            f.write(f"**Kết quả LLM:**\n")
            f.write(ans + "\n\n")

    print("Done! Saved to test_report_q3_fix.md")
except Exception as e:
    print("ERROR OCCURRED:")
    traceback.print_exc()
