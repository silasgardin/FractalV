import streamlit as st
import fractal_motor 
import meus_links 

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="FractalV Regenerative", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    .game-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #6c5ce7;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .card-header {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
    }
    .ball-container { display: flex; gap: 5px; flex-wrap: wrap; justify-content: center; }
    .ball {
        width: 35px; height: 35px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: bold; font-size: 14px;
        box-shadow: inset -2px -2px 5px rgba(0,0,0,0.2);
    }
    .bg-roxo { background: linear-gradient(135deg, #6c5ce7, #a29bfe); }
    .bg-verde { background: linear-gradient(135deg, #00b894, #55efc4); }
    .bg-azul { background: linear-gradient(135deg, #0984e3, #74b9ff); }
    .bg-gold { background: linear-gradient(135deg, #fdcb6e, #ffeaa7); color: #333 !important; }
    
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        color: white; font-weight: bold; padding: 12px; border: none; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🧬 FractalV - IA Regenerativa")
st.caption("Sistema Adaptativo de Aprendizado Contínuo")

# --- CARREGAMENTO ---
try:
    LINK_TABELA_PRECOS = meus_links.LINK_PRECOS
    SHEETS_URLS = meus_links.URLS
    SHEETS = {
        "Lotofácil":    {"url": SHEETS_URLS["Lotofácil"], "css": "bg-roxo"},
        "Mega Sena":    {"url": SHEETS_URLS["Mega Sena"], "css": "bg-verde"},
        "Quina":        {"url": SHEETS_URLS["Quina"], "css": "bg-azul"},
        "Dia de Sorte": {"url": SHEETS_URLS["Dia de Sorte"], "css": "bg-gold"},
        "Timemania":    {"url": SHEETS_URLS["Timemania"], "css": "bg-gold"},
        "Dupla Sena":   {"url": SHEETS_URLS["Dupla Sena"], "css": "bg-verde"},
        "Lotomania":    {"url": SHEETS_URLS["Lotomania"], "css": "bg-roxo"},
        "Mega da Virada": {"url": SHEETS_URLS["Mega da Virada"], "css": "bg-verde"}
    }
except:
    st.error("🚨 Erro de Links.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Parâmetros")
    gemini_key = st.secrets.get("GEMINI_KEY", st.text_input("API Key (Gemini):", type="password"))
    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("Capital (R$):", min_value=1.0, value=50.0, step=1.0)

# --- CORE ---
if st.button("ATIVAR NÚCLEO FRACTAL", type="primary"):
    with st.spinner("⚛️ Regenerando pesos neurais e calculando..."):
        try:
            cerebro = fractal_motor.FractalCerebro()
            chave_norm = loteria.replace("á","a").replace("ç","c").replace(" ","_")
            
            res = cerebro.gerar_palpite_cloud(
                SHEETS[loteria]['url'], LINK_TABELA_PRECOS, chave_norm, orcamento
            )
            
            if "erro" in res:
                st.error(res['erro'])
            else:
                fin = res['financeiro']
                jogos = res['jogos']
                meta = res['backtest']
                
                # --- VISUALIZAÇÃO DA MENTE DA IA ---
                st.markdown("### 🧠 Plasticidade Neural (Pesos Atuais)")
                cols = st.columns(3)
                pesos = meta['pesos_atuais']
                
                cols[0].metric("Markov (Inércia)", f"{pesos['Markov']*100:.1f}%", 
                               delta="Evoluindo" if meta['aprendeu'] and "Markov" in meta['vencedora'] else None)
                cols[1].metric("Fractal (Caos)", f"{pesos['Fractal']*100:.1f}%")
                cols[2].metric("Gauss (Normal)", f"{pesos['Gauss']*100:.1f}%")
                
                st.progress(pesos['Markov']) # Barra visual do peso principal
                
                if meta['aprendeu']:
                    st.success(f"✨ A IA aprendeu com o Backtest! A estratégia '{meta['vencedora']}' recebeu reforço positivo.")

                # ANÁLISE GEMINI
                if gemini_key:
                    with st.chat_message("assistant", avatar="🧬"):
                        analise = cerebro.analisar_com_gemini(
                            gemini_key, loteria, fin, jogos[:3], meta
                        )
                        st.write(analise)

                st.divider()
                # RENDERIZAÇÃO
                css_class = SHEETS[loteria].get("css", "bg-azul")
                for i, (jg, score) in enumerate(jogos):
                    bolas = "".join([f'<div class="ball {css_class}">{int(n):02d}</div>' for n in jg])
                    st.markdown(f"""
                    <div class="game-card">
                        <div class="card-header">
                            <b>SEQ #{i+1:02d}</b> <small>SCORE: {score:.2f}</small>
                        </div>
                        <div class="ball-container">{bolas}</div>
                    </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro: {e}")
