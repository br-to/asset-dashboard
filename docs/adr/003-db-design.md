# ADR-003: DB設計 - INSERT-only履歴保持

## ステータス
Accepted

## コンテキスト
残高データをどう保存するか。最新値だけ持つか、履歴を残すか。

## 決定

### INSERT-only設計を採用
- UPDATEせず、毎回INSERTで新しいレコードを追加する
- 最新残高は `SELECT ... ORDER BY fetched_at DESC LIMIT 1` で取得
- 過去の残高推移をグラフ表示できる

### スキーマ

```sql
CREATE TABLE balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,      -- 'gmo', 'coincheck', 'onchain', 'rakuten_bank', 'rakuten_sec', 'paypay'
    asset_name TEXT NOT NULL,   -- 'BTC', 'ETH', 'JPY', '普通預金', '投資信託' etc.
    amount REAL NOT NULL,       -- 数量
    jpy_value REAL,            -- 円換算（取得時点のレート）
    fetched_at TEXT NOT NULL    -- ISO 8601
);

CREATE INDEX idx_balances_service_fetched ON balances(service, fetched_at DESC);
CREATE INDEX idx_balances_fetched ON balances(fetched_at DESC);
```

### なぜINSERT-onlyか
- 資産推移の可視化が主要ユースケースの1つ。UPDATEだと履歴が消える
- SQLiteは書き込み頻度が低い（1日2-3回）のでデータ量は問題にならない
- 1年運用で: 6サービス x 平均5アセット x 3回/日 x 365日 = 約33,000行。SQLiteには余裕

### データ量が増えた場合
- 1年以上前のデータは日次サマリに集約するバッチを将来追加可能
- または単純にVACUUMで済む規模

## 結果
- 資産推移グラフをフロントで描画可能
- データのロールバック・デバッグが容易（レコードが残っている）
- パフォーマンス問題が発生する規模には当面ならない
