
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
Waits for the PostgreSQL database to become available.

This is a utility function designed for Docker environments where the
application container might start faster than the database container.
It attempts to connect multiple times before giving up.
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


    # 2. CoinMarketCap
    fetch_coinmarketcap_data(cur)

    # 3. CoinGecko
    fetch_coingecko(cur)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    wait_for_postgres()

    print('\n', '-- Coins Acquisition --')

    main()

    print('-- Coins Acquisition finished --', '\n')