# Asset Dashboard

資産管理ダッシュボード。複数サービスの残高を一元管理する。

## 構成

- `frontend/` - Next.js (App Router) + TypeScript + PWA
- `scraper/` - Python (Playwright) データ取得 + SQLite保存

## セットアップ

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Scraper

```bash
cd scraper
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 設定ファイルを作成
cp config.example.yaml config.yaml
# config.yaml にAPIキー・ログイン情報を記入

# 実行
python main.py
```

## 対象サービス

| サービス | 取得方法 |
|---------|---------|
| GMOコイン | Private API |
| Coincheck | Private API |
| オンチェーン | Alchemy / Etherscan API |
| 楽天銀行 | Playwright スクレイピング |
| 楽天証券 | Playwright スクレイピング |
| PayPay | Playwright スクレイピング |

## DBスキーマ

`scraper/data/balances.db` に保存。履歴を残す設計（INSERTのみ）。

```sql
CREATE TABLE balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    asset_name TEXT NOT NULL,
    amount REAL NOT NULL,
    jpy_value REAL,
    fetched_at TEXT NOT NULL
);
```
