import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app = FastAPI()

try:
    vectorizer = joblib.load('../models/tfidf_vectorizer_updated.pkl')
    model = joblib.load('../models/logistic_regression_updated.pkl')
except Exception as e:
    raise RuntimeError(f'Model failed loading: {e}')


class ReviewRequest(BaseModel):
    review: str

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

