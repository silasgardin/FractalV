import streamlit as st
import oraculo_motor
import meus_links  # Importa os links do arquivo externo

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Oráculo V37", page_icon="✨", layout="wide")

st.markdown("""
<style>
.big-font { font-size:18px !important; }
.metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #4285F4; }
.stButton>button { width: 100%; background-color: #4285F4; color: white; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("✨ Oráculo V37 - Auto-Discovery AI")
st.markdown("### Inteligência Híbrida: Matemática Fractal + Google Gemini")

# ==============================================================================
# 1. CARREGAMENTO DOS LINKS
# ==============================================================================
try:
    LINK_TABELA_PRECOS = meus_links.LINK_PRECOS
    SHEETS_URLS = meus_links.URLS
    SHEETS = {
        "Lotofácil":    {"url": SHEETS_URLS["Lotofácil"],    "desc": "Inércia"},
        "Mega Sena":    {"url": SHEETS_URLS["Mega Sena"],    "desc": "Entropia"},
        "Quina":        {"url": SHEETS_URLS["Quina"],        "desc": "Markov"},
        "Dia de Sorte": {"url": SHEETS_URLS["Dia de Sorte"], "desc": "Gauss"},
        "Timemania":    {"url": SHEETS_URLS["Timemania"],    "desc": "Colunas"},
        "Dupla Sena":   {"url": SHEETS_URLS["Dupla Sena"],   "desc": "Dupla"},
        "Lotomania":    {"url": SHEETS_URLS["Lotomania"],    "desc": "Espelho"},
        "Mega da Virada": {"url": SHEETS_URLS["Mega da Virada"], "desc": "Sazonal"}
    }
except:
    st.error("🚨 Erro no arquivo `meus_links.py`. Verifique os nomes.")
    st.stop()

# ==============================================================================
# 2. BARRA LATERAL (COM DIAGNÓSTICO)
# ==============================================================================
with st.sidebar:
    st.header("Configuração")
    
    gemini_key = None
    if "GEMINI_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_KEY"]
        st.success("🔐 Chave carregada (Secrets)")
    else:
        gemini_key = st.text_input("Google API Key:", type="password")

    # --- BOTÃO DE DIAGNÓSTICO ---
    if st.button("🛠️ Testar Conexão Gemini"):
        if not gemini_key:
            st.error("Insira uma chave primeiro!")
        else:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                # Tenta listar modelos
                mods = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                if mods:
                    st.success(f"✅ Conectado! Modelos disponíveis: {mods}")
                else:
                    st.warning("⚠️ Conectado, mas nenhum modelo encontrado (verifique permissões da chave).")
            except Exception as e:
                st.error(f"❌ Falha de conexão: {e}")
    # -----------------------------

    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("Orçamento (R$):", min_value=1.0, value=50.0, step=5.0)

# ==============================================================================
# 3. EXECUÇÃO
# ==============================================================================
if st.button("✨ Consultar Estratégia", type="primary"):
    with st.spinner("📡 A processar V37..."):
        try:
            cerebro = oraculo_motor.OraculoCerebro()
            chave_norm = loteria.replace("á","a").replace("ç","c").replace(" ","_")
            
            res = cerebro.gerar_palpite_cloud(
                SHEETS[loteria]['url'], LINK_TABELA_PRECOS, chave_norm, orcamento
            )
            
            if "erro" in res:
                st.error(res['erro'])
            else:
                fin = res['financeiro']
                jogos = res['jogos']
                
                st.markdown("### 📊 Relatório")
                c1, c2, c3 = st.columns(3)
                c1.metric("Jogos", fin['qtd'])
                c2.metric("Custo", f"R$ {(fin['qtd']*fin['preco_base']):.2f}")
                c3.metric("Troco", f"R$ {fin['troco']:.2f}")
                
                # CHAMA A IA
                if gemini_key:
                    with st.chat_message("assistant"):
                        st.write("🤖 A analisar...")
                        analise = cerebro.analisar_com_gemini(gemini_key, loteria, fin, jogos[:3])
                        st.write(analise)
                
                st.divider()
                st.subheader("🎲 Palpites")
                for i, (jg, sc) in enumerate(jogos):
                    st.text(f"Jogo {i+1:02d}: {jg}")
                    
        except Exception as e:
            st.error(f"Erro crítico: {e}")
