"""
楽天銀行の残高をPlaywrightでスクレイピングする
"""

from playwright.sync_api import sync_playwright


def fetch(config: dict) -> list[dict]:
    """
    楽天銀行の残高を取得して返す。
    Returns: [{"asset_name": "普通預金", "amount": 1000000, "jpy_value": 1000000}, ...]
    """
    # TODO: Playwright実装
    # username = config["username"]
    # password = config["password"]
    #
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    #     page = browser.new_page()
    #
    #     # ログイン
    #     page.goto("https://fes.rakuten-bank.co.jp/MS/main/RbS?CurrentPageID=START&&COMMAND=LOGIN")
    #     page.fill('input[name="LOGIN:USER_ID"]', username)
    #     page.fill('input[name="LOGIN:LOGIN_PASSWORD"]', password)
    #     page.click('input[name="LOGIN:_actionLogin"]')
    #     page.wait_for_load_state("networkidle")
    #
    #     # 残高取得
    #     # balance_text = page.locator(".balance-selector").text_content()
    #     # balance = int(balance_text.replace(",", "").replace("円", ""))
    #
    #     browser.close()
    #
    # return [{"asset_name": "普通預金", "amount": balance, "jpy_value": balance}]

    print("  [楽天銀行] TODO: implement")
    return []
