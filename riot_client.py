import requests
import time
from config import RIOT_API_KEY, REGION, ROUTING_REGION


class RiotClient:
    MAX_RETRIES = 3

    def __init__(self, api_key=RIOT_API_KEY, region=REGION, routing_region=ROUTING_REGION):
        self.api_key = api_key
        self.region = region
        self.routing_region = routing_region
        self.headers = {
            "X-Riot-Token": self.api_key
        }

    def _make_request(self, url):
        """Faz uma requisição GET com tratamento de erros e rate limit."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print(f"Erro 401: Chave de API inválida ou expirada.")
                    return None
                elif response.status_code == 403:
                    print(f"Erro 403: Acesso negado. Verifique as permissões da sua chave.")
                    return None
                elif response.status_code == 404:
                    print(f"Erro 404: Recurso não encontrado.")
                    return None
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2))
                    print(f"Rate limit atingido. Aguardando {retry_after}s... (tentativa {attempt + 1})")
                    time.sleep(retry_after)
                else:
                    print(f"Erro {response.status_code}: {response.text}")
                    return None
            except requests.exceptions.Timeout:
                print(f"Timeout na requisição (tentativa {attempt + 1})")
                time.sleep(1)
            except requests.exceptions.ConnectionError:
                print(f"Erro de conexão (tentativa {attempt + 1})")
                time.sleep(2)

        print("Número máximo de tentativas atingido.")
        return None

    def get_puuid(self, game_name, tag_line):
        """Busca o PUUID do jogador usando GameName e TagLine."""
        url = f"https://{self.routing_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        data = self._make_request(url)
        if data:
            return data.get('puuid')
        return None

    def get_match_ids(self, puuid, count=20):
        """Busca os IDs das últimas partidas do jogador."""
        url = f"https://{self.routing_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
        data = self._make_request(url)
        return data if data else []

    def get_match_details(self, match_id):
        """Busca os detalhes de uma partida específica."""
        url = f"https://{self.routing_region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        return self._make_request(url)
