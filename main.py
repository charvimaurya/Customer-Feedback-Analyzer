import pandas as pd
from services.preprocessing import clean_text, label_sentiment
from services.db_writer import load_reviews
# from services.genai_insights import prepare_reviews_context
def main():

    df = load_reviews(limit=1000)

    df["sentiment_score"] = df["Score"].apply(label_sentiment)
    df["review"] = df["Summary"].fillna("") + " " + df["Text"].fillna("")
    df["cleaned_review"] = df["review"].apply(clean_text)

    df = df[["cleaned_review", "sentiment_score"]]




    from services.db_writer import (
        create_cleaned_reviews_table,
        write_cleaned_reviews,
        write_sentiment_tables
    )

    create_cleaned_reviews_table()
    write_cleaned_reviews(df)
    write_sentiment_tables(df)

if __name__ == "__main__":
    main()



