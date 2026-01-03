import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | Pro Tools", layout="wide", page_icon="🧩")

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
        font-size: 12px; color: #aaa; background: #1f2937; 
        padding: 2px 6px; border-radius: 3px; margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES AUXILIARES ---
@st.cache_data(ttl=600)
def get_data(jogo_key):
    """Lê os dados e prepara estatísticas"""
    link = LINKS_CSV.get(jogo_key)
    try:
        # Leitura tolerante a falhas
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None, None, None
        
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        
        df['Soma'] = df[cols].sum(axis=1)
        series = df.head(60)['Soma'].values
        
        todas_dezenas = df.head(50)[cols].values.flatten()
        todas_dezenas = todas_dezenas[~np.isnan(todas_dezenas)]
        frequencia = pd.Series(todas_dezenas).value_counts()
        
        last_draw = df.iloc[0]
        return last_draw, series, frequencia
    except:
        return None, None, None

def gerar_palpites_inteligentes(qtd_jogos, qtd_dezenas_por_jogo, frequencia, modo_fractal):
    """Gera números com base na matemática do Fractal"""
    palpites = []
    if frequencia is None or len(frequencia) == 0: return []

    numeros_disponiveis = frequencia.index.tolist()
    
    # Pesos baseados no Hurst
    if "TENDÊNCIA" in modo_fractal:
        pesos = np.linspace(1.0, 0.2, len(numeros_disponiveis)) # Prioriza quentes
    elif "REVERSÃO" in modo_fractal:
        pesos = np.linspace(0.2, 1.0, len(numeros_disponiveis)) # Prioriza frios
    else:
        pesos = np.ones(len(numeros_disponiveis)) 
        
    pesos = pesos / pesos.sum()
    
    for _ in range(qtd_jogos):
        try:
            aposta = np.random.choice(numeros_disponiveis, int(qtd_dezenas_por_jogo), p=pesos, replace=False)
            aposta.sort()
            palpites.append(aposta)
        except:
            palpites.append(np.random.choice(numeros_disponiveis, int(qtd_dezenas_por_jogo), replace=False))
            
    return palpites

def calcular_stats_jogo(dezenas):
    """Retorna estatísticas rápidas do jogo gerado"""
    pares = len([x for x in dezenas if x % 2 == 0])
    impares = len(dezenas) - pares
    soma = int(sum(dezenas))
    return f"Pares: {pares} | Ímpares: {impares} | Soma: {soma}"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Math Engine v3.1 (Tools)")
    st.divider()
    st.success("Sistema Operacional 🟢")
    
    with st.expander("ℹ️ Legenda Hurst"):
        st.markdown("""
        - **> 0.55 (Tendência):** Repete o padrão recente.
        - **< 0.45 (Reversão):** Quebra o padrão (aposta no atrasado).
        - **0.50 (Neutro):** Aleatório puro.
        """)

# --- 5. PAINEL PRINCIPAL ---
st.title("Painel de Controle Estratégico")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))

jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            # 1. Carregar Dados
            last_draw, series_soma, freq = get_data(jogo)
            
            if series_soma is not None:
                # 2. Diagnóstico Matemático
                hurst, modo, desc = MotorFractal.diagnosticar_tendencia(series_soma)
                
                # Exibição dos Indicadores
                c1, c2 = st.columns([1, 2])
                c1.metric("Hurst", f"{hurst:.2f}")
                
                # Badge visual de modo
                if "TENDÊNCIA" in modo:
                    c2.markdown("🔥 **Modo: TENDÊNCIA (Quentes)**")
                    c2.caption("O mercado está repetindo padrões.")
                elif "REVERSÃO" in modo:
                    c2.markdown("🧊 **Modo: REVERSÃO (Frios)**")
                    c2.caption("O mercado busca equilíbrio.")
                else:
                    c2.markdown("🎲 **Modo: ALEATÓRIO**")
                
                # 3. Abas de Operação
                tab1, tab2 = st.tabs(["💰 Estratégia", "🎲 Palpites & Exportação"])
                
                # Aba Financeira
                with tab1:
                    orcamento = st.number_input("Investimento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    
                    if st.button("CALCULAR MELHOR ALOCAÇÃO", key=f"btn_{jogo}"):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'hurst_{jogo}'] = (hurst, modo)
                            st.success("Estratégia Calculada! Veja a aba 'Palpites'.")
                        else:
                            st.error(res['erro'])

                # Aba de Geração de Números
                with tab2:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modo_atual = st.session_state[f'hurst_{jogo}'][1]
                        
                        st.write(f"Distribuição: **{modo_atual}**")
                        
                        lista_para_txt = []
                        lista_para_txt.append(f"=== PALPITES FRACTALV: {jogo} ===")
                        lista_para_txt.append(f"Estratégia: {modo_atual} | Hurst: {hurst:.2f}\n")
                        
                        for item in res['carrinho']:
                            q_volantes = item['qtd_volantes']
                            q_dezenas = int(item['dezenas'])
                            
                            st.markdown(f"👉 **{q_volantes}x** Jogos de **{q_dezenas}** dezenas:")
                            
                            # Gera os números
                            palpites = gerar_palpites_inteligentes(q_volantes, q_dezenas, freq, modo_atual)
                            
                            for idx, p in enumerate(palpites):
                                # Formatação visual das bolinhas
                                p_str = [str(int(n)).zfill(2) for n in p]
                                html_nums = "".join([f"<span class='big-number'>{n}</span>" for n in p_str])
                                
                                # Cálculo de estatísticas locais (Sem IA)
                                stats = calcular_stats_jogo(p)
                                
                                st.markdown(f"{html_nums} <span class='stat-tag'>{stats}</span>", unsafe_allow_html=True)
                                
                                # Prepara texto para download
                                lista_para_txt.append(f"Jogo {idx+1}: {', '.join(p_str)}")
                            
                            st.divider()
                        
                        # --- BOTÃO DE DOWNLOAD ---
                        texto_final = "\n".join(lista_para_txt)
                        st.download_button(
                            label="📥 BAIXAR JOGOS (.txt)",
                            data=texto_final,
                            file_name=f"fractalv_{jogo.lower()}.txt",
                            mime="text/plain",
                            key=f"dl_{jogo}"
                        )
                    else:
                        st.info("Defina o orçamento e clique em Calcular primeiro.")
            
            else:
                st.warning("Aguardando conexão com base de dados...")
