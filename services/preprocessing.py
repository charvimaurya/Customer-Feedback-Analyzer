import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def label_sentiment(score: int) -> int:
    """
    Map Amazon review score to sentiment class
    0 = Negative, 1 = Neutral, 2 = Positive
    """
    if score <= 2:
        return 0
    elif score == 3:
        return 1
    return 2


def clean_text(text: str) -> str:
    """
    Clean and normalize review text
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)

    tokens = nltk.word_tokenize(text)


    return " ".join(tokens)
