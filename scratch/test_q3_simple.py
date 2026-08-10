import sys
sys.path.append(r"d:\All Code\New folder\RAG_CSDL")

with open("scratch/test_q3_simple.log", "w", encoding="utf-8") as f:
    try:
        from chatbot_pipeline import answer_question
        f.write("Import successful!\n")
        
        q3 = "Cho ví dụ về vi phạm dạng chuẩn BCNF"
        f.write(f"Testing Q3: {q3}\n")
        ans, no_rel, prompt = answer_question(q3, [], None)
        
        f.write("Answer:\n" + ans + "\n")
        f.write("Prompt:\n" + prompt + "\n")
    except Exception as e:
        import traceback
        f.write("Error:\n")
        f.write(traceback.format_exc())
