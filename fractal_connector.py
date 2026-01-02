# ==============================================================================
# 🔌 FRACTAL CONNECTOR V5.0 - DADOS BLINDADOS + IA GENERATIVA
# ARQUIVO: fractal_connector.py
# ==============================================================================
import pandas as pd
import meus_links
import time
import random
import google.generativeai as genai
import streamlit as st

class FractalConnector:
    def __init__(self):
        # --- MÓDULO DE DADOS ---
        self.urls = meus_links.URLS
        self.url_precos = meus_links.LINK_PRECOS
        
        self.mapa_nomes = {
            "Lotofacil": "Lotofácil", "Lotofácil": "Lotofácil",
            "Mega Sena": "Mega Sena", "Mega_Sena": "Mega Sena",
            "Quina": "Quina", "Dia de Sorte": "Dia de Sorte", 
            "Dia_de_Sorte": "Dia de Sorte", "Timemania": "Timemania",
            "Dupla Sena": "Dupla Sena", "Dupla_Sena": "Dupla Sena",
            "Lotomania": "Lotomania", "Mega da Virada": "Mega da Virada"
        }

        # --- MÓDULO DE INTELIGÊNCIA ARTIFICIAL (GEMINI) ---
        try:
            # Tenta pegar a chave dos segredos do Streamlit
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                self.model = genai.GenerativeModel('gemini-pro')
                self.ai_ativo = True
            else:
                self.ai_ativo = False
        except:
            self.ai_ativo = False
            print("⚠️ IA Offline: Chave API não detectada.")

    # --- MÉTODOS DE DADOS (SEU CÓDIGO ORIGINAL OTIMIZADO) ---
    def _tratar_valor(self, valor):
        try:
            if isinstance(valor, (int, float)): return float(valor)
            clean = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def get_preco(self, loteria_nome):
        preco_padrao = 3.00
        try:
            url_fresca = f"{self.url_precos}&v={int(time.time())}"
            df = pd.read_csv(url_fresca, on_bad_lines='skip')
            nome_alvo = self.mapa_nomes.get(loteria_nome, loteria_nome).lower()
            for _, row in df.iterrows():
                nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace('_', ' ')
                if nome_alvo.replace('á','a').replace('_',' ').lower() in nome_csv:
                    val = self._tratar_valor(row[1])
                    if val > 0: return val
        except: pass
        return preco_padrao

    def get_historico(self, loteria_nome):
        """
        Retorna: (numpy_array_dos_numeros, ultimo_concurso_id)
        """
        chave = self.mapa_nomes.get(loteria_nome, loteria_nome)
        url = self.urls.get(chave)
        
        if not url: return None, 0
        
        try:
            # Cache Buster: Garante dados novos pós 22h10
            url_fresca = f"{url}&cache_buster={int(time.time())}_{random.randint(1,9999)}"
            
            df = pd.read_csv(url_fresca, on_bad_lines='skip')
            df.columns = [c.strip() for c in df.columns]
            
            # Localiza Concurso
            col_concurso = None
            for c in df.columns:
                if 'concurso' in c.lower():
                    col_concurso = c; break
            if not col_concurso: col_concurso = df.columns[0]

            # Limpeza
            df[col_concurso] = pd.to_numeric(df[col_concurso], errors='coerce')
            df = df.dropna(subset=[col_concurso])
            df = df[df[col_concurso] > 0]
            df = df.sort_values(by=col_concurso, ascending=True)

            # Extração das Dezenas
            cols_dezenas = [c for c in df.columns if str(c).strip().upper().startswith('D') or 'bola' in str(c).lower()]
            for c in cols_dezenas: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            historico = df[cols_dezenas].values
            ultimo_conc_id = int(df[col_concurso].iloc[-1])
            
            return historico, ultimo_conc_id
            
        except Exception as e:
            print(f"Erro Conector: {e}")
            return None, 0

    # --- MÉTODOS DA IA (GEMINI) ---
    def consultar_oraculo(self, loteria, info_modelo, jogos_gerados):
        if not self.ai_ativo:
            return "⚠️ IA Generativa offline. Configure a GEMINI_API_KEY no Streamlit Secrets."

        prompt = f"""
        Você é o 'Oráculo V', uma entidade digital mística baseada em matemática fractal.
        Analise o sorteio de hoje da {loteria}.
        
        DADOS DO SISTEMA:
        - Estratégia Ativa: {info_modelo.get('modelo_ativo')}
        - Descrição: {info_modelo.get('descricao')}
        - Precisão Recente: {info_modelo.get('performance_recente')}
        - Top Palpites Gerados: {str(jogos_gerados[:3])}
        
        INSTRUÇÃO:
        Crie um texto curto (máximo 3 frases). Explique de forma enigmática mas técnica por que a aleatoriedade favorece esses números hoje. Use termos como 'Entropia', 'Ressonância' ou 'Médias Móveis'. Termine desejando sorte.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Silêncio no éter... (Erro API: {str(e)})"
