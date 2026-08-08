import requests

API_URL = "http://127.0.0.1:8000/api/ask"
SESSION_URL = "http://127.0.0.1:8000/api/sessions"

# Get all sessions
res = requests.get(SESSION_URL)
sessions = res.json()

print(f"Total sessions: {len(sessions)}")

if len(sessions) > 0:
    first_session_id = sessions[0]["id"]
    print(f"Testing followup on session {first_session_id} (Title: {sessions[0]['title']})")
    
    # Check messages in this session
    msg_res = requests.get(f"http://127.0.0.1:8000/api/sessions/{first_session_id}")
    print("Messages in session:", len(msg_res.json()["messages"]))
    
    payload = {
        "session_id": first_session_id,
        "question": "Tôi vừa hỏi bạn gì thế?"
    }
    
    response = requests.post(API_URL, json=payload)
    print("Response:", response.json().get("answer"))
