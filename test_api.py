from riot_client import RiotClient
from config import RIOT_API_KEY

def test_lookup(name, tag):
    client = RiotClient()
    print(f"Testando busca para: {name}#{tag}")
    print(f"API Key: {RIOT_API_KEY[:10]}...")
    
    puuid = client.get_puuid(name, tag)
    if puuid:
        print(f"Sucesso! PUUID: {puuid}")
        match_ids = client.get_match_ids(puuid, count=5)
        print(f"Partidas encontradas: {len(match_ids)}")
    else:
        print("Falha na busca do PUUID.")

if __name__ == "__main__":
    # Testar com o nome que o usuário informou
    test_lookup("cloudedppp", "xoxo")
