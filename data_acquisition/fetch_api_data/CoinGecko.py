#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get the top 250 cryptocurrencies by market cap from CoinGecko and write them to PostgreSQL.
"""

import requests
import os

API_KEY = os.getenv("DEMO_KEY_COINGECKO")
BASE_URL = os.getenv("URL_COINGECKO")
PARAMS = {
    "vs_currency":   "usd",
    "order":         "market_cap_desc",
    "per_page":      250,
    "page":          1,
    "sparkline":     False
}

def fetch_and_transform() -> list:
    # Get and structure the top 250 currency information
    try:
        resp = requests.get(BASE_URL, params=PARAMS, headers={"x-cg-demo-api-key": API_KEY}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Failed to fetch CoinGecko data: {e}")
        return []

    results = []
    for coin in data:
        results.append({
            "coin_id":            coin.get("id"), # A more secure method than coin["id"]
            "symbol":             coin.get("symbol"),
            "name":               coin.get("name"),
            "current_price":      coin.get("current_price"),
            "market_cap":         coin.get("market_cap"),
            "total_volume":       coin.get("total_volume"),
            "circulating_supply": coin.get("circulating_supply"),
            "total_supply":       coin.get("total_supply"),
            "last_updated":       coin.get("last_updated"),
        })
    return results

def fetch_coingecko(cur):
    # Write CoinGecko data to the ods.coingecko table
    print("\n##### Acquisition: CoinGecko #####\n")
    coins = fetch_and_transform()
    for coin in coins:
        # print(f"Inserting: {coin['coin_id']} | ${coin['current_price']}")
        cur.execute("""
            INSERT INTO ods.price_coingecko_quotes (
                coin_id, symbol, name,
                current_price, market_cap,
                total_volume, circulating_supply,
                total_supply, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (coin_id) DO NOTHING;
        """, (
            coin["coin_id"],
            coin["symbol"],
            coin["name"],
            coin["current_price"],
            coin["market_cap"],
            coin["total_volume"],
            coin["circulating_supply"],
            coin["total_supply"],
            coin["last_updated"]
        ))
