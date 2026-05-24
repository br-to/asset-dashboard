"""
Onchain - Etherscan API で残高取得
ETH残高 + 主要ERC-20トークン残高
"""

import json
import os

import requests
import yaml


import requests
import yaml
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config_loader import load_config


def _load_config():
    return load_config()["onchain"]


# チェーン設定
CHAINS = {
    "ethereum": {"chainid": "1", "native": "ETH", "native_decimals": 18},
    "polygon": {"chainid": "137", "native": "POL", "native_decimals": 18},
    "base": {"chainid": "8453", "native": "ETH", "native_decimals": 18},
    "worldchain": {"chainid": "480", "native": "ETH", "native_decimals": 18},
}

# 主要ERC-20トークン (チェーン別)
ERC20_TOKENS = {
    "ethereum": {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "JPYC": "0x431D5dfF03120AFA4bDf332c61A6e1766eF37BDB",
    },
    "polygon": {
        "USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        "WETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        "JPYC": "0x431D5dfF03120AFA4bDf332c61A6e1766eF37BDB",
    },
    "base": {
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "WETH": "0x4200000000000000000000000000000000000006",
    },
    "worldchain": {
        "USDC": "0x79A02482A880bCE3F13e09Da970dC34db4CD24d1",
        "Re7WLD": "0x348831b46876d3df2db98bdec5e3b4083329ab9f",
    },
}

# トークンのdecimals
TOKEN_DECIMALS = {
    "USDC": 6,
    "USDT": 6,
    "DAI": 18,
    "WETH": 18,
    "WBTC": 8,
    "POL": 18,
    "JPYC": 18,
    "Re7WLD": 18,
}


def _get_eth_price_jpy() -> float:
    """CoinGecko APIでETH/JPYレート取得 (無料、認証不要)"""
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ethereum", "vs_currencies": "jpy"},
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


def _get_pol_price_jpy() -> float:
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "polygon-ecosystem-token", "vs_currencies": "jpy"},
            timeout=10,
        )
        data = res.json()
        return data.get("polygon-ecosystem-token", {}).get("jpy", 0)
    except Exception:
        return 0


