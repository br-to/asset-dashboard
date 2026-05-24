"""
全スクレイパーを実行してDBに保存する
"""

import os
import yaml
from db import init_db, save_balances
from scrapers import gmo, coincheck, onchain, rakuten_bank, rakuten_sec, paypay


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} が見つかりません")
        print("config.example.yaml をコピーして config.yaml を作成してください")
        raise SystemExit(1)

    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def main():
    print("Asset Dashboard - Scraper")
    print("=" * 40)

    config = load_config()
    init_db()

    scrapers = [
        ("GMOコイン", gmo.fetch, config.get("gmo", {})),
        ("Coincheck", coincheck.fetch, config.get("coincheck", {})),
        ("オンチェーン", onchain.fetch, config.get("onchain", {})),
        ("楽天銀行", rakuten_bank.fetch, config.get("rakuten_bank", {})),
        ("楽天証券", rakuten_sec.fetch, config.get("rakuten_sec", {})),
        ("PayPay", paypay.fetch, config.get("paypay", {})),
    ]

    for service_name, fetch_fn, service_config in scrapers:
        print(f"\n[{service_name}] fetching...")
        try:
            assets = fetch_fn(service_config)
            if assets:
                save_balances(service_name, assets)
            else:
                print(f"  [{service_name}] no data")
        except Exception as e:
            print(f"  [{service_name}] ERROR: {e}")

    print("\n" + "=" * 40)
    print("Done.")


if __name__ == "__main__":
    main()
