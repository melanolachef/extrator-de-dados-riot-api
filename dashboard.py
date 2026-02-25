import streamlit as st
import pandas as pd
import plotly.express as px
from riot_client import RiotClient
from data_processor import process_match_data, get_matches_dataframe
from config import RIOT_API_KEY

# Layout do Streamlit
st.set_page_config(page_title="LoL Friends Dashboard", layout="wide")

st.title("🎮 Análise de Partidas de Amigos - LoL")

# Sidebar para configurações
st.sidebar.header("Configurações")
api_key = st.sidebar.text_input("Riot API Key", value=RIOT_API_KEY, type="password")
players_input = st.sidebar.text_area("Amigos (Formato: Nome#TAG)", value="Exemplo#BR1")

if st.sidebar.button("Analisar Partidas"):
    client = RiotClient(api_key=api_key)
    
    player_names = [p.strip() for p in players_input.split('\n') if '#' in p]
    
    if not player_names:
        st.warning("Por favor, insira pelo menos um jogador no formato Nome#TAG.")
    else:
        for player_str in player_names:
            name, tag = player_str.split('#')
            st.subheader(f"📊 Analisando: {name}#{tag}")
            
            with st.spinner(f"Buscando dados de {name}..."):
                puuid = client.get_puuid(name, tag)
                
                if puuid:
                    match_ids = client.get_match_ids(puuid, count=10) # Analisar as últimas 10
                    
                    processed_matches = []
                    progress_bar = st.progress(0)
                    
                    for i, m_id in enumerate(match_ids):
                        match_data = client.get_match_details(m_id)
                        if match_data:
                            summary = process_match_data(match_data, puuid)
                            if summary:
                                processed_matches.append(summary)
                        progress_bar.progress((i + 1) / len(match_ids))
                    
                    df = get_matches_dataframe(processed_matches)
                    
                    if not df.empty:
                        # Métricas principais
                        col1, col2, col3, col4 = st.columns(4)
                        win_rate = (df['win'].sum() / len(df)) * 100
                        avg_kda = df['kda'].mean()
                        
                        col1.metric("Win Rate (10 partidas)", f"{win_rate:.1f}%")
                        col2.metric("KDA Médio", f"{avg_kda:.2f}")
                        col3.metric("Dano Médio", f"{df['total_damage'].mean():.0f}")
                        col4.metric("Ouro Médio", f"{df['gold_earned'].mean():.0f}")
                        
                        # Gráfico de Win/Loss
                        fig_win = px.pie(df, names='win', title='Vitórias vs Derrotas', 
                                         color='win', color_discrete_map={True: 'blue', False: 'red'})
                        st.plotly_chart(fig_win)
                        
                        # Tabela de partidas
                        st.write("### Últimas Partidas")
                        st.dataframe(df[['game_creation', 'champion_name', 'win', 'kills', 'deaths', 'assists', 'kda', 'individual_position']])
                    else:
                        st.error("Não foram encontradas partidas para este jogador.")
                else:
                    st.error(f"Não foi possível encontrar o jogador {player_str}.")
else:
    st.info("Insira os jogadores e clique em 'Analisar Partidas' na barra lateral.")
