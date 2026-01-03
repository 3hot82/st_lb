import aiohttp
from typing import Optional, Dict, List, Any
from config import conf

class SteamService:
    BASE_URL = "http://api.steampowered.com"
    STORE_URL = "https://store.steampowered.com/api"

    def __init__(self):
        self.api_key = conf.steam_api_key

    async def resolve_vanity_url(self, vanity_url: str) -> Optional[str]:
        clean_url = vanity_url.rstrip('/').split('/')[-1]
        if clean_url.isdigit() and len(clean_url) == 17:
            return clean_url

        url = f"{self.BASE_URL}/ISteamUser/ResolveVanityURL/v0001/"
        params = {"key": self.api_key, "vanityurl": clean_url}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200: return None
                data = await resp.json()
                if data.get('response', {}).get('success') == 1:
                    return data['response']['steamid']
        return None

    async def get_player_summary(self, steam_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {"key": self.api_key, "steamids": steam_id}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                players = data.get('response', {}).get('players', [])
                return players[0] if players else {}

    async def get_owned_games(self, steam_id: str) -> Optional[List[Dict]]:
        url = f"{self.BASE_URL}/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "include_appinfo": 1,
            "include_played_free_games": 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 500: return None
                data = await resp.json()
        
        response = data.get('response', {})
        return response.get('games')

    async def get_game_price(self, app_id: int, country: str) -> Optional[str]:
        url = f"{self.STORE_URL}/appdetails"
        params = {
            "appids": app_id,
            "cc": country,
            "filters": "price_overview"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status != 200: return None
                    data = await resp.json()
                    game_data = data.get(str(app_id), {})
                    if not game_data.get('success'): return None
                    
                    if game_data.get('data', {}).get('is_free'):
                        return "Free"
                        
                    price_data = game_data.get('data', {}).get('price_overview')
                    if not price_data: return None
                        
                    return price_data.get('final_formatted')
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None

    # === НОВЫЕ МЕТОДЫ ДЛЯ АЧИВОК ===

    async def get_game_schema(self, app_id: int, language: str) -> Dict[str, Any]:
        """Получает схему ачивок (имена, описания, иконки)"""
        url = f"{self.BASE_URL}/ISteamUserStats/GetSchemaForGame/v2/"
        params = {
            "key": self.api_key,
            "appid": app_id,
            "l": language # 'russian' или 'english'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200: return {}
                data = await resp.json()
                
                # Преобразуем список в словарь {api_name: data} для удобства
                achievements = data.get('game', {}).get('availableGameStats', {}).get('achievements', [])
                return {ach['name']: ach for ach in achievements}

    async def get_global_achievement_percentages(self, app_id: int) -> Dict[str, float]:
        """Получает % получения"""
        url = f"{self.BASE_URL}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/"
        params = {"gameid": app_id}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200: return {}
                data = await resp.json()
                
                stats = data.get('achievementpercentages', {}).get('achievements', [])
                return {s['name']: s['percent'] for s in stats}

steam_service = SteamService()