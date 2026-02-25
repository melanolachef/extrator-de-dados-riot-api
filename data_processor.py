import pandas as pd

def process_match_data(match_details, target_puuid):
    """Transforma os detalhes brutos da partida em um dicionário simplificado para o jogador alvo."""
    info = match_details.get('info', {})
    participants = info.get('participants', [])
    
    # Encontrar o jogador alvo na partida
    player_data = next((p for p in participants if p['puuid'] == target_puuid), None)
    
    if not player_data:
        return None
    
    stats = {
        "match_id": match_details['metadata']['matchId'],
        "game_creation": pd.to_datetime(info['gameCreation'], unit='ms'),
        "game_duration_min": info['gameDuration'] / 60,
        "champion_name": player_data['championName'],
        "win": player_data['win'],
        "kills": player_data['kills'],
        "deaths": player_data['deaths'],
        "assists": player_data['assists'],
        "total_damage": player_data['totalDamageDealtToChampions'],
        "gold_earned": player_data['goldEarned'],
        "vision_score": player_data['vision_score'] if 'vision_score' in player_data else player_data.get('visionScore', 0),
        "individual_position": player_data.get('individualPosition', 'Unknown')
    }
    
    # Cálculo de KDA
    stats['kda'] = (stats['kills'] + stats['assists']) / max(1, stats['deaths'])
    
    return stats

def get_matches_dataframe(matches_list):
    """Converte uma lista de partidas processadas em um DataFrame do Pandas."""
    if not matches_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(matches_list)
    return df
