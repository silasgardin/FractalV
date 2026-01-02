import streamlit as st
import fractal_motor 
import fractal_connector # <--- NOVO IMPORT
import google.generativeai as genai

# ... (CONFIGURAÇÕES DE CSS E HEADER MANTÊM-SE IGUAIS) ...
# ... Copie o CSS e Config da versão anterior ...

# --- NOVA FUNÇÃO DE CACHE ---
@st.cache_data(ttl=1800, show_spinner=False)
def calcular_sistema_integrado(loteria_nome, orcamento):
    # 1. Instancia o Conector (Librarian)
    conector = fractal_connector.FractalConnector()
    
    # 2. Conector vai ao Oráculo V buscar os dados
    historico, ultimo_id = conector.get_historico(loteria_nome)
    preco = conector.get_preco(loteria_nome)
    
    # 3. Instancia o Motor (Mathematician)
    cerebro = fractal_motor.FractalCerebro()
    
    # 4. Motor processa os dados crus
    if historico is None:
        return {"erro": "Falha ao conectar ao Oráculo V"}, cerebro
        
    resultado = cerebro.processar_nucleo(
        historico, ultimo_id, preco, loteria_nome, orcamento
    )
    
    return resultado, cerebro

# ... (RESTO DO CÓDIGO DE INTERFACE MANTÉM-SE IGUAL, SÓ MUDA A CHAMADA NO BOTÃO) ...

# DENTRO DO BOTÃO:
if st.button("ATIVAR NÚCLEO FRACTAL", type="primary"):
    with st.spinner(f"📡 Conectando ao Oráculo V e processando..."):
        try:
            # CHAMA A NOVA FUNÇÃO INTEGRADA
            res, cerebro_ativo = calcular_sistema_integrado(loteria, orcamento)
            
            # ... (Resto do código de exibição é idêntico) ...
