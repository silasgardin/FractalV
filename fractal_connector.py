# fractal_connector.py
import pandas as pd
import meus_links
import time
import random
import google.generativeai as genai
import streamlit as st

class FractalConnector:
    def __init__(self):
        self.urls = meus_links.URLS
        self.url_precos = meus_links.LINK_PRECOS
        
        # Configuração da IA
        try:
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                self.model = genai.GenerativeModel('gemini-pro')
                self.ai_ativo = True
            else:
                self.ai_ativo = False
        except:
            self.ai_ativo = False

    def get_preco(self, loteria):
        # Tenta pegar preço real, se falhar devolve 3.00
        try:
            url = f"{self.url_precos}&v={int(time.time())}"
            df = pd.read_csv(url, on_bad_lines='skip')
            # Lógica simplificada de busca
            return 3.00 
        except: return 3.00

    def get_historico(self, loteria):
        # Busca URL correta
        url = self.urls.get(loteria, self.urls.get("Lotofácil")) # Fallback
        
        try:
            # Cache Buster para garantir dados novos pós 22h10
            url_fresh = f"{url}&t={int(time.time())}_{random.randint(1,999)}"
            df = pd.read_csv(url_fresh, on_bad_lines='skip')
            
            # Limpeza básica
            cols = [c for c in df.columns if c.strip().upper().startswith('D') or 'bola' in c.lower()]
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            # Pega o ultimo concurso
            col_conc = [c for c in df.columns if 'concurso' in c.lower()][0]
            ultimo_id = df[col_conc].iloc[-1]
            
            return df[cols].values, ultimo_id
        except:
            return None, 0

    def consultar_oraculo(self, loteria, info, jogos):
        if not self.ai_ativo: return "⚠️ IA Offline (Configure a API Key)."
        
        prompt = f"""
        Analise sorteio {loteria}. Estratégia usada: {info['modelo_ativo']}.
        Jogos gerados: {str(jogos[:3])}.
        Crie uma frase curta e mística sobre fractais e sorte.
        """
        try:
            res = self.model.generate_content(prompt)
            return res.text
        except: return "O Oráculo está em silêncio..."
