import os
import psycopg2
from fetch_api_data.reddit import fetch_reddit
from fetch_api_data.coinmarketcap import fetch_coinmarketcap_data  # ensure coinmarketcap.py is in the same folder
from fetch_api_data.CoinGecko import fetch_coingecko
from fetch_api_data.GNews import fetch_gnews
from fetch_api_data.Messari import fetch_messari
from fetch_api_data.newsapi import fetch_newsapi
from fetch_api_data.youtube import fetch_youtube
from fetch_api_data.banknews import fetch_banknews
import time

"""
Main orchestration script for fetching social media and news data.

This script calls various data acquisition modules to populate the database
with data from sources like Reddit, GNews, NewsAPI, Youtube, and bank-related news.
"""

def wait_for_postgres(max_retries=10, delay=2):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="db",
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                port=5432
            )
            conn.close()
            print("PostgreSQL is ready.")
            return
        except psycopg2.OperationalError:
            print(f"Waiting for PostgreSQL... (attempt {attempt + 1})")
            time.sleep(delay)
    raise RuntimeError("PostgreSQL did not become ready in time.")


def main():
    conn = psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cur = conn.cursor()

    # 1. Reddit
    fetch_reddit(cur)

    # 3. NewsAPI
    fetch_newsapi(cur)

    # 5. GNews
    fetch_gnews(cur)

    #7. Youtube
    fetch_youtube(cur)

    # banknews
    fetch_banknews(cur)

    # Commit all the transactions from the different fetchers at once.
    # This ensures that all data insertions in this run are saved atomically.

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    wait_for_postgres()

    print('\n', '-- Social media Acquisition --')

    main()

    print('-- Social media Acquisition finished --', '\n')