import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

from services.chatbot import chat_with_openai

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

vectorizer = joblib.load(
    os.path.join(MODELS_DIR, "tfidf_vectorizer_updated.pkl")
)

model = joblib.load(
    os.path.join(MODELS_DIR, "logistic_regression_updated.pkl")
)


class ReviewRequest(BaseModel):
    review: str

class ChatRequest(BaseModel):
    message: str


@app.get('/')
def root():
    return {'message': 'Hello World'};

@app.post("/predict")
def predict_sentiment(review: str):
    try:
        # Check for empty input
        if not review or review.strip() == "":
            raise HTTPException(status_code=400, detail="Review cannot be empty.")

        # Convert text to vector
        X = vectorizer.transform([review])

        # Predict
        pred = model.predict(X)[0]

        sentiment = "Good" if pred == 2 else "Neutral" if pred == 1 else "Bad"

        return {"sentiment": sentiment}

    except HTTPException:
        raise  # re-throw FastAPI errors

    except Exception as e:
        # Catch-all error
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/chat")
def chat(user_input: str):
    if not user_input or user_input.strip == "":
        raise HTTPException(status_code=400, detail="Review cannot be empty.")
    try:
        reply = chat_with_openai(user_input)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

