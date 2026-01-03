import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | Precision", layout="wide", page_icon="🧩")

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .card-title { color: #00FF99; font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; margin-bottom: 10px;}
    .big-number { 
        font-size: 18px; font-weight: bold; color: #FFF; 
        background: #262730; padding: 4px 8px; border-radius: 4px; 
        border: 1px solid #444; display: inline-block; margin: 2px;
    }
    .stat-tag {
        font-size: 11px; color: #aaa; background: #1f2937; 
        padding: 2px 6px; border-radius: 3px; margin-left: 5px; border: 1px solid #333;
    }
    .fixed-num { border-color: #00FF99 !important; color: #00FF99 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONSTANTES MATEMÁTICAS ---
PRIMOS = set([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97])
FIBONACCI = set([1, 2, 3, 5, 8, 13, 21, 34, 55, 89])

# --- 4. FUNÇÕES AUXILIARES ---
@st.cache_data(ttl=600)
def get_data(jogo_key):
    """Lê os dados e prepara estatísticas"""
    link = LINKS_CSV.get(jogo_key)
    try:
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None, None, None
        
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        
        df['Soma'] = df[cols].sum(axis=1)
        series = df.head(60)['Soma'].values
        
        todas_dezenas = df.head(50)[cols].values.flatten()
        todas_dezenas = todas_dezenas[~np.isnan(todas_dezenas)]
        frequencia = pd.Series(todas_dezenas).value_counts().sort_values(ascending=False)
        
        last_draw = df.iloc[0]
        return last_draw, series, frequencia
    except:
        return None, None, None

def gerar_palpites_controlados(qtd_jogos, qtd_dezenas, frequencia, modo_fractal, fixos=[], excluidos=[]):
    """Gera palpites respeitando Hurst + Filtros do Usuário"""
    palpites = []
    if frequencia is None or len(frequencia) == 0: return []

    # 1. Remove excluídos da lista disponível
    numeros_disponiveis = [n for n in frequencia.index.tolist() if n not in excluidos and n not in fixos]
    
    # 2. Recalcula pesos apenas para os disponíveis
    if not numeros_disponiveis: return [] # Segurança

    if "TENDÊNCIA" in modo_fractal:
        pesos = np.linspace(1.0, 0.2, len(numeros_disponiveis))
    elif "REVERSÃO" in modo_fractal:
        pesos = np.linspace(0.2, 1.0, len(numeros_disponiveis))
    else:
        pesos = np.ones(len(numeros_disponiveis)) 
    
    # Normaliza pesos
    pesos = pesos / pesos.sum()
    
    # Quantas vagas restam preencher (Total - Fixos)
    vagas_abertas = int(qtd_dezenas) - len(fixos)
    if vagas_abertas < 0: vagas_abertas = 0 # Caso o usuário fixe mais do que o jogo permite

    for _ in range(qtd_jogos):
        try:
            # Sorteia apenas para as vagas abertas
            if vagas_abertas > 0:
                escolhidos = np.random.choice(numeros_disponiveis, vagas_abertas, p=pesos, replace=False).tolist()
            else:
                escolhidos = []
            
            # Junta com os fixos
            aposta_final = list(set(escolhidos + fixos)) # Set garante unicidade
            aposta_final.sort()
            palpites.append(aposta_final)
        except:
            # Fallback
            palpites.append(list(range(1, int(qtd_dezenas)+1)))
            
    return palpites

def calcular_stats_avancadas(dezenas):
    """Retorna estatísticas completas"""
    pares = len([x for x in dezenas if x % 2 == 0])
    impares = len(dezenas) - pares
    soma = int(sum(dezenas))
    qtd_primos = len([x for x in dezenas if x in PRIMOS])
    qtd_fibo = len([x for x in dezenas if x in FIBONACCI])
    
    return f"P: {pares}/Í: {impares} | Σ: {soma} | Primos: {qtd_primos} | Fibo: {qtd_fibo}"

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Precision Module v3.2")
    st.divider()
    st.markdown("### ⚙️ Configurações de Engenharia")
    st.info("Utilize as abas dentro de cada jogo para definir números fixos ou excluídos.")

# --- 6. PAINEL PRINCIPAL ---
st.title("Painel de Controle Estratégico")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))
jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            last_draw, series_soma, freq = get_data(jogo)
            
            if series_soma is not None:
                # Diagnóstico
                hurst, modo, desc = MotorFractal.diagnosticar_tendencia(series_soma)
                
                # Header Stats
                c1, c2 = st.columns([1, 2])
                c1.metric("Hurst", f"{hurst:.2f}")
                if "TENDÊNCIA" in modo:
                    c2.success(f"Modo: {modo}")
                elif "REVERSÃO" in modo:
                    c2.info(f"Modo: {modo}")
                else:
                    c2.warning(f"Modo: {modo}")

                # --- CONTROLE ESTRATÉGICO (ABAS) ---
                tab_money, tab_config, tab_palpites = st.tabs(["💰 Budget", "⚙️ Filtros", "🎲 Gerador"])
                
                # 1. FINANCEIRO
                with tab_money:
                    orcamento = st.number_input("Investimento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    if st.button("CALCULAR ALOCAÇÃO", key=f"btn_{jogo}"):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'hurst_{jogo}'] = (hurst, modo)
                            st.success("Alocação definida! Vá para 'Filtros' ou 'Gerador'.")
                        else:
                            st.error(res['erro'])

                # 2. FILTROS E HEATMAP
                with tab_config:
                    st.caption("Analise a frequência e force sua vontade sobre o Fractal.")
                    
                    # Mapa de Frequência (Mini Heatmap)
                    if freq is not None:
                        df_freq = pd.DataFrame({'Dezena': freq.index, 'Freq': freq.values})
                        # Mostra Top 5 Quentes e Top 5 Frios
                        col_h, col_c = st.columns(2)
                        col_h.dataframe(df_freq.head(5).style.background_gradient(cmap='Reds'), hide_index=True, use_container_width=True)
                        col_c.dataframe(df_freq.tail(5).sort_values(by='Freq').style.background_gradient(cmap='Blues'), hide_index=True, use_container_width=True)
                    
                    # Inputs de Controle
                    todas_possiveis = sorted(freq.index.tolist()) if freq is not None else []
                    
                    fixos = st.multiselect("🔒 Números FIXOS (Obrigatórios):", todas_possiveis, key=f"fix_{jogo}")
                    excluidos = st.multiselect("🚫 Números EXCLUÍDOS (Banidos):", todas_possiveis, key=f"exc_{jogo}")
                    
                    # Salva filtros no session state para usar no gerador
                    st.session_state[f'filtros_{jogo}'] = {'fixos': fixos, 'excluidos': excluidos}

                # 3. GERADOR E EXPORTAÇÃO
                with tab_palpites:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modo_atual = st.session_state[f'hurst_{jogo}'][1]
                        
                        # Recupera filtros
                        filtros = st.session_state.get(f'filtros_{jogo}', {'fixos': [], 'excluidos': []})
                        
                        st.write(f"Gerando com: **{len(filtros['fixos'])} Fixos** | **{len(filtros['excluidos'])} Banidos**")
                        
                        lista_txt = [f"=== FRACTALV: {jogo} ===", f"Modo: {modo_atual} | Fixos: {filtros['fixos']}\n"]
                        
                        for item in res['carrinho']:
                            q_vol = item['qtd_volantes']
                            q_dez = int(item['dezenas'])
                            
                            st.markdown(f"👉 **{q_vol}x** Jogos de **{q_dez}** dezenas:")
                            
                            # GERAÇÃO COM FILTROS
                            palpites = gerar_palpites_controlados(q_vol, q_dez, freq, modo_atual, filtros['fixos'], filtros['excluidos'])
                            
                            for idx, p in enumerate(palpites):
                                # Formatação Visual (Destaque para Fixos)
                                html_parts = []
                                for n in p:
                                    n_str = str(int(n)).zfill(2)
                                    # Se for fixo, pinta de verde (classe css .fixed-num)
                                    css_class = "big-number fixed-num" if n in filtros['fixos'] else "big-number"
                                    html_parts.append(f"<span class='{css_class}'>{n_str}</span>")
                                
                                stats = calcular_stats_avancadas(p)
                                st.markdown("".join(html_parts) + f"<br><span class='stat-tag'>{stats}</span>", unsafe_allow_html=True)
                                
                                lista_txt.append(f"Jogo {idx+1}: {', '.join([str(x).zfill(2) for x in p])}")
                            
                            st.divider()
                        
                        st.download_button("📥 BAIXAR TXT", "\n".join(lista_txt), f"fractalv_{jogo}.txt")
                        
                    else:
                        st.info("Defina o orçamento na primeira aba.")
            else:
                st.warning("Sem dados.")
