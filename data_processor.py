import pandas as pd


def process_match_data(match_details, target_puuid):
    """Transforma os detalhes brutos da partida em um dicionário simplificado para o jogador alvo."""
    info = match_details.get('info', {})
    participants = info.get('participants', [])

    # Encontrar o jogador alvo na partida
    player_data = next((p for p in participants if p['puuid'] == target_puuid), None)

    if not player_data:
        return None

    game_duration_min = info.get('gameDuration', 1) / 60

    stats = {
        "match_id": match_details['metadata']['matchId'],
        "game_creation": pd.to_datetime(info['gameCreation'], unit='ms'),
        "game_duration_min": round(game_duration_min, 1),
        "champion_name": player_data.get('championName', 'Unknown'),
        "win": player_data.get('win', False),
        "kills": player_data.get('kills', 0),
        "deaths": player_data.get('deaths', 0),
        "assists": player_data.get('assists', 0),
        "total_damage": player_data.get('totalDamageDealtToChampions', 0),
        "gold_earned": player_data.get('goldEarned', 0),
        "vision_score": player_data.get('visionScore', 0),
        "individual_position": player_data.get('individualPosition', 'Unknown'),
        "cs": player_data.get('totalMinionsKilled', 0) + player_data.get('neutralMinionsKilled', 0),
        "wards_placed": player_data.get('wardsPlaced', 0),
        "wards_killed": player_data.get('wardsKilled', 0),
        "turret_kills": player_data.get('turretKills', 0),
        "double_kills": player_data.get('doubleKills', 0),
        "triple_kills": player_data.get('tripleKills', 0),
        "quadra_kills": player_data.get('quadraKills', 0),
        "penta_kills": player_data.get('pentaKills', 0),
    }

    # Cálculos derivados
    stats['kda'] = round((stats['kills'] + stats['assists']) / max(1, stats['deaths']), 2)
    stats['cs_per_min'] = round(stats['cs'] / max(1, game_duration_min), 1)
    stats['damage_per_min'] = round(stats['total_damage'] / max(1, game_duration_min), 0)
    stats['gold_per_min'] = round(stats['gold_earned'] / max(1, game_duration_min), 0)

    return stats


def get_matches_dataframe(matches_list):
    """Converte uma lista de partidas processadas em um DataFrame do Pandas."""
    if not matches_list:
        return pd.DataFrame()

    df = pd.DataFrame(matches_list)
    # Ordenar por data de criação (mais recente primeiro)
    if 'game_creation' in df.columns:
        df = df.sort_values('game_creation', ascending=False).reset_index(drop=True)
    return df
