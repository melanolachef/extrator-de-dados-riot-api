import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from riot_client import RiotClient
from data_processor import process_match_data, get_matches_dataframe
from config import RIOT_API_KEY

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="LoL Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS - Dark Gaming Theme ───────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Main theme */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(200, 170, 110, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .main-header h1 {
        color: #c8aa6e;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #a09b8c;
        font-size: 1rem;
        margin: 0.3rem 0 0 0;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(200, 170, 110, 0.15);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(200, 170, 110, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.3rem 0;
        line-height: 1.2;
    }
    .metric-label {
        color: #8b8589;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    .metric-sub {
        color: #6b6570;
        font-size: 0.72rem;
        margin-top: 0.2rem;
    }

    /* Color classes */
    .green { color: #00d4aa; }
    .red { color: #ff4d6a; }
    .gold { color: #c8aa6e; }
    .blue { color: #4da6ff; }
    .purple { color: #c084fc; }
    .orange { color: #f59e0b; }

    /* Player header */
    .player-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        padding: 1.2rem 1.8rem;
        border-radius: 12px;
        border-left: 4px solid #c8aa6e;
        margin: 1rem 0;
    }
    .player-header h2 {
        color: #e2e0dc;
        margin: 0;
        font-size: 1.4rem;
    }

    /* Section title */
    .section-title {
        color: #c8aa6e;
        font-size: 1.1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid rgba(200, 170, 110, 0.2);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(15, 12, 41, 0.5);
        padding: 0.4rem;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(200, 170, 110, 0.1);
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #c8aa6e;
        font-size: 1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Table styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Floating sidebar toggle button */
    .sidebar-toggle-btn {
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 999999;
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, #302b63, #24243e);
        border: 1px solid rgba(200, 170, 110, 0.3);
        color: #c8aa6e;
        font-size: 1.3rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    .sidebar-toggle-btn:hover {
        background: linear-gradient(135deg, #3b3580, #2e2d50);
        box-shadow: 0 4px 20px rgba(200, 170, 110, 0.2);
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# ─── Floating Sidebar Toggle Button ───────────────────────────
components.html("""
<style>
    .sidebar-toggle-btn {
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 999999;
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, #302b63, #24243e);
        border: 1px solid rgba(200, 170, 110, 0.3);
        color: #c8aa6e;
        font-size: 1.3rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        font-family: sans-serif;
    }
    .sidebar-toggle-btn:hover {
        background: linear-gradient(135deg, #3b3580, #2e2d50);
        box-shadow: 0 4px 20px rgba(200, 170, 110, 0.2);
        transform: scale(1.05);
    }
</style>

<div class="sidebar-toggle-btn" onclick="toggleSidebar()" id="sidebarToggle">☰</div>

<script>
function toggleSidebar() {
    const doc = window.parent.document;

    // Try clicking Streamlit's native collapse/expand buttons
    const selectors = [
        '[data-testid="collapsedControl"] button',
        '[data-testid="stSidebarCollapsedControl"] button',
        'button[data-testid="baseButton-headerNoPadding"]',
        'section[data-testid="stSidebar"] button[kind="header"]',
        'button[data-testid="baseButton-header"]',
    ];

    for (const sel of selectors) {
        const btn = doc.querySelector(sel);
        if (btn) {
            btn.click();
            return;
        }
    }

    // Fallback: directly manipulate sidebar CSS
    const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
    if (sidebar) {
        const isHidden = sidebar.getAttribute('aria-expanded') === 'false' ||
                         getComputedStyle(sidebar).transform.includes('matrix') ||
                         sidebar.offsetWidth < 50;
        if (isHidden) {
            sidebar.style.transform = 'none';
            sidebar.style.width = '21rem';
            sidebar.setAttribute('aria-expanded', 'true');
        } else {
            sidebar.style.transform = 'translateX(-21rem)';
            sidebar.style.width = '0px';
            sidebar.setAttribute('aria-expanded', 'false');
        }
    }
}
</script>
""", height=0)

# ─── Plotly Theme ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#a09b8c'),
    title_font=dict(color='#e2e0dc', size=16),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#a09b8c')),
    margin=dict(l=40, r=20, t=50, b=40),
)

COLORS = {
    'gold': '#c8aa6e',
    'blue': '#4da6ff',
    'green': '#00d4aa',
    'red': '#ff4d6a',
    'purple': '#c084fc',
    'orange': '#f59e0b',
    'cyan': '#22d3ee',
}


# ─── Helper Functions ─────────────────────────────────────────
def metric_card(label, value, sub="", color_class="gold"):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color_class}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """


def get_kda_color(kda):
    if kda >= 5:
        return "green"
    elif kda >= 3:
        return "blue"
    elif kda >= 2:
        return "gold"
    else:
        return "red"


def get_wr_color(wr):
    if wr >= 60:
        return "green"
    elif wr >= 50:
        return "blue"
    else:
        return "red"


@st.cache_data(ttl=300)
def fetch_player_data(_client, game_name, tag_line, match_count):
    """Busca e processa dados do jogador com cache de 5 minutos."""
    puuid = _client.get_puuid(game_name, tag_line)
    if not puuid:
        return None, None

    match_ids = _client.get_match_ids(puuid, count=match_count)
    processed_matches = []

    for m_id in match_ids:
        match_data = _client.get_match_details(m_id)
        if match_data:
            summary = process_match_data(match_data, puuid)
            if summary:
                processed_matches.append(summary)

    df = get_matches_dataframe(processed_matches)
    return puuid, df


# ─── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎮 LoL Friends Dashboard</h1>
    <p>Análise avançada de partidas — League of Legends</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    api_key = st.text_input("🔑 Riot API Key", value=RIOT_API_KEY, type="password")
    match_count = st.slider("📊 Partidas para analisar", min_value=5, max_value=20, value=10)

    st.markdown("---")
    st.markdown("## 👥 Jogadores")
    players_input = st.text_area(
        "Formato: Nome#TAG (um por linha)",
        value="genios#BR1",
        height=120,
        help="Insira o Riot ID dos jogadores, um por linha."
    )

    st.markdown("---")
    analyze_btn = st.button("🚀 Analisar Partidas", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown(
        "<p style='color:#6b6570; font-size:0.7rem; text-align:center;'>"
        "Dados via Riot Games API<br>Chaves expiram a cada 24h</p>",
        unsafe_allow_html=True
    )

# ─── Main Content ─────────────────────────────────────────────
if analyze_btn:
    if not api_key or api_key == "SUA_CHAVE_AQUI":
        st.error("⚠️ Insira uma chave de API válida na barra lateral.")
        st.stop()

    client = RiotClient(api_key=api_key)
    player_names = [p.strip() for p in players_input.split('\n') if '#' in p]

    if not player_names:
        st.warning("Por favor, insira pelo menos um jogador no formato Nome#TAG.")
        st.stop()

    all_players_data = {}

    # Fetch data for all players
    for player_str in player_names:
        name, tag = player_str.split('#', 1)

        st.markdown(f"""
        <div class="player-header">
            <h2>📊 {name}#{tag}</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner(f"Buscando dados de {name}..."):
            progress_bar = st.progress(0, text=f"Conectando à API Riot...")

            puuid = client.get_puuid(name, tag)

            if not puuid:
                st.error(f"❌ Não foi possível encontrar o jogador **{player_str}**. Verifique o nome e a API key.")
                progress_bar.empty()
                continue

            progress_bar.progress(10, text="Buscando partidas...")
            match_ids = client.get_match_ids(puuid, count=match_count)

            if not match_ids:
                st.warning(f"Nenhuma partida encontrada para {name}#{tag}.")
                progress_bar.empty()
                continue

            processed_matches = []
            for i, m_id in enumerate(match_ids):
                match_data = client.get_match_details(m_id)
                if match_data:
                    summary = process_match_data(match_data, puuid)
                    if summary:
                        processed_matches.append(summary)
                pct = 10 + int(((i + 1) / len(match_ids)) * 90)
                progress_bar.progress(pct, text=f"Processando partida {i+1}/{len(match_ids)}...")

            progress_bar.empty()

            df = get_matches_dataframe(processed_matches)

            if df.empty:
                st.error(f"Não foram encontradas partidas para {name}#{tag}.")
                continue

            all_players_data[f"{name}#{tag}"] = df

            # ── Tabs ──────────────────────────────────────
            tab1, tab2, tab3 = st.tabs(["📈 Visão Geral", "📋 Detalhes", "🏆 Campeões"])

            with tab1:
                # ── Metrics Row ───────────────────────────
                win_rate = (df['win'].sum() / len(df)) * 100
                avg_kda = df['kda'].mean()
                avg_cs = df['cs_per_min'].mean()
                avg_dmg = df['damage_per_min'].mean()
                avg_vision = df['vision_score'].mean()
                total_kills = df['kills'].sum()
                total_deaths = df['deaths'].sum()
                total_assists = df['assists'].sum()

                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    st.markdown(metric_card(
                        "Win Rate", f"{win_rate:.0f}%",
                        f"{df['win'].sum()}V / {len(df) - df['win'].sum()}D",
                        get_wr_color(win_rate)
                    ), unsafe_allow_html=True)
                with c2:
                    st.markdown(metric_card(
                        "KDA Médio", f"{avg_kda:.2f}",
                        f"{total_kills}/{total_deaths}/{total_assists}",
                        get_kda_color(avg_kda)
                    ), unsafe_allow_html=True)
                with c3:
                    st.markdown(metric_card(
                        "CS/Min", f"{avg_cs:.1f}",
                        f"Total: {df['cs'].mean():.0f} CS",
                        "blue"
                    ), unsafe_allow_html=True)
                with c4:
                    st.markdown(metric_card(
                        "Dano/Min", f"{avg_dmg:.0f}",
                        f"Total: {df['total_damage'].mean():.0f}",
                        "purple"
                    ), unsafe_allow_html=True)
                with c5:
                    st.markdown(metric_card(
                        "Vision Score", f"{avg_vision:.0f}",
                        f"Wards: {df['wards_placed'].mean():.0f}",
                        "orange"
                    ), unsafe_allow_html=True)

                st.markdown("")

                # ── Charts Row 1 ─────────────────────────
                col_left, col_right = st.columns(2)

                with col_left:
                    # Win/Loss Pie
                    wins = df['win'].sum()
                    losses = len(df) - wins
                    fig_wr = go.Figure(data=[go.Pie(
                        labels=['Vitórias', 'Derrotas'],
                        values=[wins, losses],
                        hole=0.55,
                        marker=dict(colors=[COLORS['green'], COLORS['red']]),
                        textfont=dict(color='white', size=14),
                        textinfo='label+value',
                    )])
                    fig_wr.update_layout(
                        title="Vitórias vs Derrotas",
                        **PLOTLY_LAYOUT,
                        showlegend=False,
                        height=350,
                        annotations=[dict(
                            text=f"<b>{win_rate:.0f}%</b>",
                            x=0.5, y=0.5, font_size=28,
                            font_color=COLORS['gold'],
                            showarrow=False
                        )]
                    )
                    st.plotly_chart(fig_wr, use_container_width=True)

                with col_right:
                    # KDA per match
                    fig_kda = go.Figure()
                    fig_kda.add_trace(go.Bar(
                        x=list(range(1, len(df) + 1)),
                        y=df['kills'].values,
                        name='Kills',
                        marker_color=COLORS['green'],
                    ))
                    fig_kda.add_trace(go.Bar(
                        x=list(range(1, len(df) + 1)),
                        y=df['deaths'].values,
                        name='Deaths',
                        marker_color=COLORS['red'],
                    ))
                    fig_kda.add_trace(go.Bar(
                        x=list(range(1, len(df) + 1)),
                        y=df['assists'].values,
                        name='Assists',
                        marker_color=COLORS['blue'],
                    ))
                    fig_kda.update_layout(
                        title="K/D/A por Partida",
                        barmode='group',
                        xaxis_title="Partida",
                        yaxis_title="Quantidade",
                        **PLOTLY_LAYOUT,
                        height=350,
                    )
                    st.plotly_chart(fig_kda, use_container_width=True)

                # ── Charts Row 2 ─────────────────────────
                col_left2, col_right2 = st.columns(2)

                with col_left2:
                    # Damage per match
                    colors_dmg = [COLORS['green'] if w else COLORS['red'] for w in df['win'].values]
                    fig_dmg = go.Figure(data=[go.Bar(
                        x=list(range(1, len(df) + 1)),
                        y=df['total_damage'].values,
                        marker_color=colors_dmg,
                        text=df['champion_name'].values,
                        textposition='outside',
                        textfont=dict(size=9, color='#a09b8c'),
                    )])
                    fig_dmg.update_layout(
                        title="Dano Total por Partida",
                        xaxis_title="Partida",
                        yaxis_title="Dano",
                        **PLOTLY_LAYOUT,
                        height=350,
                    )
                    st.plotly_chart(fig_dmg, use_container_width=True)

                with col_right2:
                    # Gold & CS
                    fig_econ = go.Figure()
                    fig_econ.add_trace(go.Scatter(
                        x=list(range(1, len(df) + 1)),
                        y=df['gold_per_min'].values,
                        name='Gold/Min',
                        line=dict(color=COLORS['gold'], width=3),
                        mode='lines+markers',
                    ))
                    fig_econ.add_trace(go.Scatter(
                        x=list(range(1, len(df) + 1)),
                        y=df['cs_per_min'].values * 50,
                        name='CS/Min (×50)',
                        line=dict(color=COLORS['cyan'], width=3),
                        mode='lines+markers',
                    ))
                    fig_econ.update_layout(
                        title="Economia por Partida",
                        xaxis_title="Partida",
                        **PLOTLY_LAYOUT,
                        height=350,
                    )
                    st.plotly_chart(fig_econ, use_container_width=True)

            with tab2:
                # ── Match History Table ───────────────────
                st.markdown('<div class="section-title">📋 Histórico de Partidas</div>', unsafe_allow_html=True)

                display_df = df[[
                    'champion_name', 'win', 'kills', 'deaths', 'assists',
                    'kda', 'cs', 'cs_per_min', 'total_damage', 'damage_per_min',
                    'gold_earned', 'vision_score', 'individual_position',
                    'game_duration_min', 'game_creation'
                ]].copy()

                display_df.columns = [
                    'Campeão', 'Vitória', 'K', 'D', 'A',
                    'KDA', 'CS', 'CS/Min', 'Dano', 'Dano/Min',
                    'Ouro', 'Visão', 'Posição',
                    'Duração (min)', 'Data'
                ]

                display_df['Vitória'] = display_df['Vitória'].map({True: '✅', False: '❌'})
                display_df['Data'] = pd.to_datetime(display_df['Data']).dt.strftime('%d/%m %H:%M')

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400,
                )

                # Multi-kills
                multi_kills = {
                    'Double Kills': df['double_kills'].sum(),
                    'Triple Kills': df['triple_kills'].sum(),
                    'Quadra Kills': df['quadra_kills'].sum(),
                    'Penta Kills': df['penta_kills'].sum(),
                }
                has_multikills = any(v > 0 for v in multi_kills.values())

                if has_multikills:
                    st.markdown('<div class="section-title">💥 Multi-Kills</div>', unsafe_allow_html=True)
                    mk_cols = st.columns(4)
                    for i, (label, val) in enumerate(multi_kills.items()):
                        with mk_cols[i]:
                            st.markdown(metric_card(label, str(val), "", "purple" if val > 0 else "red"), unsafe_allow_html=True)

            with tab3:
                # ── Champion Stats ────────────────────────
                st.markdown('<div class="section-title">🏆 Performance por Campeão</div>', unsafe_allow_html=True)

                champ_stats = df.groupby('champion_name').agg(
                    Jogos=('win', 'count'),
                    Vitórias=('win', 'sum'),
                    KDA_Médio=('kda', 'mean'),
                    Dano_Médio=('total_damage', 'mean'),
                    CS_Min=('cs_per_min', 'mean'),
                ).reset_index()
                champ_stats['Win Rate'] = (champ_stats['Vitórias'] / champ_stats['Jogos'] * 100).round(1)
                champ_stats['KDA_Médio'] = champ_stats['KDA_Médio'].round(2)
                champ_stats['Dano_Médio'] = champ_stats['Dano_Médio'].round(0).astype(int)
                champ_stats['CS_Min'] = champ_stats['CS_Min'].round(1)
                champ_stats = champ_stats.sort_values('Jogos', ascending=False)

                champ_stats.columns = ['Campeão', 'Jogos', 'Vitórias', 'KDA Médio', 'Dano Médio', 'CS/Min', 'Win Rate %']

                st.dataframe(champ_stats, use_container_width=True, hide_index=True)

                # Top champions bar chart
                if len(champ_stats) > 1:
                    fig_champ = go.Figure(data=[go.Bar(
                        y=champ_stats['Campeão'],
                        x=champ_stats['Jogos'],
                        orientation='h',
                        marker_color=COLORS['gold'],
                        text=champ_stats['Win Rate %'].apply(lambda x: f"{x}% WR"),
                        textposition='auto',
                        textfont=dict(color='white'),
                    )])
                    fig_champ.update_layout(
                        title="Campeões Mais Jogados",
                        xaxis_title="Partidas",
                        **PLOTLY_LAYOUT,
                        height=max(200, len(champ_stats) * 45),
                    )
                    st.plotly_chart(fig_champ, use_container_width=True)

        st.markdown("---")

    # ── Comparison Section ────────────────────────────────
    if len(all_players_data) > 1:
        st.markdown('<div class="section-title">⚔️ Comparação entre Jogadores</div>', unsafe_allow_html=True)

        compare_data = []
        for player_name, player_df in all_players_data.items():
            compare_data.append({
                'Jogador': player_name,
                'Win Rate': f"{(player_df['win'].sum() / len(player_df) * 100):.0f}%",
                'KDA Médio': round(player_df['kda'].mean(), 2),
                'CS/Min': round(player_df['cs_per_min'].mean(), 1),
                'Dano/Min': round(player_df['damage_per_min'].mean(), 0),
                'Vision Score': round(player_df['vision_score'].mean(), 0),
                'Partidas': len(player_df),
            })

        compare_df = pd.DataFrame(compare_data)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)

        # Comparison radar chart
        categories = ['KDA', 'CS/Min', 'Dano/Min', 'Vision', 'Win Rate']
        fig_radar = go.Figure()

        color_list = [COLORS['blue'], COLORS['green'], COLORS['purple'], COLORS['orange'], COLORS['cyan']]

        for idx, (pname, pdf) in enumerate(all_players_data.items()):
            wr = (pdf['win'].sum() / len(pdf)) * 100
            values = [
                min(pdf['kda'].mean() / 6 * 100, 100),
                min(pdf['cs_per_min'].mean() / 10 * 100, 100),
                min(pdf['damage_per_min'].mean() / 1000 * 100, 100),
                min(pdf['vision_score'].mean() / 40 * 100, 100),
                wr,
            ]
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=pname,
                line_color=color_list[idx % len(color_list)],
                fillcolor=color_list[idx % len(color_list)].replace(')', ', 0.1)').replace('rgb', 'rgba'),
            ))

        fig_radar.update_layout(
            title="Comparação de Performance (normalizada)",
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0, 100], color='#6b6570'),
                angularaxis=dict(color='#a09b8c'),
            ),
            **PLOTLY_LAYOUT,
            height=450,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

else:
    # ── Welcome Screen ────────────────────────────────────
    st.markdown("")
    col_welcome = st.columns([1, 2, 1])
    with col_welcome[1]:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 16px; border: 1px solid rgba(200, 170, 110, 0.15); margin-top: 2rem;">
            <p style="font-size: 3.5rem; margin: 0;">🎮</p>
            <h2 style="color: #c8aa6e; font-size: 1.5rem; margin: 0.5rem 0;">Pronto para analisar?</h2>
            <p style="color: #8b8589; font-size: 0.95rem; max-width: 400px; margin: 0.8rem auto;">
                Insira os nomes dos jogadores na barra lateral e clique em
                <strong style="color:#c8aa6e;">Analisar Partidas</strong> para começar.
            </p>
            <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(200, 170, 110, 0.08); border-radius: 10px;">
                <p style="color: #6b6570; font-size: 0.78rem; margin: 0;">
                    💡 Dica: Use o formato <code style="color: #c8aa6e;">Nome#TAG</code> — por exemplo: <code style="color: #c8aa6e;">Faker#KR1</code>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
