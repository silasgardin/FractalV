import streamlit as st
import pandas as pd
import plotly.express as px
from fractalv_motor import FractalVCerebro # Importa a nova classe

# Configuração da Página
st.set_page_config(page_title="FractalV Dashboard", layout="wide", page_icon="🌀")

# CSS para customizar a identidade visual
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Inicializa o Motor FractalV
@st.cache_resource
def get_fractal():
    return FractalVCerebro()

fractal = get_fractal()

# --- HEADER ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("# 🌀")
with col_title:
    st.title("FractalV System")
    st.markdown("**Matemática Estatística Adaptativa & Backtest Contínuo**")

st.markdown("---")

# --- SIDEBAR: STATUS DO SISTEMA ---
st.sidebar.header("🖥️ Status do FractalV")
st.sidebar.success("Motor Matemático: Online")
st.sidebar.info(f"Versão Core: {fractal.versao}")
st.sidebar.markdown("---")
st.sidebar.write("O sistema recalibra os pesos estatísticos (Markov vs Fractal vs IA) a cada nova execução, verificando a eficiência nos últimos 10 concursos.")

# --- ÁREA DE CARTÕES (JOGOS) ---
st.subheader("📊 Painel de Controle de Apostas")
loterias = ["Lotofacil", "Mega_Sena", "Quina"]

cols = st.columns(len(loterias))

for idx, loteria in enumerate(loterias):
    with cols[idx]:
        with st.container(border=True):
            st.markdown(f"### 🎲 {loteria.replace('_', ' ')}")
            
            # Consulta ao Cérebro FractalV
            card_info = fractal.info_card(loteria)
            
            if card_info:
                # Exibição do Modelo Adaptativo Atual
                st.markdown(f"**Modelo Ativo:** `{card_info['modelo_ativo']}`")
                st.caption(f"Lógica: {card_info['descricao']}")
                
                # Métrica de Performance
                st.metric(label="Acertos Médios (Backtest)", value=card_info['performance_recente'])
                
                st.divider()
                
                # Input Financeiro
                val_aposta = card_info['preco_aposta']
                orcamento = st.number_input(f"Investimento (R$)", min_value=val_aposta, value=20.0, step=val_aposta, key=f"orc_{loteria}")
                
                jogos_calc = int(orcamento // val_aposta)
                st.caption(f"Gera aprox. {jogos_calc} jogos")
                
                # Botão de Execução
                if st.button(f"Calcular {loteria}", type="primary", key=f"btn_{loteria}"):
                    with st.spinner(f"FractalV analisando padrões de {loteria}..."):
                        resultado = fractal.processar_jogos(loteria, orcamento)
                        
                        st.success(f"Cálculo Finalizado! Modelo usado: {resultado['modelo_utilizado']}")
                        
                        # Tabela de Jogos
                        df_jogos = pd.DataFrame(
                            [{"Dezenas": str(j[0]), "Score Potência": f"{j[1]:.4f}"} for j in resultado['jogos']]
                        )
                        st.dataframe(df_jogos, hide_index=True)
                        st.info(f"Troco Estimado: R$ {resultado['troco']:.2f}")

                # Gráfico de Evolução (Placeholder para dados reais futuros)
                with st.expander("📈 Evolução da Assertividade"):
                    # Aqui ligaremos os dados reais do histórico de acertos
                    dados_demo = pd.DataFrame({
                        'Concurso': [1,2,3,4,5],
                        'Performance': [11, 12, 11, 14, 13] if loteria == "Lotofacil" else [3, 2, 4, 3, 4]
                    })
                    fig = px.area(dados_demo, x='Concurso', y='Performance', title="Tendência Recente")
                    fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Base de dados CSV não encontrada ou vazia.")

# --- RODAPÉ ---
st.markdown("---")
st.markdown(f"© 2026 **FractalV Systems** | Valinhos, SP | Versão {fractal.versao}")
