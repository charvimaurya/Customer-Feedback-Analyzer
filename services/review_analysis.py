import pandas as pd
from fastapi import UploadFile, HTTPException
from services.sentiment_service import get_sentiments
from services.chatbot import chat_with_openai
from utils.text_utils import extract_keywords


REVIEW_COLUMNS = {
    "review", "reviews", "review_text",
    "text", "feedback", "comment", "comments"
}


def read_reviews_from_file(file: UploadFile) -> list[str]:
    if not file.filename.endswith((".csv", ".txt")):
        raise HTTPException(400, "Only CSV or TXT files allowed")

    if file.filename.endswith(".txt"):
        content = file.file.read().decode("utf-8")
        reviews = [l.strip() for l in content.split("\n") if l.strip()]
        return reviews

    df = pd.read_csv(file.file)
    df.columns = df.columns.str.lower().str.strip()

    review_column = next((c for c in df.columns if c in REVIEW_COLUMNS), None)

    if review_column is None:
        raise HTTPException(
            400, f"CSV must contain one of: {', '.join(REVIEW_COLUMNS)}"
        )

    reviews = df[review_column].dropna().astype(str).tolist()
    if not reviews:
        raise HTTPException(400, "No reviews found")

    return reviews


def analyze_reviews(reviews: list[str]) -> dict:
    classified = [
        {"review": r, "sentiment": s}
        for r, s in zip(reviews, get_sentiments(reviews))
    ]

    good = [r["review"] for r in classified if r["sentiment"] == "Good"]
    neutral = [r["review"] for r in classified if r["sentiment"] == "Neutral"]
    bad = [r["review"] for r in classified if r["sentiment"] == "Bad"]

    stats = {
        "total_reviews": len(classified),
        "good": len(good),
        "neutral": len(neutral),
        "bad": len(bad),
    }

    prompt = build_analysis_prompt(stats, good, neutral, bad)

    insights = chat_with_openai(prompt, sentiment = "Mixed", history = [], mode = "analysis")

    return {
        "statistics": stats,
        "best_reviews": good[:5],
        "worst_reviews": bad[:5],
        "insights": insights,
    }


def build_analysis_prompt(stats, good, neutral, bad) -> str:
    pos_keywords = extract_keywords(good)
    neg_keywords = extract_keywords(bad)

    return f"""
You are a product insights analyst.

Stats:
{stats}

Top positive themes:
{pos_keywords}

Top negative themes:
{neg_keywords}

Example positives:
{good[:3]}

Example negatives:
{bad[:3]}

Provide:
- Summary
- Key strengths
- Key weaknesses
- Prioritized recommendations
"""
