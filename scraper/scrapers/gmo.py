"""
GMOコイン Private API から残高を取得する
https://api.coin.z.com/docs/#margin-summary
"""

import hmac
import hashlib
import time
import requests


def fetch(config: dict) -> list[dict]:
    """
    GMOコインの残高を取得して返す。
    Returns: [{"asset_name": "BTC", "amount": 0.5, "jpy_value": 5000000}, ...]
    """
    # TODO: Private API実装
    # api_key = config["api_key"]
    # api_secret = config["api_secret"]
    #
    # timestamp = str(int(time.time() * 1000))
    # method = "GET"
    # path = "/v1/account/assets"
    # text = timestamp + method + path
    # sign = hmac.new(api_secret.encode(), text.encode(), hashlib.sha256).hexdigest()
    #
    # headers = {
    #     "API-KEY": api_key,
    #     "API-TIMESTAMP": timestamp,
    #     "API-SIGN": sign,
    # }
    # resp = requests.get("https://api.coin.z.com/private" + path, headers=headers)
    # data = resp.json()["data"]
    #
    # assets = []
    # for item in data:
    #     if float(item["amount"]) > 0:
    #         assets.append({
    #             "asset_name": item["symbol"],
    #             "amount": float(item["amount"]),
    #             "jpy_value": float(item["conversionRate"]) * float(item["amount"]),
    #         })
    # return assets

    print("  [GMO] TODO: implement")
    return []
