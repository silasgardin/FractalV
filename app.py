# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from fractal_engine import FractalVCerebro

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Oráculo V - Painel", layout="wide")

# Inicializa o Cérebro (com cache)
@st.cache_resource
def get_cerebro():
    return FractalVCerebro()

cerebro = get_cerebro()

# --- SIDEBAR ---
st.sidebar.title("🔮 Oráculo V")

# Visualização da Memória Neural
memoria_atual = cerebro.learner.memoria
st.sidebar.markdown("### 🧠 Memória Neural")
st.sidebar.caption("Pesos aprendidos via Reinforcement Learning")

col_mem1, col_mem2, col_mem3 = st.sidebar.columns(3)
col_mem1.metric("Markov", f"{memoria_atual['Markov']*100:.0f}%")
col_mem2.metric("Fractal", f"{memoria_atual['Fractal']*100:.0f}%")
col_mem3.metric("IA", f"{memoria_atual['IA']*100:.0f}%")
st.sidebar.progress(memoria_atual['Markov']) 

st.sidebar.markdown("---")

opcao_loteria = st.sidebar.selectbox(
    "Escolha a Loteria:",
    ["Lotofacil", "Mega_Sena", "Quina", "Dia_de_Sorte"]
)

orcamento = st.sidebar.number_input("Orçamento (R$):", min_value=3.0, value=30.0, step=1.0)

if st.sidebar.button("CALIBRAR E GERAR JOGOS"):
    with st.spinner(f"Calibrando IA para {opcao_loteria} e consultando memória..."):
        # 1. Pega informações do modelo
        info = cerebro.info_card(opcao_loteria)
        
        # 2. Gera os jogos
        resultado = cerebro.processar_jogos(opcao_loteria, orcamento)
        
        # --- EXIBIÇÃO ---
        st.header(f"Análise: {opcao_loteria}")
        
        # Métricas no Topo
        col1, col2, col3 = st.columns(3)
        col1.metric("Modelo Vencedor", info['modelo_ativo'])
        col2.metric("Acurácia Recente", info['performance_recente'])
        col3.metric("Jogos Gerados", len(resultado['jogos']))
        
        st.info(f"Estratégia do Dia: {info['descricao']}")
        
        # Tabela de Jogos
        st.subheader("📋 Palpites Gerados")
        dados_jogos = []
        for i, (jogo, score) in enumerate(resultado['jogos']):
            dados_jogos.append({
                "Jogo": i+1,
                "Dezenas": str(jogo),
                "Força (Score)": f"{score:.2f}"
            })
        st.table(pd.DataFrame(dados_jogos))
        
        # Gráfico de Distribuição (CORRIGIDO)
        st.subheader("📊 Distribuição de Força dos Jogos")
        df_chart = pd.DataFrame(dados_jogos)
        df_chart['Força (Score)'] = df_chart['Força (Score)'].astype(float)
        
        fig = px.bar(df_chart, x='Jogo', y='Força (Score)', title="Qualidade dos Jogos Gerados")
        
        # ID Único para evitar erro
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{opcao_loteria}")

else:
    st.write("👈 Selecione a loteria e clique em Gerar Jogos para ativar o Oráculo.")
    
st.sidebar.markdown("---")
st.sidebar.text("Versão: Oráculo_V 5.0")
