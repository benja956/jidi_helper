import subprocess
import re
import requests
import webbrowser
import tkinter as tk
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 使用WMIC命令获取LeagueClientUx.exe的启动参数
p = subprocess.Popen('WMIC PROCESS WHERE name="LeagueClientUx.exe" GET commandline',
                     shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     encoding='GBK'
                     )

stdout = p.communicate()[0]

# 从启动参数中提取令牌和端口
token = re.findall(r'--remoting-auth-token.*?"', stdout)[0].split("=")[1][:-1]
port = re.findall(r'--app-port=.*?"', stdout)[0].split("=")[1][:-1]

# 构建LCU的基础URL
baseurl = f"https://riot:{token}@127.0.0.1:{port}"


# 获取英雄ID的相关函数
def GetChampionID(summoner_id):
    api_url = f"/lol-champ-select/v1/session"

    try:
        response = requests.get(baseurl + api_url, verify=False)
        response.raise_for_status()
        data = response.json()

        for player in data['myTeam']:
            if player['summonerId'] == summoner_id:
                return player['championId']

        # 如果未找到匹配的召唤师ID
        return None

    except Exception as e:
        # print(f"Error retrieving champion ID: {e}")
        return "未开始对局"


# 在浏览器中打开指定URL
def open_browser_with_url(hero_id):
    url = f"https://101.qq.com/#/hero-detail?heroid={hero_id}&datatype=fight&tab=overview"
    webbrowser.open(url)


# 恢复客户端分辨率的函数
def resolution():
    requests.post(url=baseurl + "/riotclient/kill-and-restart-ux", verify=False)


# 定时刷新英雄ID标签的函数
def update_champion_id_label():
    current_champion_id = GetChampionID(summoner_id)
    label_id.config(text=f"当前英雄ID：{current_champion_id}")
    root.after(500, update_champion_id_label)  # 每500毫秒刷新一次


# 获取召唤师ID和名字的函数
def get_summoner_id():
    get_settings_url = f"{baseurl}/lol-chat/v1/me"
    response = requests.get(get_settings_url, verify=False)
    settings_data = response.json()
    return settings_data['summonerId'], settings_data['name']


if __name__ == '__main__':
    # 获取召唤师ID和名字
    summoner_id, name = get_summoner_id()

    # 创建Tkinter窗口
    root = tk.Tk()
    root.title("符文天赋助手")
    root.geometry("250x250")

    # 添加标签用于显示当前召唤师名字
    label_name = tk.Label(root, text=f"当前召唤师名字：{name}", width=20, height=2)
    label_name.pack(pady=5)

    # 添加标签用于显示当前英雄ID
    label_id = tk.Label(root, text="当前英雄ID：", width=20, height=2)
    label_id.pack(pady=8)

    # 添加按钮并绑定事件处理器（打开101）
    button_open_browser = tk.Button(root, text="打开101",
                                    command=lambda: open_browser_with_url(GetChampionID(summoner_id)), width=20, height=2)
    button_open_browser.pack(pady=11)

    # 添加按钮并绑定事件处理器（恢复客户端）
    button_resolution = tk.Button(root, text="恢复客户端", command=lambda: resolution(), width=20, height=2)
    button_resolution.pack(pady=13)

    # 初始刷新
    update_champion_id_label()

    # 运行Tkinter事件循环
    root.mainloop()
