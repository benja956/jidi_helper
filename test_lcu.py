from src.lcu import LCUClient
from src.analyzer import ARAMAnalyzer

def main():
    client = LCUClient()
    analyzer = ARAMAnalyzer(client)
    
    try:
        # 连接到客户端
        summoner = client.connect()
        print("当前召唤师信息:", summoner)
        
        # 获取召唤师统计信息
        puuid = summoner['puuid']
        name, aram_rate, win_rate, kda = analyzer.analyze_summoner(puuid)
        print(f"召唤师: {name}")
        print(f"大乱斗含量: {aram_rate}%")
        print(f"胜率: {win_rate}%")
        print(f"平均KDA: {kda}")
        
        # 获取游戏状态
        session = client.get_game_session()
        print("当前游戏状态:", session.get('phase', 'UNKNOWN'))
        
        # 如果在英雄选择阶段
        if session.get('phase') == 'ChampSelect':
            # 获取英雄选择信息
            champ_select = client.get_champ_select_session()
            print("英雄选择信息:", champ_select)
            
            # 获取可选英雄列表
            available_champions = client.get_available_champions()
            print("可选英雄数量:", len(available_champions))
            
            # 获取会话ID和召唤师列表
            chat_id = client.get_chat_id()
            if chat_id:
                puuid_list = client.get_summoner_list(chat_id)
                print("对局召唤师列表:", puuid_list)
        
    except Exception as e:
        print("错误:", str(e))

if __name__ == "__main__":
    main() 