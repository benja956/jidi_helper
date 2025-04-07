import subprocess
import re
import requests
import urllib3
from .errors import *
from .config import Config

class LCUClient:
    def __init__(self):
        self.auth_token = None
        self.port = None
        self.ws = None
        self.base_url = None
        self.config = Config
        # 禁用SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def get_client_key(self):
        """获取客户端key，使用PowerShell"""
        try:
            # 使用PowerShell命令获取进程信息
            # PowerShell 命令
            ps_command = '''Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "LeagueClientUx.exe" } | Select-Object -ExpandProperty CommandLine'''

            # 使用 subprocess 执行 PowerShell 命令并捕获输出
            process = subprocess.Popen(["powershell", "-Command", ps_command], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # 解码输出为字符串，使用正确的编码处理字节流
            result = stdout.decode("utf-8", errors="replace").strip()  # 使用 "replace" 处理解码错误的字符
            
            if not result.strip():
                raise ClientNotFoundError("未找到运行中的客户端")
            
            # 提取token和port
            self.auth_token = re.findall(r'--remoting-auth-token=([\w-]+)', result)[0]
            self.port = re.findall(r'--app-port=(\d+)', result)[0]
            self.base_url = f"https://riot:{self.auth_token}@127.0.0.1:{self.port}"
            
        except (subprocess.CalledProcessError, IndexError) as e:
            raise ClientNotFoundError(f"无法获取客户端信息: {str(e)}")
            
    def connect(self):
        """连接到LCU客户端"""
        if not self.auth_token or not self.port:
            self.get_client_key()
            
        # 测试连接
        try:
            response = requests.get(
                f'{self.base_url}/lol-summoner/v1/current-summoner',
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"连接LCU失败: {str(e)}")
            
    def request(self, method, endpoint, data=None):
        """发送HTTP请求到LCU"""
        try:
            response = requests.request(
                method,
                f'{self.base_url}{endpoint}',
                json=data,
                verify=False
            )
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {str(e)}")
            
    def get_chat_id(self):
        """获取当前会话ID"""
        resp = self.request('GET', '/lol-chat/v1/conversations')
        for item in resp:
            if item["type"] == "championSelect":
                print("获取会话ID成功")
                return item["id"]
        print("未发现对局会话ID")
        return None
        
    def get_summoner_list(self, chat_id):
        """获取对局召唤师列表"""
        # 获取英雄选择阶段信息
        champ_select = self.get_champ_select_session()
        if not champ_select or 'myTeam' not in champ_select:
            return []
        
        # 从myTeam中获取puuid列表
        puuid_list = []
        for member in champ_select['myTeam']:
            if member.get('puuid'):  # 确保puuid存在且非空
                puuid_list.append(member['puuid'])
            
        return puuid_list

    def get_game_session(self):
        """获取当前游戏会话信息"""
        return self.request('GET', Config.LCU_APIS['get_session'])

    def get_champ_select_session(self):
        """获取英雄选择阶段信息"""
        return self.request('GET', Config.LCU_APIS['get_champ_select'])

    def get_champion_info(self, champion_id):
        """获取英雄信息"""
        endpoint = f'/lol-champions/v1/inventories/{self.summoner_id}/champions/{champion_id}'
        return self.request('GET', endpoint)

    def pick_champion(self, action_id, champion_id, completed=True):
        """选择英雄"""
        data = {
            "actorCellId": action_id,
            "championId": champion_id,
            "completed": completed
        }
        endpoint = Config.LCU_APIS['pick_champion'].format(actionId=action_id)
        return self.request('PATCH', endpoint, data=data)

    def get_available_champions(self):
        """获取可选英雄列表"""
        return self.request('GET', '/lol-champions/v1/owned-champions-minimal')

    def get_match_history(self, puuid, begin_index=0, end_index=20):
        """获取对局历史
        
        Args:
            puuid: 召唤师的PUUID
            begin_index: 起始索引
            end_index: 结束索引
        """
        endpoint = Config.LCU_APIS['get_match_history'].format(puuid=puuid)
        return self.request('GET', f'{endpoint}?begIndex={begin_index}&endIndex={end_index}')

    def restart_client(self):
        """重启英雄联盟客户端"""
        try:
            self.request('POST', '/riotclient/kill-and-restart-ux')
        except Exception as e:
            raise Exception(f"重启客户端失败: {str(e)}")