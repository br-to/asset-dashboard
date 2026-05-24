"""
楽天証券の残高をPlaywrightでスクレイピングする
"""

from playwright.sync_api import sync_playwright


def fetch(config: dict) -> list[dict]:
    """
    楽天証券の保有資産を取得して返す。
    Returns: [{"asset_name": "投資信託", "amount": 500000, "jpy_value": 500000}, ...]
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
    #     page.goto("https://www.rakuten-sec.co.jp/")
    #     page.click("text=ログイン")
    #     page.fill('#form-login-id input[name="loginid"]', username)
    #     page.fill('#form-login-pass input[name="passwd"]', password)
    #     page.click('button[type="submit"]')
    #     page.wait_for_load_state("networkidle")
    #
    #     # 保有資産一覧ページへ
    #     # page.goto("https://member.rakuten-sec.co.jp/app/ass_all_possess_lst.do")
    #
    #     browser.close()
    #
    # return assets

    print("  [楽天証券] TODO: implement")
    return []
