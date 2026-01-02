import streamlit as st
import fractal_motor 
import meus_links 
import google.generativeai as genai

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="FractalV 3.0", page_icon="🧬", layout="wide")

# --- CSS PREMIUM (NEUMORPHIC) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
    .game-card {
        background-color: #ffffff; padding: 25px; border-radius: 16px;
        border-left: 6px solid #6c5ce7; border: 1px solid #f0f2f5;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.07); margin-bottom: 20px; transition: all 0.3s ease;
    }
    .game-card:hover { transform: translateY(-2px); box-shadow: 0 15px 30px -5px rgba(0,0,0,0.1); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #f7f7f7; padding-bottom: 10px; }
    .game-title { font-family: 'Helvetica', sans-serif; font-weight: 800; color: #2d3436; font-size: 15px; }
    .game-score { background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
    .ball-container { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; }
    .ball {
        width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-family: 'Roboto Mono', monospace; font-weight: 700; font-size: 18px; color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        box-shadow: inset 0px -3px 8px rgba(0,0,0,0.2), inset 0px 3px 8px rgba(255,255,255,0.2), 0px 8px 15px -4px rgba(0,0,0,0.15);
        border: 2px solid rgba(255,255,255,0.2); cursor: default; transition: all 0.2s;
    }
    .ball:hover { transform: translateY(-4px) scale(1.05); }
    .bg-roxo { background: linear-gradient(145deg, #8e44ad, #be93d6); }
    .bg-verde { background: linear-gradient(145deg, #27ae60, #58d68d); }
    .bg-azul { background: linear-gradient(145deg, #2980b9, #6dd5fa); }
    .bg-gold { background: linear-gradient(145deg, #f1c40f, #f9e79f); color: #333 !important; text-shadow: none; }
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #6c5ce7, #a29bfe); color: white; font-size: 18px; font-weight: 800; padding: 14px; border: none; border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([1, 5])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=85)
with c2: 
    st.title("FractalV 3.0")
    st.markdown("### Inteligência Determinística & Multi-Modelo")

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

# --- SIDEBAR (CONFIGURAÇÃO) ---
with st.sidebar:
    st.header("🧬 Parâmetros")
    
    # 1. API KEY
    if "GEMINI_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_KEY"]
        st.success("🔐 Chave Autenticada")
    else:
        gemini_key = st.text_input("API Key (Gemini):", type="password")
    
    # 2. SELETOR DE MODELOS (NOVIDADE!)
    modelo_selecionado = "gemini-pro" # Default
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            # Busca modelos que suportam geração de texto
            modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Filtra apenas os interessantes (ex: tira vision se quiser, ou deixa tudo)
            modelos_uteis = [m for m in modelos_disponiveis if 'gemini' in m]
            
            st.divider()
            st.markdown("🤖 **Cérebro da IA**")
            # Permite o usuário escolher
            modelo_selecionado = st.selectbox(
                "Escolha o Modelo Generativo:", 
                modelos_uteis, 
                index=0
            )
        except:
            st.warning("⚠️ Erro ao listar modelos (chave inválida?)")

    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("Capital (R$):", min_value=1.0, value=50.0, step=1.0)
    st.caption(f"Motor: {modelo_selecionado}")

# --- CORE ---
if st.button("ATIVAR NÚCLEO FRACTAL", type="primary"):
    with st.spinner("⚛️ Verificando estabilidade quântica e processando..."):
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
                
                # INFO DE ESTABILIDADE
                st.info(f"🔒 **Decisão Congelada:** Baseada no Concurso #{meta['ultimo_concurso']} (Se o concurso não mudou, os números mantêm-se por segurança matemática).")

                # DASHBOARD
                st.markdown("### 🧠 Plasticidade Neural")
                cols = st.columns(3)
                pesos = meta['pesos_atuais']
                cols[0].metric("Markov (Inércia)", f"{pesos['Markov']*100:.1f}%")
                cols[1].metric("Fractal (Caos)", f"{pesos['Fractal']*100:.1f}%")
                cols[2].metric("Gauss (Normal)", f"{pesos['Gauss']*100:.1f}%")
                st.progress(max(pesos.values()))
                
                if meta['aprendeu']:
                    st.success(f"✨ **Evolução!** A estratégia '{meta['vencedora']}' foi reforçada.")

                # ANÁLISE COM O MODELO ESCOLHIDO
                if gemini_key:
                    with st.chat_message("assistant", avatar="🧬"):
                        st.markdown(f"**Análise via {modelo_selecionado}:**")
                        analise = cerebro.analisar_com_gemini(
                            gemini_key, modelo_selecionado, loteria, fin, jogos[:3], meta
                        )
                        st.write(analise)

                st.divider()
                st.subheader(f"Sequências Otimizadas ({len(jogos)})")
                
                css_class = SHEETS[loteria].get("css", "bg-azul")
                for i, (jg, score) in enumerate(jogos):
                    bolas_html = ""
                    for num in jg:
                        bolas_html += f'<div class="ball {css_class}">{int(num):02d}</div>'
                    
                    st.markdown(f"""
                    <div class="game-card">
                        <div class="card-header">
                            <span class="game-title">SEQ #{i+1:02d}</span>
                            <span class="game-score">SCORE: {score:.2f}</span>
                        </div>
                        <div class="ball-container">{bolas_html}</div>
                    </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro: {e}")
