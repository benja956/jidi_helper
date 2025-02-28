class Config:
    # 自动抢英雄开关
    AUTO_PICK_ENABLED = False
    
    # LCU API 接口映射
    LCU_APIS = {
        'get_session': '/lol-gameflow/v1/session',  # 获取当前会话
        'get_champ_select': '/lol-champ-select/v1/session',  # 获取英雄选择阶段信息
        'get_summoner': '/lol-summoner/v4/summoners',  # 获取召唤师信息
        'pick_champion': '/lol-champ-select/v1/session/actions/{actionId}',  # 选择英雄
        'get_champion_info': '/lol-champions/v1/inventories/{summonerId}/champions/{championId}',  # 获取英雄信息
        'get_available_champions': '/lol-champions/v1/owned-champions-minimal',  # 获取可选英雄列表
        'get_conversations': '/lol-chat/v1/conversations',  # 获取会话列表
        'get_messages': '/lol-chat/v1/conversations/{conversationId}/messages',  # 获取会话消息
        'get_match_history': '/lol-match-history/v1/products/lol/{puuid}/matches',  # 获取对局历史
    } 