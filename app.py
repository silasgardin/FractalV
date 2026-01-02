import streamlit as st
import fractal_motor 
import meus_links 
import google.generativeai as genai

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="FractalV System", page_icon="🧬", layout="wide")

# --- CSS PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');

    .game-card {
        background-color: #ffffff; padding: 30px; border-radius: 20px;
        border-left: 8px solid #6c5ce7; border: 1px solid #f0f2f5;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08); margin-bottom: 25px; transition: transform 0.3s ease;
    }
    .game-card:hover { transform: translateY(-3px); }

    .card-header { 
        display: flex; justify-content: space-between; align-items: center; 
        margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #f5f5f5; 
    }
    .game-title { 
        font-family: 'Helvetica', sans-serif; font-weight: 900; color: #2d3436; 
        font-size: 18px; text-transform: uppercase; letter-spacing: 1px;
    }
    .game-score { 
        background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white; 
        padding: 8px 18px; border-radius: 30px; font-size: 14px; font-weight: 800; 
        box-shadow: 0 4px 10px rgba(108, 92, 231, 0.4);
    }

    .ball-container { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; padding: 10px; }

    .ball {
        width: 65px; height: 65px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center;
        font-family: 'Roboto Mono', monospace; font-weight: 700; font-size: 28px; 
        color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.25);
        box-shadow: inset 0px -5px 12px rgba(0,0,0,0.3), inset 0px 5px 12px rgba(255,255,255,0.25), 0px 10px 20px -5px rgba(0,0,0,0.2);
        border: 3px solid rgba(255,255,255,0.15); cursor: default; transition: all 0.2s;
    }
    .ball:hover { transform: scale(1.1); box-shadow: 0px 15px 30px -5px rgba(0,0,0,0.3); z-index: 10; }

    .bg-roxo { background: radial-gradient(circle at 30% 30%, #be93d6, #8e44ad); }
    .bg-verde { background: radial-gradient(circle at 30% 30%, #58d68d, #27ae60); }
    .bg-azul { background: radial-gradient(circle at 30% 30%, #6dd5fa, #2980b9); }
    .bg-gold { background: radial-gradient(circle at 30% 30%, #f9e79f, #f1c40f); color: #333 !important; text-shadow: none; }

    .stButton>button {
        width: 100%; height: 60px; background: linear-gradient(90deg, #6c5ce7, #a29bfe); 
        color: white; font-size: 20px; font-weight: 800; border: none; border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- CACHE ---
@st.cache_data(ttl=1800, show_spinner=False)
def calcular_fractal_estavel(loteria_nome, orcamento, link_precos, url_dados):
    cerebro = fractal_motor.FractalCerebro()
    chave_norm = loteria_nome.replace("á","a").replace("ç","c").replace(" ","_")
    
    resultado = cerebro.gerar_palpite_cloud(
        url_dados, link_precos, chave_norm, orcamento
    )
    return resultado, cerebro

# --- HEADER ---
c1, c2 = st.columns([1, 6])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
with c2: 
    st.title("FractalV System")
    st.markdown("### Inteligência Determinística & Gestão de Banca")

try:
    LINK_TABELA_PRECOS = meus_links.LINK_PRECOS
    SHEETS_URLS = meus_links.URLS
    SHEETS = {
        "Lotofácil": {"url": SHEETS_URLS["Lotofácil"], "css": "bg-roxo"}, "Mega Sena": {"url": SHEETS_URLS["Mega Sena"], "css": "bg-verde"},
        "Quina": {"url": SHEETS_URLS["Quina"], "css": "bg-azul"}, "Dia de Sorte": {"url": SHEETS_URLS["Dia de Sorte"], "css": "bg-gold"},
        "Timemania": {"url": SHEETS_URLS["Timemania"], "css": "bg-gold"}, "Dupla Sena": {"url": SHEETS_URLS["Dupla Sena"], "css": "bg-verde"},
        "Lotomania": {"url": SHEETS_URLS["Lotomania"], "css": "bg-roxo"}, "Mega da Virada": {"url": SHEETS_URLS["Mega da Virada"], "css": "bg-verde"}
    }
except: st.error("🚨 `meus_links.py` não encontrado."); st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧬 Parâmetros")
    
    if "GEMINI_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_KEY"]
        st.success("🔐 Chave Autenticada")
    else:
        gemini_key = st.text_input("API Key (Gemini):", type="password")
    
    modelo_selecionado = "gemini-pro"
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            raw_models = genai.list_models()
            modelos_uteis = [m.name for m in raw_models if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name]
            st.divider()
            st.markdown("🤖 **Cérebro IA**")
            modelo_selecionado = st.selectbox("Versão:", modelos_uteis, index=0)
        except: pass

    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("Capital (R$):", min_value=1.0, value=50.0, step=1.0)
    
    if st.button("🔄 Forçar Recálculo"):
        st.cache_data.clear()
        st.rerun()

# --- CORE ---
if st.button("ATIVAR NÚCLEO FRACTAL", type="primary"):
    with st.spinner("⚛️ Materializando dados quânticos..."):
        try:
            res, cerebro_ativo = calcular_fractal_estavel(
                loteria, orcamento, LINK_TABELA_PRECOS, SHEETS[loteria]['url']
            )
            
            if "erro" in res:
                st.error(res['erro'])
            else:
                fin = res['financeiro']
                jogos = res['jogos']
                meta = res['backtest']
                
                st.info(f"🔒 **Decisão Congelada:** Baseada no Concurso #{meta.get('ultimo_concurso', 'N/A')}.")

                # PAINEL FINANCEIRO
                st.markdown("### 📊 Gestão de Banca")
                col_fin1, col_fin2, col_fin3 = st.columns(3)
                col_fin1.metric("Jogos Calculados", f"{fin['qtd']} jogos")
                col_fin2.metric("Custo Total", f"R$ {fin['custo_total']:.2f}")
                col_fin3.metric("Seu Troco", f"R$ {fin['troco']:.2f}", delta="Saldo")
                
                st.divider()

                # INTELIGÊNCIA
                st.markdown("### 🧠 Plasticidade Neural & Entropia")
                cols = st.columns(3)
                pesos = meta['pesos_atuais']
                cols[0].metric("Markov (Inércia)", f"{pesos['Markov']*100:.0f}%")
                cols[1].metric("Fractal (Caos)", f"{pesos['Fractal']*100:.0f}%")
                cols[2].metric("Gauss (Normal)", f"{pesos['Gauss']*100:.0f}%")
                st.progress(max(pesos.values()))

                if gemini_key:
                    with st.chat_message("assistant", avatar="🧬"):
                        st.markdown(f"**Análise ({modelo_selecionado}):**")
                        analise = cerebro_ativo.analisar_com_gemini(
                            gemini_key, modelo_selecionado, loteria, fin, jogos[:3], meta
                        )
                        st.write(analise)

                st.divider()
                st.subheader(f"Sequências Otimizadas ({len(jogos)})")
                
                css_class = SHEETS[loteria].get("css", "bg-azul")
                for i, (jg, score, entropia) in enumerate(jogos):
                    bolas_html = ""
                    for num in jg:
                        bolas_html += f'<div class="ball {css_class}">{int(num):02d}</div>'
                    
                    cor_entr = "#e74c3c"
                    if 0.4 <= entropia <= 0.8: cor_entr = "#2ecc71"
                    elif entropia > 0.8: cor_entr = "#f1c40f"

                    st.markdown(f"""
                    <div class="game-card">
                        <div class="card-header">
                            <span class="game-title">JOGO #{i+1:02d}</span>
                            <div style="text-align: right;">
                                <span class="game-score">SCORE: {score:.2f}</span>
                                <br>
                                <small style="color: #666; font-size: 11px;">
                                    ENTROPIA: <b style="color:{cor_entr}">{entropia:.4f}</b>
                                </small>
                            </div>
                        </div>
                        <div class="ball-container">{bolas_html}</div>
                    </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro: {e}")
