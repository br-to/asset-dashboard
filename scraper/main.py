"""
asset-dashboard main scraper
全スクレイパーを実行してDBに保存する
"""

import sys
import traceback
from db import init_db, save_balances


def run_api_scrapers():
    """API系スクレイパー（軽量、10分ごと向き）"""
    results = {}

    # GMOコイン
    try:
        from scrapers.gmo import fetch_balances as gmo_fetch
        data = gmo_fetch()
        save_balances("GMO", data)
        results["GMO"] = len(data)
    except Exception as e:
        results["GMO"] = f"ERROR: {e}"
        traceback.print_exc()

    # Coincheck
    try:
        from scrapers.coincheck import fetch_balances as cc_fetch
        data = cc_fetch()
        save_balances("Coincheck", data)
        results["Coincheck"] = len(data)
    except Exception as e:
        results["Coincheck"] = f"ERROR: {e}"
        traceback.print_exc()

    # Binance Japan
    try:
        from scrapers.binance import fetch_balances as bn_fetch
        data = bn_fetch()
        save_balances("Binance", data)
        results["Binance"] = len(data)
    except Exception as e:
        results["Binance"] = f"ERROR: {e}"
        traceback.print_exc()

    # Onchain
    try:
        from scrapers.onchain import fetch_balances as onchain_fetch
        data = onchain_fetch()
        save_balances("Onchain", data)
        results["Onchain"] = len(data)
    except Exception as e:
        results["Onchain"] = f"ERROR: {e}"
        traceback.print_exc()

    return results


def run_bank_scrapers():
    """銀行系スクレイパー（重い、1日2回向き）"""
    results = {}

    # 楽天銀行
    try:
        from scrapers.rakuten_bank import fetch_balances as rb_fetch
        data = rb_fetch()
        for item in data:
            save_balances(item["service"], [item])
        results["rakuten_bank"] = len(data)
    except Exception as e:
        results["rakuten_bank"] = f"ERROR: {e}"
        traceback.print_exc()

    return results


def main():
    init_db()

    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode == "api":
        results = run_api_scrapers()
    elif mode == "bank":
        results = run_bank_scrapers()
    elif mode == "all":
        results = {}
        results.update(run_api_scrapers())
        results.update(run_bank_scrapers())
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python main.py [api|bank|all]")
        sys.exit(1)

    print("\n--- Results ---")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
