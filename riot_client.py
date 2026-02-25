import requests
import time
from config import RIOT_API_KEY, REGION, ROUTING_REGION

class RiotClient:
    def __init__(self, api_key=RIOT_API_KEY, region=REGION, routing_region=ROUTING_REGION):
        self.api_key = api_key
        self.region = region
        self.routing_region = routing_region
        self.headers = {
            "X-Riot-Token": self.api_key
        }

    def get_puuid(self, game_name, tag_line):
        """Busca o PUUID do jogador usando GameName e TagLine."""
        url = f"https://{self.routing_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['puuid']
        else:
            print(f"Erro ao buscar PUUID: {response.status_code} - {response.text}")
            return None

    def get_match_ids(self, puuid, count=20):
        """Busca os IDs das últimas partidas do jogador."""
        url = f"https://{self.routing_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao buscar IDs de partidas: {response.status_code}")
            return []

    def get_match_details(self, match_id):
        """Busca os detalhes de uma partida específica."""
        url = f"https://{self.routing_region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit atingido. Aguardando...")
            time.sleep(1) # Simples espera para rate limit
            return self.get_match_details(match_id)
        else:
            print(f"Erro ao buscar detalhes da partida {match_id}: {response.status_code}")
            return None
