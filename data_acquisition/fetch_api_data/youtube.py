
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetches recent YouTube videos matching keywords and inserts them into PostgreSQL.
"""

import os
import requests
from datetime import datetime, timedelta

API_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_URL = os.getenv("YOUTUBE_URL")

SEARCH_KEYWORDS = [
    "cryptocurrency"
]

def fetch_youtube(cur):
    print("\n##### Acquisition: YouTube #####\n")

    if not API_KEY:
        print(" YOUTUBE_API_KEY not set.")
        return

    published_after = (datetime.utcnow() - timedelta(hours=2)).isoformat("T") + "Z"

    for keyword in SEARCH_KEYWORDS:
        params = {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": 10,
            "order": "date",
            "publishedAfter": published_after,
            "key": API_KEY
        }

        try:
            response = requests.get(SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            videos = response.json().get("items", [])

            for video in videos:
                snippet = video["snippet"]
                video_id = video["id"]["videoId"]
                title = snippet.get("title")
                description = snippet.get("description")
                channel_title = snippet.get("channelTitle")
                published_at = snippet.get("publishedAt")
                url = f"https://www.youtube.com/watch?v={video_id}"

                cur.execute(
                    """
                    INSERT INTO ods.media_youtube_videos (
                        video_id, title, description, channel_title,
                        published_at, keyword, url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (video_id) DO NOTHING;
                    """, (
                        video_id, title, description, channel_title,
                        published_at, keyword, url
                    )
                )

        except Exception as e:
            print(f"Error fetching YouTube data for keyword '{keyword}': {e}")
