import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAIAPI_KEY"))

SENTIMENT_MAP = {0: "negative", 1: "neutral", 2: "positive"}


def prepare_reviews_context(df: pd.DataFrame, sample_size=200):
    df_sample = df.sample(min(len(df), sample_size))
    reviews = []

    for _, row in df_sample.iterrows():
        sentiment = SENTIMENT_MAP.get(row["sentiment_score"], "neutral")
        reviews.append(f"{sentiment} review: {row['cleaned_review']}")

    return "\n".join(reviews)


def chatbot(df: pd.DataFrame):
    print("🤖 Customer Insights Chatbot")
    print("Type 'exit' to quit.\n")

    reviews_context = prepare_reviews_context(df)

    system_prompt = f"""
You are a senior product analyst.
You analyze customer reviews and answer questions with clear insights,
themes, and business recommendations.

Customer Reviews:
{reviews_context}
"""

    conversation = [
        {"role": "system", "content": system_prompt}
    ]

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye! 👋")
            break

        conversation.append({"role": "user", "content": user_input})

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=conversation,
            temperature=0.3
        )

        bot_reply = response.output_text
        print(f"\nBot: {bot_reply}\n")

        conversation.append({"role": "assistant", "content": bot_reply})
