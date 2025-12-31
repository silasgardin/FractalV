import streamlit as st
import oraculo_motor

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="Oráculo V33 Pro",
    page_icon="🔮",
    layout="wide"
)

# Cabeçalho
st.title("🔮 Oráculo V33 - Sistema Financeiro Integrado")
st.markdown("""
<style>
.big-font { font-size:18px !important; }
.metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("### 🤖 Assistente de Lotaria com Precificação Dinâmica (Sheets)")

# --- 1. CONFIGURAÇÃO DOS LINKS (EDITAR AQUI) ---

# Link da aba "Vlr_jogo" (Onde estão os preços das apostas)
LINK_TABELA_PRECOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1620341582&single=true&output=csv"

# Links dos Históricos (Onde estão os resultados passados)
SHEETS = {
    "Lotofácil": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1063211255&single=true&output=csv", 
        "desc": "Aposte na Inércia (Repetição)"
    },
    "Mega Sena": {
        "url": "COLE_LINK_CSV_MEGA_SENA",
        "desc": "Aposte na Entropia (Caos)"
    },
    "Quina": {
        "url": "COLE_LINK_CSV_QUINA",
        "desc": "Equilíbrio Markoviano"
    },
    "Dia de Sorte": {
        "url": "COLE_LINK_CSV_DIA_DE_SORTE",
        "desc": "Distribuição Normal (Gauss)"
    },
    "Timemania": {
        "url": "COLE_LINK_CSV_TIMEMANIA",
        "desc": "Foco em Colunas"
    },
    "Dupla Sena": {
        "url": "COLE_LINK_CSV_DUPLA_SENA",
        "desc": "Dupla Chance Fractal"
    },
    "Lotomania": {
        "url": "COLE_LINK_CSV_LOTOMANIA",
        "desc": "Espelhamento de Quadrantes"
    },
    "Mega da Virada": {
        "url": "COLE_LINK_CSV_MEGA_VIRADA", 
        "desc": "Especial de Fim de Ano"
    }
}

# --- 2. BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("Parâmetros")
    
    loteria = st.selectbox("Escolha a Modalidade:", list(SHEETS.keys()))
    
    st.info(f"ℹ️ **Lógica V33:** {SHEETS[loteria]['desc']}")
    
    orcamento = st.number_input(
        "💰 Seu Orçamento (R$):", 
        min_value=1.0, 
        value=50.0, 
        step=5.0,
        help="Quanto quer investir? O Oráculo verifica o preço atualizado na planilha e calcula a melhor estratégia."
    )

# --- 3. EXECUÇÃO DO ORÁCULO ---
if st.button("🔮 Consultar Estratégia & Gerar Jogos", type="primary", use_container_width=True):
    
    # Validação Básica de Links
    if "COLE_" in LINK_TABELA_PRECOS or "COLE_" in SHEETS[loteria]['url']:
        st.error("🚨 **ERRO DE CONFIGURAÇÃO:**")
        st.warning("Você precisa configurar os links CSV do Google Sheets no ficheiro `app.py` antes de usar.")
        st.stop()

    with st.spinner(f"📡 A buscar preços atualizados na Nuvem e processar V33 para {loteria}..."):
        try:
            # Instancia o Cérebro
            cerebro = oraculo_motor.OraculoCerebro()
            
            # Normaliza o nome da lotaria para a chave interna (ex: "Lotofácil" -> "Lotofacil")
            chave_normalizada = loteria.replace("á","a").replace("ç","c").replace(" ","_")
            
            # Executa o Motor V33 com Precificação Dinâmica
            resultado = cerebro.gerar_palpite_cloud(
                url_dados=SHEETS[loteria]['url'],
                url_precos=LINK_TABELA_PRECOS,
                loteria_chave=chave_normalizada, 
                orcamento=orcamento
            )
            
            # Tratamento de Erros
            if "erro" in resultado:
                st.error(f"❌ Erro do Oráculo: {resultado['erro']}")
            
            else:
                # SUCESSO!
                fin = resultado['financeiro']
                jogos = resultado['jogos']
                
                # Feedback de Preço Encontrado
                preco_base = fin.get('preco_base', 0)
                if preco_base > 0:
                    st.toast(f"Preço Base Atualizado Detectado: R$ {preco_base:.2f}", icon="💲")
                
                # Bloco 1: Consultoria Financeira
                st.markdown("---")
                colA, colB, colC = st.columns(3)
                colA.metric("Estratégia Definida", fin['estrategia'])
                colB.metric("Quantidade de Jogos", fin['qtd'])
                colC.metric("Troco (Saldo)", f"R$ {fin['troco']:.2f}")
                
                st.success(f"💡 **Conselho V33:** {fin['conselho']}")
                
                # Bloco 2: Os Palpites
                st.markdown(f"### 🎲 Palpites Gerados ({len(jogos)} jogos)")
                
                for i, (jg, score) in enumerate(jogos):
                    # Formatação visual dos números
                    numeros_fmt = "  -  ".join([f"**{n:02d}**" for n in jg])
                    
                    with st.expander(f"🎫 Jogo {i+1:02d} (Score Fractal: {score:.2f})", expanded=(i<5)):
                        st.markdown(f"## {numeros_fmt}")
                        if i == 0: st.caption("🏆 *Melhor oportunidade matemática identificada*")

        except Exception as e:
            st.error(f"Ocorreu um erro crítico na execução: {e}")
