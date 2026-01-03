import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import requests
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV



# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="FRACTALV", layout="wide", page_icon="🧩")

# --- CSS PARA VISUAL TECH ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; font-size: 14px;}
    .success { background-color: #1f77b4; color: white; }
    .error { background-color: #d62728; color: white; }
    .card-title { color: #00FF99; font-size: 22px; font-weight: bold; border-bottom: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DIAGNÓSTICO ---
# No src/app.py, procure a função check_connection_drive e troque por esta:

def check_connection_drive():
    """Testa a conexão lendo a primeira linha real do arquivo"""
    url = LINKS_CSV.get("VALORES")
    
    # 1. Verifica se o link ainda é o de exemplo (placeholder)
    if "..." in url or "INSIRA_O_ID" in url:
        return False
        
    # 2. Tenta ler o arquivo de verdade
    try:
        # Lê apenas 1 linha para ser rápido
        pd.read_csv(url, nrows=1, decimal=",", thousands=".", on_bad_lines='skip')
        return True
    except Exception as e:
        # Se quiser debugar, descomente a linha abaixo para ver o erro no terminal
        # print(f"Erro de Conexão: {e}")
        return False

# --- SIDEBAR: MONITORAMENTO DE SISTEMA ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Monitoramento de Recursos")
    st.divider()

    # Status Base de Dados
    drive_ok = check_connection_drive()
    if drive_ok:
        st.success("Base de Dados (Drive): CONECTADO 🟢")
    else:
        st.error("Base de Dados (Drive): FALHA 🔴")

    # Status IA
    ai_ok = check_ai_connection()
    if ai_ok:
        st.success("Módulo Gemini AI: ATIVO 🟢")
        # Configura a IA silenciosamente
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.warning("Módulo Gemini AI: DESCONECTADO 🟠")
        model = None
    
    st.divider()
    st.markdown("**Versão:** FractalV-1.2 (Auto-Backtest)")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=600)
def get_data(jogo_key):
    link = LINKS_CSV.get(jogo_key)
    try:
        # Lê e limpa
        df = pd.read_csv(link, decimal=",", thousands=".")
        # Pega colunas D1, D2... para cálculo
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        series = df.head(60)[cols].sum(axis=1).values # Soma das dezenas para Hurst
        last_draw = df.iloc[0]
        return last_draw, series
    except:
        return None, None

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))

# --- INTERFACE PRINCIPAL ---
st.title("Painel de Controle Estratégico")

jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols = st.columns(3)

for i, jogo in enumerate(jogos):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            # 1. Backtest Automático
            last_draw, series_numerica = get_data(jogo)
            
            if series_numerica is not None:
                st.caption(f"Último: {last_draw['Data']} (Conc. {last_draw['Concurso']})")
                
                # O CÓDIGO DECIDE SOZINHO:
                hurst, estrategia_nome, explicacao_tec = MotorFractal.diagnosticar_tendencia(series_numerica)
                
                # Exibe o resultado do diagnóstico
                st.metric("Hurst (Volatilidade)", f"{hurst:.2f}")
                st.info(f"🎯 Modo Ativo: **{estrategia_nome}**")
                
            else:
                st.warning("Aguardando dados...")
                hurst = 0.5
                estrategia_nome = "Neutro"

            st.divider()
            
            # 2. Gestão de Orçamento
            orcamento = st.number_input("Budget (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
            
            if st.button("PROCESSAR ESTRATÉGIA", key=f"btn_{jogo}", disabled=not drive_ok):
                with st.spinner("Otimizando alocação..."):
                    # Cálculo Financeiro
                    res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                    
                    if "erro" not in res:
                        st.success("Alocação Otimizada!")
                        for item in res['carrinho']:
                            st.write(f"• **{item['qtd_volantes']}x** jogos de **{item['dezenas']}** dezenas.")
                        
                        # Análise da IA se disponível
                        if model and ai_ok:
                            try:
                                prompt = f"O backtest do FRACTALV para {jogo} indicou Hurst {hurst:.2f} ({estrategia_nome}). Com R$ {orcamento}, o sistema sugeriu {res['carrinho']}. Valide essa tática matematicamente em 2 frases."
                                response = model.generate_content(prompt)
                                st.markdown(f"**🤖 Análise:** {response.text}")
                            except:
                                st.caption("IA indisponível temporariamente.")
                    else:
                        st.error(res["erro"])
