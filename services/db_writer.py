import os
import gdown
import nltk
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
#

# engine = create_engine("postgresql://postgres:Charvi1234!@localhost:5432/Customer Feedback Analyzer")

engine = create_engine(DATABASE_URL)

DATA_DIR = "data"

GDRIVE_FILES = {
    "Reviews.csv": "1cFBCtZjZGrMh9NlJ1Eseg7Cp439XITPg",
    "cleaned_reviews.csv": "1YK_2NRcXuz0B6x1WUCgFSBBgT9MQgj8l",
}


def ensure_nltk_resources():
    """
    Download required NLTK resources if missing
    """
    resources = ["stopwords", "punkt", "wordnet"]
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(resource)



def ensure_data_files():
    """
    Download dataset from Google Drive if not present locally
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    for filename, file_id in GDRIVE_FILES.items():
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, file_path, quiet=False)


def load_reviews(limit: int | None = None) -> pd.DataFrame:
    ensure_nltk_resources()
    ensure_data_files()

    path = os.path.join(DATA_DIR, "Reviews.csv")

    if limit:
        return pd.read_csv(path, nrows=limit)

    return pd.read_csv(path)


# # Load CSV
# df = pd.read_csv("../data/Reviews.csv")

def create_cleaned_reviews_table():
    """
    Create cleaned_reviews table if it does not exist
    """
    query = """
    CREATE TABLE IF NOT EXISTS cleaned_reviews (
        id SERIAL PRIMARY KEY,
        cleaned_review TEXT NOT NULL,
        sentiment_score INT NOT NULL
    );
    """
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


def write_cleaned_reviews(df):
    """
    Append cleaned reviews to database
    """
    df.to_sql(
        name="cleaned_reviews",
        con=engine,
        if_exists="append",
        index=False
    )


def write_sentiment_tables(df):
    """
    Split and write positive / neutral / negative reviews
    """
    df[df["sentiment_score"] == 0].to_sql(
        "negative_reviews", engine, if_exists="replace", index=False
    )

    df[df["sentiment_score"] == 1].to_sql(
        "neutral_reviews", engine, if_exists="replace", index=False
    )

    df[df["sentiment_score"] == 2].to_sql(
        "positive_reviews", engine, if_exists="replace", index=False
    )
