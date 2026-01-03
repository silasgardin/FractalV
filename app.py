import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from motor_matematico import OtimizadorFinanceiro, MotorInferencia
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | Purple Edition", layout="wide", page_icon="🧩")

# --- 2. CSS PERSONALIZADO (Visual Roxo/Neon) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    
    /* Card do Jogo */
    .card-header {
        color: #00FF99; 
        font-size: 22px; 
        font-weight: bold; 
        border-bottom: 2px solid #333; 
        margin-bottom: 15px;
        display: flex;
        justify_content: space-between;
        align-items: center;
    }
    
    /* Índice do Jogo (#01, #02...) */
    .game-index {
        font-family: 'Courier New', monospace;
        color: #00FF99;
        font-size: 16px;
        font-weight: bold;
        margin-right: 10px;
        vertical-align: middle;
        display: inline-block;
    }
    
    /* Bolas de Lotaria - Base */
    .loto-ball { 
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        font-weight: bold;
        color: #FFF; 
        margin: 2px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        font-size: 14px;
        vertical-align: middle;
    }
    
    /* Cores das Bolas */
    .ball-normal { 
        background: radial-gradient(circle at 10px 10px, #a855f7, #581c87); /* Roxo */
        border: 1px solid #c084fc; 
    }
    
    .ball-fixed { 
        background: radial-gradient(circle at 10px 10px, #00FF99, #008f55); /* Verde */
        color: #000; 
        border: 1px solid #00FF99; 
    }
    
    /* Tags e Stats */
    .winner-tag { background-color: #00FF99; color: black; padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 12px; }
    .stat-box { font-size: 11px; color: #aaa; background: #1f2937; padding: 4px 8px; border-radius: 4px; margin-top: 5px; display: inline-block; }
    
    /* Barra de Progresso Custom */
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
    st.caption("Pro Analyst v5.2")
    st.divider()
    st.info("Sistema de Análise Híbrida Ativo.")
    
    with st.expander("📖 Legenda das Bolas"):
        st.markdown("""
        <div class='loto-ball ball-normal'>01</div> Gerado pelo Modelo<br>
        <div class='loto-ball ball-fixed'>10</div> Fixo (Sua escolha)<br>
        """, unsafe_allow_html=True)

# --- 5. PAINEL PRINCIPAL ---
st.title("Painel Estratégico de Lotarias")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))
jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols_layout = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols_layout[i % 2]:
        with st.container(border=True):
            st.markdown(f"""
            <div class='card-header'>
                <span>{jogo.replace('_', ' ')}</span>
            </div>
            """, unsafe_allow_html=True)
            
            df, cols_dezenas, vencedor, placar, freq = get_data_and_backtest(jogo)
            
            if df is not None:
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"Modelo Vencedor: <span class='winner-tag'>{vencedor}</span>", unsafe_allow_html=True)
                with c2:
                    st.caption(f"Score Backtest: {placar[vencedor]} acertos")

                tab_orc, tab_filtros, tab_gerador = st.tabs(["💰 Budget", "⚙️ Filtros", "🎲 Mesa de Análise"])
                
                with tab_orc:
                    orcamento = st.number_input("Investimento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    if st.button("CALCULAR ESTRATÉGIA", key=f"btn_{jogo}", use_container_width=True):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'modelo_{jogo}'] = vencedor
                            st.success(f"Cálculo concluído com modelo {vencedor}!")
                        else:
                            st.error(res['erro'])

                with tab_filtros:
                    if freq is not None:
                        st.caption("Top 10 Dezenas Mais Frequentes")
                        st.bar_chart(freq.head(10), height=120, color="#a855f7")
                        
                        todas_possiveis = sorted(freq.index.tolist())
                        fixos = st.multiselect("🔒 Números Fixos (Obrigatórios):", todas_possiveis, key=f"fix_{jogo}")
                        excluidos = st.multiselect("🚫 Números Excluídos (Banidos):", todas_possiveis, key=f"exc_{jogo}")
                        
                        st.session_state[f'filtros_{jogo}'] = {'fixos': fixos, 'excluidos': excluidos}

                with tab_gerador:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modelo_ativo = st.session_state[f'modelo_{jogo}']
                        filtros = st.session_state.get(f'filtros_{jogo}', {'fixos': [], 'excluidos': []})
                        
                        dados_exportacao = []
                        st.markdown(f"**Estratégia Ativa:** {modelo_ativo}")
                        
                        for item in res['carrinho']:
                            q_vol = item['qtd_volantes']
                            q_dez = int(item['dezenas'])
                            
                            st.markdown(f"👉 **{q_vol}x** Jogos de **{q_dez}** dezenas:")
                            
                            palpites_gerados = []
                            for _ in range(q_vol):
                                p = MotorInferencia.prever_proximo(
                                    modelo_ativo, df, cols_dezenas, q_dez, 
                                    fixos=filtros['fixos'], excluidos=filtros['excluidos']
                                )
                                palpites_gerados.append(p)
                            
                            # RENDERIZAÇÃO COM NUMERAÇÃO
                            for idx, p in enumerate(palpites_gerados):
                                # Adiciona o número do jogo (#01, #02...)
                                html_balls = f"<span class='game-index'>#{idx+1:02d}</span>"
                                
                                for n in p:
                                    n_str = str(int(n)).zfill(2)
                                    css_class = "ball-fixed" if n in filtros['fixos'] else "ball-normal"
                                    html_balls += f"<div class='loto-ball {css_class}'>{n_str}</div>"
                                
                                stats_txt = calcular_stats(p)
                                score_eq = calcular_score_visual(p, q_dez)
                                
                                col_visual, col_info = st.columns([3, 1])
                                with col_visual:
                                    st.markdown(html_balls, unsafe_allow_html=True)
                                with col_info:
                                    st.progress(score_eq, text="Equilíbrio")
                                    st.markdown(f"<div class='stat-box'>{stats_txt}</div>", unsafe_allow_html=True)
                                
                                dados_exportacao.append({
                                    "Jogo": idx + 1,
                                    "Dezenas": p,
                                    "Pares": len([x for x in p if x % 2 == 0]),
                                    "Soma": sum(p),
                                    "Modelo": modelo_ativo
                                })
                            
                            st.divider()
                        
                        c_dl1, c_dl2 = st.columns(2)
                        if dados_exportacao:
                            txt_data = "\n".join([f"Jogo {d['Jogo']}: {d['Dezenas']}" for d in dados_exportacao])
                            c_dl1.download_button("📄 Baixar Texto (.txt)", txt_data, f"{jogo}_fractalv.txt")
                            csv_data = to_csv(dados_exportacao)
                            c_dl2.download_button("📊 Baixar Excel (.csv)", csv_data, f"{jogo}_fractalv.csv", "text/csv")
                        
                    else:
                        st.info("⚠️ Vá à aba 'Budget' e clique em Calcular.")
            else:
                st.warning("Aguardando conexão...")
