# mamoru for git

import asyncio
import random
import discord
from discord.ext import commands, tasks
import datetime
import json
import ast
import os
import string
from dotenv import load_dotenv
from pathlib import Path

mode = input("gati or sub: ")
if mode == "":
    mode = "sub"
print(mode, "で起動します")
# gati or sub
with open(f"../data/setting/{mode}.json", "r", encoding="utf-8") as file:
    data = json.load(file)  # JSONデータを辞書として読み込む

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

web_url = os.getenv("REDIRECT_URL").replace("callback", "")
tukaikatachid = data["tukaikatachid"]
kadaichid = data["kadaichid"]
cmdchid = data["cmdchid"]
osirasechid = data["osirasechid"]
testchid = data["testchid"]

mentionchid = data["mentionchid"]

kanrishachid = data["kanrishachid"]
logchid = data["logchid"]

guildid = data["guildid"]

TOKEN = data["TOKEN"]


if not os.path.exists("../data/count.json"):
    print("no file count.json")
    exit(1)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)


@bot.event
async def on_ready():
    print("start GIT mode", mode)
    global today
    today = datetime.datetime.now().day  # 1ケタday
    await bot.change_presence(activity=discord.Game(f"{today}日だお"))
    loop.start()


@tasks.loop(minutes=1)
async def loop():
    global today
    nowday = datetime.datetime.now().day
    if nowday == today:
        channel = bot.get_channel(osirasechid)
    else:
        today = nowday
        await bot.change_presence(activity=discord.Game(f"{today}日だお"))
        channel = bot.get_channel(osirasechid)
        await channel.send(f"日付を{today}日に更新")
        await daily()
        await kda()
        await kdl()
        await auto_set()  # ->set課題へ飛ばす


@bot.command()
async def h(ctx):
    if ctx.channel.id != kanrishachid:
        return
    # await daily()
    # await kda()
    # await kdl()
    await auto_set()


