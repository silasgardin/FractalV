import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | AI Analyst", layout="wide", page_icon="🧩")

# --- 2. CSS PERSONALIZADO (Visual Tech Clean) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .card-title { color: #00FF99; font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; margin-bottom: 10px;}
    .big-number { 
        font-size: 18px; font-weight: bold; color: #FFF; 
        background: #262730; padding: 4px 8px; border-radius: 4px; 
        border: 1px solid #444; display: inline-block; margin: 2px;
    }
    .ai-box {
        background-color: #1a2332;
        border-left: 3px solid #00FF99;
        padding: 15px;
        border-radius: 5px;
        margin-top: 15px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES AUXILIARES ---
@st.cache_data(ttl=600)
def get_data(jogo_key):
    """Lê os dados e prepara estatísticas"""
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
        
        # Cria coluna de SOMA (para o cálculo do Hurst)
        df['Soma'] = df[cols].sum(axis=1)
        series = df.head(60)['Soma'].values # Série temporal para Hurst
        
        # Calcula frequência para gerar palpites
        todas_dezenas = df.head(50)[cols].values.flatten()
        todas_dezenas = todas_dezenas[~np.isnan(todas_dezenas)] # Remove NaNs
        frequencia = pd.Series(todas_dezenas).value_counts()
        
        last_draw = df.iloc[0]
        return last_draw, series, frequencia
    except:
        return None, None, None

def gerar_palpites_inteligentes(qtd_jogos, qtd_dezenas_por_jogo, frequencia, modo_fractal):
    """Gera números usando pesos matemáticos (Hurst)"""
    palpites = []
    if frequencia is None or len(frequencia) == 0:
        return []

    numeros_disponiveis = frequencia.index.tolist()
    
    # Lógica de Pesos: Tendência (Quem sai mais) vs Reversão (Quem sai menos)
    if "TENDÊNCIA" in modo_fractal:
        pesos = np.linspace(1.0, 0.2, len(numeros_disponiveis))
    elif "REVERSÃO" in modo_fractal:
        pesos = np.linspace(0.2, 1.0, len(numeros_disponiveis))
    else:
        pesos = np.ones(len(numeros_disponiveis)) 
        
    pesos = pesos / pesos.sum()
    
    for _ in range(qtd_jogos):
        try:
            # Sorteio ponderado
            aposta = np.random.choice(numeros_disponiveis, int(qtd_dezenas_por_jogo), p=pesos, replace=False)
            aposta.sort()
            palpites.append(aposta)
        except:
            # Fallback (Sorteio simples se der erro nos pesos)
            palpites.append(np.random.choice(numeros_disponiveis, int(qtd_dezenas_por_jogo), replace=False))
            
    return palpites

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("AI Analyst Module v2.1")
    st.divider()
    
    # Conexão IA
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
    
    st.info("A geração de gráficos foi removida para priorizar a análise textual dos números.")

# --- 5. PAINEL PRINCIPAL ---
st.title("Painel de Controle Estratégico")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))

jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols = st.columns(2)

for i, jogo in enumerate(jogos):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            # 1. Carregar Dados e Diagnóstico
            last_draw, series_soma, freq = get_data(jogo)
            
            if series_soma is not None:
                # Diagnóstico Hurst
                hurst, modo, desc = MotorFractal.diagnosticar_tendencia(series_soma)
                
                # Exibição Rápida
                c1, c2 = st.columns([1, 2])
                c1.metric("Hurst", f"{hurst:.2f}")
                c2.info(f"Modo: **{modo}**")
                
                # --- NOVO SISTEMA DE ABAS (Simplificado: Sem Gráfico) ---
                tab1, tab2 = st.tabs(["💰 Estratégia (Budget)", "🧠 Palpites & Análise IA"])
                
                # ABA 1: ORÇAMENTO
                with tab1:
                    orcamento = st.number_input("Orçamento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    
                    if st.button("CALCULAR ESTRATÉGIA", key=f"btn_{jogo}"):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        
                        if "erro" not in res:
                            # Salva tudo no estado para a próxima aba
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'hurst_{jogo}'] = (hurst, modo)
                            st.success("Cálculo Realizado! Vá para a aba 'Palpites' para ver os números.")
                        else:
                            st.error(res['erro'])

                # ABA 2: PALPITES + ANÁLISE GEMINI
                with tab2:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modo_atual = st.session_state[f'hurst_{jogo}'][1]
                        
                        st.write(f"Distribuição Otimizada ({modo_atual}):")
                        
                        todos_jogos_texto = [] # Armazena para mandar para a IA
                        
                        for item in res['carrinho']:
                            q_volantes = item['qtd_volantes']
                            q_dezenas = int(item['dezenas'])
                            
                            st.markdown(f"👉 **{q_volantes}x** Jogos de **{q_dezenas}** dezenas:")
                            
                            # Gera números
                            palpites = gerar_palpites_inteligentes(q_volantes, q_dezenas, freq, modo_atual)
                            
                            for idx, p in enumerate(palpites):
                                # Formatação Visual
                                p_str = [str(int(n)).zfill(2) for n in p]
                                html_nums = "".join([f"<span class='big-number'>{n}</span>" for n in p_str])
                                st.markdown(html_nums, unsafe_allow_html=True)
                                
                                # Guarda texto para a IA analisar
                                todos_jogos_texto.append(f"Jogo {idx+1} ({q_dezenas} dz): {', '.join(p_str)}")
                            
                            st.divider()

                        # --- ANÁLISE FINAL DA IA SOBRE OS NÚMEROS ---
                        if model and todos_jogos_texto:
                            if st.button("🤖 ANALISAR ESCOLHA DOS NÚMEROS", key=f"ai_{jogo}"):
                                with st.spinner("Gemini está analisando a simetria dos palpites..."):
                                    try:
                                        jogos_str = "\n".join(todos_jogos_texto)
                                        prompt = f"""
                                        Atue como o sistema FRACTALV. O algoritmo gerou estes palpites para {jogo} baseado em uma lógica de {modo_atual} (Hurst {hurst:.2f}).
                                        
                                        Jogos Gerados:
                                        {jogos_str}
                                        
                                        Analise tecnicamente a escolha desses números específicos:
                                        1. A distribuição entre Pares e Ímpares está equilibrada?
                                        2. Existem sequências perigosas?
                                        3. Dê uma nota de 0 a 10 para a qualidade estatística desse conjunto.
                                        Seja direto e breve.
                                        """
                                        analise = model.generate_content(prompt).text
                                        st.markdown(f"<div class='ai-box'>{analise}</div>", unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"Erro na análise IA: {e}")
                            else:
                                st.caption("Clique no botão acima para validar os jogos com a IA.")

                    else:
                        st.info("Defina o orçamento na aba anterior primeiro.")
            
            else:
                st.warning("Aguardando conexão com base de dados...")
