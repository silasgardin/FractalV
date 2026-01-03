import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
import plotly.express as px
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | Pro", layout="wide", page_icon="🧩")

# --- 2. CSS PERSONALIZADO (Visual Tech) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .card-title { color: #00FF99; font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; margin-bottom: 10px;}
    .big-number { 
        font-size: 18px; font-weight: bold; color: #FFF; 
        background: #262730; padding: 4px 8px; border-radius: 4px; 
        border: 1px solid #444; display: inline-block; margin: 2px;
    }
    .metric-box { background: #1f2937; padding: 10px; border-radius: 5px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES AUXILIARES ---
@st.cache_data(ttl=600)
def get_data(jogo_key):
    """Lê os dados e prepara séries temporais"""
    link = LINKS_CSV.get(jogo_key)
    try:
        # Tenta ler ignorando erros de linha
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        
        # Identifica colunas de dezenas (D1, D2...)
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None, None, None
        
        # Garante que sejam números
        for c in cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        
        # Cria coluna de SOMA (para o gráfico fractal)
        df['Soma'] = df[cols].sum(axis=1)
        
        # Pega últimos 100 resultados para gráfico
        series = df.head(100)['Soma'].values
        
        # Calcula frequência para gerar palpites inteligentes
        todas_dezenas = df.head(50)[cols].values.flatten()
        todas_dezenas = todas_dezenas[~np.isnan(todas_dezenas)] # Remove NaNs
        frequencia = pd.Series(todas_dezenas).value_counts()
        
        last_draw = df.iloc[0]
        return last_draw, series, frequencia
    except:
        return None, None, None

def gerar_palpites_inteligentes(qtd_jogos, qtd_dezenas_por_jogo, frequencia, modo_fractal):
    """Gera números baseados na lógica Quente/Frio do Fractal"""
    palpites = []
    if frequencia is None or len(frequencia) == 0:
        return []

    numeros_disponiveis = frequencia.index.tolist()
    
    # Lógica de Pesos
    if "TENDÊNCIA" in modo_fractal:
        pesos = np.linspace(1.0, 0.2, len(numeros_disponiveis))
    elif "REVERSÃO" in modo_fractal:
        pesos = np.linspace(0.2, 1.0, len(numeros_disponiveis))
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

# --- 4. SIDEBAR (CONFIGURAÇÃO) ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Sistema de Inteligência Fractal v2.0")
    st.divider()
    
    # Status IA
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        st.success("IA Gemini: CONECTADO 🟢")
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-pro')
        except:
            model = None
    else:
        st.warning("IA Gemini: OFF 🟠")
        model = None
    
    st.divider()
    st.info("O modelo ajusta os pesos matemáticos automaticamente baseado no Hurst.")

# --- 5. PAINEL PRINCIPAL ---
st.title("Painel de Controle Estratégico")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))

jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            # 1. Dados e Diagnóstico
            last_draw, series_soma, freq = get_data(jogo)
            
            if series_soma is not None:
                # Diagnóstico Fractal
                hurst, modo, desc = MotorFractal.diagnosticar_tendencia(series_soma)
                
                # Exibição Rápida
                c1, c2 = st.columns([1, 2])
                c1.metric("Hurst", f"{hurst:.2f}")
                c2.info(f"Modo: **{modo}**")
                
                # --- SISTEMA DE ABAS ---
                tab1, tab2, tab3 = st.tabs(["💰 Estratégia", "🎲 Palpites", "📈 Gráfico"])
                
                # ABA 1: DEFINIÇÃO DE ORÇAMENTO
                with tab1:
                    orcamento = st.number_input("Orçamento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    
                    if st.button("CALCULAR ESTRATÉGIA", key=f"btn_{jogo}"):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'hurst_{jogo}'] = (hurst, modo)
                            st.success("Cálculo Realizado! Veja a aba 'Palpites'.")
                            
                            if model:
                                with st.spinner("Consultando IA..."):
                                    try:
                                        p = f"Analise curto: Jogo {jogo}, Hurst {hurst:.2f} ({modo}). Orçamento R$ {orcamento}. Sugestão: {res['carrinho']}."
                                        analise = model.generate_content(p).text
                                        st.caption(f"🤖 **IA:** {analise}")
                                    except:
                                        pass
                        else:
                            st.error(res['erro'])

                # ABA 2: PALPITES GERADOS
                with tab2:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modo_atual = st.session_state[f'hurst_{jogo}'][1]
                        
                        st.write(f"Distribuição Otimizada ({modo_atual}):")
                        
                        for item in res['carrinho']:
                            q_volantes = item['qtd_volantes']
                            q_dezenas = int(item['dezenas'])
                            
                            st.markdown(f"👉 **{q_volantes}x** Jogos de **{q_dezenas}** dezenas:")
                            
                            palpites = gerar_palpites_inteligentes(q_volantes, q_dezenas, freq, modo_atual)
                            
                            for p in palpites:
                                p_str = [str(int(n)).zfill(2) for n in p]
                                html_nums = "".join([f"<span class='big-number'>{n}</span>" for n in p_str])
                                st.markdown(html_nums, unsafe_allow_html=True)
                            
                            st.divider()
                    else:
                        st.info("Calcule a estratégia na aba anterior primeiro.")

                # ABA 3: GRÁFICO (CORRIGIDO AQUI)
                with tab3:
                    if len(series_soma) > 0:
                        dados_grafico = series_soma[::-1] 
                        fig = px.line(y=dados_grafico, labels={'x': 'Tempo', 'y': 'Soma Dezenas'})
                        fig.update_layout(title="Onda Fractal (Últimos 100)", template="plotly_dark", height=250, margin=dict(l=20, r=20, t=30, b=20))
                        fig.add_hline(y=np.mean(dados_grafico), line_dash="dot", annotation_text="Média", annotation_position="bottom right")
                        
                        # --- A CORREÇÃO ESTÁ NESTA LINHA ABAIXO ---
                        # Adicionamos key=f"graf_{jogo}" para evitar duplicação de ID
                        st.plotly_chart(fig, use_container_width=True, key=f"graf_{jogo}")
            
            else:
                st.warning("Aguardando conexão com base de dados...")
