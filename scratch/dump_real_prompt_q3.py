import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r"d:\All Code\New folder\RAG_CSDL")
from chatbot_pipeline import answer_question

q3 = "Cho ví dụ về vi phạm dạng chuẩn BCNF"
ans, no_rel, prompt = answer_question(q3, [], None)

print("--- BẮT ĐẦU DUMP PROMPT CHO Q3 ---")
print(prompt)
print("--- KẾT THÚC DUMP PROMPT CHO Q3 ---")
