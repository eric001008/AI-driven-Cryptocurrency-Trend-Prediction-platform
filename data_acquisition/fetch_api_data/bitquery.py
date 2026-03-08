import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
BITQUERY_KEY = os.getenv("BITQUERY_KEY")
BITQUERY_URL = os.getenv("BITQUERY_URL")


TOKEN_CONTRACTS = {
    "AAVE": {"address": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DdAe9", "network": "ethereum"},
    "ADA": {"address": "0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47", "network": "bsc"},
    "APT": {"address": "0x1E0b2992079b620aaB27b5aB6A9322eFeC5cD33C", "network": "ethereum"},
    "AVAX": {"address": "0x85f138bfEE4ef8e540890CFb48F620571d67Eda3", "network": "ethereum"},
    "BCH": {"address": "0x6013e06972e3Ed6d06364b8f4d5862c37c94EeA8", "network": "ethereum"},
    "BGB": {"address": "0x54D2252757e1672EEaD234D27B1270728fF90581", "network": "ethereum"},
    "BNB": {"address": "0xB8c77482e45F1F44dE1745F52C74426C631bDD52", "network": "bsc"},
    "BSC-USD": {"address": "0x55d398326f99059fF775485246999027B3197955", "network": "bsc"},
    "BTC": {"address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "network": "ethereum"},
    "CBBTC": {"address": "0xD1F12370b2ba1C79838337648F820a87eDF5e1e6", "network": "ethereum"},
    "CRO": {"address": "0xA0b73E1Ff0B80914AB6fe0444e65848C4C34450b", "network": "ethereum"},
    "DAI": {"address": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "network": "ethereum"},
    "DOGE": {"address": "0xba2ae424d960c26247dd6c32edc70b295c744c43", "network": "bsc"},
    "DOT": {"address": "0x2D4fB6dD969992C881d8e534C747cC925D5Ba221", "network": "ethereum"},
    "ETH": {"address": "0x0000000000000000000000000000000000000000", "network": "ethereum"},
    "LINK": {"address": "0x514910771AF9Ca656af840dff83E8264EcF986CA", "network": "ethereum"},
    "UNI": {"address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", "network": "ethereum"},
    "USDC": {"address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "network": "ethereum"},
    "USDT": {"address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "network": "ethereum"},
    "WBTC": {"address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "network": "ethereum"},
    "WETH": {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "network": "ethereum"},
    "SHIB": {"address": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE", "network": "ethereum"},
    "PEPE": {"address": "0x6982508145454Ce325dDbE47a25d4ec3d2311933", "network": "ethereum"},
    "HBAR": {"address": "0xD6D7f1ec1B827c7B1B59aA09Bf3aD682c2cFb487", "network": "ethereum"},  # Wrapped
    "LEO": {"address": "0x2AF5D2aD76741191D15Dfe7bF6aC92d4Bd912Ca3", "network": "ethereum"},
    "LTC": {"address": "0x4338665CBB7B2485A8855A139b75D5e34AB0DB94", "network": "bsc"},
    "TRX": {"address": "0xF230b790E05390FC8295F4d3F60332c93BED42e2", "network": "ethereum"},  # Wrapped
    "XRP": {"address": "0x1D2F0dA169ceB9Fc7B3144628dB3F1A7dE94c8A0", "network": "bsc"}
    # 
}
for symbol, data in TOKEN_CONTRACTS.items():
    try:
        data["address"] = Web3.to_checksum_address(data["address"])
    except:
        print(f"Skipping invalid address checksum for {symbol}")

def fetch_token_transfers(symbol, cur, limit=10):
    symbol = symbol.upper()
    entry = TOKEN_CONTRACTS.get(symbol)
    if not entry:
        print(f"Unknown symbol: {symbol}")
        return

    contract_address = entry["address"]
    network = entry["network"]
    if network == "ethereum":
        graphql_root = "ethereum"
    elif network == "bsc":
        graphql_root = "binance_smart_chain"
    else:
        print(f"Unsupported network: {network}")
        return

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=10)
    start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%S")

    if network == "ethereum":
        network_param = 'network: ethereum'
    elif network == "bsc":
        network_param = 'network: bsc'
    else:
        print(f"Unsupported network: {network}")
        return

    query = f"""
    {{
      ethereum({network_param}) {{
        transfers(
          currency: {{is: "{contract_address}"}},
          date: {{since: "{start_iso}", till: "{end_iso}"}},
          options: {{desc: ["block.timestamp.time"], limit: {limit}}}
        ) {{
          block {{ timestamp {{ time }} }}
          transaction {{ hash }}
          sender {{ address }}
          receiver {{ address }}
          amount
          currency {{ symbol }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {BITQUERY_KEY}",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "query": query,
        "variables": "{}"
    })

    try:
        response = requests.post(BITQUERY_URL, headers=headers, data=payload, timeout=10)
        # print(" Raw JSON Response:")
        # print(response.text)

        result = response.json()

        if "errors" in result:
            print("GraphQL Error:", result["errors"])
            return

        transfers = result.get("data", {}).get("ethereum", {}).get("transfers")
        if not transfers:
            print(" No transfer data returned.")
            return

        for tx in transfers:
            time_str = tx["block"]["timestamp"]["time"]
            tx_hash = tx["transaction"]["hash"][-8:]
            sender = tx["sender"]["address"][-8:]
            receiver = tx["receiver"]["address"][-8:]
            amount = str(tx["amount"])
            token_symbol = tx["currency"]["symbol"]

            date, clock = time_str.split(" ")
            clock = clock[:8]

            cur.execute(
                "INSERT INTO ods.bitquery_records (time, date, sender, receiver, amount, currency) VALUES (%s, %s, %s, %s, %s, %s)",
                (clock, date, sender, receiver, amount, token_symbol)
            )

    except Exception as e:
        print("Bitquery fetch error:", e)
