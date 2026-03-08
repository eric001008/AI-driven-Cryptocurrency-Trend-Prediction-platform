"""
A mock database cursor for testing purposes.

This class simulates the behavior of a real psycopg2 cursor but instead of
executing SQL commands against a database, it prints the query and its
parameters to the console. This allows for testing data pipeline logic
without a live database connection.
"""

from dotenv import load_dotenv
load_dotenv()
import requests
from fetch_api_data.youtube import fetch_youtube
from fetch_api_data.banknews import fetch_banknews
from fetch_api_data.etherscan import fetch_etherscan_transactions

# Dummy cursor replaces database writing
class DummyCursor:
    def execute(self, *args, **kwargs):
        txt = f"DB execute called with: {args}, {kwargs}"
        print(txt[:160])
        query = args[0] if len(args) > 0 else ""
        values = args[1] if len(args) > 1 else ""

        print(f"SQL: {query.strip()}")
        print(f"Values: {values}")
    def close(self):
        print("Dummy cursor closed")

if __name__ == "__main__":
    cur = DummyCursor()

    print("\nTesting etherscan...")
    # Example address (one of Vitalik’s wallets)
    test_address = "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae"
    # Call the test function (to fetch the last 5 transaction records)
    fetch_etherscan_transactions(cur, test_address, limit=5)


