# fetch_api_data/etherscan.py

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BASE_URL = os.getenv("ETHERSCAN_URL")

def fetch_etherscan_transactions(cur, address, limit=10, sort="desc"):
    """
    Get the transaction records of the specified address from Etherscan and write them to the database or print them.
    """
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": sort,
        "apikey": ETHERSCAN_API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()

        if data["status"] != "1":
            print(f"Etherscan error: {data['message']}")
            return

        transactions = data["result"][:limit]

        for tx in transactions:
            from_addr = tx["from"]
            to_addr = tx["to"]
            value_eth = int(tx["value"]) / 1e18
            timestamp = datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d %H:%M:%S")
            tx_hash = tx["hash"]

            cur.execute(
                """
        INSERT INTO temp_etherscan_tx (
            tx_hash, from_address, to_address, value_eth, timestamp
        ) VALUES (
            %s, %s, %s, %s, %s
        );
        """,
                (tx_hash, from_addr, to_addr, value_eth, timestamp)
            )

            print(f"TX {tx_hash[:10]}... | {value_eth:.4f} ETH | {from_addr[:6]} → {to_addr[:6]} at {timestamp}")

    except Exception as e:
        print(f"Exception while fetching from Etherscan: {e}")