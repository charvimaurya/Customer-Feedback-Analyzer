import openai
import requests
from openai import OpenAI
openai.api_key = "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"

client = OpenAI(api_key=openai.api_key)
API_URL = "http://127.0.0.1:8000/predict"

def classify_review(review_text):
    payload = {"review": review_text}
    response = requests.post(API_URL, json=payload)
    return response.json()["sentiment"]


def chatbot_reply(user_input):
    sentiment = classify_review(user_input)

    prompt = f"The user said: '{user_input}'. The sentiment is {sentiment}. Respond helpfully."
    response = client.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

if __name__ == "__main__":
    user_input = input("Enter a review or a product link: ")
    reply = chatbot_reply(user_input)
    print(reply)