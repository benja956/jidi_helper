class ARAMAnalyzer:
    def __init__(self, lcu_client):
        self.lcu = lcu_client

    def analyze_summoner(self, puuid, begin_index=0, end_index=20):
        """分析召唤师的大乱斗数据
        
        Args:
            puuid: 召唤师的PUUID
            begin_index: 起始索引
            end_index: 结束索引
            
        Returns:
            tuple: (名字, 大乱斗含量, 胜率, KDA)
        """
        # 使用 lcu 客户端的方法获取对局历史
        resp = self.lcu.get_match_history(puuid, begin_index, end_index)
        return self._calculate_stats(resp["games"]["games"])
        
    def _calculate_stats(self, games):
        """计算统计数据
        
        Args:
            games: 对局记录列表
            
        Returns:
            tuple: (名字, 大乱斗含量, 胜率, KDA)
        """
        total_games = len(games)
        aram_games = 0
        wins = 0
        kda = 0
        name = ""
        
        for game in games:
            # 获取基本信息
            participant = game["participants"][0]
            stats = participant["stats"]
            name = game["participantIdentities"][0]["player"]["gameName"]
            
            # 统计大乱斗场次
            if game["queueId"] == 450:  # 450是大乱斗模式
                aram_games += 1
                
            # 统计胜场
            if stats["win"]:
                wins += 1
                
            # 计算KDA
            kills = stats["kills"]
            assists = stats["assists"]
            deaths = max(1, stats["deaths"])  # 防止除以0
            kda += (kills + assists) / deaths
        
        # 计算最终统计数据
        aram_rate = round(aram_games / total_games * 100)  # 大乱斗含量
        win_rate = round(wins / total_games * 100)  # 胜率
        avg_kda = round(kda / total_games, 1)  # 平均KDA
        
        return name, aram_rate, win_rate, avg_kda 