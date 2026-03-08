
import os
import psycopg2
from fetch_api_data.bitquery import fetch_token_transfers
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

"""
Waits for the PostgreSQL database to become available.

This is a utility function designed for Docker environments where the
application container might start faster than the database container.
It attempts to connect multiple times before giving up.
"""

TOKENS = ['AAVE', 'ADA', 'AVAX', 'BCH', 'BGB', 'BSC-USD', 'BTC', 'CBBTC', 'CRO', 'DAI', 'DOGE', 'DOT', 'ETH', 'LEO', 'LINK', 'LTC', 'PEPE', 'SHIB', 'TRX', 'UNI', 'USDC', 'USDT', 'WBTC', 'WETH']
# symbols_failed = [
#     'apt', 'bnb', 'ena', 'etc', 'hbar', 'hype', 'icp', 'jitosol', 'near',
#     'ondo', 'pi', 'sol', 'steth', 'sui', 'susde', 'tao', 'ton', 'usde',
#     'usds', 'wbeth', 'wbt', 'weeth', 'wsteth', 'xlm', 'xmr', 'xrp'
# ]

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


def fetch_symbol_with_db(s):
    try:
        conn = psycopg2.connect(
            host="db",
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=5432
        )
        cur = conn.cursor()
        fetch_token_transfers(symbol=s, cur=cur, limit=1)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error fetching {s}: {e}")


if __name__ == "__main__":
    wait_for_postgres()

    print('\n', '-- TRADING RECORDS --')

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_symbol_with_db, symbol) for symbol in TOKENS[:3]]  # set 3 for test

    print('-- Trading records Acquisition finished --', '\n')