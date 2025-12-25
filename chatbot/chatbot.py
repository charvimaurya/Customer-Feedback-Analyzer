import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Use environment variable for API key
api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
client = OpenAI(api_key=api_key)

# API URL - can be overridden by environment variable for Docker
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")

def classify_review(review_text):
    try:
        payload = {"review": review_text}
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()["sentiment"]
    except Exception as e:
        print(f"Error classifying review: {e}")
        return "Unknown"

def chatbot_reply(user_input):
    sentiment = classify_review(user_input)

    prompt = f"The user said: '{user_input}'. The sentiment is {sentiment}. Respond helpfully."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # More affordable model, good for chatbots
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Chatbot error: {str(e)}"

if __name__ == "__main__":
    print("Welcome to Customer Feedback Chatbot!")
    while True:
        user_input = input("\nEnter a review (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        reply = chatbot_reply(user_input)
        print(f"\nAI: {reply}")