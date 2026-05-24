"""
Binance Japan - 残高取得
Spot wallet + Funding wallet
"""

import hmac
import hashlib
import time
import json
import os
import sys

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config_loader import load_config


def _load_config():
    return load_config()["binance"]


def _signed_get(api_key: str, api_secret: str, path: str) -> dict:
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
    signature = hmac.new(
        api_secret.encode(), query_string.encode(), hashlib.sha256
    ).hexdigest()
    url = f"https://api.binance.com{path}?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": api_key}
    res = requests.get(url, headers=headers, timeout=10)
    return res.json()


def _signed_post(api_key: str, api_secret: str, path: str) -> list:
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
    signature = hmac.new(
        api_secret.encode(), query_string.encode(), hashlib.sha256
    ).hexdigest()
    url = f"https://api.binance.com{path}?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": api_key}
    res = requests.post(url, headers=headers, timeout=10)
    return res.json()


def _calc_jpy(symbol: str, amount: float, rates: dict):
    if symbol == "JPY":
        return amount
    elif symbol in rates:
        return amount * rates[symbol]
    return None


def fetch_balances(config: dict = None) -> list[dict]:
    """Binance Japanの残高を取得する (Spot + Funding)"""
    if config is None:
        config = _load_config()

    api_key = config["api_key"]
    api_secret = config["api_secret"]

    rates = _get_rates()
    balances = []

    # 1. Spot wallet
    spot_data = _signed_get(api_key, api_secret, "/api/v3/account")
    for asset_info in spot_data.get("balances", []):
        free = float(asset_info.get("free", 0))
        locked = float(asset_info.get("locked", 0))
        total = free + locked
        if total == 0:
            continue
        symbol = asset_info["asset"]
        jpy_value = _calc_jpy(symbol, total, rates)
        balances.append({
            "service": "binance",
            "asset_name": symbol,
            "amount": total,
            "jpy_value": jpy_value,
        })

    # 2. Funding wallet
    funding_data = _signed_post(api_key, api_secret, "/sapi/v1/asset/get-funding-asset")
    if isinstance(funding_data, list):
        for asset_info in funding_data:
            free = float(asset_info.get("free", 0))
            locked = float(asset_info.get("locked", 0))
            total = free + locked
            if total == 0:
                continue
            symbol = asset_info["asset"]
            # Spotと重複する場合は合算
            existing = next((b for b in balances if b["asset_name"] == symbol), None)
            if existing:
                existing["amount"] += total
                existing["jpy_value"] = _calc_jpy(symbol, existing["amount"], rates)
            else:
                jpy_value = _calc_jpy(symbol, total, rates)
                balances.append({
                    "service": "binance",
                    "asset_name": symbol,
                    "amount": total,
                    "jpy_value": jpy_value,
                })

    return balances


def _get_rates() -> dict[str, float]:
    """Binanceのティッカーから主要通貨のJPYレートを取得"""
    try:
        res = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            timeout=10,
        )
        tickers = res.json()

        jpy_rates = {}
        usdt_jpy = None

        for ticker in tickers:
            symbol = ticker["symbol"]
            price = float(ticker["price"])

            if symbol == "USDTJPY":
                usdt_jpy = price
            elif symbol.endswith("JPY"):
                base = symbol[:-3]
                jpy_rates[base] = price

        # USDTペアからJPY換算
        if usdt_jpy:
            for ticker in tickers:
                symbol = ticker["symbol"]
                price = float(ticker["price"])
                if symbol.endswith("USDT") and not symbol.startswith("JPY"):
                    base = symbol[:-4]
                    if base not in jpy_rates:
                        jpy_rates[base] = price * usdt_jpy

            if "USDT" not in jpy_rates:
                jpy_rates["USDT"] = usdt_jpy

        return jpy_rates
    except Exception:
        return {}


if __name__ == "__main__":
    results = fetch_balances()
    print(json.dumps(results, indent=2, ensure_ascii=False))
