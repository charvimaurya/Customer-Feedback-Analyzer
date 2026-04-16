import requests
from bs4 import BeautifulSoup

def scrape_reviews(url: str):
    """
    Fetch reviews from a webpage (static HTML version)
    """
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # ⚠️ This selector depends on the site you're scraping
    review_elements = soup.select(".review-text")

    reviews = []
    for el in review_elements:
        text = el.get_text(strip=True)
        if text:
            reviews.append(text)

    return reviews