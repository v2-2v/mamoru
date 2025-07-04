from flask import Flask, redirect, request, session, url_for, render_template
import requests
import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
import json
from datetime import datetime
import urllib.parse

#LOG ADD add_log(session['user']["global_name"],"msg")

app = Flask(__name__)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
TARGET_DISCORD_SERVER=os.getenv("SERVER_ID")
app.secret_key = os.getenv("SECRET_KEY")
REDIRECT_URI = os.getenv("REDIRECT_URL")
WEBHOOK_URL=os.getenv("WEBHOOK_URL")

AUTH_URL = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=identify+guilds"

TOKEN_URL = 'https://discord.com/api/oauth2/token'
API_URL = 'https://discord.com/api/users/@me'
GUILDS_API_URL = 'https://discord.com/api/users/@me/guilds'

app.permanent_session_lifetime = timedelta(days=20)  # 任意の期間に変更可

def add_log(user,message):
    with open('../data/web_log.txt', 'a', encoding='utf-8') as f:
        f.write(f'{datetime.now().strftime('%Y-%m-%d-%H-%M')}::{user}::{message}\n')


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
        message = {
            "content": f"不正ログイン疑惑 {user_data}"
        }
        requests.post(WEBHOOK_URL, json=message)
        return "ERROR" #!-- Alart --!#
    session.permanent = True
    for guild in guilds_data:
        if guild["id"]==TARGET_DISCORD_SERVER:
            session['guilds'] = [guild]
    session['user'] = user_data
    add_log(session['user']["global_name"],"login")
    return redirect(url_for("sp1"))


