# Nora 天気予報アプリ

Noraによって開発された天気予報アプリです。このアプリは、日本の主要都市の天気情報を表示します。

## 機能

- 都市名を入力して天気を検索
- 気温、湿度、風速、気圧などの詳細情報を表示
- モバイルフレンドリーなレスポンシブデザイン

## 技術スタック

- Python 3.9
- Flask
- HTML/CSS
- Docker
- Fly.io (デプロイ)

## ローカルでの実行方法

```bash
# リポジトリをクローン
git clone https://github.com/yukihamada/nora.git
cd nora/data/generated/weather_app

# 依存関係をインストール
pip install -r requirements.txt

# アプリを実行
python app.py
```

ブラウザで http://localhost:8080 にアクセスしてアプリを使用できます。

## デプロイ

このアプリはFly.ioにデプロイされています。GitHub Actionsを使用して自動デプロイが設定されています。

## ライセンス

MIT

## 開発者

Nora - Autonomous Software Development Agent