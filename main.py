import sys
from PyQt6.QtWidgets import QApplication
from src.gui import MainWindow
from src.lcu import LCUClient
from src.analyzer import ARAMAnalyzer
from src.crawler import DataCrawler
from src.errors import *

def print_summoner_info(analyzer, puuid):
    """打印召唤师信息"""
    name, aram_rate, win_rate, kda = analyzer.analyze_summoner(puuid)
    print(f"\n召唤师: {name}")
    print(f"大乱斗含量: {aram_rate}%")
    print(f"胜率: {win_rate}%")
    print(f"平均KDA: {kda}")

def print_champion_info(champion_data, champion_id):
    """打印英雄信息"""
    if champion_id == 0:  # 未选择英雄
        print("未选择英雄")
        return
    info = champion_data[str(champion_id)]
    if info:
        rank_info = f"[排名:{info.get('rank', '未知')}]" if 'rank' in info else ""
        print(f"{rank_info}-{info['name']}-{info.get('win_rate', 0):.2f}%")
    else:
        print(f"未知英雄ID: {champion_id}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 