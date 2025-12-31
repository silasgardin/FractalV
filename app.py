import streamlit as st
import oraculo_motor

# Configuração da Página
st.set_page_config(page_title="Oráculo V32", page_icon="🔮", layout="centered")

st.title("🔮 Oráculo V32 - Advisor Edition")
st.markdown("### Inteligência Artificial Fractal para Loterias")

# --- 1. CONFIGURAÇÕES (Onde você cola os links do Google Sheets) ---
# DICA: No Google Sheets, vá em Arquivo > Compartilhar > Publicar na Web > Escolha "CSV" e copie o link.
SHEETS = {
    "Lotofácil": {
        "url": "https://docs.google.com/spreadsheets/d/1Uawi-DjZiY5wVZyqntQYctboRPqvu1vBFoiL7h4GkMw/edit?usp=sharing", 
        "preco": 3.50
    },
    "Mega_Sena": {
        "url": "https://docs.google.com/spreadsheets/d/1Uawi-DjZiY5wVZyqntQYctboRPqvu1vBFoiL7h4GkMw/edit?usp=sharing",
        "preco": 6.00
    },
    "Dia de Sorte": {
        "url": "https://docs.google.com/spreadsheets/d/1Uawi-DjZiY5wVZyqntQYctboRPqvu1vBFoiL7h4GkMw/edit?usp=sharing",
        "preco": 2.50
    }
}

# --- 2. INTERFACE ---
col1, col2 = st.columns(2)
with col1:
    loteria = st.selectbox("Escolha a Loteria:", list(SHEETS.keys()))
with col2:
    orcamento = st.number_input("O seu Orçamento (R$):", min_value=1.0, value=30.0, step=5.0)

if st.button("🔮 Consultar Oráculo", type="primary"):
    with st.spinner(f"A processar algoritmos Fractais para {loteria}..."):
        # Inicializa Cérebro
        cerebro = oraculo_motor.OraculoCerebro()
        dados = SHEETS[loteria]
        
        # Executa
        # Se você ainda não pôs o link real, vai dar erro.
        if "LINK_DA_SUA" in dados['url']:
            st.error("⚠️ Você precisa configurar os links do Google Sheets no arquivo app.py!")
        else:
            resultado = cerebro.gerar_palpite_cloud(
                url_dados=dados['url'],
                loteria_chave=loteria.replace("ó","o").replace(" ","_"), # Normaliza nome
                preco=dados['preco'],
                orcamento=orcamento
            )
            
            if "erro" in resultado:
                st.error(f"Erro: {resultado['erro']}")
            else:
                # Exibe Consultoria
                fin = resultado['financeiro']
                st.success(f"**Estratégia:** {fin['nome']}")
                st.info(f"💡 {fin['conselho']} | Jogos: {fin['qtd']} (Troco: R$ {fin['troco']:.2f})")
                
                # Exibe Jogos
                st.divider()
                st.subheader("🎲 Jogos Gerados")
                for i, (jg, score) in enumerate(resultado['jogos']):
                    st.text(f"Jogo {i+1:02d} | Força {score:.2f} | {jg}")
