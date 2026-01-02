import streamlit as st
import oraculo_motor
import meus_links 

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Oráculo V43 - Studio", page_icon="🔮", layout="wide")

# --- CSS AVANÇADO (BOLAS DE LOTERIA) ---
st.markdown("""
<style>
    /* Estilo do Cartão Principal */
    .game-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    
    /* Cabeçalho do Cartão (Score) */
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 10px;
    }
    .game-title {
        font-weight: bold;
        font-size: 16px;
        color: #555;
    }
    .game-score {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }

    /* Container das Bolas */
    .ball-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
    }

    /* Estilo da Bola (Círculo) */
    .ball {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Helvetica', sans-serif;
        font-weight: bold;
        font-size: 18px;
        color: white;
        box-shadow: inset -3px -3px 5px rgba(0,0,0,0.2);
    }
    
    /* CORES OFICIAIS DAS LOTERIAS */
    .color-lotofacil { background-color: #930089; } /* Roxo */
    .color-mega { background-color: #209869; }     /* Verde */
    .color-quina { background-color: #260085; }    /* Azul Escuro */
    .color-mania { background-color: #f78100; }    /* Laranja */
    .color-timemania { background-color: #fff600; color: #333 !important; } /* Amarelo */
    .color-dupla { background-color: #be003c; }    /* Vinho */
    .color-dia { background-color: #cb852b; }      /* Ouro */
    .color-default { background-color: #4285F4; }  /* Azul Padrão */

    /* Botão Principal */
    .stButton>button {
        width: 100%;
        background-color: #4285F4;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 12px;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 6px rgba(66, 133, 244, 0.3);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #3367d6;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔮 Oráculo V43 - Studio Edition")
st.markdown("### Visualização Profissional com Backtest Matemático")

# --- CARREGAMENTO DE DADOS ---
try:
    LINK_TABELA_PRECOS = meus_links.LINK_PRECOS
    SHEETS_URLS = meus_links.URLS
    SHEETS = {
        "Lotofácil":    {"url": SHEETS_URLS["Lotofácil"], "css": "color-lotofacil"},
        "Mega Sena":    {"url": SHEETS_URLS["Mega Sena"], "css": "color-mega"},
        "Quina":        {"url": SHEETS_URLS["Quina"], "css": "color-quina"},
        "Dia de Sorte": {"url": SHEETS_URLS["Dia de Sorte"], "css": "color-dia"},
        "Timemania":    {"url": SHEETS_URLS["Timemania"], "css": "color-timemania"},
        "Dupla Sena":   {"url": SHEETS_URLS["Dupla Sena"], "css": "color-dupla"},
        "Lotomania":    {"url": SHEETS_URLS["Lotomania"], "css": "color-mania"},
        "Mega da Virada": {"url": SHEETS_URLS["Mega da Virada"], "css": "color-mega"}
    }
except:
    st.error("🚨 Erro: `meus_links.py` não encontrado.")
    st.stop()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuração")
    
    gemini_key = st.secrets.get("GEMINI_KEY", None)
    if not gemini_key:
        gemini_key = st.text_input("API Key:", type="password")
    else:
        st.success("🔐 Chave Autenticada")

    st.divider()
    loteria = st.selectbox("Modalidade:", list(SHEETS.keys()))
    orcamento = st.number_input("💰 Orçamento (R$):", min_value=1.0, value=50.0, step=1.0)

# --- EXECUÇÃO ---
if st.button("🔮 GERAR PALPITES V43", type="primary"):
    with st.spinner("📡 A calibrar esferas e rodar Backtest..."):
        try:
            cerebro = oraculo_motor.OraculoCerebro()
            chave_norm = loteria.replace("á","a").replace("ç","c").replace(" ","_")
            
            # Gera dados
            res = cerebro.gerar_palpite_cloud(
                SHEETS[loteria]['url'], LINK_TABELA_PRECOS, chave_norm, orcamento
            )
            
            if "erro" in res:
                st.error(f"❌ {res['erro']}")
            else:
                fin = res['financeiro']
                jogos = res['jogos']
                
                # --- PAINEL DE KPI ---
                st.markdown("### 📊 Resultado da Análise")
                c1, c2, c3 = st.columns(3)
                c1.metric("Estratégia Vencedora", res['backtest']['vencedora'])
                c2.metric("Jogos Gerados", fin['qtd'])
                c3.metric("Custo Total", f"R$ {fin['custo_total']:.2f}")
                
                if gemini_key:
                    with st.chat_message("assistant", avatar="🤖"):
                        analise = cerebro.analisar_com_gemini(
                            gemini_key, loteria, fin, jogos[:3], res['backtest']
                        )
                        st.write(analise)

                st.divider()
                st.subheader(f"🎲 Seus Jogos ({len(jogos)})")
                
                # --- RENDERIZAÇÃO DAS BOLAS ---
                css_class = SHEETS[loteria].get("css", "color-default")
                
                for i, (jg, score) in enumerate(jogos):
                    # Cria o HTML das bolas
                    bolas_html = ""
                    for num in jg:
                        bolas_html += f'<div class="ball {css_class}">{int(num):02d}</div>'
                    
                    # Renderiza o cartão completo
                    st.markdown(f"""
                    <div class="game-card">
                        <div class="card-header">
                            <span class="game-title">JOGO {i+1:02d}</span>
                            <span class="game-score">SCORE: {score:.2f}</span>
                        </div>
                        <div class="ball-container">
                            {bolas_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro inesperado: {e}")
