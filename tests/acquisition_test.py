from dotenv import load_dotenv

load_dotenv()

import requests
from data_acquisition.fetch_api_data.banknews import fetch_banknews
from data_acquisition.fetch_api_data.bitquery import fetch_token_transfers
from data_acquisition.fetch_api_data.CoinGecko import fetch_coingecko
from data_acquisition.fetch_api_data.coinmarketcap import fetch_coinmarketcap_data
from data_acquisition.fetch_api_data.GNews import fetch_gnews
from data_acquisition.fetch_api_data.Messari import fetch_messari
from data_acquisition.fetch_api_data.newsapi import fetch_newsapi
from data_acquisition.fetch_api_data.reddit import fetch_reddit
from data_acquisition.fetch_api_data.youtube import fetch_youtube

# A list of crypto token symbols to test API functionality
symbols_to_test = [
    'aave', 'ada', 'avax', 'bch', 'bgb', 'bsc-usd', 'btc', 'cbbtc',
    'cro', 'dai', 'doge', 'dot', 'eth', 'leo', 'link', 'ltc', 'pepe',
    'shib', 'trx', 'uni', 'usdc', 'usdt', 'wbtc', 'weth'
]


# Dummy cursor class to simulate database write behavior without connecting to a real database.
# This is useful for testing API data fetching functions independently of the database layer.
class DummyCursor:
    def execute(self, *args, **kwargs):
        txt = f"DB execute called with: {args}, {kwargs}"
        print(txt[:160])  # Limit output length to prevent excessively long logs

        query = args[0] if len(args) > 0 else ""
        values = args[1] if len(args) > 1 else ""

        # Print query values for verification
        print(f"Values: {values}")

    def close(self):
        print("Dummy cursor closed")


if __name__ == "__main__":
    cur = DummyCursor()

    print("\nTesting CoinMarketCap API...")
    fetch_coinmarketcap_data(cur)

    print("\nTesting CoinGecko API...")
    fetch_coingecko(cur)

    print("\nTesting GNews API...")
    fetch_gnews(cur)

    print("\nTesting Messari API...")
    fetch_messari(cur)

    print("\nTesting NewsAPI...")
    fetch_newsapi(cur)

    print("\nTesting Reddit API...")
    fetch_reddit(cur)

    print("\nTesting YouTube API...")
    fetch_youtube(cur)

    print("\nTesting BankNews scraping...")
    fetch_banknews(cur)

    print("\nTesting Bitquery API for token transfers...")
    for symbol in symbols_to_test:
        print(f"\nTesting symbol: {symbol.upper()}")
        try:
            # Fetch token transfers with a result limit of 1 for the given symbol
            fetch_token_transfers(symbol, cur, limit=1)
        except Exception as e:
            print(f"Error while processing {symbol.upper()}: {e}")
