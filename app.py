import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from motor_matematico import OtimizadorFinanceiro, MotorInferencia
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | Deterministic", layout="wide", page_icon="🧩")

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .card-header { color: #00FF99; font-size: 22px; font-weight: bold; border-bottom: 2px solid #333; margin-bottom: 15px; display: flex; justify_content: space-between; align-items: center; }
    .game-index { font-family: 'Courier New', monospace; color: #00FF99; font-size: 16px; font-weight: bold; margin-right: 10px; vertical-align: middle; display: inline-block; }
    .loto-ball { display: inline-flex; align-items: center; justify-content: center; width: 35px; height: 35px; border-radius: 50%; font-weight: bold; color: #FFF; margin: 2px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); font-size: 14px; vertical-align: middle; }
    .ball-normal { background: radial-gradient(circle at 10px 10px, #a855f7, #581c87); border: 1px solid #c084fc; }
    .ball-fixed { background: radial-gradient(circle at 10px 10px, #00FF99, #008f55); color: #000; border: 1px solid #00FF99; }
    .winner-tag { background-color: #00FF99; color: black; padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 12px; }
    .stat-box { font-size: 11px; color: #aaa; background: #1f2937; padding: 4px 8px; border-radius: 4px; margin-top: 5px; display: inline-block; }
    .stProgress > div > div > div > div { background-color: #a855f7; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES AUXILIARES ---
@st.cache_data(ttl=600)
def get_data_and_backtest(jogo_key):
    link = LINKS_CSV.get(jogo_key)
    try:
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None, None, None, None, None
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts().sort_values(ascending=False)
        vencedor, score, placar = MotorInferencia.executar_backtest(df, cols)
        return df, cols, vencedor, placar, freq
    except:
        return None, None, None, None, None

def calcular_stats(p):
    pares = len([x for x in p if x % 2 == 0])
    soma = sum(p)
    return f"P:{pares} Í:{len(p)-pares} | Σ:{soma}"

def calcular_score_visual(p, total_dezenas):
    if len(p) == 0: return 0
    pares = len([x for x in p if x % 2 == 0])
    ratio = pares / len(p)
    diff = abs(ratio - 0.5) 
    score = max(0, 1.0 - (diff * 2))
    return score

def to_csv(lista_jogos):
    output = BytesIO()
    df = pd.DataFrame(lista_jogos)
    df_clean = df.drop(columns=['Dezenas'])
    df_clean['Dezenas'] = [", ".join(map(str, x)) for x in df['Dezenas']]
    df_clean.to_csv(output, index=False, sep=';')
    return output.getvalue()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Deterministic Engine v6.0")
    st.divider()
    st.success("Modo de Precisão Ativo")
    st.info("Os resultados agora são fixos para o dia (Determinísticos). O modelo não muda de opinião até o próximo sorteio.")

# --- 5. PAINEL PRINCIPAL ---
st.title("Painel Estratégico de Lotarias")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))
jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols_layout = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols_layout[i % 2]:
        with st.container(border=True):
            st.markdown(f"<div class='card-header'><span>{jogo.replace('_', ' ')}</span></div>", unsafe_allow_html=True)
            
            df, cols_dezenas, vencedor, placar, freq = get_data_and_backtest(jogo)
            
            if df is not None:
                c1, c2 = st.columns([2, 1])
                with c1: st.markdown(f"Modelo Vencedor: <span class='winner-tag'>{vencedor}</span>", unsafe_allow_html=True)
                with c2: st.caption(f"Score Backtest: {placar[vencedor]} acertos")

                tab_orc, tab_filtros, tab_gerador = st.tabs(["💰 Budget", "⚙️ Filtros", "🎲 Mesa de Análise"])
                
                with tab_orc:
                    orcamento = st.number_input("Investimento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    if st.button("CALCULAR ESTRATÉGIA", key=f"btn_{jogo}", use_container_width=True):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'modelo_{jogo}'] = vencedor
                            st.success(f"Cálculo fixado com modelo {vencedor}!")
                        else: st.error(res['erro'])

                with tab_filtros:
                    if freq is not None:
                        st.caption("Top 10 Dezenas Mais Frequentes")
                        st.bar_chart(freq.head(10), height=120, color="#a855f7")
                        todas_possiveis = sorted(freq.index.tolist())
                        fixos = st.multiselect("🔒 Números Fixos:", todas_possiveis, key=f"fix_{jogo}")
                        excluidos = st.multiselect("🚫 Números Excluídos:", todas_possiveis, key=f"exc_{jogo}")
                        st.session_state[f'filtros_{jogo}'] = {'fixos': fixos, 'excluidos': excluidos}

                with tab_gerador:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modelo_ativo = st.session_state[f'modelo_{jogo}']
                        filtros = st.session_state.get(f'filtros_{jogo}', {'fixos': [], 'excluidos': []})
                        dados_exportacao = []
                        
                        st.markdown(f"**Estratégia Ativa:** {modelo_ativo}")
                        
                        global_game_index = 0 # Contador global de jogos para seed
                        
                        for item in res['carrinho']:
                            q_vol = item['qtd_volantes']
                            q_dez = int(item['dezenas'])
                            st.markdown(f"👉 **{q_vol}x** Jogos de **{q_dez}** dezenas:")
                            
                            palpites_gerados = []
                            for _ in range(q_vol):
                                global_game_index += 1
                                # PASSAMOS O GLOBAL_GAME_INDEX COMO SEED
                                p = MotorInferencia.prever_proximo(
                                    modelo_ativo, df, cols_dezenas, q_dez, 
                                    fixos=filtros['fixos'], excluidos=filtros['excluidos'],
                                    seed_index=global_game_index
                                )
                                palpites_gerados.append(p)
                            
                            for idx, p in enumerate(palpites_gerados):
                                html_balls = f"<span class='game-index'>#{idx+1:02d}</span>"
                                for n in p:
                                    n_str = str(int(n)).zfill(2)
                                    css_class = "ball-fixed" if n in filtros['fixos'] else "ball-normal"
                                    html_balls += f"<div class='loto-ball {css_class}'>{n_str}</div>"
                                
                                stats_txt = calcular_stats(p)
                                score_eq = calcular_score_visual(p, q_dez)
                                
                                c_v, c_i = st.columns([3, 1])
                                with c_v: st.markdown(html_balls, unsafe_allow_html=True)
                                with c_i:
                                    st.progress(score_eq, text="Equilíbrio")
                                    st.markdown(f"<div class='stat-box'>{stats_txt}</div>", unsafe_allow_html=True)
                                
                                dados_exportacao.append({"Jogo": idx+1, "Dezenas": p, "Modelo": modelo_ativo})
                            st.divider()
                        
                        c1, c2 = st.columns(2)
                        if dados_exportacao:
                            txt = "\n".join([f"Jogo {d['Jogo']}: {d['Dezenas']}" for d in dados_exportacao])
                            c1.download_button("📄 Baixar Texto", txt, f"{jogo}.txt")
                            c2.download_button("📊 Baixar Excel", to_csv(dados_exportacao), f"{jogo}.csv", "text/csv")
                    else: st.info("Vá à aba 'Budget' e clique em Calcular.")
            else: st.warning("Aguardando conexão...")
