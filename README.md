# mamoru

mamoruはDiscordとWEBで管理できる課題管理ツールです
通常の課題管理ツール機能に加え、友達や同じ講義をとっている人達をDiscord Serverに呼ぶことで、自分で課題をセットしなくても誰かがやってくれるので忘れないというメリットがあります。
1年生のハッカソンで作成し、以降ブラッシュアップをし続けています。

```
mamoru-env
│  .env
│
├── data
│   ├── auto.json
│   ├── count.json
│   ├── onde.json
│   ├── task.json
│   ├── test.json
│   ├── tukaikata.txt
│   ├── web_log.txt
│   └── setting
│       ├── gati.json
│       └── sub.json
│
└── mamoru <--- this repository
    ├── .gitignore
    ├── mamoru.py
    ├── README.md
    ├── tukaikata.txt
    ├── web.py
    └── templates
        └── base.html
```
WEB
- あなたの課題、テストを見る OK
- 自動定義を設定する　OK
- 自動定義を閲覧、削除する OK
- Webhookによる不正ログイン通知 OK
- logの追加 誰が何をしたか、バックアップファイルの名前 ../dataに OK

git pull origin main
