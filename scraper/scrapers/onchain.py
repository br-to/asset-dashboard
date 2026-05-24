"""
Onchain - Etherscan API で残高取得
ETH残高 + 主要ERC-20トークン残高
"""

import json
import os

import requests
import yaml


def _load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)["onchain"]


# 主要ERC-20トークン (Ethereum mainnet)
ERC20_TOKENS = {
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
}

# トークンのdecimals
TOKEN_DECIMALS = {
    "USDC": 6,
    "USDT": 6,
    "DAI": 18,
    "WETH": 18,
    "WBTC": 8,
}


def _get_eth_price_jpy() -> float:
    """CoinGecko APIでETH/JPYレート取得 (無料、認証不要)"""
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ethereum,bitcoin", "vs_currencies": "jpy"},
            timeout=10,
        )
        data = res.json()
        return data.get("ethereum", {}).get("jpy", 0)
    except Exception:
        return 0


def _get_btc_price_jpy() -> float:
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "jpy"},
            timeout=10,
        )
        data = res.json()
        return data.get("bitcoin", {}).get("jpy", 0)
    except Exception:
        return 0


def _get_usdjpy_rate() -> float:
    """1 USD = ? JPY"""
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "usd-coin", "vs_currencies": "jpy"},
            timeout=10,
        )
        data = res.json()
        # USDC/JPYがほぼUSD/JPY
        return data.get("usd-coin", {}).get("jpy", 155)
    except Exception:
        return 155


def fetch_balances(config: dict = None) -> list[dict]:
    """Etherscan APIでETH + ERC-20残高を取得"""
    if config is None:
        config = _load_config()

    api_key = config["etherscan_api_key"]
    wallets = config.get("wallets", [])

    if not api_key or not wallets:
        return []

    balances = []
    eth_price = _get_eth_price_jpy()
    btc_price = _get_btc_price_jpy()
    usdjpy = _get_usdjpy_rate()

    for wallet in wallets:
        address = wallet["address"]
        label = wallet.get("label", "wallet")

        # ETH残高取得 (Etherscan V2)
        res = requests.get(
            "https://api.etherscan.io/v2/api",
            params={
                "chainid": "1",
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest",
                "apikey": api_key,
            },
            timeout=10,
        )
        data = res.json()
        if data.get("status") == "1":
            eth_wei = int(data["result"])
            eth_amount = eth_wei / 1e18
            if eth_amount > 0:
                balances.append({
                    "service": "onchain",
                    "asset_name": f"ETH ({label})",
                    "amount": eth_amount,
                    "jpy_value": eth_amount * eth_price if eth_price else None,
                })

        # ERC-20トークン残高取得 (Etherscan V2)
        for token_name, contract_address in ERC20_TOKENS.items():
            res = requests.get(
                "https://api.etherscan.io/v2/api",
                params={
                    "chainid": "1",
                    "module": "account",
                    "action": "tokenbalance",
                    "contractaddress": contract_address,
                    "address": address,
                    "tag": "latest",
                    "apikey": api_key,
                },
                timeout=10,
            )
            data = res.json()
            if data.get("status") == "1":
                raw_balance = int(data["result"])
                decimals = TOKEN_DECIMALS.get(token_name, 18)
                amount = raw_balance / (10 ** decimals)

                if amount == 0:
                    continue

                # 円換算
                if token_name in ("USDC", "USDT", "DAI"):
                    jpy_value = amount * usdjpy
                elif token_name == "WETH":
                    jpy_value = amount * eth_price if eth_price else None
                elif token_name == "WBTC":
                    jpy_value = amount * btc_price if btc_price else None
                else:
                    jpy_value = None

                balances.append({
                    "service": "onchain",
                    "asset_name": f"{token_name} ({label})",
                    "amount": amount,
                    "jpy_value": jpy_value,
                })

    return balances


if __name__ == "__main__":
    results = fetch_balances()
    print(json.dumps(results, indent=2, ensure_ascii=False))
