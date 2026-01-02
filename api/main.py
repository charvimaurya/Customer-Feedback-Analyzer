import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from services.review_analysis import read_reviews_from_file, analyze_reviews
from services.sentiment_service import get_sentiment
from services.chatbot import chat_with_openai

from database.db import SessionLocal
from database.models import (
    RawFeedback,
    CleanedFeedback,
    PositiveFeedback,
    NegativeFeedback,
    FeedbackLegacy
)

# ----------------------
# App setup
# ----------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Database dependency
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# Schemas
# ----------------------
class ChatRequest(BaseModel):
    user_input: str

# ----------------------
# In-memory chat history (temporary)
# ----------------------
chat_history = []

def add_to_chat_history(user_input: str, sentiment: str, reply: str):
    chat_history.append({
        "user_input": user_input,
        "sentiment": sentiment,
        "reply": reply
    })

# ----------------------
# Utility
# ----------------------
def clean_text(text: str) -> str:
    return text.lower().strip()

# ----------------------
# Routes
# ----------------------
@app.get("/")
def root():
    return {"message": "Customer Feedback Analyzer API running"}

# ----------------------
# Predict sentiment only
# ----------------------
@app.post("/predict")
def predict_sentiment(
    review: str,
    db: Session = Depends(get_db)
):
    if not review.strip():
        raise HTTPException(status_code=400, detail="Review cannot be empty")

    cleaned = clean_text(review)
    sentiment = get_sentiment(cleaned)

    # Save to DB
    raw = RawFeedback(review=review)
    db.add(raw)
    db.flush()

    db.add(CleanedFeedback(
        cleaned_review=cleaned,
        source_id=raw.id
    ))

    if sentiment == "Good":
        db.add(PositiveFeedback(review=cleaned))
    elif sentiment == "Bad":
        db.add(NegativeFeedback(review=cleaned))

    db.add(FeedbackLegacy(
        review=cleaned,
        sentiment=sentiment
    ))

    db.commit()

    return {"sentiment": sentiment}

# ----------------------
# Chat endpoint (single review + explanation)
# ----------------------
@app.post("/chat")
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    if not req.user_input.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    cleaned = clean_text(req.user_input)
    sentiment = get_sentiment(cleaned)

    # Save to DB
    raw = RawFeedback(review=req.user_input)
    db.add(raw)
    db.flush()

    db.add(CleanedFeedback(
        cleaned_review=cleaned,
        source_id=raw.id
    ))

    if sentiment == "Good":
        db.add(PositiveFeedback(review=cleaned))
    elif sentiment == "Bad":
        db.add(NegativeFeedback(review=cleaned))

    db.add(FeedbackLegacy(
        review=cleaned,
        sentiment=sentiment
    ))

    db.commit()

    # AI explanation
    reply = chat_with_openai(
        cleaned,
        sentiment,
        history=chat_history,
        mode="simple"
    )

    add_to_chat_history(req.user_input, sentiment, reply)

    return {
        "sentiment": sentiment,
        "reply": reply
    }

# ----------------------
# Analyze file endpoint
# ----------------------
@app.post("/analyze-file")
def analyze_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    reviews = read_reviews_from_file(file)

    for review in reviews:
        cleaned = clean_text(review)
        sentiment = get_sentiment(cleaned)

        raw = RawFeedback(review=review)
        db.add(raw)
        db.flush()

        db.add(CleanedFeedback(
            cleaned_review=cleaned,
            source_id=raw.id
        ))

        if sentiment == "Good":
            db.add(PositiveFeedback(review=cleaned))
        elif sentiment == "Bad":
            db.add(NegativeFeedback(review=cleaned))

        db.add(FeedbackLegacy(
            review=cleaned,
            sentiment=sentiment
        ))

    db.commit()

    return analyze_reviews(reviews)

# ----------------------
# Chat history
# ----------------------
@app.get("/history")
def history():
    return chat_history



