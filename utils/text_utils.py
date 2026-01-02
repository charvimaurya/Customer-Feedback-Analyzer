import re
from collections import Counter


def extract_keywords(reviews: list[str], top_n: int = 5) -> list[str]:
    words = []
    for review in reviews:
        tokens = re.findall(r"\b[a-z]{3,}\b", review.lower())
        words.extend(tokens)

    return [word for word, _ in Counter(words).most_common(top_n)]
