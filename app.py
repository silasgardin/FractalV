import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from motor_matematico import OtimizadorFinanceiro, MotorInferencia
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | Stable", layout="wide", page_icon="🧩")

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    
    /* Header do Card com Botão */
    .card-header-container {
        display: flex;
        justify_content: space-between;
        align-items: center;
        border-bottom: 2px solid #333;
        margin-bottom: 15px;
        padding-bottom: 5px;
    }
    .card-title-text { color: #00FF99; font-size: 22px; font-weight: bold; }
    
    /* Elementos Visuais */
    .game-index { font-family: 'Courier New', monospace; color: #00FF99; font-size: 16px; font-weight: bold; margin-right: 10px; vertical-align: middle; display: inline-block; }
    .loto-ball { display: inline-flex; align-items: center; justify-content: center; width: 35px; height: 35px; border-radius: 50%; font-weight: bold; color: #FFF; margin: 2px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); font-size: 14px; vertical-align: middle; }
    .ball-normal { background: radial-gradient(circle at 10px 10px, #a855f7, #581c87); border: 1px solid #c084fc; }
    .ball-fixed { background: radial-gradient(circle at 10px 10px, #00FF99, #008f55); color: #000; border: 1px solid #00FF99; }
    .winner-tag { background-color: #00FF99; color: black; padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 12px; }
    .stat-box { font-size: 11px; color: #aaa; background: #1f2937; padding: 4px 8px; border-radius: 4px; margin-top: 5px; display: inline-block; }
    .stProgress > div > div > div > div { background-color: #a855f7; }
    div[data-testid="stTable"] { font-size: 14px; }
    .financial-box { border: 1px solid #333; background: #1a1a1a; padding: 15px; border-radius: 10px; margin-top: 10px; }
    .update-info { font-size: 12px; color: #666; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES AUXILIARES ---

# Removemos o cache global aqui para forçar atualização quando o botão for clicado
# O controle de cache será feito via Session State
def processar_dados_online(jogo_key):
    link = LINKS_CSV.get(jogo_key)
    try:
        # Lê sempre fresco da URL
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None, None, None, None, None, None
        
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        
        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts().sort_values(ascending=False)
        
        # Executa Backtest
        vencedor, score_total, placar_dict = MotorInferencia.executar_backtest_profundo(df, cols, profundidade=12)
        
        return df, cols, vencedor, score_total, placar_dict, freq
    except Exception as e:
        return None, None, None, None, None, None

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
    st.caption("Stable Engine v10.0")
    st.divider()
    st.success("Modo Estável Ativo")
    st.info("A estratégia agora é FIXA. Ela só muda quando você clica no botão 'Atualizar' de cada jogo.")
    
    if st.button("🗑️ Limpar Tudo (Reset Geral)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 5. PAINEL PRINCIPAL ---
st.title("Painel Estratégico de Lotarias")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))
jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols_layout = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols_layout[i % 2]:
        with st.container(border=True):
            
            # --- CABEÇALHO COM BOTÃO DE ATUALIZAÇÃO ---
            # Layout em colunas dentro do card para o título e o botão
            col_titulo, col_btn = st.columns([3, 1])
            
            with col_titulo:
                st.markdown(f"<div class='card-title-text'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            with col_btn:
                # Botão único que dispara a atualização
                if st.button("🔄 Atualizar", key=f"up_{jogo}", help="Baixa dados novos e refaz o backtest"):
                    with st.spinner("Analisando..."):
                        dados = processar_dados_online(jogo)
                        # Salva tudo no Session State (Memória Persistente)
                        st.session_state[f'dados_{jogo}'] = dados
                        # Limpa resultados antigos de cálculo
                        if f'res_{jogo}' in st.session_state: del st.session_state[f'res_{jogo}']
                        st.rerun()

            # --- VERIFICAÇÃO DE ESTADO ---
            # Se temos dados na memória, usamos eles. Se não, pedimos para atualizar.
            if f'dados_{jogo}' in st.session_state and st.session_state[f'dados_{jogo}'][0] is not None:
                # Recupera dados da memória
                df, cols_dezenas, vencedor, score_total, placar_dict, freq = st.session_state[f'dados_{jogo}']
                
                # Mostra Informações
                c1, c2 = st.columns([2, 1])
                with c1: 
                    st.markdown(f"Estratégia Fixada: <span class='winner-tag'>{vencedor}</span>", unsafe_allow_html=True)
                with c2: 
                    st.caption(f"Score Backtest: {score_total}")

                # Abas
                tab_backtest, tab_orc, tab_filtros, tab_gerador = st.tabs(["📊 Auditoria", "💰 Budget", "⚙️ Filtros", "🎲 Mesa"])
                
                with tab_backtest:
                    st.caption("Performance nos últimos 12 concursos (Dados Congelados):")
                    if placar_dict:
                        df_placar = pd.DataFrame(list(placar_dict.items()), columns=['Modelo', 'Total Acertos'])
                        df_placar = df_placar.sort_values(by='Total Acertos', ascending=False)
                        st.dataframe(df_placar, hide_index=True, use_container_width=True)

                with tab_orc:
                    orcamento = st.number_input("Investimento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    if st.button("CALCULAR ESTRATÉGIA", key=f"btn_{jogo}", use_container_width=True):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            
                            total_gasto = sum([item['custo_total'] for item in res['carrinho']])
                            total_volantes = sum([item['qtd_volantes'] for item in res['carrinho']])
                            troco = res['sobra']
                            
                            st.markdown("<div class='financial-box'>", unsafe_allow_html=True)
                            f1, f2, f3 = st.columns(3)
                            f1.metric("Investimento", f"R$ {total_gasto:.2f}")
                            f2.metric("Troco", f"R$ {troco:.2f}")
                            f3.metric("Jogos", f"{total_volantes}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        else: st.error(res['erro'])

                with tab_filtros:
                    if freq is not None:
                        todas_possiveis = sorted(freq.index.tolist())
                        # Recupera filtros salvos ou inicia vazio
                        filtros_salvos = st.session_state.get(f'filtros_{jogo}', {'fixos': [], 'excluidos': []})
                        
                        fixos = st.multiselect("🔒 Fixos:", todas_possiveis, default=filtros_salvos['fixos'], key=f"fix_{jogo}")
                        excluidos = st.multiselect("🚫 Excluídos:", todas_possiveis, default=filtros_salvos['excluidos'], key=f"exc_{jogo}")
                        
                        # Salva filtros no estado
                        st.session_state[f'filtros_{jogo}'] = {'fixos': fixos, 'excluidos': excluidos}

                with tab_gerador:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        filtros = st.session_state.get(f'filtros_{jogo}', {'fixos': [], 'excluidos': []})
                        dados_exportacao = []
                        
                        st.markdown(f"**Modelo Ativo:** {vencedor}")
                        global_idx = 0
                        
                        for item in res['carrinho']:
                            q_vol = item['qtd_volantes']
                            q_dez = int(item['dezenas'])
                            st.markdown(f"👉 **{q_vol}x** Jogos de **{q_dez}** dezenas:")
                            
                            for _ in range(q_vol):
                                global_idx += 1
                                # Usa o dataframe congelado no session_state
                                p = MotorInferencia.prever_proximo(
                                    vencedor, df, cols_dezenas, q_dez, 
                                    fixos=filtros['fixos'], excluidos=filtros['excluidos'],
                                    seed_index=global_idx
                                )
                                
                                html_balls = f"<span class='game-index'>#{global_idx:02d}</span>"
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
                                
                                dados_exportacao.append({"Jogo": global_idx, "Dezenas": p, "Modelo": vencedor})
                            st.divider()
                        
                        c1, c2 = st.columns(2)
                        if dados_exportacao:
                            txt = "\n".join([f"Jogo {d['Jogo']}: {d['Dezenas']}" for d in dados_exportacao])
                            c1.download_button("📄 TXT", txt, f"{jogo}.txt")
                            c2.download_button("📊 CSV", to_csv(dados_exportacao), f"{jogo}.csv", "text/csv")
                    else: st.info("Defina o orçamento e clique em Calcular.")
            
            else:
                # Estado Inicial (Sem dados)
                st.info("⚠️ Dados pendentes.")
                st.caption("Clique em '🔄 Atualizar' para baixar a planilha do dia e rodar a I.A.")
