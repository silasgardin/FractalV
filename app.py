import streamlit as st
import pandas as pd
import time
from motor_matematico import OtimizadorFinanceiro, MotorFractal
from links_planilhas import LINKS_CSV

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="FRACTALV | Gestão Estratégica",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (Visual Dark/Tech) ---
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
    }
    .card-header {
        font-size: 18px;
        font-weight: bold;
        color: #00FF99;
        margin-bottom: 10px;
        border-bottom: 1px solid #444;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
@st.cache_data(ttl=3600) # Cache de 1 hora para não ficar recarregando CSV toda hora
def carregar_dados_jogo(nome_jogo, link_csv):
    """Lê o CSV do jogo e retorna o último resultado e estatísticas básicas"""
    try:
        # Se for usar links WEB, use pd.read_csv(link_csv)
        # Aqui, como exemplo, vamos assumir que o pandas consegue ler o link direto
        df = pd.read_csv(link_csv, decimal=",", thousands=".")
        
        # Pega o último concurso válido
        ultimo_resultado = df.iloc[0] # Assumindo que a linha 0 é a mais recente conforme seus CSVs
        
        # Tratamento para pegar as dezenas (D1, D2...)
        colunas_dezenas = [c for c in df.columns if c.startswith('D') and '2º' not in c] # Filtra D1, D2...
        dezenas = ultimo_resultado[colunas_dezenas].values
        
        return {
            "concurso": ultimo_resultado['Concurso'],
            "data": ultimo_resultado['Data'],
            "dezenas": dezenas,
            "historico_completo": df
        }
    except Exception as e:
        return None

# --- BARRA LATERAL (CONFIGURAÇÕES GERAIS) ---
with st.sidebar:
    st.title("🧩 FRACTALV")
    st.markdown("v1.0 - *Chaos Math Engine*")
    st.divider()
    
    st.subheader("⚙️ Parâmetros Globais")
    modo_analise = st.selectbox("Modo de Análise", ["Padrão (Hurst + Markov)", "Experimental (Redes Neurais)", "Conservador (Médias)"])
    
    st.info("Status do Sistema: ONLINE 🟢\n\nBase de Dados: Conectada\nAPI LLM: Aguardando")

# --- ÁREA PRINCIPAL ---
st.title("Painel de Controle de Apostas")
st.markdown("Analise a tendência fractal e distribua seu orçamento com precisão matemática.")

# Inicializa o Motor Financeiro
# (Nota: Em produção, verifique se o caminho do CSV de valores está correto)
otimizador = OtimizadorFinanceiro("src/Oraculo_DB_Master - Vlr_jogo.csv") # Ou use o link web

# Lista de Jogos para Gerar os CARDS
jogos_ativos = ["MEGA_SENA", "LOTOFACIL", "QUINA", "LOTOMANIA", "TIMEMANIA", "DIA_DE_SORTE", "DUPLA_SENA"]

# Cria o Grid de Cards (3 colunas)
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for i, jogo_key in enumerate(jogos_ativos):
    # Distribui os jogos nas colunas ciclicamente
    col_atual = cols[i % 3]
    
    with col_atual:
        # --- O CARD DO JOGO ---
        with st.container(border=True):
            # 1. Cabeçalho e Último Resultado
            st.markdown(f"<div class='card-header'>{jogo_key.replace('_', ' ')}</div>", unsafe_allow_html=True)
            
            # Carrega dados reais
            dados = carregar_dados_jogo(jogo_key, LINKS_CSV.get(jogo_key, ""))
            
            if dados:
                dezenas_formatadas = " - ".join([str(int(d)) for d in dados['dezenas'] if pd.notna(d)])
                st.caption(f"Último: Conc {dados['concurso']} ({dados['data']})")
                st.code(dezenas_formatadas, language="text")
                
                # 2. Análise Rápida de Hurst (Simulada aqui, mas usando o motor real)
                # Pega a soma das dezenas dos últimos 50 jogos para calcular Hurst
                try:
                    # Pequena adaptação para pegar colunas de dezenas e somar
                    hist = dados['historico_completo'].head(50).copy()
                    cols_d = [c for c in hist.columns if c.startswith('D') and '2º' not in c]
                    serie_somas = hist[cols_d].sum(axis=1).values
                    
                    hurst_val = MotorFractal.calcular_hurst(serie_somas)
                    
                    # Exibe o "Velocímetro" do Hurst
                    if hurst_val > 0.6:
                        status_hurst = "TENDÊNCIA 📈"
                        cor_delta = "normal" # Verde
                    elif hurst_val < 0.4:
                        status_hurst = "REVERSÃO 📉"
                        cor_delta = "inverse" # Vermelho
                    else:
                        status_hurst = "ALEATÓRIO 🎲"
                        cor_delta = "off" # Cinza

                    st.metric("Índice Hurst (Memória)", f"{hurst_val:.2f}", status_hurst, delta_color=cor_delta)
                except:
                    st.warning("Dados insuficientes para Hurst")

            else:
                st.error("Erro ao carregar dados.")

            st.divider()

            # 3. Área de Orçamento e Ação
            orcamento = st.number_input(f"Orçamento (R$)", min_value=0.0, value=30.00, step=5.00, key=f"orc_{jogo_key}")
            
            if st.button(f"⚡ GERAR ESTRATÉGIA", key=f"btn_{jogo_key}"):
                with st.spinner("Otimizando recursos..."):
                    time.sleep(0.5) # Efeito visual
                    
                    # Chama o Motor Matemático
                    estrategia = otimizador.calcular_melhor_estrategia(jogo_key, orcamento)
                    
                    if "erro" not in estrategia:
                        st.success(f"Estratégia Definida!")
                        
                        # Mostra o carrinho de compras inteligente
                        for item in estrategia['carrinho']:
                            st.markdown(f"""
                            **{item['quantidade_volantes']}x** Jogos de **{item['qtd_dezenas']} Dezenas**
                            <br><small>Custo: R$ {item['custo_total']:.2f} | Prob: 1/{item['probabilidade_teorica']}</small>
                            """, unsafe_allow_html=True)
                            
                        st.caption(f"Troco Estimado: R$ {estrategia['sobra']:.2f}")
                        
                        # Aqui viria a chamada para o AI Analyst explicar o porquê
                        with st.expander("🤖 Análise do FRACTALV"):
                            st.write(f"Com base no Hurst de {hurst_val:.2f}, o sistema recomenda esta distribuição para maximizar a cobertura em um cenário de {status_hurst}.")
                    else:
                        st.error(estrategia['erro'])
