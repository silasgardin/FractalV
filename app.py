import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FRACTALV | AI Analyst", layout="wide", page_icon="🧩")

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
        frequencia = pd.Series(todas_dezenas).value_counts()
        
        last_draw = df.iloc[0]
        return last_draw, series, frequencia
    except:
        return None, None, None

def gerar_palpites_inteligentes(qtd_jogos, qtd_dezenas_por_jogo, frequencia, modo_fractal):
    palpites = []
    if frequencia is None or len(frequencia) == 0: return []

    numeros_disponiveis = frequencia.index.tolist()
    
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

# --- 4. SIDEBAR INTELIGENTE (RESOLUÇÃO DE ERROS) ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("AI Analyst Module v2.3 (Debug)")
    st.divider()
    
    model = None
    nome_modelo_usado = "Nenhum"

    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        st.success("API Key: Encontrada 🟢")
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # TENTATIVA DE AUTO-CONFIGURAÇÃO DO MODELO
        try:
            # Lista de prioridade (do mais novo para o mais antigo)
            modelos_tentativa = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-1.0-pro']
            
            # Tenta instanciar o primeiro que funcionar
            model = genai.GenerativeModel('gemini-1.5-flash')
            nome_modelo_usado = 'gemini-1.5-flash'
            
        except Exception as e:
            st.error("Erro ao configurar modelo padrão.")
            
        # Botão de Diagnóstico (Para listar o que realmente está disponível)
        with st.expander("🛠️ Diagnóstico de Modelos"):
            try:
                st.write("Modelos disponíveis para sua chave:")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name)
            except Exception as e:
                st.write(f"Erro ao listar modelos: {e}")
                
    else:
        st.warning("API Key: Não configurada 🟠")
    
    if model:
        st.info(f"Modelo Ativo: {nome_modelo_usado}")

# --- 5. PAINEL PRINCIPAL ---
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
                hurst, modo, desc = MotorFractal.diagnosticar_tendencia(series_soma)
                
                c1, c2 = st.columns([1, 2])
                c1.metric("Hurst", f"{hurst:.2f}")
                c2.info(f"Modo: **{modo}**")
                
                tab1, tab2 = st.tabs(["💰 Estratégia", "🧠 Palpites & Análise"])
                
                with tab1:
                    orcamento = st.number_input("Orçamento (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
                    
                    if st.button("CALCULAR", key=f"btn_{jogo}"):
                        res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                        if "erro" not in res:
                            st.session_state[f'res_{jogo}'] = res
                            st.session_state[f'hurst_{jogo}'] = (hurst, modo)
                            st.success("Calculado! Veja a aba 'Palpites'.")
                        else:
                            st.error(res['erro'])

                with tab2:
                    if f'res_{jogo}' in st.session_state:
                        res = st.session_state[f'res_{jogo}']
                        modo_atual = st.session_state[f'hurst_{jogo}'][1]
                        
                        todos_jogos_texto = []
                        
                        for item in res['carrinho']:
                            q_volantes = item['qtd_volantes']
                            q_dezenas = int(item['dezenas'])
                            
                            st.markdown(f"👉 **{q_volantes}x** Jogos de **{q_dezenas}** dezenas:")
                            palpites = gerar_palpites_inteligentes(q_volantes, q_dezenas, freq, modo_atual)
                            
                            for idx, p in enumerate(palpites):
                                p_str = [str(int(n)).zfill(2) for n in p]
                                html_nums = "".join([f"<span class='big-number'>{n}</span>" for n in p_str])
                                st.markdown(html_nums, unsafe_allow_html=True)
                                todos_jogos_texto.append(f"Jogo {idx+1} ({q_dezenas} dz): {', '.join(p_str)}")
                            st.divider()

                        if model and todos_jogos_texto:
                            if st.button("🤖 ANALISAR COM IA", key=f"ai_{jogo}"):
                                with st.spinner(f"Analisando com {nome_modelo_usado}..."):
                                    try:
                                        jogos_str = "\n".join(todos_jogos_texto)
                                        prompt = f"Analise estatisticamente para {jogo} ({modo_atual}, Hurst {hurst:.2f}):\n{jogos_str}\n\nResponda: Pares/Ímpares estão bons? Nota de 0 a 10? Breve."
                                        analise = model.generate_content(prompt).text
                                        st.markdown(f"<div class='ai-box'>{analise}</div>", unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"Erro IA: {e}")
                                        st.caption("Dica: Verifique o 'Diagnóstico de Modelos' na barra lateral.")
                            else:
                                st.caption("Clique para validar com IA.")

                    else:
                        st.info("Calcule a estratégia primeiro.")
            else:
                st.warning("Sem conexão com dados.")
