#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch bank/macro-related news using NewsData.io API and write to PostgreSQL.
"""

import os
import requests
from datetime import datetime, timedelta

API_KEY = os.getenv("NEWSDATA_API_KEY")
BASE_URL = os.getenv("NEWSDATA_URL")

KEYWORDS = [
    "crypto", "bank", "inflation", "interest",
    "KYC", "liquidity", "regulation", "policy"
]



def fetch_banknews(cur):
    print("\n##### Acquisition: Bank / Macro News (NewsData.io) #####\n")

    # Defensive check to confirm whether the API key exists
    if not API_KEY:
        print("NEWSDATA_API_KEY not set.")
        return

    # Combine keywords into a single OR-based query
    combined_query = " OR ".join(KEYWORDS)

    params = {
        "apikey": API_KEY,
        "q": combined_query,
        "language": "en",
        "category": "business",
        "country": "us"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        articles = response.json().get("results", [])  # Retrieve a list of news articles

    #  Iterating and Storing Data
        for art in articles:
            article_id = art.get("link")
            title = art.get("title")
            content = art.get("description")
            published_at = art.get("pubDate")
            url = art.get("link")
            source_name = art.get("source_id")

            # Detect keyword match from original list
            matched_kw = next((kw for kw in KEYWORDS if kw.lower() in (title or "").lower() or kw.lower() in (content or "").lower()), "unknown")

            cur.execute(
                """
                INSERT INTO ods.media_banknews_articles (
                    article_id, title, content,
                    published_at, url, source_name, keyword
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (article_id) DO NOTHING;
                """, (
                    article_id, title, content,
                    published_at, url, source_name, matched_kw
                )
            )

    except Exception as e:
        print(f"Error fetching bank news: {e}")