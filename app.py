import streamlit as st
import oraculo_motor

st.set_page_config(page_title="Oráculo V34 AI", page_icon="🤖", layout="wide")

st.title("🤖 Oráculo V34 - I.A. Generativa Integrada")
st.markdown("### Matemática Fractal + Análise de GPT")

# --- 1. CONFIGURAÇÃO DOS LINKS (Mantenha os seus links aqui) ---
LINK_TABELA_PRECOS = "COLE_AQUI_O_LINK_CSV_DA_ABA_VLR_JOGO"
SHEETS = {
    "Lotofácil":    {"url": "COLE_LINK_CSV", "desc": "Inércia"},
    "Mega Sena":    {"url": "COLE_LINK_CSV", "desc": "Entropia"},
    # ... (seus outros links) ...
}

# --- 2. SIDEBAR COM CHAVE DE API ---
with st.sidebar:
    st.header("Configuração")
    
    # Campo para senha da OpenAI
    openai_key = st.text_input("OpenAI API Key (Opcional):", type="password", help="Cole sua chave sk-... aqui para ativar a análise de texto inteligente.")
    
    st.divider()
    loteria = st.selectbox("Loteria:", list(SHEETS.keys()))
    orcamento = st.number_input("Orçamento (R$):", min_value=1.0, value=50.0, step=10.0)

# --- 3. EXECUÇÃO ---
if st.button("🔮 Gerar Estratégia", type="primary"):
    # (Validação de links omitida para brevidade, mas mantenha a sua)
    
    with st.spinner("Processando Matemática V33..."):
        cerebro = oraculo_motor.OraculoCerebro()
        
        # 1. Gera a Matemática (V33)
        resultado = cerebro.gerar_palpite_cloud(
            url_dados=SHEETS[loteria]['url'],
            url_precos=LINK_TABELA_PRECOS,
            loteria_chave=loteria.replace("á","a").replace(" ","_"),
            orcamento=orcamento
        )
        
        if "erro" in resultado:
            st.error(resultado['erro'])
        else:
            fin = resultado['financeiro']
            jogos = resultado['jogos']
            
            # --- MOSTRA RESULTADO MATEMÁTICO ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Estratégia", fin['estrategia'])
            col2.metric("Jogos", fin['qtd'])
            col3.metric("Preço Base", f"R$ {fin.get('preco_base', 0):.2f}")
            
            st.info(f"💡 Math Advice: {fin['conselho']}")
            
            # --- MÁGICA DA I.A. (V34) ---
            if openai_key:
                with st.spinner("🤖 A I.A. está analisando os jogos gerados..."):
                    # Pega os 3 melhores jogos para a IA opinar
                    top3 = jogos[:3]
                    analise_ia = cerebro.analisar_com_gpt(openai_key, loteria, fin, top3)
                    
                    st.markdown("### 🧠 Análise do Agente I.A.")
                    st.success(analise_ia)
            else:
                st.warning("⚠️ Insira uma API Key na barra lateral para ver a análise qualitativa da I.A.")

            # --- LISTA DE JOGOS ---
            st.divider()
            st.subheader("🎲 Palpites Finais")
            for i, (jg, score) in enumerate(jogos):
                st.text(f"Jogo {i+1:02d} | Força {score:.2f} | {jg}")
