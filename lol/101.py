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

p = subprocess.Popen('WMIC PROCESS WHERE name="LeagueClientUx.exe" GET commandline',
                     shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     encoding='GBK'
                     )

stdout = p.communicate()[0]
print(stdout)

token = re.findall(r'--remoting-auth-token.*?"', stdout)[0].split("=")[1][:-1]

port = re.findall(r'--app-port=.*?"', stdout)[0].split("=")[1][:-1]

baseurl = f"https://riot:{token}@127.0.0.1:{port}"
print(baseurl)


# 根据召唤师ID获取当前选择的英雄ID
def get_champion_id(summoner_id):
    api_url = f"/lol-champ-select/v1/session"

    try:
        response = requests.get(baseurl+api_url, verify=False)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        for player in data['myTeam']:
            if player['summonerId'] == summoner_id:
                return player['championId']

        # 如果未找到匹配的召唤师ID
        return None

    except Exception as e:
        print(f"Error retrieving champion ID: {e}")
        return None


# 使用示例
# 替换以下的 'your_summoner_id'、'your_token' 和 'your_port' 为实际的召唤师ID、令牌和端口
summoner_id = 4013442975
champion_id = get_champion_id(summoner_id)

if champion_id is not None:
    print(f"Champion ID for summoner {summoner_id}: {champion_id}")
else:
    print("Champion ID not found.")
