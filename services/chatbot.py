import os
from openai import OpenAI
from dotenv import load_dotenv

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

def chat_with_openai(user_message: str):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.4
    )

    return response.output_text

if __name__ == "__main__":
    print("Welcome to Customer Feedback Chatbot!")
    while True:
        user_input = input("\nEnter a review (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        reply = chat_with_openai(user_input)
        print(f"\nAI: {reply}")
