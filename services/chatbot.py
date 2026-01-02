import os
from openai import OpenAI
from dotenv import load_dotenv
from services.sentiment_service import get_sentiment
from services.chat_history import add_to_chat_history
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAIAPI_KEY"))



SYSTEM_PROMPT = """
You are a helpful AI assistant for a Customer Feedback Analyzer.
You can:
- Analyze customer sentiment
- Explain trends
- Answer questions about reviews
Be concise and professional.
"""

def chat_with_openai(
    review: str,
    sentiment: str,
    history: list,
    mode: str = "simple"
):
    """
    mode = "simple"   → short explanation (single review / chatbot)
    mode = "analysis" → detailed business insights (file analysis)
    """

    # 1️⃣ Start with system role
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # 2️⃣ Add previous conversation (last 3 turns only)
    for chat in history[-3:]:
        messages.append({
            "role": "user",
            "content": chat["user_input"]
        })
        messages.append({
            "role": "assistant",
            "content": chat["reply"]
        })

    # 3️⃣ Build prompt depending on mode
    if mode == "simple":
        user_prompt = f"""
Review:
"{review}"

Predicted sentiment: {sentiment}

Explain briefly why this sentiment was assigned.
"""
    else:  # analysis mode
        user_prompt = f"""
You are a senior business analyst AI assisting product managers.

Customer reviews:
{review}

Overall predicted sentiment: {sentiment}

Provide your analysis as a JSON object with:
1. reason
2. strengths
3. weaknesses
4. recommendations
5. trends

Be concise, actionable, and product-focused.
Output strictly valid JSON.
"""

    # 4️⃣ Add the new user message
    messages.append({
        "role": "user",
        "content": user_prompt
    })

    # 5️⃣ Call OpenAI
    response = client.responses.create(
        model="gpt-4o-mini",
        input=messages,
        temperature=0.3
    )

    return response.output_text

if __name__ == "__main__":
    print("Welcome to Customer Feedback Chatbot!")


    while True:
        user_input = input("\nEnter a review (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        sentiment = get_sentiment(user_input)
        reply = chat_with_openai(user_input,
                                 sentiment,
                                 chat_history,
                                 mode = "simple")
        add_to_chat_history(user_input, sentiment, reply)
        print(f"\nAI: {reply}")
