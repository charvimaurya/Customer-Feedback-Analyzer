import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pandas as pd
from services.review_analysis import read_reviews_from_file, analyze_reviews
from services.sentiment_service import get_sentiment, get_sentiments
from services.chatbot import chat_with_openai
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

class ChatRequest(BaseModel):
    user_input: str
@app.get('/')
def root():
    return {'message': 'Hello World'};

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)




# API Endpoints
@app.post("/predict")
def predict_sentiment(review: str):
    try:
        # Check for empty input
        if not review or review.strip() == "":
            raise HTTPException(status_code=400, detail="Review cannot be empty.")

        return {"sentiment": get_sentiment(review)}

    except Exception as e:
        # Catch-all error
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/chat")
def chat(req: ChatRequest):
    if not req.user_input or req.user_input.strip() == "":
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    sentiment = get_sentiment(req.user_input)
    reply = chat_with_openai(req.user_input, sentiment, history = chat_history, mode = "simple")
    add_to_chat_history(req.user_input, sentiment, reply)

    return {
        "sentiment": sentiment,
        "reply": reply
    }

@app.post("/analyze-file")
def analyze_file(file: UploadFile = File(...)):
    reviews = read_reviews_from_file(file)
    return analyze_reviews(reviews)

@app.get("/history")
def history():
    return chat_history








