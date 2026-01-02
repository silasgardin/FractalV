import streamlit as st
import fractal_motor  # IMPORTANTE: MUDAMOS O IMPORT AQUI
import meus_links 

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="FractalV System", page_icon="🧬", layout="wide")

# --- CSS FRACTAL V (DESIGN FUTURISTA) ---
st.markdown("""
<style>
    /* Estilo do Cartão Principal */
    .game-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #6c5ce7; /* Roxo Fractal */
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* Cabeçalho do Cartão */
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        border-bottom: 1px solid #f1f1f1;
        padding-bottom: 8px;
    }
    .game-title {
        font-weight: 700;
        color: #2d3436;
        font-size: 14px;
        letter-spacing: 1px;
    }
    .game-score {
        background-color: #a29bfe;
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }

    /* Bolas (Esferas Matemáticas) */
    .ball-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
    }
    .ball {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 16px;
        color: white;
        box-shadow: inset -2px -2px 5px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .ball:hover { transform: scale(1.1); }
    
    /* CORES FRACTAL */
    .bg-roxo { background: linear-gradient(135deg, #6c5ce7, #a29bfe); }
    .bg-verde { background: linear-gradient(135deg, #00b894, #55efc4); }
    .bg-azul { background: linear-gradient(135deg, #0984e3, #74b9ff); }
    .bg-laranja { background: linear-gradient(135deg, #e17055, #fab1a0); }
    .bg-gold { background: linear-gradient(135deg, #fdcb6e, #ffeaa7); color: #2d3436 !important; }

    /* Botão Principal */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px;
        border: none;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);
    }
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(108, 92, 231, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
c1, c2 = st.columns([1, 4])
with c1:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
with c2:
    st.title("FractalV System")
    st.caption("Inteligência Generativa & Matemática Pura")

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
        "Dupla Sena":   {"url": SHEETS_URLS["Dupla Sena"], "css": "bg-laranja"},
        "Lotomania":    {"url": SHEETS_URLS["Lotomania"], "css": "bg-laranja"},
        "Mega da Virada": {"url": SHEETS_URLS["Mega da Virada"], "css": "bg-verde"}
    }
except:
    st.error("🚨 Erro de Links.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧬 Parâmetros")
    gemini_key = st.secrets.get("GEMINI_KEY", None)
    if not gemini_key:
        gemini_key = st.text_input("API Key (Gemini):", type="password")
    
    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("Capital (R$):", min_value=1.0, value=50.0, step=1.0)
    st.info("FractalV v1.0 • Build 2026")

# --- CORE ---
if st.button("CALCULAR FRACTAL", type="primary"):
    with st.spinner("⚛️ Processando geometria dos dados..."):
        try:
            # Chama o novo motor Fractal
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
                
                # DASHBOARD
                st.markdown("### 📊 Análise de Viabilidade")
                c1, c2, c3 = st.columns(3)
                c1.metric("Padrão Identificado", res['backtest']['vencedora'])
                c2.metric("Jogos Otimizados", fin['qtd'])
                c3.metric("Custo Real", f"R$ {fin['custo_total']:.2f}")
                
                if gemini_key:
                    with st.chat_message("assistant", avatar="🧬"):
                        analise = cerebro.analisar_com_gemini(
                            gemini_key, loteria, fin, jogos[:3], res['backtest']
                        )
                        st.write(analise)

                st.divider()
                st.subheader(f"Sequências Geradas ({len(jogos)})")
                
                # RENDERIZAÇÃO
                css_class = SHEETS[loteria].get("css", "bg-azul")
                
                for i, (jg, score) in enumerate(jogos):
                    bolas_html = ""
                    for num in jg:
                        bolas_html += f'<div class="ball {css_class}">{int(num):02d}</div>'
                    
                    st.markdown(f"""
                    <div class="game-card">
                        <div class="card-header">
                            <span class="game-title">SEQ #{i+1:02d}</span>
                            <span class="game-score">FRACTAL SCORE: {score:.2f}</span>
                        </div>
                        <div class="ball-container">
                            {bolas_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro de processamento: {e}")
