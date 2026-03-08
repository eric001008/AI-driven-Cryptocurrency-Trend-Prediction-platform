#!/usr/bin/env python3
"""
Fetches top cryptocurrency market data from CoinMarketCap,
prints results and inserts them into PostgreSQL.
"""

import os
import requests
from typing import List, Dict, Any

API_KEY = os.getenv("COINMARKETCAP_SECRET")
BASE_URL = os.getenv("URL_COINMARKETCAP")
HEADERS = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": API_KEY,
}

def _get(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_latest_quotes(symbols: List[str], convert: str = "USD") -> List[Dict[str, Any]]:
    if not API_KEY:
        raise EnvironmentError("Environment variable COINMARKETCAP_SECRET is not set.")
    data = _get("/v1/cryptocurrency/quotes/latest", {
        "symbol": ",".join(symbols),
        "convert": convert
    })["data"]

    results = []
    for symbol, info in data.items():
        q = info["quote"][convert]
        results.append({
            "symbol": symbol,
            "name": info.get("name"),
            "slug": info.get("slug"),
            "price": q.get("price"),
            "volume_24h": q.get("volume_24h"),
            "percent_change_1h": q.get("percent_change_1h"),
            "percent_change_24h": q.get("percent_change_24h"),
            "percent_change_7d": q.get("percent_change_7d"),
            "market_cap": q.get("market_cap"),
            "circulating_supply": info.get("circulating_supply"),
            "total_supply": info.get("total_supply"),
            "max_supply": info.get("max_supply"),
            "last_updated": q.get("last_updated"),
        })
    return results

def get_top_listings(limit: int = 100, convert: str = "USD") -> List[str]:
    if not API_KEY:
        raise EnvironmentError("Environment variable COINMARKETCAP_SECRET is not set.")
    data = _get("/v1/cryptocurrency/listings/latest", {
        "start": 1,
        "limit": limit,
        "convert": convert
    })["data"]
    return [coin["symbol"] for coin in data]

def fetch_coinmarketcap_data(cur, top_n: int = 50):
    print(f"\n##### Acquisition: CoinMarketCap (Top {top_n}) #####\n")
    try:
        symbols = get_top_listings(limit=top_n)
        coin_quotes = get_latest_quotes(symbols)

        for quote in coin_quotes:
            cur.execute(
                """
                INSERT INTO ods.price_coinmarketcap_quotes (
                    symbol, name, slug, price, volume_24h,
                    percent_change_1h, percent_change_24h, percent_change_7d,
                    market_cap, circulating_supply, total_supply, max_supply,
                    last_updated
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, last_updated) DO NOTHING;
                """,
                (
                    quote["symbol"],
                    quote["name"],
                    quote["slug"],
                    quote["price"],
                    quote["volume_24h"],
                    quote["percent_change_1h"],
                    quote["percent_change_24h"],
                    quote["percent_change_7d"],
                    quote["market_cap"],
                    quote["circulating_supply"],
                    quote["total_supply"],
                    quote["max_supply"],
                    quote["last_updated"]
                )
            )
    except Exception as e:
        print(f"Failed to fetch CoinMarketCap data: {e}")

