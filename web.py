from flask import Flask, redirect, request, session, url_for, render_template
import requests
import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
import json

app = Flask(__name__)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
TARGET_DISCORD_SERVER=os.getenv("SERVER_ID")
app.secret_key = os.getenv("SECRET_KEY")
REDIRECT_URI = 'http://localhost:5100/callback'
AUTH_URL = "https://discord.com/oauth2/authorize?client_id=1149037728449699861&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5100%2Fcallback&scope=identify+guilds"

TOKEN_URL = 'https://discord.com/api/oauth2/token'
API_URL = 'https://discord.com/api/users/@me'
GUILDS_API_URL = 'https://discord.com/api/users/@me/guilds'

app.permanent_session_lifetime = timedelta(days=60)  # 任意の期間に変更可

def check_true_member(guilds): #give me session['guilds']
    for guild in guilds:
        if guild["id"]==TARGET_DISCORD_SERVER:
            return True
    return False

@app.route('/')
def home():
    if 'user' not in session:
        return '<a href="/login">Discordでログイン</a>'
    guilds = session['guilds'] 
    user = session['user']
    return redirect(url_for("sp1"))

@app.route('/login')
def login():
    return redirect(AUTH_URL)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return '<a href="/login">Discordでログイン</a>'
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
        return '<a href="/login">Discordでログイン</a>'

    # ユーザー情報を取得
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_response = requests.get(API_URL, headers=headers)
    user_data = user_response.json()

    guilds_response = requests.get(GUILDS_API_URL, headers=headers)
    guilds_data = guilds_response.json()
    if check_true_member(guilds_data)==False:
        return "ERROR" #!-- Alart --!#
    session.permanent = True
    session['guilds'] = guilds_data
    session['user'] = user_data

    return redirect(url_for("sp1"))

@app.route("/sp2")
def sp2():
    ###正規チェック
    if 'user' not in session:
        return '<a href="/login">Discordでログイン</a>'
    if check_true_member(session["guilds"])==False:
        return "ERROR"
    ###正規チェック
    body="sss"
    
    return render_template("base.html",title=f"オンデマンドの自動登録を設定する",body=body)
@app.route("/sp1")
def sp1():
    ###正規チェック
    if 'user' not in session:
        return '<a href="/login">Discordでログイン</a>'
    if check_true_member(session["guilds"])==False:
        return "ERROR"
    ###正規チェック
    body=""
    session_user=session['user']
    user_id=session_user['id']
    kadai_data="""
    <table>
        <tr>
            <th>課題名</th>
            <th>締め切り</th>
        </tr>
    """
    with open('../data/task.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    the_data=[]
    i=0
    for task in data:
        if user_id in task["user"]:
            the_data.append({
                "name":f"{task["task_name"]}",
                "date":f"{task["task_date"]}"
            })
            i+=1
    sorted_data = sorted(the_data, key=lambda x: x['date'])
    for ss in sorted_data:
        kadai_data+=f"""
        <tr>
            <td>{ss["name"]}</td>
            <td>{ss["date"]}</td>
        </tr>
        """
    print(sorted_data)
    body+=f"""<h4>あなたの課題</h4><p>課題数{i}</p>"""
    body+=kadai_data
    body+="""
    </table>
    <h4>あなたのテスト</h4>
    """
    with open('../data/test.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    the_data=[]
    for test in data:
        if user_id in test["user"]:
            the_data.append({
                "name":f"{test["task_name"]}",
                "date":f"{test["task_date"]}"
            })
    sorted_data = sorted(the_data, key=lambda x: x['date'])
    test_data="""
    <table>
        <tr>
            <th>テスト名</th>
            <th>日にち</th>
        </tr>
    """
    for ss in sorted_data:
        test_data+=f"""
        <tr>
            <td>{ss["name"]}</td>
            <td>{ss["date"]}</td>
        </tr>
        """
    body+=test_data
    body+="""
    </table>
    """
    addstyle="""
        table {
      border-collapse: collapse;
      width: 100%;
    }
    th, td {
      border: 1px solid #333;
      padding: 8px;
      text-align: center;
    }
    th {
      background-color: #f2f2f2;
    }
    """
    return render_template("base.html",title=f"ようこそ {session_user['global_name']}!",body=body,addstyle=addstyle)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('guilds', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True,port=5100,host="0.0.0.0")
