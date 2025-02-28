from PyQt6.QtCore import QObject, pyqtSignal
from .lcu import LCUClient
from .analyzer import ARAMAnalyzer
from .crawler import DataCrawler

class DataManager(QObject):
    # 定义信号
    summoner_data_updated = pyqtSignal(int, str, float, float, float, str)  # index, name, aram_rate, win_rate, kda, champion_info
    champion_data_updated = pyqtSignal(list)  # [(champion_id, name, rank, win_rate), ...]
    
    def __init__(self):
        super().__init__()
        self.lcu = LCUClient()
        self.analyzer = ARAMAnalyzer(self.lcu)
        self.crawler = DataCrawler()
        self.champion_data = {}
        self.last_select_data = None
        
    def init_data(self):
        """初始化数据"""
        try:
            # 连接客户端
            self.lcu.connect()
            # 获取英雄数据
            self.champion_data = self.crawler.get_champion_data()
            return True
        except Exception as e:
            print(f"初始化数据失败: {str(e)}")
            return False
            
    def update_game_data(self):
        """更新游戏数据"""
        try:
            # 获取游戏状态
            session = self.lcu.get_game_session()
            if session.get('phase') != 'ChampSelect':
                return
                
            # 获取英雄选择信息
            champ_select = self.lcu.get_champ_select_session()
            if not champ_select:
                return
                
            # 检查数据是否有更新
            current_select_data = (
                tuple(member.get('championId', 0) for member in champ_select.get('myTeam', [])),
                tuple(champ.get('championId') for champ in champ_select.get('benchChampions', []))
            )
            
            if current_select_data != self.last_select_data:
                # 更新召唤师信息
                summoner_list = self.lcu.get_summoner_list(None)
                for i, puuid in enumerate(summoner_list):
                    name, aram_rate, win_rate, kda = self.analyzer.analyze_summoner(puuid)
                    # 获取当前选择的英雄信息
                    current_champion_id = champ_select['myTeam'][i].get('championId', 0)
                    champion_info = "未选择"
                    if current_champion_id > 0 and str(current_champion_id) in self.champion_data:
                        info = self.champion_data[str(current_champion_id)]
                        champion_info = f"{info['name']} [{info.get('rank', '未知')}] {info.get('win_rate', 0):.1f}%"
                    
                    self.summoner_data_updated.emit(i, name, aram_rate, win_rate, kda, champion_info)
                
                # 更新可选英雄信息
                bench_champions = []
                if 'benchChampions' in champ_select and champ_select['benchChampions']:
                    # 有备选英雄时，只显示备选英雄
                    for bench_champ in champ_select['benchChampions']:
                        champion_id = bench_champ['championId']
                        if str(champion_id) in self.champion_data:
                            info = self.champion_data[str(champion_id)]
                            bench_champions.append((
                                champion_id,
                                info['name'],
                                info.get('rank', 999),
                                info.get('win_rate', 0)
                            ))
                else:
                    # 没有备选英雄时，显示胜率最高的12个英雄
                    all_champions = []
                    for champion_id, info in self.champion_data.items():
                        all_champions.append((
                            int(champion_id),
                            info['name'],
                            info.get('rank', 999),
                            info.get('win_rate', 0)
                        ))
                    # 按胜率排序并取前12个
                    all_champions.sort(key=lambda x: x[3], reverse=True)
                    bench_champions = all_champions[:12]
                
                # 发送更新信号（包含实际数量的英雄信息）
                self.champion_data_updated.emit(bench_champions)
                
                self.last_select_data = current_select_data
                
        except Exception as e:
            print(f"更新游戏数据失败: {str(e)}") 