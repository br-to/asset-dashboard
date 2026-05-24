"""
Coincheck Private API から残高を取得する
https://coincheck.com/ja/documents/exchange/api#account-balance
"""

import hmac
import hashlib
import time
import requests


def fetch(config: dict) -> list[dict]:
    """
    Coincheckの残高を取得して返す。
    Returns: [{"asset_name": "BTC", "amount": 0.1, "jpy_value": 1000000}, ...]
    """
    # TODO: Private API実装
    # access_key = config["access_key"]
    # secret_key = config["secret_key"]
    #
    # url = "https://coincheck.com/api/accounts/balance"
    # nonce = str(int(time.time()))
    # message = nonce + url
    # signature = hmac.new(
    #     secret_key.encode(), message.encode(), hashlib.sha256
    # ).hexdigest()
    #
    # headers = {
    #     "ACCESS-KEY": access_key,
    #     "ACCESS-NONCE": nonce,
    #     "ACCESS-SIGNATURE": signature,
    # }
    # resp = requests.get(url, headers=headers)
    # data = resp.json()
    #
    # assets = []
    # for symbol, amount_str in data.items():
    #     if symbol.endswith("_reserved") or symbol == "success":
    #         continue
    #     amount = float(amount_str)
    #     if amount > 0:
    #         assets.append({
    #             "asset_name": symbol.upper(),
    #             "amount": amount,
    #             "jpy_value": None,  # 別途価格APIで変換が必要
    #         })
    # return assets

    print("  [Coincheck] TODO: implement")
    return []