def count(user, type):
    with open("../data/count.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    find = False
    for hoge in data:
        if user == hoge["user"] and type == hoge["type"]:
            hoge["count"] += 1
            find = True
    if not find:
        data.append(
            {
                "user": user,
                "type": type,
                "count": 1,
            }
        )
    with open("../data/count.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


@bot.command()
async def ao(ctx, name, youbi, target):
    if ctx.channel.id != cmdchid:
        return
    try:  # オンデマンド自動セット
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        days = ["1", "2", "3", "4", "5", "6", "7"]
        if not youbi in weekdays:
            await ctx.send("arg2を月〜日で指定してください")
            return
        if not target in days:
            await ctx.send("arg3を1-7で指定してください")
            return
        new_data = {"pushyoubi": youbi, "targetday": target, "name": name}
        with open("../data/onde.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # JSONデータを辞書として読み込む
        find = False
        for ff in data:
            if ff["name"] == new_data["name"]:
                ff["pushyoubi"] = new_data["pushyoubi"]
                ff["targetday"] = new_data["targetday"]
                find = True
                await ctx.send(
                    f"上書き完了です。__{name}__という科目を__{youbi}曜日__になった瞬間自動でセットし、__{target}日後__を締め切りとして設定し直しました。"
                )
        if not find:
            data.append(new_data)
            await ctx.send(
                f"登録完了です。__{name}__という科目を__{youbi}曜日__になった瞬間自動でセットし、__{target}日後__を締め切りとして設定しました。"
            )
        with open("../data/onde.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        await ctx.send("onde.jsonが見つかりません")


async def auto_set():
    channel = bot.get_channel(logchid)
    tomorrow = datetime.date.today()
    today = tomorrow.strftime("%m%d")  # 今日をstr 4ケタで取得
    try:
        with open("../data/auto.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # JSONデータを辞書として読み込む
        for line in data:
            if line["pushday"] == today and line["pushed"] == "no":
                line["pushed"] = "yes"
                await setkadai(line["name"], line["end"])

        with open("../data/auto.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        channel = bot.get_channel(logchid)
        await channel.send("auto.jsonが見つかりません")

    try:  # オンデマンド自動セット
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        sss = datetime.datetime.today().weekday()
        youbi = weekdays[sss]  # 今の月火水木金土日
        with open("../data/onde.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # JSONデータを辞書として読み込む
        todaymmdd = datetime.date.today().strftime("%m%d")
        for line in data:
            if youbi == line["pushyoubi"]:  # 対象の日付が今日なら
                targetday = int(line["targetday"])
                targetdaymmdd = (
                    datetime.date.today() + datetime.timedelta(days=targetday)
                ).strftime("%m%d")
                await setkadai(line["name"] + " " + todaymmdd, str(targetdaymmdd))
        with open("../data/onde.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        channel = bot.get_channel(logchid)
        await channel.send("onde.jsonが見つかりません")
    return


async def setkadai(kadai, day):  ##自動
    try:
        int(day)
    except ValueError:
        return
    data = {"task_name": kadai, "task_date": day, "user": ""}
    try:
        # ファイルが存在する場合、データを読み込む
        with open("../data/task.json", "r", encoding="utf-8") as file:
            file_content = file.read()
        if file_content:
            olddata = json.loads(file_content)
        else:
            olddata = []
    except FileNotFoundError:
        channel = bot.get_channel(logchid)
        await channel.send("ファイルを作成")
        olddata = []
    if not isinstance(
        olddata, list
    ):  # 既存のデータをリストに変換するか、空のリストから始める
        olddata = []
    name_exists = any(
        item["task_name"] == kadai for item in olddata
    )  # 重複データのチェック（課題名をチェック）
    if name_exists:
        return
    else:
        olddata.append(data)
        with open(
            "../data/task.json", "w", encoding="utf-8"
        ) as file:  # ファイルへの書き込み
            json.dump(olddata, file, ensure_ascii=False, indent=4)
    embed = discord.Embed(title=f"{kadai}", description=f"{day}")
    embed.add_field(
        name=f"by 自動書記",
        value="取り組む場合は🫡を押してください\n取り組んだ場合は☑を押してください\n締切済やミス等でクローズする場合は❌を押してください",
        inline=False,
    )
    channel = bot.get_channel(kadaichid)
    new_message = await channel.send(embed=embed)
    channel = bot.get_channel(mentionchid)
    await channel.send(f"{kadai}({day})が自動で追加されました")
    await new_message.add_reaction("🫡")
    await new_message.add_reaction("☑")
    await new_message.add_reaction("❌")
    count("自動書記", "課題定義")


async def kdl():
    delday = datetime.date.today() - datetime.timedelta(days=1)  # 1日前
    dalday = delday.strftime("%m%d")  # str 4ケタで取得
    with open("../data/task.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    for item in data:
        if str(item["task_date"]) == dalday:
            delname = item["task_name"]
            with open("../data/task.json", "r", encoding="utf-8") as file:
                tasks = json.load(file)
                split_strings = [
                    task for task in tasks if task["task_name"] != f"{delname}"
                ]  # 科目によってデータを消す
                newalldata = ",".join(
                    map(str, split_strings)
                )  # []がないstrにする ここまで正常6:19
                newalldata = newalldata.replace("'", '"')
                jjdata = f"[\n{newalldata}\n]"
                dict_obj = dict_obj = ast.literal_eval(jjdata)
                with open("../data/task.json", "w", encoding="utf-8") as new_json_file:
                    json.dump(dict_obj, new_json_file, ensure_ascii=False, indent=4)
                channel = bot.get_channel(osirasechid)
                await channel.send(f"1日前({delday})の課題{delname}をデータから削除")


async def kda():
    status = 1
    tomorrow = datetime.date.today()
    tomorrow = tomorrow.strftime("%m%d")  # 明日をstr 4ケタで取得
    with open("../data/task.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    channel = bot.get_channel(osirasechid)

    for item in data:
        if str(item["task_date"]) == tomorrow:
            status = 0
            jtaskname = item["task_name"]
            juser = item["user"]  # JSONから入手したuser
            if juser == "":
                ms = f"### 今日は__{jtaskname}__の締切日である__{tomorrow}__です。\n取り組んでいる人はいません。"
                await channel.send(ms)
            else:
                str_list = juser.split(",")
                userid_list = [item for item in str_list]
                mentions = [f"<@{user_id}>" for user_id in userid_list]
                mention_text = " ".join(mentions)
                ms = f"### 今日は__{jtaskname}__の締切日である__{tomorrow}__です。\n{mention_text}"
                await channel.send(ms)
    if status == 1:
        await channel.send(
            "今日締切の課題はありません。\n"
        )  # ここより上のtomorrowはtoday
    status = 1
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = tomorrow.strftime("%m%d")  # 明日をstr 4ケタで取得
    channel = bot.get_channel(osirasechid)
    with open("../data/task.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    for item in data:
        if str(item["task_date"]) == tomorrow:
            status = 0
            jtaskname = item["task_name"]
            juser = item["user"]  # JSONから入手したuser
            if juser == "":
                ms = f"### 明日は__{jtaskname}__の締切日である__{tomorrow}__です。\n取り組んでいる人はいません。"

                await channel.send(ms)
            else:
                str_list = juser.split(",")
                userid_list = [item for item in str_list]
                mentions = [f"<@{user_id}>" for user_id in userid_list]
                mention_text = " ".join(mentions)
                ms = f"### 明日は__{jtaskname}__の締切日である__{tomorrow}__です。はよやれ。\n{mention_text}"

                await channel.send(ms)
    if status == 1:
        await channel.send("明日締切の課題はありません。")
    random_number = random.randint(0, 9)
    await channel.send("https://picsum.photos/640/5" + str(random_number))  ##GG


async def daily():  # デイリー報告
    www = datetime.datetime.now().strftime("%m%d")
    channel = bot.get_channel(osirasechid)
    random_number = random.randint(0, 9)
    await channel.send("https://picsum.photos/640/5" + str(random_number))  ##GG
    await channel.send(f"# 本日({www})の未終了課題一覧の報告です")
    guild = bot.get_guild(guildid)
    allmemberid = [str(member.id) for member in guild.members if not member.bot]
    with open("../data/task.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    user_tasks = {user: [] for user in allmemberid}
    result = ""
    for task in data:
        user_ids = task["user"].split(",")
        for user_id in user_ids:
            if user_id in user_tasks:
                user_tasks[user_id].append(
                    {"task_name": task["task_name"], "task_date": task["task_date"]}
                )
    for user_id, tasks in user_tasks.items():
        # タスクが存在しないユーザーをスキップ
        if not tasks:
            continue
        result = f"<@{user_id}>\n"
        for task in tasks:
            result += f'__{task["task_name"]}({task["task_date"]})__\n'
        channel = bot.get_channel(osirasechid)
        await channel.send(result)


@bot.command()
async def myid(ctx):
    await ctx.send(f"{ctx.author.id}")

@bot.command()
async def myt(ctx):
    # コマンドを実行したユーザーのメンション
    user = ctx.author
    # ユーザーが個人DMでコマンドを実行した場合
    if True:
        i = 0
        await ctx.send(f"{user}の未終了テスト一覧です")
        allmemberid = [f"{user.id}"]
        try:
            with open("../data/test.json", "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            await ctx.send("テストデータがありません")
            return
            
        user_tasks = {user: [] for user in allmemberid}
        result = ""
        for task in data:
            user_ids = task["user"].split(",")
            for user_id in user_ids:
                if user_id in user_tasks:
                    user_tasks[user_id].append(
                        {"task_name": task["task_name"], "task_date": task["task_date"]}
                    )
                    i = i + 1
        for user_id, tasks in user_tasks.items():
            # タスクが存在しないユーザーをスキップ
            if not tasks:
                continue
        name = f"<@{user_id}>\n"
        for task in tasks:
            result += f'__{task["task_name"]}({task["task_date"]})__\n'
        lines = result.split("\n")
        sorted_lines = sorted(
            [line for line in lines if line.rfind("(") != -1 and line.rfind(")") != -1],
            key=lambda line: int(line[line.rfind("(") + 1 : line.rfind(")")]),
            reverse=False,
        )
        sorted_data = "\n".join(sorted_lines)
        await ctx.send(name + sorted_data + f"\nテスト数: {i}")
        count(f"{user.id}", "!mytコマンド使用")
    # サーバーチャンネルの場合は無視
    else:
        pass  # 何もしない


@bot.command()
async def my(ctx):
    # コマンドを実行したユーザーのメンション
    user = ctx.author
    # ユーザーが個人DMでコマンドを実行した場合
    if True:
        i = 0
        await ctx.send(f"{user}の未終了課題一覧です")
        allmemberid = [f"{user.id}"]
        with open("../data/task.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        user_tasks = {user: [] for user in allmemberid}
        result = ""
        for task in data:
            user_ids = task["user"].split(",")
            for user_id in user_ids:
                if user_id in user_tasks:
                    user_tasks[user_id].append(
                        {"task_name": task["task_name"], "task_date": task["task_date"]}
                    )
                    i = i + 1
        for user_id, tasks in user_tasks.items():
            # タスクが存在しないユーザーをスキップ
            if not tasks:
                continue
        name = f"<@{user_id}>\n"
        for task in tasks:
            result += f'__{task["task_name"]}({task["task_date"]})__\n'
        lines = result.split("\n")
        sorted_lines = sorted(
            [line for line in lines if line.rfind("(") != -1 and line.rfind(")") != -1],
            key=lambda line: int(line[line.rfind("(") + 1 : line.rfind(")")]),
            reverse=False,
        )
        sorted_data = "\n".join(sorted_lines)
        await ctx.send(
            name
            + sorted_data
            + f"\n課題数: {i}\n [ここ]({web_url})で見たり自動登録が設定できます"
        )
        count(f"{user.id}", "!myコマンド使用")
    # サーバーチャンネルの場合は無視
    else:
        pass  # 何もしない


@bot.command()
async def fs(ctx):
    if ctx.channel.id != kanrishachid:
        return
    await daily()


@bot.command()
async def fc(ctx):
    if ctx.channel.id != kanrishachid:
        return
    await kda()


@bot.command()
async def ff(ctx):
    if ctx.channel.id != kanrishachid:
        return
    await kdl()


@bot.command()
async def o(ctx, kadai, day):
    if ctx.channel.id != cmdchid:
        return
    try:
        int(day)
    except ValueError:
        await ctx.reply("4桁半角数字の正しい期日を入力してください")
        await ctx.message.add_reaction("💩")
        return
    random_number = random.randint(0, 318)
    if random_number == 77:
        channel = bot.get_channel(cmdchid)
        await channel.send("おめでとうございます。319分の1の確率を引きました！")
    data = {"task_name": kadai, "task_date": day, "user": ""}
    try:
        # ファイルが存在する場合、データを読み込む
        with open("../data/task.json", "r", encoding="utf-8") as file:
            file_content = file.read()
        if file_content:
            olddata = json.loads(file_content)
        else:
            olddata = []
    except FileNotFoundError:
        channel = bot.get_channel(logchid)
        await channel.send("ファイルを作成")
        olddata = []
    if not isinstance(
        olddata, list
    ):  # 既存のデータをリストに変換するか、空のリストから始める
        olddata = []
    name_exists = any(
        item["task_name"] == kadai for item in olddata
    )  # 重複データのチェック（課題名をチェック）
    if name_exists:
        await ctx.reply("課題名が重複しています")
        await ctx.message.add_reaction("💩")
        return
    else:
        olddata.append(data)
        with open(
            "../data/task.json", "w", encoding="utf-8"
        ) as file:  # ファイルへの書き込み
            json.dump(olddata, file, ensure_ascii=False, indent=4)
    embed = discord.Embed(title=f"{kadai}", description=f"{day}")
    embed.add_field(
        name=f"by {ctx.author.name}",
        value="取り組む場合は🫡を押してください\n取り組んだ場合は☑を押してください\n締切済やミス等でクローズする場合は❌を押してください",
        inline=False,
    )
    channel = bot.get_channel(kadaichid)
    new_message = await channel.send(embed=embed)
    await ctx.message.add_reaction("⭕")
    await new_message.add_reaction("🫡")
    await new_message.add_reaction("☑")
    await new_message.add_reaction("❌")
    count(f"{ctx.author.id}", "課題定義")


@bot.command()
async def t(ctx, kadai, day):
    if ctx.channel.id != cmdchid:
        return
    try:
        int(day)
    except ValueError:
        await ctx.reply("4桁半角数字の正しい期日を入力してください")
        await ctx.message.add_reaction("💩")
        return
    if not "テスト" in kadai:
        await ctx.reply("最後にテストと追加してください")
        await ctx.message.add_reaction("💩")
        return
    random_number = random.randint(0, 318)
    if random_number == 77:
        channel = bot.get_channel(cmdchid)
        await channel.send("おめでとうございます。319分の1の確率を引きました！")
    data = {"task_name": kadai, "task_date": day, "user": ""}
    try:
        # ファイルが存在する場合、データを読み込む
        with open("../data/test.json", "r", encoding="utf-8") as file:
            file_content = file.read()
        if file_content:
            olddata = json.loads(file_content)
        else:
            olddata = []
    except FileNotFoundError:
        # ファイルが存在しない場合は空のリストで開始
        olddata = []
        # ファイルを作成
        with open("../data/test.json", "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
    
    if not isinstance(olddata, list):
        olddata = []
        
    name_exists = any(
        item["task_name"] == kadai for item in olddata
    )  # 重複データのチェック（課題名をチェック）
    if name_exists:
        await ctx.reply("課題名が重複しています")
        await ctx.message.add_reaction("💩")
        return
    else:
        olddata.append(data)
        with open(
            "../data/test.json", "w", encoding="utf-8"
        ) as file:  # ファイルへの書き込み
            json.dump(olddata, file, ensure_ascii=False, indent=4)
    embed = discord.Embed(title=f"{kadai}", description=f"{day}")
    embed.add_field(
        name=f"by {ctx.author.name}",
        value="取り組む場合は🫡を押してください\n取り組んだ場合は☑を押してください\n締切済やミス等でクローズする場合は❌を押してください",
        inline=False,
    )
    channel = bot.get_channel(testchid)
    new_message = await channel.send(embed=embed)
    await ctx.message.add_reaction("⭕")
    await new_message.add_reaction("🫡")
    await new_message.add_reaction("☑")
    await new_message.add_reaction("❌")
    count(f"{ctx.author.id}", "テスト定義")


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    if user == bot.user:
        return
    
    # チャンネルに応じてJSONファイルを選択
    if channel.id == testchid:
        json_name = "../data/test.json"
    else:
        json_name = "../data/task.json"
    
    embed = message.embeds[0]
    title = embed.title
    reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
    
    if str(reaction.emoji) == "🫡":  # 参加マーク
        try:
            with open(json_name, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            await channel.send(f"{json_name}ファイルが見つかりません")
            return
            
        for item in data:
            if str(item["task_name"]) == str(title):
                juser = item["user"]  # JSONから入手したuser
                if juser == "":  # userがいないなら
                    newjuser = str(user.id)
                else:  # userがいたら,の後に追加
                    split_strings = juser.split(",")  # strをリストに整形
                    if str(user.id) in split_strings:
                        return
                    split_strings.append(str(user.id))  # リストにuser.idを追加
                    newjuser = ",".join(map(str, split_strings))  # []がないstrにする
                
                item["user"] = newjuser
                with open(json_name, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                return

    elif str(reaction.emoji) == "☑":
        try:
            with open(json_name, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            await channel.send(f"{json_name}ファイルが見つかりません")
            return
            
        for item in data:
            if str(item["task_name"]) == str(title):
                juser = item["user"]  # JSONから入手したuser
                if juser == "":
                    return
                split_strings = juser.split(",")  # strをリストに整形
                if str(user.id) not in split_strings:
                    return
                split_strings.remove(str(user.id))  # リストからuser.idを消す
                newjuser = ",".join(map(str, split_strings))  # []がないstrにする
                item["user"] = newjuser
                with open(json_name, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                return
                
    elif str(reaction.emoji) == "❌":
        try:
            with open(json_name, "r", encoding="utf-8") as file:
                tasks = json.load(file)
        except FileNotFoundError:
            await channel.send(f"{json_name}ファイルが見つかりません")
            return
            
        mention_text = ""
        for item in tasks:
            if str(item["task_name"]) == str(title):
                juser = item["user"]  # JSONから入手したuserのstr
                if juser != "":
                    str_list = juser.split(",")
                    userid_list = [item for item in str_list if item != ""]
                    mentions = [f"<@{user_id}>" for user_id in userid_list]
                    mention_text = " ".join(mentions)
                break
                
        split_strings = [
            task for task in tasks if task["task_name"] != f"{title}"
        ]  # 科目によってデータを消す
        
        if not split_strings:
            # 空のリストの場合
            with open(json_name, "w", encoding="utf-8") as new_json_file:
                json.dump([], new_json_file, ensure_ascii=False, indent=4)
        else:
            with open(json_name, "w", encoding="utf-8") as new_json_file:
                json.dump(split_strings, new_json_file, ensure_ascii=False, indent=4)
                
        day = embed.description
        embed.clear_fields()
        embed.description = f"{user.name}によって{title}({day})がクローズされました\nこのメッセージは5秒後に消えます"
        await message.edit(embed=embed)
        await reaction.message.clear_reactions()
        await asyncio.sleep(5)
        await message.delete()  # 2.0追加りあくしょん消す
        channel = bot.get_channel(osirasechid)
        if mention_text == "<@>":
            mention_text = ""
        await channel.send(
            f"{title} {day}が{user.name}によってクローズされました。\n{mention_text}"
        )


@bot.command()
async def sss(ctx):
    if ctx.channel.id != kanrishachid:
        return
    file = open(f"tukaikata.txt", "r", encoding="utf-8")
    welcome = file.read()
    file.close()
    embed = discord.Embed(
        title="ようこそ",
        description=welcome + f"\n# 自動登録は[ここ]({web_url})でできます",
    )
    channel = bot.get_channel(tukaikatachid)
    await channel.send(embed=embed)


@bot.command()
async def app(ctx):
    # 個人DMでのみ動作
    if ctx.guild is not None:
        return
    characters = string.ascii_lowercase + string.digits
    random_code = ''.join(random.choice(characters) for _ in range(8))
    text=f"です。アプリ内で連携コードを入力してください\n"
    try:
        with open("../data/auth.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        # ファイルが存在しない場合は空のリストで開始
        json_data = []
    find=False
    for item in json_data:
        if item["user_id"] == str(ctx.author.id):
            find=True
            item["code"]=random_code # コードを更新
            item["user_name"]=str(ctx.author.name)
            text+=f"連携コードを更新したので以前のコードは無効化されました\n"
            break
    if not find:
        json_data.append({
        "user_name": str(ctx.author.name),
        "user_id": str(ctx.author.id),
        "code": random_code,
        "daily_houkoku":True
        })
    with open("../data/auth.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)
    await ctx.send("連携コードは")
    await ctx.send(random_code)
    await ctx.send(text)


def run_bot():
    bot.run(TOKEN)


if __name__ == "__main__":
    run_bot()
