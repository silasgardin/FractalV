# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from fractal_engine import FractalVCerebro
from fractal_connector import FractalConnector

st.set_page_config(page_title="Oráculo V - Reset", layout="wide")

@st.cache_resource
def load():
    return FractalVCerebro(), FractalConnector()

cerebro, conector = load()

st.sidebar.title("🔮 Oráculo V5.2")
loteria = st.sidebar.selectbox("Loteria", ["Lotofácil", "Mega Sena", "Quina", "Dia de Sorte"])
orcamento = st.sidebar.number_input("Orçamento", value=30.0, step=3.0)

if st.sidebar.button("GERAR"):
    info = cerebro.info_card(loteria)
    res = cerebro.processar_jogos(loteria, orcamento)
    
    st.title(f"Resultado: {loteria}")
    st.write(f"Concurso Base: {info['ultimo_concurso']}")
    
    # IA
    msg = conector.consultar_oraculo(loteria, info, [j[0] for j in res['jogos']])
    st.info(f"Oráculo: {msg}")
    
    # Tabela
    data = [{"Dezenas": str(j[0]), "Força": j[1]} for j in res['jogos']]
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Grafico
    if not df.empty:
        fig = px.bar(df, x=df.index, y="Força")
        st.plotly_chart(fig, key="grafico_unico")
