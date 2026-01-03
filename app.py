import streamlit as st
import pandas as pd
import plotly.express as px
import time
from fractal_engine import FractalVCerebro
from fractal_connector import FractalConnector

# --- CONFIGURAÇÃO DA PÁGINA (DESIGN WIDE) ---
st.set_page_config(
    page_title="Oráculo V - Interface Neural",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔮"
)

# --- ESTILIZAÇÃO CSS (VISUAL FUTURISTA) ---
st.markdown("""
<style>
    /* Fundo dos Metrics */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 8px;
        color: white;
    }
    /* Destaque para a Voz do Oráculo */
    .oraculo-box {
        background-color: #2b2d42;
        border-left: 5px solid #8d99ae;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-style: italic;
    }
    h1 { color: #edf2f4; }
    h3 { color: #8d99ae; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO (COM CACHE) ---
@st.cache_resource
def iniciar_sistema():
    # Carrega o Motor (Cérebro) e o Conector (Dados + Gemini)
    cerebro = FractalVCerebro()
    conector = FractalConnector()
    return cerebro, conector

# Inicializa
try:
    cerebro, conector = iniciar_sistema()
except Exception as e:
    st.error(f"❌ Falha crítica ao carregar módulos: {e}")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🔮 Oráculo V")
st.sidebar.caption("v6.0 - Neural Interface")

# STATUS DA IA (GEMINI)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Conexão Neural")
if conector.ai_ativo:
    st.sidebar.success("Gemini AI: ONLINE")
else:
    st.sidebar.error("Gemini AI: OFFLINE")
    st.sidebar.caption("Verifique 'GEMINI_API_KEY' nos Secrets.")

# VISUALIZADOR DA MEMÓRIA (O CÉREBRO APRENDENDO)
if hasattr(cerebro, 'learner'):
    memoria = cerebro.learner.get_pesos()
    st.sidebar.markdown("### 🧠 Pesos da Rede")
    c1, c2, c3 = st.sidebar.columns(3)
    c1.metric("Markov", f"{memoria.get('Markov',0):.2f}")
    c2.metric("Fractal", f"{memoria.get('Fractal',0):.2f}")
    c3.metric("IA", f"{memoria.get('IA',0):.2f}")
    
    # Barra de progresso visual para a tendência dominante
    dominante = max(memoria, key=memoria.get)
    st.sidebar.progress(memoria[dominante])
    st.sidebar.caption(f"Tendência Atual: {dominante}")

st.sidebar.markdown("---")

# CONTROLES
loteria = st.sidebar.selectbox("Objeto de Estudo:", ["Lotofacil", "Mega_Sena", "Quina", "Dia_de_Sorte"])

# Busca preço inteligente
try:
    preco_un = conector.get_preco(loteria)
except:
    preco_un = 3.00

orcamento = st.sidebar.number_input(
    "Investimento Disponível (R$):", 
    min_value=float(preco_un), 
    value=30.0, 
    step=float(preco_un),
    help=f"Preço por jogo: R$ {preco_un:.2f}"
)

btn_processar = st.sidebar.button("🌀 INVOCAR ORÁCULO", type="primary")

# --- ÁREA PRINCIPAL ---
st.title(f"Análise Fractal: {loteria.replace('_', ' ')}")

if btn_processar:
    with st.spinner("⏳ Sincronizando dados, calculando fractais e consultando o Gemini..."):
        try:
            # 1. PROCESSAMENTO MATEMÁTICO
            info = cerebro.info_card(loteria)
            resultado = cerebro.processar_jogos(loteria, orcamento)
            
            # Prepara dados para a IA
            jogos_para_analise = [j[0] for j in resultado['jogos']]
            
            # 2. CONSULTA AO GEMINI (IA) - AQUI ESTÁ A MÁGICA
            analise_oraculo = conector.consultar_oraculo(
                loteria=loteria,
                info=info,
                jogos=jogos_para_analise
            )
            
            # --- EXIBIÇÃO ---
            
            # BLOCO 1: A VOZ DA IA (Destaque Principal)
            st.markdown("### 👁️ Revelação do Oráculo")
            with st.container():
                # Ícone de Chat para simular conversa
                with st.chat_message("assistant", avatar="🔮"):
                    if "⚠️" in analise_oraculo:
                        st.warning(analise_oraculo)
                    else:
                        st.write(analise_oraculo)
            
            st.divider()

            # BLOCO 2: KPI's (Indicadores)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Estratégia Ativa", info['modelo_ativo'])
            k2.metric("Concurso Base", info['ultimo_concurso'])
            k3.metric("Jogos Gerados", len(resultado['jogos']))
            k4.metric("Custo Real", f"R$ {resultado['total_investido']:.2f}")

            # BLOCO 3: DADOS DETALHADOS (Abas)
            tab_jogos, tab_graficos = st.tabs(["📋 Lista de Palpites", "📊 Análise Gráfica"])
            
            # Monta DataFrame
            dados_display = []
            for i, item in enumerate(resultado['jogos']):
                numeros, forca = item
                dados_display.append({
                    "Jogo": i+1,
                    "Dezenas": str(numeros).replace('[','').replace(']',''),
                    "Força Fractal": f"{forca:.4f}"
                })
            df = pd.DataFrame(dados_display)

            with tab_jogos:
                st.dataframe(
                    df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Força Fractal": st.column_config.ProgressColumn(
                            "Potência",
                            format="%.4f",
                            min_value=0,
                            max_value=max([float(x['Força']) for x in resultado['jogos']]) * 1.2
                        )
                    }
                )
                st.caption(f"Troco Estimado: R$ {resultado['troco']:.2f}")

            with tab_graficos:
                if not df.empty:
                    df['Força Fractal'] = df['Força Fractal'].astype(float)
                    fig = px.bar(
                        df, 
                        x='Jogo', 
                        y='Força Fractal',
                        color='Força Fractal',
                        color_continuous_scale='Viridis',
                        title="Distribuição de Entropia dos Jogos"
                    )
                    st.plotly_chart(fig, use_container_width=True, key="grafico_principal")
                else:
                    st.warning("Nenhum jogo gerado para exibir gráficos.")

        except Exception as e:
            st.error("⚠️ Ocorreu um erro no processamento.")
            st.code(str(e))
            st.info("Dica: Verifique se 'fractal_connector.py' e 'fractal_engine.py' estão na mesma pasta.")

else:
    # TELA DE BOAS-VINDAS (ESTADO ZERO)
    st.info("👈 Configure o orçamento na barra lateral e clique em 'INVOCAR ORÁCULO'.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Status do Sistema:**
        - Motor Matemático: ✅ Pronto
        - Banco de Dados (Drive): ✅ Conectado
        """)
    with col_b:
        st.markdown(f"""
        **Status da IA:**
        - Gemini Generator: {'✅ Ativo' if conector.ai_ativo else '❌ Inativo (Verifique API Key)'}
        """)
