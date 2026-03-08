#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pull a list of assets from the Messari API and write to the database.
"""

import os
import requests

API_KEY = os.getenv("API_KEY_MESSARI")
URL      = os.getenv("URL_MESSARI")
PARAMS   = {"limit": 50}

def fetch_and_transform():
    """
    Pull Messari asset data and convert it into a list of unified format
    Each dictionary in the returned list contains asset_id, slug, symbol, name,
    current_price, market_cap, total_volume,
    circulating_supply, total_supply, last_updated
    """
    try:
        resp = requests.get(
            URL,
            params=PARAMS,
            headers={"x-messari-api-key": API_KEY},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        print(f"Error fetching Messari data: {e}")
        return []

    results = []
    for asset in data:
        metrics = asset.get("metrics", {}).get("market_data", {})
        supply = metrics.get("supply", {})
        results.append({
            "asset_id":           asset.get("id"),
            "slug":               asset.get("slug"),
            "symbol":             asset.get("symbol"),
            "name":               asset.get("name"),
            "current_price":      metrics.get("price_usd"),
            "market_cap":         metrics.get("marketcap", {}).get("current_marketcap_usd"),
            "total_volume":       metrics.get("real_volume_last_24_hours"),
            "circulating_supply": supply.get("circulating"),
            "total_supply":       supply.get("max_supply"),
            "last_updated":       metrics.get("last_updated")
        })
    return results

def fetch_messari(cur):
# Get data from Messari and write to the PostgreSQL table ods.messari
    assets = fetch_and_transform()
    for asset in assets:
        cur.execute("""
            INSERT INTO ods.messari (
                asset_id, slug, symbol, name,
                current_price, market_cap, total_volume,
                circulating_supply, total_supply, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (asset_id) DO NOTHING;
        """, (
            asset["asset_id"],
            asset["slug"],
            asset["symbol"],
            asset["name"],
            asset["current_price"],
            asset["market_cap"],
            asset["total_volume"],
            asset["circulating_supply"],
            asset["total_supply"],
            asset["last_updated"]
        ))
