import streamlit as st
import pandas as pd
import plotly.express as px
from fractal_engine import FractalVCerebro
from fractal_connector import FractalConnector

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Oráculo V - Painel", layout="wide")

# --- CSS CUSTOMIZADO PARA VISUAL PROFISSIONAL ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4B0082;
    }
    div[data-testid="stSidebarUserContent"] {
        background-color: #f8f9fa;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO SISTEMA ---
@st.cache_resource
def carregar_sistemas():
    # Inicia o cérebro matemático e o conector de dados/IA
    cerebro = FractalVCerebro()
    conector = FractalConnector() # Agora sem argumentos, ele se vira sozinho
    return cerebro, conector

try:
    cerebro, conector = carregar_sistemas()
except Exception as e:
    st.error(f"Erro crítico ao iniciar sistemas: {e}")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🔮 Oráculo V")
st.sidebar.caption("Sistema de Inteligência Fractal")

# Monitor de Memória Neural (Barra de Progresso)
if hasattr(cerebro, 'learner'):
    memoria_atual = cerebro.learner.memoria
    st.sidebar.markdown("### 🧠 Rede Neural Viva")
    
    col_mem1, col_mem2, col_mem3 = st.sidebar.columns(3)
    col_mem1.metric("Markov", f"{memoria_atual.get('Markov', 0)*100:.0f}%")
    col_mem2.metric("Fractal", f"{memoria_atual.get('Fractal', 0)*100:.0f}%")
    col_mem3.metric("IA", f"{memoria_atual.get('IA', 0)*100:.0f}%")
    
    st.sidebar.progress(memoria_atual.get('Markov', 0.4))
else:
    st.sidebar.warning("Módulo de aprendizado carregando...")

st.sidebar.markdown("---")

# Controles de Entrada
opcao_loteria = st.sidebar.selectbox(
    "Objeto de Estudo:",
    ["Lotofacil", "Mega_Sena", "Quina", "Dia_de_Sorte"]
)

# Pega o preço atualizado via Conector para sugerir orçamento
preco_ref = conector.get_preco(opcao_loteria)
orcamento = st.sidebar.number_input(
    f"Investimento (R$): (Preço un: R$ {preco_ref:.2f})", 
    min_value=float(preco_ref), 
    value=float(preco_ref)*10, 
    step=float(preco_ref)
)

st.sidebar.markdown("---")

# --- ÁREA PRINCIPAL ---
st.title(f"Análise Fractal: {opcao_loteria.replace('_', ' ')}")

if st.sidebar.button("🌀 EXECUTAR MODELO MATEMÁTICO", type="primary"):
    with st.spinner("Conectando ao fluxo de dados e processando fractais..."):
        try:
            # 1. Executa o Motor Matemático (Calcula os jogos)
            # O info_card agora retorna também o 'ultimo_concurso' graças à atualização anterior
            info = cerebro.info_card(opcao_loteria)
            resultado = cerebro.processar_jogos(opcao_loteria, orcamento)
            
            # 2. Consulta a IA Generativa (Gemini) para interpretar os números
            jogos_simples = [j[0] for j in resultado['jogos']]
            analise_ia = conector.consultar_oraculo(
                loteria=opcao_loteria,
                info_modelo=info,
                jogos_gerados=jogos_simples
            )
            
            # --- EXIBIÇÃO DOS RESULTADOS ---
            
            # Bloco de Métricas Principais
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Estratégia Ativa", info['modelo_ativo'], help=info['descricao'])
            col2.metric("Precisão (Backtest)", info['performance_recente'])
            col3.metric("Concurso Base", info.get('ultimo_concurso', 'N/A'))
            col4.metric("Jogos Gerados", len(resultado['jogos']))

            # Bloco da Voz do Oráculo (Gemini)
            with st.container():
                st.markdown("### 👁️ Visão do Oráculo")
                if "⚠️" in analise_ia:
                    st.warning(analise_ia)
                else:
                    st.info(f"**{analise_ia}**")

            # Tabela e Gráfico
            col_esq, col_dir = st.columns([1, 1])
            
            with col_esq:
                st.subheader("📋 Palpites Matemáticos")
                dados_tabela = []
                for i, (jogo, score) in enumerate(resultado['jogos']):
                    dados_tabela.append({
                        "Jogo": i+1,
                        "Dezenas": str(jogo).replace('[','').replace(']',''),
                        "Força": score
                    })
                df_jogos = pd.DataFrame(dados_tabela)
                st.dataframe(df_jogos, hide_index=True, use_container_width=True)
                st.caption(f"Troco estimado: R$ {resultado['troco']:.2f}")

            with col_dir:
                st.subheader("📊 Potência Estatística")
                if not df_jogos.empty:
                    fig = px.bar(
                        df_jogos, 
                        x='Jogo', 
                        y='Força', 
                        title="Score de Probabilidade por Jogo",
                        color='Força',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"grafico_{opcao_loteria}")

        except Exception as e:
            st.error(f"Erro durante o processamento: {str(e)}")
            st.code("Dica: Verifique se o arquivo 'meus_links.py' contém os links corretos.")

else:
    # Estado inicial (Tela de espera)
    st.info("👈 Ajuste o orçamento na barra lateral e clique em EXECUTAR para iniciar.")
    
    # Check de integridade
    if not conector.ai_ativo:
        st.warning("⚠️ Nota: A chave API do Gemini não foi detectada. O sistema funcionará apenas no modo Matemático (sem textos explicativos).")
    else:
        st.success("✅ Sistema Neural Conectado.")

# Rodapé
st.markdown("---")
st.markdown("<div style='text-align: center; color: grey;'>Oráculo V - Versão 5.1 (Data Fusion)</div>", unsafe_allow_html=True)
