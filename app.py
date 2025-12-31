import streamlit as st
import oraculo_motor

st.set_page_config(page_title="Oráculo V32", page_icon="🔮")

st.title("🔮 Oráculo V32 Advisor")
st.markdown("### Inteligência Artificial Fractal para Loterias")

# --- CONFIGURAÇÃO DAS PLANILHAS (COLE SEUS LINKS AQUI) ---
# Passo a passo para pegar o link:
# 1. No Google Sheets > Arquivo > Compartilhar > Publicar na Web
# 2. Escolha a aba (ex: "Mega Sena") e o formato "Valores separados por vírgula (.csv)"
# 3. Copie o link e cole abaixo.

SHEETS = {
    "Mega Sena": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=936546416&single=true&output=csv", 
        "preco": 6.00
    },
    "Lotofácil": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pubhtml?gid=1063211255&single=true",
        "preco": 3.50
    },
    "Quina": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pubhtml?gid=1703483549&single=true",
        "preco": 3.00
    },
    "Dia de Sorte": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pubhtml?gid=1059501941&single=true",
        "preco": 2.50
    },
    "Timemania": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pubhtml?gid=1575649264&single=true",
        "preco": 3.50
    },
    "Dupla Sena": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=152509825&single=true&output=csv",
        "preco": 3.00
    },
    "Loto Mania": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pubhtml?gid=848764653&single=true",
        "preco": 3.00
}

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Parâmetros")
    loteria = st.selectbox("Escolha o Jogo:", list(SHEETS.keys()))
    orcamento = st.number_input("Orçamento Disponível (R$):", min_value=1.0, value=50.0, step=10.0)
    st.info(f"Preço da aposta: R$ {SHEETS[loteria]['preco']:.2f}")

# --- BOTÃO PRINCIPAL ---
if st.button("🔮 Consultar Oráculo", type="primary"):
    with st.spinner(f"A conectar ao Google Sheets e processar V32 Fractal para {loteria}..."):
        
        cerebro = oraculo_motor.OraculoCerebro()
        dados = SHEETS[loteria]
        
        # Verifica se o link foi configurado
        if "COLE_O_LINK" in dados['url']:
            st.error("⚠️ ERRO: Você precisa editar o arquivo app.py e colocar os links do Google Sheets!")
        else:
            # Executa o Motor
            resultado = cerebro.gerar_palpite_cloud(
                url_dados=dados['url'],
                loteria_chave=loteria.replace(" ","_").replace("á","a"),
                preco_aposta=dados['preco'],
                orcamento=orcamento
            )
            
            if "erro" in resultado:
                st.error(resultado['erro'])
            else:
                fin = resultado['financeiro']
                
                # Exibe Estratégia
                st.success(f"**Estratégia Recomendada:** {fin['estrategia']}")
                col1, col2 = st.columns(2)
                col1.metric("Jogos Possíveis", fin['qtd'])
                col2.metric("Troco", f"R$ {fin['troco']:.2f}")
                st.caption(fin['conselho'])
                
                # Exibe Tabela de Jogos
                st.divider()
                st.subheader("🎲 Palpites Gerados")
                
                for i, (jg, score) in enumerate(resultado['jogos']):
                    st.text(f"Jogo {i+1:02d} | Força: {score:.2f} | {jg}")
