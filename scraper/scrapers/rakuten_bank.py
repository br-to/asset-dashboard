"""
楽天銀行 - 残高取得 (Playwright + Firefox)
Cookie永続化で合言葉認証をスキップ。Cookieが無効な場合はエラーを返す。
"""

import os
import sys
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config_loader import load_config

LOGIN_URL = "https://fes.rakuten-bank.co.jp/MS/main/RbS?CurrentPageID=START&&COMMAND=LOGIN"
COOKIE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rakuten_cookies.json")


def _load_config():
    return load_config()["rakuten_bank"]


def _load_cookies():
    if os.path.exists(COOKIE_PATH):
        with open(COOKIE_PATH) as f:
            return json.load(f)
    return None


def _save_cookies(cookies):
    os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
    with open(COOKIE_PATH, "w") as f:
        json.dump(cookies, f)


def fetch_balances(config: dict = None) -> list[dict]:
    """楽天銀行の残高を取得する"""
    from playwright.sync_api import sync_playwright

    if config is None:
        config = _load_config()

    username = config["username"]
    password = config["password"]

    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=True)
        context = browser.new_context()

        # Cookie復元
        saved_cookies = _load_cookies()
        if saved_cookies:
            context.add_cookies(saved_cookies)

        page = context.new_page()

        # ログイン
        page.goto(LOGIN_URL, timeout=30000)
        page.wait_for_selector('input[id="LOGIN:USER_ID"]', timeout=15000)
        page.fill('input[id="LOGIN:USER_ID"]', username)
        page.fill('input[id="LOGIN:LOGIN_PASSWORD"]', password)
        page.click("a.btn-login-01")
        page.wait_for_load_state("networkidle", timeout=20000)

        text = page.inner_text("body")

        # 合言葉認証が出た場合
        if "INPUT_BRANCH_CODE" in page.content():
            browser.close()
            raise Exception(
                "合言葉認証が必要です。手動でログインしてCookieを更新してください。"
            )

        # 通知ページをスキップ
        for _ in range(5):
            text = page.inner_text("body")
            if "My Accountへ進む" in text:
                page.click("text=My Accountへ進む")
                page.wait_for_load_state("networkidle", timeout=20000)
            elif "変更しない" in text and "変更不要" in text:
                page.click("text=変更不要")
                page.wait_for_load_state("networkidle", timeout=20000)
            else:
                break

        text = page.inner_text("body")

        # Cookie保存
        _save_cookies(context.cookies())

        balances = []

        # 普通預金
        match = re.search(r"普通預金\s*(?:\S+\s*)*?([0-9,]+)円", text)
        if match:
            amount = int(match.group(1).replace(",", ""))
            balances.append({
                "service": "rakuten_bank",
                "asset_name": "JPY(普通預金)",
                "amount": amount,
                "jpy_value": amount,
            })

        # 定期預金
        match = re.search(r"定期預金\s*\n?\s*([0-9,]+)円", text)
        if match:
            amount = int(match.group(1).replace(",", ""))
            if amount > 0:
                balances.append({
                    "service": "rakuten_bank",
                    "asset_name": "JPY(定期預金)",
                    "amount": amount,
                    "jpy_value": amount,
                })

        # 楽天証券連携
        match = re.search(r"楽天証券\s*\n?資産残高\s*([0-9,]+)\s*円", text)
        if match:
            amount = int(match.group(1).replace(",", ""))
            if amount > 0:
                balances.append({
                    "service": "rakuten_sec",
                    "asset_name": "JPY(証券)",
                    "amount": amount,
                    "jpy_value": amount,
                })

        # フォールバック: 総額から取得
        if not balances:
            match = re.search(r"総額（評価額）\s*([0-9,]+)\s*円", text)
            if match:
                amount = int(match.group(1).replace(",", ""))
                balances.append({
                    "service": "rakuten_bank",
                    "asset_name": "JPY(総額)",
                    "amount": amount,
                    "jpy_value": amount,
                })

        browser.close()

    return balances


if __name__ == "__main__":
    results = fetch_balances()
    print(json.dumps(results, indent=2, ensure_ascii=False))
