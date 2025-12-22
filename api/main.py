import joblib
import os
import re
import string
import nltk
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, RawFeedback, CleanedFeedback, PositiveFeedback, NegativeFeedback, Feedback, init_db

# Download NLTK resources if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

app = FastAPI(title="Customer Feedback Analyzer API")

# Ensure DB tables are created
init_db()

# Load models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

try:
    vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer_updated.pkl'))
    model = joblib.load(os.path.join(MODELS_DIR, 'logistic_regression_updated.pkl'))
except Exception:
    vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'))
    model = joblib.load(os.path.join(MODELS_DIR, 'logistic_regression.pkl'))

# Cleaning logic from notebook
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(tokens)

class ReviewRequest(BaseModel):
    review: str

class ReviewResponse(BaseModel):
    sentiment: str

@app.get('/')
def root():
    return {'status': 'healthy', 'message': 'Customer Feedback Analyzer API is running with 4-table storage'}

@app.post("/predict", response_model=ReviewResponse)
def predict_sentiment(request: ReviewRequest, db: Session = Depends(get_db)):
    try:
        raw_review = request.review
        if not raw_review or raw_review.strip() == "":
            raise HTTPException(status_code=400, detail="Review cannot be empty.")

        # 1. Save to Raw Data Storage
        new_raw = RawFeedback(review=raw_review)
        db.add(new_raw)
        db.flush() # Get the ID for linking

        # 2. Clean and Save to Cleaned Data Storage
        cleaned_review = clean_text(raw_review)
        new_cleaned = CleanedFeedback(cleaned_review=cleaned_review, source_id=new_raw.id)
        db.add(new_cleaned)

        # 3. Predict Sentiment
        X = vectorizer.transform([cleaned_review]) # Predict on cleaned text
        pred = model.predict(X)[0]
        sentiment = "Good" if pred == 2 else "Neutral" if pred == 1 else "Bad"

        # 4. Save to Positive/Negative/Legacy Storage
        if sentiment == "Good":
            db.add(PositiveFeedback(review=raw_review))
        elif sentiment == "Bad":
            db.add(NegativeFeedback(review=raw_review))
        
        # Also maintain legacy feedbacks table for the history endpoint
        db.add(Feedback(review=raw_review, sentiment=sentiment))
        
        db.commit()

        return {"sentiment": sentiment}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).order_by(Feedback.created_at.desc()).limit(10).all()
    return feedbacks

