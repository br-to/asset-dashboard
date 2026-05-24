"""
Coincheck Private API - 残高取得
https://coincheck.com/documents/exchange/api#account-balance
"""

import hmac
import hashlib
import time
import json

import requests
import yaml
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config_loader import load_config


def _load_config():
    return load_config()["coincheck"]


def fetch_balances(config: dict = None) -> list[dict]:
    """Coincheckの残高を取得する"""
    if config is None:
        config = _load_config()

    access_key = config["access_key"]
    secret_key = config["secret_key"]

    url = "https://coincheck.com/api/accounts/balance"
    nonce = str(int(time.time() * 1000))
    message = nonce + url
    signature = hmac.new(
        bytes(secret_key.encode("ascii")),
        bytes(message.encode("ascii")),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "ACCESS-KEY": access_key,
        "ACCESS-NONCE": nonce,
        "ACCESS-SIGNATURE": signature,
    }

    res = requests.get(url, headers=headers)
    data = res.json()

    if not data.get("success", False):
        raise Exception(f"Coincheck API error: {data}")

    # 主要通貨のレートを取得して円換算する
    rates = _get_rates()

    balances = []
    # dataにはjpy, btc, eth, etc...がフラットに入っている
    # {通貨}_reservedは注文中の分
    skip_suffixes = ["_reserved", "_lend_in_use", "_lent", "_debt"]
    for key, value in data.items():
        if key == "success":
            continue
        if any(key.endswith(s) for s in skip_suffixes):
            continue

        amount = float(value)
        if amount == 0:
            continue

        asset_name = key.upper()

        # 円換算
        if asset_name == "JPY":
            jpy_value = amount
        elif asset_name in rates:
            jpy_value = amount * rates[asset_name]
        else:
            jpy_value = None

        balances.append({
            "service": "coincheck",
            "asset_name": asset_name,
            "amount": amount,
            "jpy_value": jpy_value,
        })

    return balances


def _get_rates() -> dict[str, float]:
    """Coincheckのレート情報を取得する"""
    try:
        res = requests.get("https://coincheck.com/api/rate/all")
        data = res.json()
        # data: {"jpy": {"btc": "12223404.5", "eth": "337632.5", ...}, ...}
        rates = {}
        jpy_rates = data.get("jpy", {})
        for symbol, rate in jpy_rates.items():
            if symbol == "jpy":
                continue
            if rate and rate != "0.0":
                rates[symbol.upper()] = float(rate)
        return rates
    except Exception:
        return {}


if __name__ == "__main__":
    results = fetch_balances()
    print(json.dumps(results, indent=2, ensure_ascii=False))