@app.route("/sp4")
def sp4():
    ###正規チェック
    if 'user' not in session:
        return '<a href="/login">Discordでログイン</a>'
    if check_true_member(session["guilds"])==False:
        return "ERROR"
    ###正規チェック
    arg_ond_name = request.args.get('ond_name', '')
    body=""
    with open("../data/onde.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # JSONデータを辞書として読み込む
    for ff in data:
        if ff["name"]==arg_ond_name:
            data.remove(ff)
            body+=f"<h3>{arg_ond_name}を削除しました</h3>"
            msg=f"remove-{ff["name"]}-{ff["pushyoubi"]}-{ff["targetday"]}"
    
    with open("../data/onde.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    add_log(session['user']["global_name"],msg)
    message = {
            "content": msg
        }
    requests.post(WEBHOOK_URL, json=message)
    return render_template("base.html",title=f"削除完了",body=body)

@app.route("/sp3")
def sp3():
    ###正規チェック
    if 'user' not in session:
        return '<a href="/login">Discordでログイン</a>'
    if check_true_member(session["guilds"])==False:
        return "ERROR"
    ###正規チェック
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
    if request.method == 'GET':
        body="""
            <table>
                <tr>
                <th>科目名</th>
                <th>セットする曜日</th>
                <th>何日後</th>
                <th></th>
                <th></th>
                </tr>
        """
        with open("../data/onde.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # JSONデータを辞書として読み込む
        for kadai in data:
            body+=f"""
            <tr>
            <td>{kadai["name"]}</td>
            <td>{kadai["pushyoubi"]}</td>
            <td>{kadai["targetday"]}</td>
            <td><a href="sp2?ond_name={urllib.parse.quote(kadai["name"])}&weak={kadai["pushyoubi"]}&date={kadai["targetday"]}">変更</a></td>
            <td><a href="sp4?ond_name={urllib.parse.quote(kadai["name"])}">削除</a></td>
            </tr>
            """
        body+="</table>"

        return render_template("base.html",title=f"設定変更",body=body,addstyle=addstyle)


@app.route("/sp2",methods=["GET","POST"])
def sp2():
    ###正規チェック
    if 'user' not in session:
        return '<a href="/login">Discordでログイン</a>'
    if check_true_member(session["guilds"])==False:
        return "ERROR"
    ###正規チェック
    if request.method == 'POST':
        subject_name = request.form.get('ond_name')
        weekday = request.form.get('weak')
        days_later = request.form.get('date')
        if subject_name == "" or (not weekday in ["月","火","水","木","金","土"]) or (not days_later in ["1","2","3","4","5","6","7"]):
            return "error"

        new_data={
            "pushyoubi": weekday,
            "targetday": days_later,
            "name": subject_name
        }
        with open("../data/onde.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # JSONデータを辞書として読み込む
        
        find=False
        for ff in data:
            if ff["name"]==new_data["name"]:
                ff["pushyoubi"]=new_data["pushyoubi"]
                ff["targetday"]=new_data["targetday"]
                find=True
                body=f"<h3>{subject_name} という科目を {weekday}曜日 になった瞬間自動でセットし、 その日から{days_later}日後 を締め切りとして設定変更しました。</h3>"
                msg=f"change-{subject_name}-{weekday}-{days_later}"
        if not find:
            data.append(new_data)
            body=f"<h3>{subject_name} という科目を {weekday}曜日 になった瞬間自動でセットし、 その日から{days_later}日後 を締め切りとして設定しました。</h3>"
            msg=f"adding-{subject_name}-{weekday}-{days_later}"

        with open("../data/onde.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        add_log(session['user']["global_name"],msg)
        message = {
            "content": msg
        }
        requests.post(WEBHOOK_URL, json=message)
        return render_template("base.html",title=f"設定完了",body=body)
    arg_ond_name = request.args.get('ond_name', '')
    arg_weak = request.args.get('weak', '')
    arg_date = request.args.get('date', '')
    weak_select=""
    for www in ["月","火","水","木","金","土"]:
        if www == arg_weak:
            weak_select+=f'<option value="{www}" selected>{www}曜日</option>'
        else:
            weak_select+=f'<option value="{www}">{www}曜日</option>'
    date_select=""
    for www in ["7","6","5","4","3","2","1"]:
        if www == arg_date:
            date_select+=f'<option value="{www}" selected>{www}日後</option>'
        else:
            date_select+=f'<option value="{www}">{www}日後</option>'
    body=f"""
    <form action="/sp2" method="post">
    <label for="ond_name">科目名は？</label><br>
    <input type="text" id="ond_name" name="ond_name" value="{arg_ond_name}" required><br><br>

    <label for="weak">何曜日になった瞬間自動定義？</label><br>
    <select id="weak" name="weak">
    {weak_select}
    </select><br><br>

    <label for="date">何日後を締め切り？</label><br>
    <select id="date" name="date">
    {date_select}
    </select><br><br>

    <input type="submit" value="設定する">
    </form>

    """
    
    return render_template("base.html",title=f"自動登録を設定する",body=body)

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
    sorted_data = sorted(the_data, key=lambda x: x['date'],reverse=False)
    for ss in sorted_data:
        kadai_data+=f"""
        <tr>
            <td>{ss["name"].replace("<","").replace(">","")}</td>
            <td>{ss["date"]}</td>
        </tr>
        """
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
    sorted_data = sorted(the_data, key=lambda x: x['date'],reverse=False)
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
            <td>{ss["name"].replace("<","").replace(">","")}</td>
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

@app.route("/api/<string:id>")
def api(id):
    with open('../data/task.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    the_data=[]
    for task in data:
        if id in task["user"]:
            the_data.append({
                "name":f"{task["task_name"]}",
                "date":f"{task["task_date"]}"
            })
    sorted_data = sorted(the_data, key=lambda x: x['date'],reverse=False)
    kadai_data=[]
    for ss in sorted_data:
        kadai_data.append(
            {
                "name":ss["name"],
                "date":ss["date"]
            }
        )
    return json.dumps(kadai_data,ensure_ascii=False,indent=4)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('guilds', None)
    return redirect(url_for('home'))


def check_auth(code):
    if code == "":
        return False
    with open("../data/auth.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)
    for item in json_data:
        if item["code"]==code:
            return True
    return False

def get_user_data(code):
    if not check_auth(code):
        return {"ERROR":True}
    with open("../data/auth.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)
    for item in json_data:
        if item["code"]==code:
            return {
                "ERROR":False,
                "user_id":item["user_id"],
                "user_name":item["user_name"],
                "daily_houkoku":item["daily_houkoku"]
            }
    return {"ERROR":True}

@app.route("/auth/check",methods=["POST"])
def auth_check():
    code = request.json.get('code', '') if request.json else ''
    if check_auth(code):
        return json.dumps(get_user_data(code),ensure_ascii=False,indent=4)
    return json.dumps({"ERROR":True},ensure_ascii=False,indent=4)

@app.route("/auth/operation",methods=["POST"])
def auth_operation():
    code = request.json.get('code', '') if request.json else ''
    if not check_auth(code):
        return {"ERROR":True}
    arg2=request.json.get('arg2', '') if request.json else ''
    arg3=request.json.get('arg3', '') if request.json else ''
    user_data= get_user_data(code)
    if user_data["ERROR"]==True:
        return {"ERROR":True}
    #こっから先は正規ユーザーだ！
    if arg2=="get_my_task": #ここについか
        with open('../data/task.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        the_data=[]
        for task in data:
            if user_data["user_id"] in task["user"]:
                the_data.append({
                "name":f"{task["task_name"]}",
                "date":f"{task["task_date"]}"
            })
        sorted_data = sorted(the_data, key=lambda x: x['date'],reverse=False)
        task_data=[]
        for ss in sorted_data:
            task_data.append(
            {
                "name":ss["name"],
                "date":ss["date"]
            }
        )
        return json.dumps(task_data,ensure_ascii=False,indent=4)

    elif arg2=="get_all_task":
        with open('../data/task.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        the_data=[]
        for task in data:
            the_data.append({
                "name":f"{task["task_name"]}",
                "date":f"{task["task_date"]}"
            })
        return json.dumps(the_data,ensure_ascii=False,indent=4)
    
    elif arg2=="join_new_task":
        with open('../data/task.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for task in data:
            if task["task_name"]==arg3:
                if user_data["user_id"] in task["user"]:
                    return {"ERROR":True}
                task["user"]+=str(",")+str(user_data["user_id"])
                with open('../data/task.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                return {"ERROR":False}
        return {"ERROR":True}
    
    elif arg2=="delete_task":
        with open('../data/task.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for task in data:
            if task["task_name"]==arg3:
                if not user_data["user_id"] in task["user"]:
                    return {"ERROR":True}
                tasks=task["user"].split(",")
                tasks.remove(str(user_data["user_id"]))  # リストからuser.idを消す
                task["user"] = ",".join(map(str, tasks))  # []がないstrにする
                with open('../data/task.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                return {"ERROR":False}
        return {"ERROR":True}
    
    return {"ERROR":True}

if __name__ == '__main__':
    app.run(port=5100,host="0.0.0.0")
