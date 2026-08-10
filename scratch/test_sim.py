import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r"d:\All Code\New folder\RAG_CSDL")
from chatbot_pipeline import search

q1 = "Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?"
r1, _ = search(q1)
print("CHUNKS FOR Q1:")
for chunk in r1:
    print("---")
    print(chunk['chunk']['text'])

q3 = "Cho ví dụ về vi phạm dạng chuẩn BCNF"
r3, _ = search(q3)
print("CHUNKS FOR Q3:")
for chunk in r3:
    print("---")
    print(chunk['chunk']['text'])
