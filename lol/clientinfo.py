import subprocess
import re
import requests
import time
import json
import tkinter as tk

headers = {
    'Host': 'lol.sw.game.qq.com',
    'Referer': 'https://101.qq.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

ts = time.time() // 600

ps_command = '''Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "LeagueClientUx.exe" } | Select-Object -ExpandProperty CommandLine'''

# 使用 subprocess 执行 PowerShell 命令并捕获输出
process = subprocess.Popen(["powershell", "-Command", ps_command], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

# 解码输出为字符串，使用正确的编码处理字节流
result = stdout.decode("utf-8", errors="replace").strip()  # 使用 "replace" 处理解码错误的字符


# 提取token和port
auth_token = re.findall(r'--remoting-auth-token=([\w-]+)', result)[0]
port = re.findall(r'--app-port=(\d+)', result)[0]
baseurl = f"https://riot:{auth_token}@127.0.0.1:{port}"
print(baseurl)


def GetCurrConversationID():
    chatid = None
    foundcode = 0
    url = baseurl + "/lol-chat/v1/conversations"
    resp = requests.get(url, verify=False).json()
    for item in resp:
        if item["type"] == "championSelect":
            chatid = item["id"]
            foundcode = 1
            print("获取会话ID成功")
    if foundcode == 0:
        print("未发现对局会话ID")
    return chatid


def getgamerlist(cid):
    gamerlist = []
    url = baseurl + f"/lol-chat/v1/conversations/{cid}/messages"
    resp = requests.get(url, verify=False).json()
    for item in resp:
        gamerlist.append(item["fromSummonerId"])
    return list(set(gamerlist))


def calararate(uid, begIndex=0, endIndex=20):
    url = baseurl + f"/lol-match-history/v3/matchlist/account/{uid}?begIndex={begIndex}&endIndex={endIndex}"
    url = baseurl + f"/lol-match-history/v3/matchlist/account/d3162efc-cd4a-591f-a4a5-b548ac8ac281?begIndex={begIndex}&endIndex={endIndex}"
    url = baseurl + f"/lol-match-history/v1/products/lol/{puuid}/matches?begIndex={begIndex}&endIndex={endIndex}"
    resp = requests.get(url, verify=False).json()
    games = resp["games"]["games"]
    totaltime = len(games)
    aratime = 0
    wintime = 0
    kda = 0
    name = ""
    for item in games:
        if item["queueId"] == 450:
            aratime += 1
        if item["participants"][0]["stats"]["win"]:
            wintime += 1
        kills = item["participants"][0]["stats"]["kills"]
        assists = item["participants"][0]["stats"]["assists"]
        deaths = item["participants"][0]["stats"]["deaths"]
        if deaths == 0:
            deaths = 1
        kda += round((kills + assists) / deaths, 2)
        name = item["participantIdentities"][0]["player"]["summonerName"]
    ararate = round(aratime / totaltime * 100)
    winrate = round(wintime / totaltime * 100)
    kdaave = round(kda / totaltime, 1)
    return name, ararate, winrate, kdaave


def sendmsg(cid, text):
    url = baseurl + f"/lol-chat/v1/conversations/{cid}/messages"
    print(url)
    data = {
        "body": text,
        "type": "chat"
    }
    resp = requests.post(url, json=data, verify=False)


def info():
    chatid = GetCurrConversationID()
    gamerlist = getgamerlist(chatid)
    # gamerlist.append(4013697928)
    text = "近20场游戏数据\n"
    for uid in gamerlist:
        name, ararate, winrate, kdaave = calararate(uid)
        if winrate < 48:
            winlogo = "🥉"
        elif 48 <= winrate < 52:
            winlogo = "🥈"
        else:
            winlogo = "🥇"
        if ararate < 30:
            aralogo = "🥉"
        elif 30 <= ararate < 60:
            aralogo = "🥈"
        else:
            aralogo = "🥇"
        text += f"👶🏻{name}:胜率{str(winrate)}%{winlogo} 乱斗忠诚度{str(ararate)}%{aralogo} KDA{kdaave}\n"
    print(text)
    sendmsg(chatid, text)


def herolist():
    herodict = {}
    url = f"https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js?ts={ts}"
    response = requests.request("GET", url)
    response = response.json()
    ls = response["hero"]
    for item in ls:
        hid = item["heroId"]
        hname = item["name"]
        herodict[hid] = hname
    return herodict


def rankinfo():
    rankdict = {}

    dtstatdate = time.strftime("%Y%m%d", time.localtime(time.time() - 1 * 60 * 60 * 24))
    url = f"https://lol.sw.game.qq.com/lol/lwdcommact/a20211015billboard/a20211015api/fight?dtstatdate={dtstatdate}&callback=getRankFightCallback&ts={ts}"
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text[21:-1])
    listcollect = data["data"]["result"]
    if listcollect == "":
        dtstatdate = time.strftime("%Y%m%d", time.localtime(time.time() - 2 * 60 * 60 * 24))
        url = f"https://lol.sw.game.qq.com/lol/lwdcommact/a20211015billboard/a20211015api/fight?dtstatdate={dtstatdate}&callback=getRankFightCallback&ts={ts}"
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text[21:-1])
        listcollect = data["data"]["result"]
    listcollect = json.loads(listcollect)["listcollect"]
    rankinfolist = listcollect.split("#")
    for rankinfo in rankinfolist:
        rankinfo = rankinfo.split(",")[0].split("_")
        rankdict[rankinfo[0]] = {"win": rankinfo[3],
                                 "pick": rankinfo[4],
                                 "change": rankinfo[2]}
    rankdict = sorted(rankdict.items(), reverse=True, key=lambda x: x[1]["win"])
    return rankdict, dtstatdate


def rate(herolist=herolist()):
    chatid = GetCurrConversationID()
    rank, updatetime = rankinfo()
    wintext = f"\n😍‍😍‍😍‍胜率最高😍‍😍‍😍‍\n"
    losetext = f"\n😭😭😭胜率最低😭😭😭\n"
    updatetext = f"🆕{updatetime}"
    for index, item in enumerate(rank[:10]):
        wintext += f"⚡{herolist[item[0]]}"
        # if (index+1) % 3 == 0:
        #     wintext += "\n"

    for index, item in enumerate(rank[-10:]):
        losetext += f"⚡{herolist[item[0]]}"
        # if (index+1) % 3 == 0:
        #     losetext += "\n"

    msg = f"💯💯💯分奴小助手{updatetext}💯💯💯{wintext}{losetext}"
    sendmsg(chatid, msg)
    print(msg)


if __name__ == '__main__':
    window = tk.Tk()
    window.title('乱斗小工具')  # 标题
    window.geometry('250x120')  # 窗口尺寸
    bt1 = tk.Button(window, text='胜率', width=10, height=2, command=rate)
    bt1.place(x=30, y=30)
    bt2 = tk.Button(window, text='信息', width=10, height=2, command=info)
    bt2.place(x=150, y=30)
    window.mainloop()  # 显示
