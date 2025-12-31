import streamlit as st
import oraculo_motor
import meus_links  # <--- IMPORTAMOS O SEU ARQUIVO DE LINKS AQUI

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Oráculo V35 Gemini", page_icon="✨", layout="wide")

# ... (resto do código visual) ...

# ==============================================================================
# CONFIGURAÇÃO DOS LINKS (AUTOMÁTICA)
# ==============================================================================
# Agora o código puxa do arquivo externo. Não precisa colar nada aqui!
LINK_TABELA_PRECOS = meus_links.LINK_PRECOS

SHEETS = {
    "Lotofácil":    {"url": meus_links.URLS["Lotofácil"],    "desc": "Inércia (Repetição)"},
    "Mega Sena":    {"url": meus_links.URLS["Mega Sena"],    "desc": "Entropia (Caos)"},
    "Quina":        {"url": meus_links.URLS["Quina"],        "desc": "Equilíbrio Markov"},
    "Dia de Sorte": {"url": meus_links.URLS["Dia de Sorte"], "desc": "Gaussiana"},
    "Timemania":    {"url": meus_links.URLS["Timemania"],    "desc": "Colunas"},
    "Dupla Sena":   {"url": meus_links.URLS["Dupla Sena"],   "desc": "Dupla Chance"},
    "Lotomania":    {"url": meus_links.URLS["Lotomania"],    "desc": "Espelhamento"},
    "Mega da Virada": {"url": meus_links.URLS["Mega da Virada"], "desc": "Sazonal"}
}

# ... (O resto do código continua exatamente igual) ...
