# mamoru

mamoruはDiscordとWEBで管理できる課題管理ツールです
通常の課題管理ツール機能に加え、友達や同じ講義をとっている人達をDiscord Serverに呼ぶことで、自分で課題をセットしなくても誰かがやってくれるので忘れないというメリットがあります。
1年生のハッカソンで作成し、以降ブラッシュアップを継続しています。


# System Tree
```
mamoru-env
│  .env <--Get from https://github.com/v2-2v/mamoru-env
│
├── data <--Get from https://github.com/v2-2v/mamoru-env
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
    ├── requirements.txt
    ├── web.py
    └── templates
        └── base.html
```
# Discord BOTの機能
- 課題、テストをセットする
- 課題、テスト題に対し、リアクションで取り組み、取り組み完了を操作
- あなたのの課題、テストを見る
-課題をセットした貢献数をカウントする
<img width="484" alt="スクリーンショット 2025-05-31 13 32 02" src="https://github.com/user-attachments/assets/3dba7fc7-4a47-454e-bd69-1b14dad2c0ba" />


# WEBの機能
- あなたの課題、テストを見る
- 自動定義を設定する
- 自動定義を閲覧、削除する
- Webhookによる不正ログイン通知を行う
<img width="1701" alt="スクリーンショット 2025-05-31 13 31 12" src="https://github.com/user-attachments/assets/0d259382-308c-4762-b7b1-78ffa630510e" />

![2025-06-22_15h53_31](https://github.com/user-attachments/assets/f9af6231-0b91-4fa9-93df-60f919f22d1d)


# setup

https://github.com/v2-2v/mamoru-env

# update
`git pull origin main`
