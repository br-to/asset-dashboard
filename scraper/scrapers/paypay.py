"""
PayPayの残高をPlaywrightでスクレイピングする
"""

from playwright.sync_api import sync_playwright


def fetch(config: dict) -> list[dict]:
    """
    PayPayの残高を取得して返す。
    Returns: [{"asset_name": "PayPay残高", "amount": 10000, "jpy_value": 10000}, ...]
    """
    # TODO: Playwright実装
    # phone = config["phone"]
    # password = config["password"]
    #
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    #     page = browser.new_page()
    #
    #     # PayPayはWebログインが限定的なので
    #     # モバイルUA偽装やAPI直接叩きが必要かもしれない
    #     # page.goto("https://www.paypay.ne.jp/portal/")
    #
    #     browser.close()
    #
    # return [{"asset_name": "PayPay残高", "amount": balance, "jpy_value": balance}]

    print("  [PayPay] TODO: implement")
    return []
