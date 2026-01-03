import streamlit as st
import pandas as pd
import numpy as np
import time
from io import BytesIO
from motor_matematico import OtimizadorFinanceiro, MotorInferencia
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | Auto-Pilot", layout="wide", page_icon="🧩")

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .card-header-container { display: flex; justify_content: space-between; align-items: center; border-bottom: 2px solid #333; margin-bottom: 15px; padding-bottom: 5px; }
    .card-title-text { color: #00FF99; font-size: 20px; font-weight: bold; }
    .game-index { font-family: 'Courier New', monospace; color: #00FF99; font-size: 16px; font-weight: bold; margin-right: 10px; }
    .loto-ball { display: inline-flex; align-items: center; justify-content: center; width: 35px; height: 35px; border-radius: 50%; font-weight: bold; color: #FFF; margin: 2px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); font-size: 14px; }
    .ball-normal { background: radial-gradient(circle at 10px 10px, #a855f7, #581c87); border: 1px solid #c084fc; }
    .ball-fixed { background: radial-gradient(circle at 10px 10px, #00FF99, #008f55); color: #000; border: 1px solid #00FF99; }
    .winner-tag { background-color: #00FF99; color: black; padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 12px; }
    .stat-container { margin-top: 5px; font-family: monospace; font-size: 12px; color: #ccc; }
    .stat-tag { background-color: #1f2937; border: 1px solid #374151; padding: 2px 6px; border-radius: 4px; margin-right: 5px; display: inline-block; }
    .stat-highlight { color: #facc15; }
    .stProgress > div > div > div > div { background-color: #a855f7; }
    div[data-testid="stTable"] { font-size: 14px; }
    .financial-box { border: 1px solid #333; background: #1a1a1a; padding: 15px; border-radius: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# Lista Global de Jogos
JOGOS_LISTA = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
PRIMOS = set([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97])
FIBONACCI = set([1, 2, 3, 5, 8, 13, 21, 34, 55, 89])

# --- 3. FUNÇÕES DE PROCESSAMENTO ---
def processar_jogo_individual(jogo_key):
    link = LINKS_CSV.get(jogo_key)
    try:
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts().sort_values(ascending=False)
        vencedor, score_total, placar_dict = MotorInferencia.executar_backtest_profundo(df, cols, profundidade=12)
        return (df, cols, vencedor, score_total, placar_dict, freq)
    except Exception as e: return None

def executar_atualizacao_geral():
    progresso = st.progress(0, text="Iniciando sistema FractalV...")
    total = len(JOGOS_LISTA)
    for i, jogo in enumerate(JOGOS_LISTA):
        progresso.progress(int((i / total) * 100), text=f"Baixando e Analisando: {jogo}...")
        dados = processar_jogo_individual(jogo)
        st.session_state[f'dados_{jogo}'] = dados
        if f'res_{jogo}' in st.session_state: del st.session_state[f'res_{jogo}']
    progresso.progress(100, text="Sistema Pronto!")
    time.sleep(1)
    progresso.empty()

def calcular_stats_completas(p):
    pares = len([x for x in p if x % 2 == 0])
    impares = len(p) - pares
    soma = int(sum(p))
    qtd_primos = len([x for x in p if x in PRIMOS])
    qtd_fibo = len([x for x in p if x in FIBONACCI])
    return f"""<div class='stat-container'><span class='stat-tag'>Pares: {pares}</span><span class='stat-tag'>Ímpares: {impares}</span><span class='stat-tag'>Σ: {soma}</span><span class='stat-tag stat-highlight'>Primos: {qtd_primos}</span><span class='stat-tag stat-highlight'>Fibo: {qtd_fibo}</span></div>"""

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
    df_clean['Dezenas'] = [", ".join([str(int(n)) for n in x['Dezenas']]) for x in lista_jogos]
    df_clean['Stats'] = [f"P:{len([n for n in x['Dezenas'] if n%2==0])} S:{sum(x['Dezenas'])}" for x in lista_jogos]
    df_clean.to_csv(output, index=False, sep=';')
    return output.getvalue()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Auto-Pilot v11.5 (UX Fix)")
    st.divider()
    if st.button("🔄 ATUALIZAR TUDO", type="primary", use_container_width=True):
        executar_atualizacao_geral()
        st.rerun()
    if st.button("🗑️ Resetar Memória"):
        st.session_state.clear()
        st.rerun()
    st.divider()
    with st.expander("📘 Guia do Operador", expanded=False):
        st.info("Valores de investimento agora iniciam com o preço mínimo do jogo.")

# --- 5. AUTO-START ---
if 'startup_check' not in st.session_state:
    st.session_state['startup_check'] = True
    if f'dados_{JOGOS_LISTA[0]}' not in st.session_state:
        executar_atualizacao_geral()

# --- 6. PAINEL PRINCIPAL ---
st.title("Painel Estratégico de Lotarias")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))
cols_layout = st.columns(2)

for i, jogo in enumerate(JOGOS_LISTA):
    with cols_layout[i % 2]:
        with st.container(border=True):
            
            c_tit, c_btn = st.columns([3, 1.2])
            with c_tit: st.markdown(f"<div class='card-title-text'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            with c_btn:
                if st.button("🔄 Atualizar", key=f"up_{jogo}", help="Atualizar apenas este jogo"):
                    with st.spinner(f"Atualizando {jogo}..."):
                        dados = processar_jogo_individual(jogo)
                        st.session_state[f'dados_{jogo}'] = dados
                        if f'res_{jogo}' in st.session_state: del st.session_state[f'res_{jogo}']
                        st.rerun()

            if f'dados_{jogo}' in st.session_state and st.session_state[f'dados_{jogo}'] is not None:
                df, cols_dezenas, vencedor, score_total, placar_dict, freq = st.session_state[f'dados_{jogo}']
                
                c1, c2 = st.columns([2, 1])
                with c1: st.markdown(f"Modelo: <span class='winner-tag'>{vencedor}</span>", unsafe_allow_html=True)
                with c2: st.caption(f"Score (12 jogos): {score_total}")

                tab_auditoria, tab_orc, tab_filtros, tab_mesa = st.tabs(["📊 Auditoria", "💰 Budget", "⚙️ Filtros", "🎲 Mesa"])
                
                with tab_auditoria:
                    if placar_dict:
                        df_placar = pd.DataFrame(list(placar_dict.items()), columns=['Modelo', 'Total Acertos'])
                        df_placar = df_placar.sort_values(by='Total Acertos', ascending=False)
                        st.dataframe(df_placar, hide_index=True, use_container_width=True)

                with tab_orc:
                    # UX: PEGA O VALOR DO JOGO DINAMICAMENTE
                    valor_minimo_jogo = otimizador.obter_preco_minimo(jogo)
                    
                    orcamento = st.number_input(
                        "Investimento (R$)", 
                        min_value=valor_minimo_jogo, 
                        value=valor_minimo_jogo, # AQUI: Valor padrão = Preço do jogo
                        step=valor_minimo_jogo,  # Step inteligente (pula de jogo em jogo)
                        key=f"b_{jogo}"
                    )
                    
                    if st.button("CALCULAR", key=f"btn_{jogo}", use_container_width=True):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            custo = sum(x['custo_total'] for x in res['carrinho'])
                            volantes = sum(x['qtd_volantes'] for x in res['carrinho'])
                            troco = res['sobra']
                            st.markdown("<div class='financial-box'>", unsafe_allow_html=True)
                            k1, k2, k3 = st.columns(3)
                            k1.metric("Custo", f"R${custo:.2f}")
                            k2.metric("Troco", f"R${troco:.2f}")
                            k3.metric("Jogos", f"{volantes}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        else: st.error(res['erro'])

                with tab_filtros:
                    if freq is not None:
                        todas_possiveis = sorted(freq.index.tolist())
                        todas_possiveis_int = [int(x) for x in todas_possiveis]
                        salvos = st.session_state.get(f'filtros_{jogo}', {'fixos': [], 'excluidos': []})
                        fixos = st.multiselect("🔒 Fixos:", todas_possiveis_int, default=salvos['fixos'], key=f"fix_{jogo}")
                        excluidos = st.multiselect("🚫 Excluídos:", todas_possiveis_int, default=salvos['excluidos'], key=f"exc_{jogo}")
                        st.session_state[f'filtros_{jogo}'] = {'fixos': fixos, 'excluidos': excluidos}

                with tab_mesa:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        filtros = st.session_state.get(f'filtros_{jogo}', {'fixos': [], 'excluidos': []})
                        dados_exp = []
                        st.markdown(f"**Estratégia:** {vencedor}")
                        idx_global = 0
                        for item in res['carrinho']:
                            q_v = item['qtd_volantes']
                            q_d = int(item['dezenas'])
                            st.markdown(f"👉 **{q_v}x** Jogos de **{q_d}** dezenas:")
                            for _ in range(q_v):
                                idx_global += 1
                                p = MotorInferencia.prever_proximo(vencedor, df, cols_dezenas, q_d, filtros['fixos'], filtros['excluidos'], seed_index=idx_global)
                                html = f"<span class='game-index'>#{idx_global:02d}</span>"
                                for n in p:
                                    cls = "ball-fixed" if n in filtros['fixos'] else "ball-normal"
                                    html += f"<div class='loto-ball {cls}'>{str(int(n)).zfill(2)}</div>"
                                stats_html = calcular_stats_completas(p)
                                score_eq = calcular_score_visual(p, q_d)
                                cv, ci = st.columns([3, 1])
                                cv.markdown(html, unsafe_allow_html=True)
                                with ci: st.progress(score_eq, "Equilíbrio")
                                st.markdown(stats_html, unsafe_allow_html=True)
                                dados_exp.append({"Jogo": idx_global, "Dezenas": p, "Modelo": vencedor})
                            st.divider()
                        d1, d2 = st.columns(2)
                        if dados_exp:
                            txt_str = "\n".join([f"Jogo {x['Jogo']}: {x['Dezenas']}" for x in dados_exp])
                            d1.download_button("📄 TXT", txt_str, f"{jogo}.txt")
                            d2.download_button("📊 CSV", to_csv(dados_exp), f"{jogo}.csv", "text/csv")
                    else: st.info("Calcule o orçamento.")
            else:
                st.warning("Falha ao carregar dados.")
                st.caption("Tente clicar no botão de atualizar.")
