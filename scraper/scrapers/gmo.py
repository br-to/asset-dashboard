"""
GMOコイン Private API - 残高取得
https://api.coin.z.com/docs/#assets
"""

import hmac
import hashlib
import time
import json
from datetime import datetime

import requests
import yaml


def _load_config():
    import os
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)["gmo"]


def _make_headers(method: str, path: str, body: str = "") -> dict:
    config = _load_config()
    api_key = config["api_key"]
    api_secret = config["api_secret"]

    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    text = timestamp + method + path + body
    sign = hmac.new(
        bytes(api_secret.encode("ascii")),
        bytes(text.encode("ascii")),
        hashlib.sha256
    ).hexdigest()

    return {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign,
    }


def fetch_balances(config: dict = None) -> list[dict]:
    """GMOコインの残高を取得する"""
    if config is None:
        config = _load_config()

    api_key = config["api_key"]
    api_secret = config["api_secret"]

    endpoint = "https://api.coin.z.com/private"
    path = "/v1/account/assets"
    method = "GET"

    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    text = timestamp + method + path
    sign = hmac.new(
        bytes(api_secret.encode("ascii")),
        bytes(text.encode("ascii")),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign,
    }

    res = requests.get(endpoint + path, headers=headers)
    data = res.json()

    if data.get("status") != 0:
        raise Exception(f"GMO API error: {data}")

    balances = []
    for asset in data.get("data", []):
        amount = float(asset.get("amount", 0))
        available = float(asset.get("available", 0))
        # 残高0のものはスキップ
        if amount == 0:
            continue

        # 円換算: conversionRateが提供される
        conversion_rate = float(asset.get("conversionRate", 0))
        jpy_value = amount * conversion_rate if conversion_rate > 0 else None

        balances.append({
            "service": "gmo",
            "asset_name": asset.get("symbol", "UNKNOWN"),
            "amount": amount,
            "jpy_value": jpy_value,
        })

    return balances


if __name__ == "__main__":
    results = fetch_balances()
    print(json.dumps(results, indent=2, ensure_ascii=False))
