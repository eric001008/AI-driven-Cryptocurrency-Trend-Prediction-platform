# -*- coding: utf-8 -*-

import os

import requests

API_KEY = os.getenv("API_KEY_GNEWS")
URL = os.getenv("URL_GNEWS")

PARAMS  = {
    "apikey":   API_KEY,
    "category": "business", 
    "lang":     "en",          
    "max":      10           
}

def fetch_and_transform() -> list:

    try:
        resp = requests.get(URL, params=PARAMS, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])

        return [
            {
                "title":        art.get("title"),
                "content":      art.get("content"),
                "published_at": art.get("publishedAt"),
                "url":          art.get("url"),
                # Safely access the nested 'name' key.
                # .get("source", {}) returns an empty dict if 'source' key doesn't exist,
                # preventing an error on the subsequent .get("name") call.
                "source_name":  art.get("source", {}).get("name"),
                # Use the article's URL as its unique identifier.
                # This serves as a reliable primary key for the database table.
                "article_id":   art.get("url")
            }
            for art in articles
        ]
    except Exception as e:
        print(f"Error fetching GNews: {e}")
        return []

def fetch_gnews(cur):

    print("\n##### Acquisition: GNews #####\n")
    articles = fetch_and_transform()
    for art in articles:
        cur.execute("""
            INSERT INTO ods.media_gnews_articles (
                article_id, title, content,
                published_at, url, source_name
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (article_id) DO NOTHING;
        """, (
            art["article_id"],
            art["title"],
            art["content"],
            art["published_at"],
            art["url"],
            art["source_name"]
        ))
