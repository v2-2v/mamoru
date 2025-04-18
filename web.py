from flask import Flask, redirect, request, session, url_for
import requests
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション管理用のキー（開発用）
app.permanent_session_lifetime = timedelta(days=60)  # 任意の期間に変更可

# Discordアプリの設定
CLIENT_ID = '1149037728449699861'
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://localhost:5100/callback'

# 認証URL
AUTH_URL = "https://discord.com/oauth2/authorize?client_id=1149037728449699861&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5100%2Fcallback&scope=identify+guilds"

TOKEN_URL = 'https://discord.com/api/oauth2/token'
API_URL = 'https://discord.com/api/users/@me'
GUILDS_API_URL = 'https://discord.com/api/users/@me/guilds'


@app.route('/')
def home():
    if 'user' not in session:
        return '<a href="/login">Discordでログイン</a>'

    user = session['user']
    return f"hello {user['global_name']}"

@app.route('/login')
def login():
    return redirect(AUTH_URL)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'エラー：コードが見つかりませんでした'
    # トークンを取得
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': "identify guilds"
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    token_json = response.json()
    access_token = token_json.get('access_token')

    

    if not access_token:
        return 'トークンの取得に失敗しました'

    # ユーザー情報を取得
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_response = requests.get(API_URL, headers=headers)
    user_data = user_response.json()

    guilds_response = requests.get(GUILDS_API_URL, headers=headers)
    guilds_data = guilds_response.json()

    session.permanent = True
    session['guilds'] = guilds_data
    session['user'] = user_data

    return f'''
    <h1>ログイン成功！</h1>
    <p>{user_data["username"]}#{user_data["discriminator"]}</p>
    <p>{str(user_data)}</p>
    <p>{str(guilds_data)}</p>
    <a href="/logout">ログアウト</a>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('guilds', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True,port=5100)
