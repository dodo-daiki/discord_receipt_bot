# Discord会計Bot / Discord Receipt Bot

## 📝 概要 / Overview

このBotは、Discord上で簡単に会計報告を行うためのBotです。レシート画像を送信すると、購入者名・店舗名・金額を入力し、GoogleスプレッドシートおよびGoogle Driveに記録されます。

This bot enables easy receipt tracking in Discord. Users upload a receipt image, input store name and amount, and the data is recorded to Google Sheets and Drive.

---

## 🧩 機能一覧 / Features

- レシート画像をアップロード → 情報入力モーダルが表示
- サーバーごとに店舗リストを管理（「その他」から自由追加可）
- 合計金額の入力後、Google Apps Script 経由でシート・Driveに送信
- `/set_account_channel`, `/set_sheet_url`, `/set_folder_url`, `/show_settings` などの管理用コマンド

- Upload a receipt image → Modal prompts input of store and amount
- Per-server store list management (custom stores can be added)
- Submits data to Google Sheets and Drive via GAS
- Admin commands: `/set_account_channel`, `/set_sheet_url`, `/set_folder_url`, `/show_settings`

---

## 💬 Discordコマンド一覧 / Discord Slash Commands

以下のスラッシュコマンドは、サーバー管理者がBotを設定・運用するために使用します。

The following slash commands are for server administrators to configure and operate the bot:

| コマンド / Command              | 説明 / Description |
|--------------------------------|---------------------|
| `/set_account_channel`         | 現在のチャンネルをレシート投稿チャンネルとして設定します。<br>Sets the current channel as the designated receipt channel. |
| `/set_sheet_url [URL]`         | Googleスプレッドシートの共有URLを登録します。<br>Registers the Google Spreadsheet URL. |
| `/set_folder_url [URL]`        | Google Driveフォルダの共有URLを登録します。<br>Registers the Google Drive folder URL. |
| `/show_settings`               | 現在の設定状況（チャンネルID、シートID、フォルダID）を表示します。<br>Shows the current bot settings for the server. |

---

## 🚀 セットアップ手順 / Setup Instructions

### 1. クローン / Clone this repo
```bash
git clone https://github.com/yourname/discord_receipt_bot.git
cd discord_receipt_bot
```

### 2. 仮想環境構築 / Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージのインストール / Install dependencies
```bash
pip install -r requirements.txt
```

### 4. トークン・Webhookの設定 / Configure token & webhook
- `config_sample.py` をコピーして `config.py` を作成し、以下を設定してください：
```python
DISCORD_TOKEN = "あなたのBotトークン"
GAS_WEBHOOK_URL = "Google Apps ScriptのURL"
```

Copy `config_sample.py` to `config.py` and fill in:
- Your Discord bot token
- GAS Webhook URL

### 5. 起動 / Run the bot
```bash
python main.py
```

---

## 📌 注意事項 / Notes

- このBotは画像を一時的に `tmp/` フォルダに保存します。
- 「その他」で入力された店舗は、サーバーごとに `store_list.json` に記録されます。
- Google Apps Script 側の受信処理（画像受け取り、シート記録）も別途必要です。

- This bot saves images temporarily in the `tmp/` folder.
- Stores added via "その他/Other" are stored per-server in `store_list.json`.
- A separate Google Apps Script for receiving and storing data is required.

---

## 📄 ライセンス / License

MIT License

---

## 📧 開発者 / Author

- Dodo Daiki
- GitHub: [dodo-daiki](https://github.com/dodo-daiki)