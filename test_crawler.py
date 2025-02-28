from src.crawler import DataCrawler

def main():
    crawler = DataCrawler()

    # 获取英雄数据
    data = crawler.get_champion_data(force_update=True)
    print(f"成功获取 {len(data)} 个英雄的数据")

    # 打印一些示例数据
    for champion_id, info in list(data.items())[:10]:
        print(f"\n英雄ID: {champion_id}")
        print(f"名称: {info['name']}")
        print(f"称号: {info['title']}")
        print(f"定位: {info['roles']}")
        if 'win_rate' in info:
            print(f"胜率: {info['win_rate']}%")
            print(f"登场率: {info['pick_rate']}%")
            # print(f"禁用率: {info['ban_rate']}%")

    # print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 