import streamlit as st
import fractal_motor 
import meus_links 

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="FractalV Premium", page_icon="🧬", layout="wide")

# --- CSS PREMIUM (DESIGN "NEUMORPHIC" MODERNO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');

    /* Estilo do Cartão Principal */
    .game-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 16px;
        border-left: 6px solid #6c5ce7;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.07), 0 5px 10px -5px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        transition: all 0.3s ease;
        border: 1px solid #f0f2f5;
    }
    .game-card:hover {
        box-shadow: 0 15px 30px -5px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #f7f7f7;
    }
    .game-title {
        font-family: 'Helvetica', sans-serif; font-weight: 800; color: #2d3436;
        font-size: 15px; letter-spacing: 0.5px; text-transform: uppercase;
    }
    .game-score {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white;
        padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;
        box-shadow: 0 2px 5px rgba(108, 92, 231, 0.3);
    }

    .ball-container {
        display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; padding: 5px;
    }

    /* ESTILO VISUAL DAS BOLAS (NEUMORPHIC) */
    .ball {
        width: 48px; height: 48px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Roboto Mono', monospace; font-weight: 700; font-size: 18px; color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        box-shadow: 
            inset 0px -3px 8px rgba(0, 0, 0, 0.2), 
            inset 0px 3px 8px rgba(255, 255, 255, 0.2), 
            0px 8px 15px -4px rgba(0,0,0,0.15);
        border: 2px solid rgba(255,255,255,0.2);
        transition: all 0.2s ease-in-out; cursor: default;
    }
    .ball:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: inset 0px -3px 8px rgba(0, 0, 0, 0.2), inset 0px 3px 8px rgba(255, 255, 255, 0.3), 0px 12px 20px -4px rgba(0,0,0,0.25);
    }
    
    /* CORES */
    .bg-roxo { background: linear-gradient(145deg, #8e44ad, #be93d6); }
    .bg-verde { background: linear-gradient(145deg, #27ae60, #58d68d); }
    .bg-azul { background: linear-gradient(145deg, #2980b9, #6dd5fa); }
    .bg-gold { background: linear-gradient(145deg, #f1c40f, #f9e79f); color: #333 !important; text-shadow: none; }

    /* Botão Principal */
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        color: white; font-size: 18px; font-weight: 800; padding: 14px;
        border: none; border-radius: 12px; box-shadow: 0 6px 15px rgba(108, 92, 231, 0.3);
        text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.5); transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([1, 5])
with c1:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=85)
with c2:
    st.title("FractalV System")
    st.markdown("### Inteligência Generativa & Matemática Pura")

# --- CARREGAMENTO SEGURO ---
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
    st.error("🚨 Erro crítico: Arquivo `meus_links.py` não encontrado.")
    st.stop()

# --- SIDEBAR (CORRIGIDA) ---
with st.sidebar:
    st.header("🧬 Parâmetros")
    
    # --- CORREÇÃO DA API KEY ---
    # Verifica se a chave existe nos secrets (oculta) ANTES de pedir input
    if "GEMINI_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_KEY"]
        st.success("🔐 Chave Autenticada (Secrets)")
    else:
        # Se não tiver no secrets, mostra o campo
        gemini_key = st.text_input("API Key (Gemini):", type="password")
    # ---------------------------
    
    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("Capital Disponível (R$):", min_value=1.0, value=50.0, step=1.0)
    
    st.markdown("---")
    st.caption("FractalV Premium v2.2 • Configuração Segura")

# --- CORE ---
if st.button("ATIVAR NÚCLEO FRACTAL", type="primary"):
    with st.spinner("⚛️ Processando geometria dos dados e regenerando pesos..."):
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
                
                # DASHBOARD
                st.markdown("### 🧠 Plasticidade Neural (Status Atual)")
                cols = st.columns(3)
                pesos = meta['pesos_atuais']
                
                cols[0].metric("Markov (Inércia)", f"{pesos['Markov']*100:.1f}%")
                cols[1].metric("Fractal (Caos)", f"{pesos['Fractal']*100:.1f}%")
                cols[2].metric("Gauss (Normal)", f"{pesos['Gauss']*100:.1f}%")
                
                st.progress(max(pesos.values()))
                
                if meta['aprendeu']:
                    st.success(f"✨ **Evolução Confirmada!** A IA aprendeu com o Backtest e reforçou a estratégia '{meta['vencedora']}'.")

                # ANÁLISE GEMINI
                if gemini_key:
                    with st.chat_message("assistant", avatar="🧬"):
                        st.markdown("**Análise do Núcleo Generativo:**")
                        analise = cerebro.analisar_com_gemini(
                            gemini_key, loteria, fin, jogos[:3], meta
                        )
                        st.write(analise)

                st.divider()
                st.subheader(f"Sequências Otimizadas ({len(jogos)})")
                
                # RENDERIZAÇÃO VISUAL PREMIUM
                css_class = SHEETS[loteria].get("css", "bg-azul")
                
                for i, (jg, score) in enumerate(jogos):
                    bolas_html = ""
                    for num in jg:
                        num_fmt = f"{int(num):02d}"
                        bolas_html += f'<div class="ball {css_class}">{num_fmt}</div>'
                    
                    st.markdown(f"""
                    <div class="game-card">
                        <div class="card-header">
                            <span class="game-title">SEQUÊNCIA #{i+1:02d}</span>
                            <span class="game-score">FRACTAL SCORE: {score:.2f}</span>
                        </div>
                        <div class="ball-container">
                            {bolas_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro de processamento visual: {e}")
