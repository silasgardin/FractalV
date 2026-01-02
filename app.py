import streamlit as st
import oraculo_motor
import meus_links 

st.set_page_config(page_title="Oráculo V40 Pro", page_icon="🔮", layout="wide")

st.markdown("""
<style>
    .game-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #4285F4;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .lottery-numbers {
        font-family: 'Courier New', monospace;
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        letter-spacing: 2px;
        text-align: center;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    .game-score {
        font-size: 14px;
        color: #27ae60;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .stButton>button {
        width: 100%;
        background-color: #4285F4;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔮 Oráculo V40 - Adaptive Backtest")

try:
    LINK_TABELA_PRECOS = meus_links.LINK_PRECOS
    SHEETS_URLS = meus_links.URLS
    SHEETS = {
        "Lotofácil": {"url": SHEETS_URLS["Lotofácil"], "desc": "Repetição 9/6"},
        "Mega Sena": {"url": SHEETS_URLS["Mega Sena"], "desc": "Equilíbrio Par/Ímpar"},
        "Quina": {"url": SHEETS_URLS["Quina"], "desc": "Cadeias de Markov"},
        "Dia de Sorte": {"url": SHEETS_URLS["Dia de Sorte"], "desc": "Soma Gaussiana"},
        "Timemania": {"url": SHEETS_URLS["Timemania"], "desc": "Colunas"},
        "Dupla Sena": {"url": SHEETS_URLS["Dupla Sena"], "desc": "Dupla Chance"},
        "Lotomania": {"url": SHEETS_URLS["Lotomania"], "desc": "Espelhamento"},
        "Mega da Virada": {"url": SHEETS_URLS["Mega da Virada"], "desc": "Sazonal"}
    }
except:
    st.error("🚨 Erro: Verifique `meus_links.py`.")
    st.stop()

with st.sidebar:
    st.header("⚙️ Configuração")
    
    gemini_key = None
    if "GEMINI_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_KEY"]
        st.success("🔐 Chave Autenticada")
    else:
        gemini_key = st.text_input("API Key:", type="password")

    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("💰 Orçamento (R$):", min_value=1.0, value=50.0, step=1.0)

if st.button("🔮 EXECUTAR BACKTEST E GERAR", type="primary"):
    with st.spinner("📡 A rodar Backtest..."):
        try:
            cerebro = oraculo_motor.OraculoCerebro()
            chave_norm = loteria.replace("á","a").replace("ç","c").replace(" ","_")
            
            res = cerebro.gerar_palpite_cloud(
                SHEETS[loteria]['url'], LINK_TABELA_PRECOS, chave_norm, orcamento
            )
            
            if "erro" in res:
                st.error(f"❌ {res['erro']}")
            else:
                fin = res['financeiro']
                jogos = res['jogos']
                
                st.markdown("### 📊 Resultado do Backtest")
                c1, c2, c3 = st.columns(3)
                c1.metric("Estratégia Vencedora", res['backtest']['vencedora'])
                c2.metric("Jogos", fin['qtd'])
                c3.metric("Troco", f"R$ {fin['troco']:.2f}")
                
                if gemini_key:
                    with st.chat_message("assistant", avatar="🤖"):
                        analise = cerebro.analisar_com_gemini(
                            gemini_key, loteria, fin, jogos[:3], res['backtest']
                        )
                        st.write(analise)

                st.divider()
                for i, (jg, score) in enumerate(jogos):
                    nums_fmt = " - ".join([f"{n:02d}" for n in jg])
                    st.markdown(f"""
                    <div class="game-card">
                        <div class="game-score">JOGO {i+1:02d} (Score: {score:.2f})</div>
                        <div class="lottery-numbers">{nums_fmt}</div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro crítico: {e}")
