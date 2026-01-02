import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

vectorizer = joblib.load(
    os.path.join(MODELS_DIR, "tfidf_vectorizer_updated.pkl")
)

model = joblib.load(
    os.path.join(MODELS_DIR, "logistic_regression_updated.pkl")
)

def get_sentiment(text: str) -> str:
    X = vectorizer.transform([text])  # ← FIX IS HERE
    pred = model.predict(X)[0]

    return (
        "Good" if pred == 2
        else "Neutral" if pred == 1
        else "Bad"
    )

def get_sentiments(texts: list[str]) -> list[str]:
    X = vectorizer.transform(texts)
    preds = model.predict(X)

    return [
        "Good" if p == 2 else "Neutral" if p == 1 else "Bad"
        for p in preds
    ]
