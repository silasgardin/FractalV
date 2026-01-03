import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import requests
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV

# --- 1. CONFIGURAÇÃO INICIAL (Sempre a primeira coisa) ---
st.set_page_config(page_title="FRACTALV", layout="wide", page_icon="🧩")

# --- 2. CSS PARA VISUAL TECH ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; font-size: 14px;}
    .success { background-color: #1f77b4; color: white; }
    .error { background-color: #d62728; color: white; }
    .card-title { color: #00FF99; font-size: 22px; font-weight: bold; border-bottom: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# --- 3. DEFINIÇÃO DE FUNÇÕES (O Python precisa ler isso antes de desenhar a tela) ---

def check_connection_drive():
    """Testa a conexão lendo a primeira linha real do arquivo de Valores"""
    url = LINKS_CSV.get("VALORES")
    if not url or "INSIRA_O_ID" in url:
        return False
    try:
        # Tenta ler apenas 1 linha para validar conexão
        pd.read_csv(url, nrows=1, decimal=",", thousands=".", on_bad_lines='skip')
        return True
    except:
        return False

def check_ai_connection():
    """Verifica se a chave API existe nos segredos do Streamlit"""
    # Verifica se o arquivo secrets foi carregado corretamente
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        return True
    return False

@st.cache_data(ttl=600)
def get_data(jogo_key):
    """Lê os dados do jogo específico"""
    link = LINKS_CSV.get(jogo_key)
    try:
        # Lê e limpa
        df = pd.read_csv(link, decimal=",", thousands=".", on_bad_lines='skip')
        # Pega colunas D1, D2... para cálculo
        cols = [c for c in df.columns if c.startswith('D') and '2º' not in c]
        if not cols: return None, None
        
        series = df.head(60)[cols].sum(axis=1).values # Soma das dezenas para Hurst
        last_draw = df.iloc[0]
        return last_draw, series
    except:
        return None, None

# --- 4. EXECUÇÃO DA INTERFACE (SIDEBAR) ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.caption("Monitoramento de Recursos")
    st.divider()

    # AGORA VAI FUNCIONAR: As funções já foram lidas nas linhas acima
    drive_ok = check_connection_drive()
    if drive_ok:
        st.success("Base de Dados (Drive): CONECTADO 🟢")
    else:
        st.error("Base de Dados (Drive): FALHA 🔴")
        st.caption("Verifique o arquivo links_planilhas.py")

    ai_ok = check_ai_connection()
    if ai_ok:
        st.success("Módulo Gemini AI: ATIVO 🟢")
        # Configura a IA
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-pro')
        except:
            st.warning("Erro ao iniciar Gemini")
            model = None
    else:
        st.warning("Módulo Gemini AI: DESCONECTADO 🟠")
        model = None
    
    st.divider()
    st.markdown("**Versão:** FractalV-1.3 (Stable)")

# --- 5. EXECUÇÃO DA INTERFACE (PRINCIPAL) ---
st.title("Painel de Controle Estratégico")

otimizador = OtimizadorFinanceiro(LINKS_CSV.get("VALORES"))

jogos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]
cols = st.columns(3)

for i, jogo in enumerate(jogos):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>{jogo.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            # Backtest Automático
            last_draw, series_numerica = get_data(jogo)
            
            if series_numerica is not None:
                st.caption(f"Último: {last_draw.get('Data', '---')} (Conc. {last_draw.get('Concurso', '---')})")
                
                hurst, estrategia_nome, explicacao_tec = MotorFractal.diagnosticar_tendencia(series_numerica)
                
                st.metric("Hurst (Volatilidade)", f"{hurst:.2f}")
                st.info(f"🎯 Modo: **{estrategia_nome}**")
            else:
                st.warning("Aguardando conexão...")
                hurst = 0.5
                estrategia_nome = "Neutro"

            st.divider()
            
            # Gestão de Orçamento
            orcamento = st.number_input("Budget (R$)", 5.0, 5000.0, 30.0, step=5.0, key=f"b_{jogo}")
            
            # Botão só ativa se tiver conexão com banco de dados
            if st.button("PROCESSAR ESTRATÉGIA", key=f"btn_{jogo}", disabled=not drive_ok):
                with st.spinner("Otimizando alocação..."):
                    res = otimizador.calcular_melhor_estrategia(jogo, orcamento)
                    
                    if "erro" not in res:
                        st.success("Alocação Otimizada!")
                        for item in res['carrinho']:
                            st.write(f"• **{item['qtd_volantes']}x** jogos de **{item.get('dezenas', item.get('qtd_dezenas'))}** dezenas.")
                        
                        st.caption(f"Custo Total: R$ {sum(i['custo_total'] for i in res['carrinho']):.2f}")

                        if model and ai_ok:
                            try:
                                prompt = f"Analise matematicamente para {jogo}: Hurst {hurst:.2f} ({estrategia_nome}). Orçamento R$ {orcamento} distribuído em {len(res['carrinho'])} tipos de apostas."
                                response = model.generate_content(prompt)
                                st.markdown(f"**🤖 Análise:** {response.text}")
                            except:
                                st.caption("IA indisponível.")
                    else:
                        st.error(res["erro"])
