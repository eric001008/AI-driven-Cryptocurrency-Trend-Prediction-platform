# newsapi_module.py
import os
import requests
from datetime import datetime, timedelta

BASE_URL = os.getenv("NEWSAPI_URL")
API_KEY = os.getenv("NEWS_API_KEY")
QUERY = "cryptocurrency"
LANG = "en"
PAGE_SIZE = 100


def fetch_newsapi(cur):

    print("\n##### Acquisition: NewsAPI #####\n")

    if not API_KEY:
        print("NEWS_API_KEY not set. Skipping NewsAPI fetch.")
        return

    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    params = {
        "q": QUERY,
        "language": LANG,
        "from": from_date,
        "sortBy": "relevancy",
        "apiKey": API_KEY,
        "pageSize": PAGE_SIZE
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])

        for art in articles:
            cur.execute(
                """
                INSERT INTO ods.media_newsapi_articles (
                    title, description, url, source_name, published_at
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """, (
                    art.get("title"),
                    art.get("description"),
                    art.get("url"),
                    art.get("source", {}).get("name"),
                    art.get("publishedAt")
                )
            )

    except Exception as e:
        print(f"Failed to fetch NewsAPI data: {e}")
