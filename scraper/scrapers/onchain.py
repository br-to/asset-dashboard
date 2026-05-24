"""
オンチェーン残高を取得する (Alchemy / Etherscan)
"""

import requests


def fetch(config: dict) -> list[dict]:
    """
    ウォレットのオンチェーン残高を取得して返す。
    Returns: [{"asset_name": "ETH", "amount": 1.5, "jpy_value": 750000}, ...]
    """
    # TODO: Alchemy/Etherscan API実装
    # alchemy_api_key = config["alchemy_api_key"]
    # wallets = config.get("wallets", [])
    #
    # assets = []
    # for wallet in wallets:
    #     address = wallet["address"]
    #     url = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_api_key}"
    #     payload = {
    #         "jsonrpc": "2.0",
    #         "method": "eth_getBalance",
    #         "params": [address, "latest"],
    #         "id": 1,
    #     }
    #     resp = requests.post(url, json=payload)
    #     balance_wei = int(resp.json()["result"], 16)
    #     balance_eth = balance_wei / 1e18
    #
    #     if balance_eth > 0:
    #         assets.append({
    #             "asset_name": f"ETH ({wallet.get('label', address[:8])})",
    #             "amount": balance_eth,
    #             "jpy_value": None,
    #         })
    #
    # return assets

    print("  [Onchain] TODO: implement")
    return []
