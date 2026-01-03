import streamlit as st
import pandas as pd
import numpy as np
from motor_matematico import OtimizadorFinanceiro, MotorInferencia, MotorFractal
from links_planilhas import LINKS_CSV

st.set_page_config(page_title="FRACTALV | Auto-Learning", layout="wide", page_icon="🧩")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .card-title { color: #00FF99; font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; margin-bottom: 5px;}
    .winner-tag { background-color: #00FF99; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .score-row { font-size: 12px; color: #ccc; margin-bottom: 2px; }
    .big-number { font-size: 18px; font-weight: bold; color: #FFF; background: #262730; padding: 4px 8px; border-radius: 4px; border: 1px solid #444; display: inline-block; margin: 2px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def get_data_and_backtest(jogo_key):
    link = LINKS_CSV.get(jogo_key)
    try:
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None, None, None, None
        
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        
        # Executa o Backtest (Quem teria acertado o último jogo?)
        vencedor, score, placar = MotorInferencia.executar_backtest(df, cols)
        
        last_draw = df.iloc[0]
        return df, cols, vencedor, placar
    except:
        return None, None, None, None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Auto-Learning Engine v4.0")
    st.info("O sistema agora realiza um backtest no último sorteio para escolher automaticamente o melhor modelo matemático para hoje.")

# --- PAINEL ---
st.title("Oráculo Matemático Autoadaptável")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))
jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols_layout = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols_layout[i % 2]:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            # 1. Processamento Inteligente
            df, cols_dezenas, vencedor, placar = get_data_and_backtest(jogo)
            
            if df is not None:
                # Exibe o Vencedor do Backtest
                st.markdown(f"<span class='winner-tag'>🏆 Melhor Modelo: {vencedor}</span>", unsafe_allow_html=True)
                
                with st.expander(f"📊 Ver Backtest (Último Sorteio)"):
                    st.caption("Quantas dezenas cada modelo teria acertado no concurso passado:")
                    for mod, acertos in placar.items():
                        bar_char = "🟩" * acertos + "⬜" * (15-acertos if acertos < 15 else 0)
                        st.markdown(f"<div class='score-row'>{mod}: <b>{acertos}</b> acertos</div>", unsafe_allow_html=True)

                tab1, tab2 = st.tabs(["💰 Orçamento", "🎲 Palpites Otimizados"])
                
                with tab1:
                    orcamento = st.number_input("Investimento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    if st.button("CALCULAR ESTRATÉGIA", key=f"btn_{jogo}"):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'modelo_{jogo}'] = vencedor
                            st.success(f"Estratégia Pronta! Usando: {vencedor}")
                        else:
                            st.error(res['erro'])

                with tab2:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modelo_ativo = st.session_state[f'modelo_{jogo}']
                        
                        st.write(f"Gerando números via **{modelo_ativo}**:")
                        
                        lista_txt = [f"=== FRACTALV: {jogo} ===", f"Modelo Vencedor: {modelo_ativo}\n"]
                        
                        for item in res['carrinho']:
                            q_vol = item['qtd_volantes']
                            q_dez = int(item['dezenas'])
                            
                            st.markdown(f"👉 **{q_vol}x** Jogos de **{q_dez}** dezenas:")
                            
                            palpites_gerados = []
                            for _ in range(q_vol):
                                # O Motor gera baseado no modelo vencedor
                                p = MotorInferencia.prever_proximo(modelo_ativo, df, cols_dezenas, q_dez)
                                p_lista = sorted(list(p))
                                palpites_gerados.append(p_lista)
                            
                            for idx, p in enumerate(palpites_gerados):
                                html_parts = "".join([f"<span class='big-number'>{str(n).zfill(2)}</span>" for n in p])
                                st.markdown(html_parts, unsafe_allow_html=True)
                                lista_txt.append(f"Jogo {idx+1}: {', '.join([str(x).zfill(2) for x in p])}")
                            
                            st.divider()
                        
                        st.download_button("📥 BAIXAR TXT", "\n".join(lista_txt), f"fractalv_{jogo}.txt")
                    else:
                        st.info("Defina o orçamento primeiro.")
            else:
                st.warning("Sem dados.")
