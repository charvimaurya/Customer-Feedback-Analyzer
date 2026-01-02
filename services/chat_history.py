chat_history = []

def add_to_chat_history(user_input: str, sentiment: str, reply:str) -> dict:
        chat_history.append({
            "user_input": user_input,
            "sentiment": sentiment,
            "reply": reply,
            "timestamp": datetime.utcnow().isoformat()
        })

def get_chat_history():
    return chat_history
