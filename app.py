import streamlit as st
import oraculo_motor
import meus_links  # Importa os links do arquivo externo

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="Oráculo V35 Gemini",
    page_icon="✨",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
.big-font { font-size:18px !important; }
.metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #4285F4; }
.stButton>button { width: 100%; background-color: #4285F4; color: white; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("✨ Oráculo V35 - Powered by Gemini")
st.markdown("### Inteligência Híbrida: Matemática Fractal + Google Gemini AI")

# ==============================================================================
# 1. CARREGAMENTO DOS LINKS (VIA MEUS_LINKS.PY)
# ==============================================================================
try:
    # Busca as variáveis dentro do arquivo meus_links.py
    LINK_TABELA_PRECOS = meus_links.LINK_PRECOS
    SHEETS_URLS = meus_links.URLS
    
    # Recria o dicionário completo com as descrições
    SHEETS = {
        "Lotofácil":    {"url": SHEETS_URLS["Lotofácil"],    "desc": "Inércia (Padrão de Repetição)"},
        "Mega Sena":    {"url": SHEETS_URLS["Mega Sena"],    "desc": "Entropia (Caos e Atrasos)"},
        "Quina":        {"url": SHEETS_URLS["Quina"],        "desc": "Equilíbrio Markoviano"},
        "Dia de Sorte": {"url": SHEETS_URLS["Dia de Sorte"], "desc": "Distribuição Normal (Gauss)"},
        "Timemania":    {"url": SHEETS_URLS["Timemania"],    "desc": "Foco em Colunas"},
        "Dupla Sena":   {"url": SHEETS_URLS["Dupla Sena"],   "desc": "Dupla Chance Fractal"},
        "Lotomania":    {"url": SHEETS_URLS["Lotomania"],    "desc": "Espelhamento de Quadrantes"},
        "Mega da Virada": {"url": SHEETS_URLS["Mega da Virada"], "desc": "Especial Sazonal"}
    }
except (AttributeError, KeyError) as e:
    st.error(f"🚨 Erro no arquivo `meus_links.py`: Variável ou chave não encontrada: {e}")
    st.info("Verifique se o arquivo `meus_links.py` contém 'LINK_PRECOS' e o dicionário 'URLS' com todos os nomes corretos.")
    st.stop()

# ==============================================================================
# 2. BARRA LATERAL (CONFIGURAÇÃO)
# ==============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg", width=150)
    st.header("Configuração")
    
    # --- GESTÃO DE CHAVE DE API (VIA STREAMLIT SECRETS) ---
    gemini_key = None
    
    # Tenta pegar a chave do cofre seguro (.streamlit/secrets.toml)
    # Se você configurou no Streamlit Cloud, ele vai pegar daqui automaticamente.
    if "GEMINI_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_KEY"]
        st.success("🔐 Chave Gemini autenticada via Secrets!")
    else:
        # Fallback apenas para não travar se você esquecer de configurar o segredo
        st.warning("⚠️ Chave não encontrada nos Secrets.")
        gemini_key = st.text_input("Cole sua chave AIza... manualmente:", type="password")

    st.divider()
    
    st.subheader("Parâmetros de Jogo")
    loteria = st.selectbox("Escolha a Modalidade:", list(SHEETS.keys()))
    
    st.info(f"ℹ️ **Lógica V35:** {SHEETS[loteria]['desc']}")
    
    orcamento = st.number_input(
        "💰 Seu Orçamento (R$):", 
        min_value=1.0, 
        value=50.0, 
        step=5.0,
        help="O Oráculo verifica o preço atualizado na planilha e calcula a melhor estratégia."
    )
    
    st.caption("v35.0 (Gemini Edition)")

# ==============================================================================
# 3. EXECUÇÃO DO ORÁCULO
# ==============================================================================
if st.button("✨ Consultar Estratégia & Gerar Jogos", type="primary"):
    
    # Validação de Links (Garante que você editou o meus_links.py)
    if "COLE_" in LINK_TABELA_PRECOS or "COLE_" in SHEETS[loteria]['url']:
        st.error("🚨 **ERRO DE CONFIGURAÇÃO:**")
        st.warning("Parece que o arquivo `meus_links.py` ainda tem os links de exemplo ('COLE_AQUI...'). Atualize com os links reais.")
        st.stop()

    with st.spinner(f"📡 A conectar ao Cérebro V35... Processando {loteria}..."):
        try:
            # Instancia o Cérebro
            cerebro = oraculo_motor.OraculoCerebro()
            
            # Normaliza chave
            chave_normalizada = loteria.replace("á","a").replace("ç","c").replace(" ","_")
            
            # 1. Executa Cálculos Matemáticos e Financeiros
            resultado = cerebro.gerar_palpite_cloud(
                url_dados=SHEETS[loteria]['url'],
                url_precos=LINK_TABELA_PRECOS,
                loteria_chave=chave_normalizada, 
                orcamento=orcamento
            )
            
            # Tratamento de Erros
            if "erro" in resultado:
                st.error(f"❌ Erro do Oráculo: {resultado['erro']}")
            
            else:
                fin = resultado['financeiro']
                jogos = resultado['jogos']
                
                # Feedback de Preço
                if fin.get('preco_base', 0) > 0:
                    st.toast(f"Preço Base Detectado: R$ {fin['preco_base']:.2f}", icon="💲")
                
                # --- BLOCO 1: CONSULTORIA MATEMÁTICA ---
                st.markdown("### 📊 Relatório Financeiro")
                colA, colB, colC = st.columns(3)
                colA.metric("Estratégia", fin['estrategia'])
                colB.metric("Qtd. Jogos", fin['qtd'])
                colC.metric("Troco", f"R$ {fin['troco']:.2f}")
                
                st.info(f"💡 **Math Insight:** {fin['conselho']}")
                
                # --- BLOCO 2: ANÁLISE DE I.A. GEMINI ---
                if gemini_key:
                    with st.spinner("✨ O Gemini está a analisar a qualidade dos jogos..."):
                        top3 = jogos[:3]
                        # Chama o método específico do V35 (Gemini)
                        analise_ia = cerebro.analisar_com_gemini(gemini_key, loteria, fin, top3)
                        
                        with st.chat_message("assistant", avatar="✨"):
                            st.markdown("### Análise do Gemini")
                            st.write(analise_ia)
                else:
                    st.warning("⚠️ A I.A. não foi ativada porque a chave não foi encontrada nos Secrets nem inserida manualmente.")

                # --- BLOCO 3: LISTA DE JOGOS ---
                st.divider()
                st.markdown(f"### 🎲 Palpites Finais ({len(jogos)} jogos)")
                
                for i, (jg, score) in enumerate(jogos):
                    numeros_fmt = "  -  ".join([f"**{n:02d}**" for n in jg])
                    
                    with st.expander(f"🎫 Jogo {i+1:02d} (Score Fractal: {score:.2f})", expanded=(i<3)):
                        st.markdown(f"## {numeros_fmt}")
                        if i == 0: st.caption("🏆 *Matematicamente o jogo mais equilibrado*")
                        if i < 3: st.write(f"Probabilidade estimada: {(score/10)*100:.1f}%")

        except Exception as e:
            st.error(f"Ocorreu um erro crítico na execução: {e}")