def _get_all_prices() -> dict:
    """全レートを一括取得 (APIコール節約)"""
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "ethereum,bitcoin,polygon-ecosystem-token,usd-coin,worldcoin-wld",
                "vs_currencies": "jpy",
            },
            timeout=10,
        )
        data = res.json()
        return {
            "eth": data.get("ethereum", {}).get("jpy", 0),
            "btc": data.get("bitcoin", {}).get("jpy", 0),
            "pol": data.get("polygon-ecosystem-token", {}).get("jpy", 0),
            "usdjpy": data.get("usd-coin", {}).get("jpy", 155),
            "wld": data.get("worldcoin-wld", {}).get("jpy", 0),
        }
    except Exception:
        return {"eth": 0, "btc": 0, "pol": 0, "usdjpy": 155, "wld": 0}


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
    """Etherscan V2で複数チェーンのETH + ERC-20残高を取得"""
    if config is None:
        config = _load_config()

    api_key = config["etherscan_api_key"]
    wallets = config.get("wallets", [])

    if not api_key or not wallets:
        return []

    balances = []
    prices = _get_all_prices()
    eth_price = prices["eth"]
    btc_price = prices["btc"]
    pol_price = prices["pol"]
    usdjpy = prices["usdjpy"]
    wld_price = prices["wld"]

    # 対応チェーン一覧
    # ethereum/polygon: Etherscan V2 (free)
    # base: Blockscout (free, no key needed)
    ETHERSCAN_CHAINS = ["ethereum", "polygon"]
    BLOCKSCOUT_CHAINS = {
        "base": "https://base.blockscout.com/api",
        "worldchain": "https://worldchain-mainnet.explorer.alchemy.com/api",
    }

    for wallet in wallets:
        address = wallet["address"]
        label = wallet.get("label", "wallet")

        for chain_name in ETHERSCAN_CHAINS:
            chain = CHAINS[chain_name]
            chainid = chain["chainid"]
            native = chain["native"]

            # ネイティブトークン残高取得
            try:
                res = requests.get(
                    "https://api.etherscan.io/v2/api",
                    params={
                        "chainid": chainid,
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
                    raw = int(data["result"])
                    amount = raw / (10 ** chain["native_decimals"])
                    if amount > 0:
                        if native == "ETH":
                            jpy_value = amount * eth_price if eth_price else None
                        elif native == "POL":
                            jpy_value = amount * pol_price if pol_price else None
                        else:
                            jpy_value = None

                        chain_label = chain_name if chain_name != "ethereum" else "eth"
                        balances.append({
                            "service": "onchain",
                            "asset_name": f"{native} ({label}/{chain_label})",
                            "amount": amount,
                            "jpy_value": jpy_value,
                        })
            except Exception:
                pass

            # ERC-20トークン残高取得
            tokens = ERC20_TOKENS.get(chain_name, {})
            for token_name, contract_address in tokens.items():
                try:
                    res = requests.get(
                        "https://api.etherscan.io/v2/api",
                        params={
                            "chainid": chainid,
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

                        if token_name in ("USDC", "USDT", "DAI"):
                            jpy_value = amount * usdjpy
                        elif token_name == "JPYC":
                            jpy_value = amount
                        elif token_name == "WETH":
                            jpy_value = amount * eth_price if eth_price else None
                        elif token_name == "WBTC":
                            jpy_value = amount * btc_price if btc_price else None
                        elif token_name == "Re7WLD":
                            jpy_value = amount * wld_price if wld_price else None
                        else:
                            jpy_value = None

                        chain_label = chain_name if chain_name != "ethereum" else "eth"
                        balances.append({
                            "service": "onchain",
                            "asset_name": f"{token_name} ({label}/{chain_label})",
                            "amount": amount,
                            "jpy_value": jpy_value,
                        })
                except Exception:
                    pass

        # Blockscout対応チェーン (Base等)
        for chain_name, blockscout_url in BLOCKSCOUT_CHAINS.items():
            chain = CHAINS[chain_name]
            native = chain["native"]

            # ネイティブトークン残高
            try:
                res = requests.get(
                    blockscout_url,
                    params={
                        "module": "account",
                        "action": "balance",
                        "address": address,
                    },
                    timeout=10,
                )
                data = res.json()
                if data.get("status") == "1":
                    raw = int(data["result"])
                    amount = raw / (10 ** chain["native_decimals"])
                    if amount > 0:
                        if native == "ETH":
                            jpy_value = amount * eth_price if eth_price else None
                        else:
                            jpy_value = None
                        balances.append({
                            "service": "onchain",
                            "asset_name": f"{native} ({label}/{chain_name})",
                            "amount": amount,
                            "jpy_value": jpy_value,
                        })
            except Exception:
                pass

            # ERC-20トークン
            tokens = ERC20_TOKENS.get(chain_name, {})
            for token_name, contract_address in tokens.items():
                try:
                    res = requests.get(
                        blockscout_url,
                        params={
                            "module": "account",
                            "action": "tokenbalance",
                            "contractaddress": contract_address,
                            "address": address,
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
                        if token_name in ("USDC", "USDT", "DAI"):
                            jpy_value = amount * usdjpy
                        elif token_name == "JPYC":
                            jpy_value = amount
                        elif token_name == "WETH":
                            jpy_value = amount * eth_price if eth_price else None
                        elif token_name == "Re7WLD":
                            jpy_value = amount * wld_price if wld_price else None
                        else:
                            jpy_value = None
                        balances.append({
                            "service": "onchain",
                            "asset_name": f"{token_name} ({label}/{chain_name})",
                            "amount": amount,
                            "jpy_value": jpy_value,
                        })
                except Exception:
                    pass

    return balances


if __name__ == "__main__":
    results = fetch_balances()
    print(json.dumps(results, indent=2, ensure_ascii=False))
