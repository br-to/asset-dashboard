# ADR-001: 技術スタック選定

## ステータス
Accepted

## コンテキスト
複数の金融サービス（暗号資産取引所、銀行、証券、電子マネー）の残高を一元管理するダッシュボードを個人用途で構築する。

## 決定

### フロントエンド: Next.js (App Router) + TypeScript + Tailwind CSS
- App Routerを採用する理由: Server Componentsでバックエンドとの統合がシンプル。API RoutesでPythonスクレイパーの結果を返すだけなので軽量に保てる
- Tailwind CSS: ダッシュボードUIを素早く組める。デザインシステム不要な個人プロジェクトに適している
- TypeScript: 残高データの型定義で安全にフロントを書ける

### PWA対応
- next-pwaでService Worker + manifest.jsonを追加
- スマホからホーム画面追加で使える。ネイティブアプリ化は将来の選択肢として残す
- オフライン時はキャッシュ済みの最終取得データを表示

### スクレイパー: Python + Playwright
- GMOコイン/CoincheckはREST APIで取得。Pythonのrequestsで十分
- 楽天銀行/楽天証券/PayPayは公式APIが個人に開放されていないため、Playwrightでブラウザ操作してスクレイピング
- Playwrightを選んだ理由: Seleniumより高速、ヘッドレス動作が安定、async対応
- Node.js (Puppeteer等) ではなくPythonを選んだ理由: 暗号資産取引所のAPIライブラリがPythonに多い。ccxtなども将来使える

### データ保存: SQLite
- 個人用途でスケール不要。ファイル1つで完結するのでバックアップが楽
- INSERT-only設計で残高履歴を保持する。時系列で資産推移を追える
- 将来PostgreSQLに移行する場合もスキーマはそのまま使える

### 定期実行: cron
- VPS上でcronで定期実行。GitHub Actionsはスクレイピングに不向き（IP制限、ブラウザ起動コスト）
- 実行頻度: 1日2-3回程度で十分（リアルタイム性は不要）

## 却下した選択肢

### MoneyForward/Moneytree等の既存サービス
- 楽天銀行のAPI連携はある。ただし自分でデータを持てない、カスタマイズ不可、暗号資産のオンチェーン資産は対象外
- 自作することで全データを手元に保持し、好きなように加工・表示できる

### Supabase/PlanetScale等のクラウドDB
- 個人用途で外部DBは過剰。SQLiteで十分。ネットワークレイテンシもない

### React Native / Flutter (モバイルネイティブ)
- 初期はWeb+PWAで十分。ネイティブ機能（プッシュ通知等）が必要になったら検討する

## 結果
- フロント/バックエンドの分離が明確で、各層を独立して開発・テストできる
- Pythonスクレイパーは単独でもCLIとして動く
- SQLiteファイルをフロントから直接読むのでインフラが最小限
