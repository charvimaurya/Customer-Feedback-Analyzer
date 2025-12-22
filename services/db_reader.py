import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine("postgresql://postgres:Charvi1234!@localhost:5433/Customer Feedback Analyzer DB")


def load_cleaned_reviews(limit = 1000):
    """
    Loads reviews data from postgreSQL.
    :return:
    """
    query = f"""
    SELECT cleaned_review, sentiment_score
    FROM cleaned_reviews
    LIMIT {limit}
    """
    return pd.read_sql(query, engine)


