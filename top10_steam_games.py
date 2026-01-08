import aiohttp
import asyncio
import json

class SteamDynamicTop:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def get_dynamic_top_appids(self, country: str = 'RU', limit: int = 50) -> list:
        """ДИНАМИЧЕСКИЙ топ Steam (скидки + продажи)"""
        url = f"https://store.steampowered.com/api/featured/?cc={country}"
        async with self.session.get(url) as resp:
            data = await resp.json()
        
        appids = []
        
        # 1. Топ-продажи
        if 'top_sellers' in data:
            appids.extend([item['id'] for item in data['top_sellers']['items'][:20]])
            print(f"📈 Топ-продажи: {len(data['top_sellers']['items'])} игр")
        
        # 2. Скидки (specials)
        if 'specials' in data:
            appids.extend([item['id'] for item in data['specials']['items'][:20]])
            print(f"🔥 Скидки: {len(data['specials']['items'])} игр")
        
        # 3. Рекомендации/фичи
        if 'featured_windows' in data:
            appids.extend([item['id'] for item in data['featured_windows']['items'][:10]])
            print(f"⭐ Фичи: {len(data['featured_windows']['items'])} игр")
        
        # Уникальные + лимит
        appids = list(set(appids))[:limit]
        return appids
    
    async def get_game_details(self, appid: int, country: str) -> dict:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc={country}&filters=everything"
        try:
            async with self.session.get(url) as resp:
                data = await resp.json()
                game = data.get(str(appid), {}).get('data', {})
                if game:
                    game['appid'] = appid
                return game
        except:
            return {}
    
    async def scrape_dynamic_top(self, country: str = 'RU', limit: int = 10) -> list:
        appids = await self.get_dynamic_top_appids(country, limit * 2)  # Больше, чем нужно
        print(f"📊 Собираем {len(appids)} динамических топ-игр...")
        
        games = []
        for i, appid in enumerate(appids[:limit], 1):
            print(f"  {i}/{limit}: {appid}", end=' ')
            game = await self.get_game_details(appid, country)
            if game:
                games.append(game)
                print("✅")
            else:
                print("❌")
            await asyncio.sleep(0.2)
        
        return games

async def main():
    country = input("Страна (RU/US/KZ)? [RU]: ").strip() or 'RU'
    limit = int(input("Количество игр? [10]: ").strip() or 10)
    
    async with SteamDynamicTop() as scraper:
        games = await scraper.scrape_dynamic_top(country, limit)
        
        filename = f'dynamic_top{limit}_{country.lower()}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(games, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Сохранено: {filename}")
        print("\n📋 Топ игр:")
        for game in games[:5]:
            print(f"  {game.get('name', 'N/A')} ({game['appid']})")
            discount = game.get('price_overview', {}).get('discount_percent', 0)
            if discount > 0:
                print(f"     Скидка: {discount}%")
            print(f"     Image: {game.get('header_image', 'N/A')[:60]}...")

if __name__ == '__main__':
    asyncio.run(main())
