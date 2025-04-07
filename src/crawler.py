import json
import os
import time
import requests
from .errors import DataUpdateError
from datetime import datetime, timedelta

class DataCrawler:
    def __init__(self):
        self.data_dir = "./data"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://101.qq.com/'
        }
        
    def get_current_date(self):
        """获取当前数据日期"""
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y%m%d")
        
    def get_data_path(self, date):
        """获取指定日期的数据文件路径"""
        return os.path.join(self.data_dir, f"champion_data_{date}.json")
        
    def load_local_data(self):
        """读取本地英雄数据"""
        current_date = self.get_current_date()
        data_path = self.get_data_path(current_date)
        
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f), current_date
        return None, current_date
        
    def fetch_online_data(self):
        """获取在线英雄数据"""
        yesterday = datetime.now() - timedelta(days=1)
        before_yesterday = datetime.now() - timedelta(days=2)
        
        # 先尝试获取昨天的数据
        date = yesterday.strftime("%Y%m%d")
        data = self.fetch_data_for_date(date)
        
        # 如果昨天的数据不存在，则获取前天的数据
        if not data:
            date = before_yesterday.strftime("%Y%m%d")
            data = self.fetch_data_for_date(date)
        
        return data

    def fetch_data_for_date(self, date):
        try:
            # 获取基础英雄列表
            hero_url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
            hero_response = requests.get(hero_url, headers=self.headers)
            hero_response.raise_for_status()
            hero_data = hero_response.json()
            
            # 获取胜率数据
            dtstatdate = date
            ts = int(time.time() * 1000)
            win_rate_url = f"https://lol.sw.game.qq.com/lol/lwdcommact/a20211015billboard/a20211015api/fight?dtstatdate={dtstatdate}&callback=getRankFightCallback&ts={ts}"
            win_rate_response = requests.get(win_rate_url, headers=self.headers)
            win_rate_response.raise_for_status()
            
            # 处理JSONP响应
            win_rate_text = win_rate_response.text
            win_rate_json = win_rate_text[win_rate_text.find('(') + 1:win_rate_text.rfind(')')]
            win_rate_data = json.loads(win_rate_json)
            
            # 解析result字符串
            result_data = json.loads(win_rate_data['data']['result'])
            champion_stats = {}
            
            # 解析英雄数据
            # 格式: "listcollect":"championId_rank_状态_胜率_登场率_对手数据..."
            for item in result_data['listcollect'].split('#'):
                if not item:
                    continue
                # 分割主要数据和对手数据
                main_data = item.split('_')
                if len(main_data) >= 5:
                    champion_id = int(main_data[0])  # 转为整数
                    rank = int(main_data[1])  # 排名
                    champion_stats[champion_id] = {
                        'rank': rank,
                        'win_rate': float(main_data[3]) * 100,  # 转换为百分比
                        'pick_rate': float(main_data[4]) * 100  # 转换为百分比
                    }
            
            # 合并数据
            champions = {}
            for champ in hero_data['hero']:
                champion_id = int(champ['heroId'])
                champions[champion_id] = {
                    'name': champ['name'],
                    'title': champ['title'],
                    'roles': champ['roles'],
                    'alias': champ['alias']
                }
                
                # 添加胜率数据
                if champion_id in champion_stats:
                    stats = champion_stats[champion_id]
                    champions[champion_id].update({
                        'rank': stats['rank'],
                        'win_rate': stats['win_rate'],
                        'pick_rate': stats['pick_rate']
                    })
            
            # 获取英雄详细数据
            # for champion_id in champions:
            #     detail_url = f"https://game.gtimg.cn/images/lol/act/img/js/hero/{champion_id}.js"
            #     detail_response = requests.get(detail_url, headers=self.headers)
            #     if detail_response.status_code == 200:
            #         detail_data = detail_response.json()
            #         if 'skins' in detail_data:
            #             champions[champion_id]['skins'] = len(detail_data['skins'])
            #         if 'spells' in detail_data:
            #             champions[champion_id]['abilities'] = [spell['name'] for spell in detail_data['spells']]
            
            # 保存数据
            self.save_data(champions, dtstatdate)
            return {str(k): v for k, v in champions.items()}
            
        except requests.exceptions.RequestException as e:
            raise DataUpdateError(f"获取在线数据失败: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise DataUpdateError(f"解析数据失败: {str(e)}")
    
    def save_data(self, data, date):
        """保存数据到本地"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            data_path = self.get_data_path(date)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise DataUpdateError(f"保存数据失败: {str(e)}")
            
    def get_champion_data(self, force_update=False):
        """获取英雄数据，优先使用本地数据
        
        Args:
            force_update: 是否强制更新在线数据
        """
        if not force_update:
            local_data, current_date = self.load_local_data()
            if local_data:
                print(f"使用本地数据 (日期: {current_date})")
                return local_data
                
        print("获取在线数据...")
        return self.fetch_online_data() 