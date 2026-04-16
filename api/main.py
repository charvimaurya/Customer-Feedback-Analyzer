import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from services.review_analysis import read_reviews_from_file, analyze_reviews
from services.scraper.scraper_service import scrape_reviews
from services.sentiment_service import get_sentiment
from services.chatbot import chat_with_openai

from database.db import SessionLocal
from database.models import (
    RawFeedback,
    CleanedFeedback,
    PositiveFeedback,
    NegativeFeedback,
    Feedback
)

# ----------------------
# App setup
# ----------------------
app = FastAPI()

#enabling cors to connect to front end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    db.add(Feedback(
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

    db.add(Feedback(
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

        db.add(Feedback(
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
# ----------------------
# Scrape
# ----------------------

@app.post("/scrape")
def scrape_endpoint(url: str, db: Session = Depends(get_db)):
    """
    Scrapes reviews from a URL and processes them immediately.
    """
    try:
        reviews = scrape_reviews(url)

        results = []

        for review in reviews:
            cleaned = clean_text(review)
            sentiment = predict_sentiment(cleaned)

            #store_review_pipeline(db, review, cleaned, sentiment)

            results.append({
                "review": review,
                "sentiment": sentiment
            })

        return {
            "total_scraped": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_scraper_job(url: str):
    """
    Runs scraping pipeline in background.
    """
    from database.db import SessionLocal

    db = SessionLocal()

    try:
        reviews = scrape_reviews(url)

        for review in reviews:
            cleaned = clean_text(review)
            sentiment = predict_sentiment(cleaned)

            #store_review_pipeline(db, review, cleaned, sentiment)

    finally:
        db.close()


@app.post("/scrape-async")
def scrape_async(url: str, bg: BackgroundTasks):
    """
    Starts scraping in background and returns immediately.
    """
    bg.add_task(run_scraper_job, url)

    return {
        "status": "scraping started",
        "url": url
    }

