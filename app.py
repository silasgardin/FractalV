import streamlit as st
import oraculo_motor

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="Oráculo V32 Advisor",
    page_icon="🔮",
    layout="wide"
)

# Cabeçalho
st.title("🔮 Oráculo V32 - Inteligência Fractal")
st.markdown("""
<style>
.big-font { font-size:18px !important; }
.metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("### 🤖 Assistente de Loteria com Análise Financeira e Fractal")

# --- 1. CONFIGURAÇÃO DOS LINKS (EDITAR AQUI) ---
# Substitua os textos "COLE_O_LINK..." pelos seus links CSV do Google Sheets.
# O preço já está atualizado conforme o padrão atual (Dez/2025).

SHEETS = {
    "Lotofácil": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1063211255&single=true&output=csv", 
        "preco": 3.50,
        "desc": "Aposte na Inércia (Repetição)"
    },
    "Mega Sena": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=936546416&single=true&output=csv",
        "preco": 6.00,
        "desc": "Aposte na Entropia (Caos)"
    },
    "Quina": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1703483549&single=true&output=csv",
        "preco": 3.00,
        "desc": "Equilíbrio Markoviano"
    },
    "Dia de Sorte": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1059501941&single=true&output=csv",
        "preco": 2.50,
        "desc": "Distribuição Normal (Gauss)"
    },
    "Timemania": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1575649264&single=true&output=csv",
        "preco": 3.50,
        "desc": "Foco em Colunas"
    },
    "Dupla Sena": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=152509825&single=true&output=csv",
        "preco": 3.00,
        "desc": "Dupla Chance Fractal"
    },
    "Lotomania": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=848764653&single=true&output=csv",
        "preco": 3.00,
        "desc": "Espelhamento de Quadrantes"
    },
    "Mega da Virada": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=298407214&single=true&output=csv", # Pode usar o mesmo da Mega Sena se quiser
        "preco": 6.00,
        "desc": "Especial de Fim de Ano"
    }
}

# --- 2. BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4206/4206233.png", width=80)
    st.header("Configuração de Jogo")
    
    loteria = st.selectbox("Escolha a Modalidade:", list(SHEETS.keys()))
    
    st.info(f"ℹ️ **Lógica V32:** {SHEETS[loteria]['desc']}")
    
    orcamento = st.number_input(
        "💰 Seu Orçamento (R$):", 
        min_value=1.0, 
        value=50.0, 
        step=5.0,
        help="Quanto você quer investir hoje? O Oráculo calculará a melhor estratégia."
    )
    
    preco = SHEETS[loteria]['preco']
    qtd_estimada = int(orcamento // preco)
    st.caption(f"Custo por aposta: R$ {preco:.2f} | Jogos estimados: {qtd_estimada}")

# --- 3. EXECUÇÃO DO ORÁCULO ---
if st.button("🔮 Consultar Estratégia & Gerar Jogos", type="primary", use_container_width=True):
    
    # Validação Básica de Link
    dados = SHEETS[loteria]
    if "COLE_O_LINK" in dados['url']:
        st.error("🚨 **ERRO DE CONFIGURAÇÃO:**")
        st.warning(f"Você ainda não configurou o link do Google Sheets para **{loteria}** no código `app.py`.")
        st.code(f'SHEETS = {{ "{loteria}": {{ "url": "COLE_SEU_LINK_AQUI", ... }} }}')
        st.stop()

    with st.spinner(f"📡 Conectando ao Google Sheets... Processando Matemática Fractal V32..."):
        try:
            # Instancia o Cérebro
            cerebro = oraculo_motor.OraculoCerebro()
            
            # Chama a função Cloud
            # Normalizamos o nome da chave para evitar erros de acento (ex: 'Lotofácil' -> 'Lotofacil')
            chave_normalizada = loteria.replace("á","a").replace("ç","c").replace(" ","_")
            
            resultado = cerebro.gerar_palpite_cloud(
                url_dados=dados['url'],
                loteria_chave=chave_normalizada, 
                preco_aposta=dados['preco'],
                orcamento=orcamento
            )
            
            # Tratamento de Erros do Motor
            if "erro" in resultado:
                st.error(f"❌ Erro do Oráculo: {resultado['erro']}")
            
            else:
                # SUCESSO! EXIBIÇÃO DOS DADOS
                fin = resultado['financeiro']
                jogos = resultado['jogos']
                
                # Bloco 1: Consultoria Financeira
                st.markdown("---")
                colA, colB, colC = st.columns(3)
                colA.metric("Estratégia Definida", fin['estrategia'])
                colB.metric("Quantidade de Jogos", fin['qtd'])
                colC.metric("Troco (Saldo)", f"R$ {fin['troco']:.2f}")
                
                st.success(f"💡 **Conselho do Advisor:** {fin['conselho']}")
                
                # Bloco 2: Os Palpites
                st.markdown("### 🎲 Palpites Gerados (V32 Fractal)")
                
                for i, (jg, score) in enumerate(jogos):
                    # Formatação visual dos números
                    numeros_fmt = "  -  ".join([f"**{n:02d}**" for n in jg])
                    
                    with st.expander(f"🎫 Jogo {i+1:02d} (Score Fractal: {score:.2f})", expanded=(i<5)):
                        st.markdown(f"## {numeros_fmt}")
                        if i < 3: st.caption("🔥 *Este jogo está no Top 3 da Elite Matemática*")

        except Exception as e:
            st.error(f"Ocorreu um erro crítico na execução: {e}")
