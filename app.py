import streamlit as st
import oraculo_motor

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="Oráculo V35 Gemini",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
.big-font { font-size:18px !important; }
.stButton>button { width: 100%; background-color: #4285F4; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("✨ Oráculo V35 - Powered by Gemini")
st.markdown("### Fusão: Matemática Fractal + Google Gemini AI")

# ==============================================================================
# CONFIGURAÇÃO DOS LINKS (RECOLOQUE SEUS LINKS AQUI)
# ==============================================================================
LINK_TABELA_PRECOS = "COLE_AQUI_O_LINK_CSV_DA_ABA_VLR_JOGO"

SHEETS = {
    "Lotofácil":    {"url": "COLE_LINK_CSV_LOTOFACIL", "desc": "Inércia (Repetição)"},
    "Mega Sena":    {"url": "COLE_LINK_CSV_MEGA_SENA", "desc": "Entropia (Caos)"},
    "Quina":        {"url": "COLE_LINK_CSV_QUINA", "desc": "Equilíbrio Markov"},
    "Dia de Sorte": {"url": "COLE_LINK_CSV_DIA_DE_SORTE", "desc": "Gaussiana"},
    "Timemania":    {"url": "COLE_LINK_CSV_TIMEMANIA", "desc": "Colunas"},
    "Dupla Sena":   {"url": "COLE_LINK_CSV_DUPLA_SENA", "desc": "Dupla Chance"},
    "Lotomania":    {"url": "COLE_LINK_CSV_LOTOMANIA", "desc": "Espelhamento"},
    "Mega da Virada": {"url": "COLE_LINK_CSV_MEGA_VIRADA", "desc": "Sazonal"}
}

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg", width=150)
    st.header("Configuração")
    
    # Campo específico para Gemini
    gemini_key = st.text_input(
        "Google Gemini API Key:", 
        type="password", 
        help="Cole sua chave (AIza...) do Google AI Studio aqui."
    )
    
    st.divider()
    loteria = st.selectbox("Loteria:", list(SHEETS.keys()))
    orcamento = st.number_input("Orçamento (R$):", min_value=1.0, value=50.0, step=5.0)
    
# ==============================================================================
# EXECUÇÃO
# ==============================================================================
if st.button("✨ Consultar Oráculo & Gemini", type="primary"):
    
    if "COLE_" in LINK_TABELA_PRECOS:
        st.error("⚠️ Configure os links no app.py primeiro!")
        st.stop()

    with st.spinner(f"📡 Conectando... Processando V35 para {loteria}..."):
        cerebro = oraculo_motor.OraculoCerebro()
        chave_norm = loteria.replace("á","a").replace("ç","c").replace(" ","_")
        
        # 1. Cálculos Matemáticos
        resultado = cerebro.gerar_palpite_cloud(
            url_dados=SHEETS[loteria]['url'],
            url_precos=LINK_TABELA_PRECOS,
            loteria_chave=chave_norm, 
            orcamento=orcamento
        )
        
        if "erro" in resultado:
            st.error(resultado['erro'])
        else:
            fin = resultado['financeiro']
            jogos = resultado['jogos']
            
            # --- Bloco 1: Matemática ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Estratégia", fin['estrategia'])
            col2.metric("Jogos", fin['qtd'])
            col3.metric("Preço Base", f"R$ {fin.get('preco_base',0):.2f}")
            
            st.info(f"📊 {fin['conselho']}")
            
            # --- Bloco 2: Integração Gemini ---
            if gemini_key:
                with st.spinner("✨ O Gemini está analisando seus jogos..."):
                    top3 = jogos[:3]
                    # Chamada ao método do Gemini
                    analise = cerebro.analisar_com_gemini(gemini_key, loteria, fin, top3)
                    
                    with st.chat_message("assistant", avatar="✨"):
                        st.markdown("### Análise do Gemini")
                        st.write(analise)
            else:
                st.warning("⚠️ Insira a chave do Gemini na barra lateral para ver a análise de IA.")
                
            # --- Bloco 3: Jogos ---
            st.divider()
            st.subheader("🎲 Palpites Gerados")
            for i, (jg, score) in enumerate(jogos):
                with st.expander(f"Jogo {i+1:02d} (Score: {score:.2f})", expanded=(i<3)):
                    st.markdown(f"## {'  -  '.join([f'{n:02d}' for n in jg])}")
