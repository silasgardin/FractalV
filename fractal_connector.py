# ==============================================================================
# 🔌 FRACTAL CONNECTOR V6.0 - DADOS BLINDADOS + IA GENERATIVA
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
        
        # Mapa para corrigir nomes diferentes entre Sistema e Planilha
        self.mapa_nomes = {
            "Lotofacil": "Lotofácil", "Lotofácil": "Lotofácil",
            "Mega_Sena": "Mega Sena", "Mega Sena": "Mega Sena",
            "Quina": "Quina", 
            "Dia_de_Sorte": "Dia de Sorte", "Dia de Sorte": "Dia de Sorte"
        }

        # --- MÓDULO DE INTELIGÊNCIA ARTIFICIAL (GEMINI) ---
        self.ai_ativo = False
        try:
            # Tenta pegar a chave dos segredos do Streamlit
            if "GEMINI_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_KEY"])
                self.model = genai.GenerativeModel('gemini-pro')
                self.ai_ativo = True
            else:
                print("⚠️ Aviso: GEMINI_KEY não encontrada nos Secrets.")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar IA: {e}")

    # --- MÉTODOS DE DADOS (COM CACHE BUSTER) ---
    def _tratar_valor(self, valor):
        try:
            if isinstance(valor, (int, float)): return float(valor)
            clean = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def get_preco(self, loteria_nome):
        preco_padrao = 3.00
        try:
            # O truque do &v=time força o Google a entregar a versão nova da planilha
            url_fresca = f"{self.url_precos}&v={int(time.time())}"
            df = pd.read_csv(url_fresca, on_bad_lines='skip')
            
            nome_alvo = self.mapa_nomes.get(loteria_nome, loteria_nome).lower()
            
            for _, row in df.iterrows():
                # Tenta encontrar o nome da loteria na coluna A
                nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace('_', ' ')
                if nome_alvo.replace('á','a').replace('_',' ').lower() in nome_csv:
                    val = self._tratar_valor(row[1])
                    if val > 0: return val
        except: 
            pass # Se der erro, retorna o padrão
            
        return preco_padrao

    def get_historico(self, loteria_nome):
        """
        Retorna: (numpy_array_dos_numeros, ultimo_concurso_id)
        """
        chave = self.mapa_nomes.get(loteria_nome, loteria_nome)
        url = self.urls.get(chave)
        
        # Fallback se a chave não for encontrada exata, tenta pegar pela Lotofácil padrão
        if not url: 
             url = self.urls.get("Lotofácil")
        
        try:
            # CACHE BUSTER: Garante dados novos pós 22h10
            # Adiciona parâmetros aleatórios na URL para o Google não servir cache
            url_fresca = f"{url}&cache_buster={int(time.time())}_{random.randint(1,9999)}"
            
            df = pd.read_csv(url_fresca, on_bad_lines='skip')
            df.columns = [c.strip() for c in df.columns]
            
            # Localiza a coluna do Concurso
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

            # Extração das Dezenas (Colunas que começam com D ou Bola)
            cols_dezenas = [c for c in df.columns if str(c).strip().upper().startswith('D') or 'bola' in str(c).lower()]
            
            # Converte tudo para número
            for c in cols_dezenas: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            historico = df[cols_dezenas].values
            ultimo_conc_id = int(df[col_concurso].iloc[-1])
            
            return historico, ultimo_conc_id
            
        except Exception as e:
            print(f"Erro Conector (Get Histórico): {e}")
            return None, 0

    # --- MÉTODOS DA IA (GEMINI) ---
    def consultar_oraculo(self, loteria, info, jogos):
        if not self.ai_ativo:
            return "⚠️ A IA Generativa está offline. Configure a GEMINI_KEY no Streamlit Secrets para receber as previsões místicas."

        # Cria o prompt para o Gemini
        prompt = f"""
        Você é o 'Oráculo V', uma inteligência digital focada em padrões de Caos e Fractais.
        
        CONTEXTO ATUAL:
        - Sorteio: {loteria}
        - Último Concurso Registrado: {info.get('ultimo_concurso', '?')}
        - Estratégia Matemática Detectada: {info.get('modelo_ativo', 'Híbrido')}
        - Descrição da Estratégia: {info.get('descricao', 'Análise Profunda')}
        
        DADOS GERADOS:
        Os 3 melhores jogos calculados pelo motor foram: {str(jogos[:3])}
        
        SUA MISSÃO:
        Escreva um parágrafo curto (máximo 3 frases) e enigmático.
        Interprete esses números falando sobre "Entropia", "Alinhamento Fractal" ou "Ressonância".
        Não prometa vitória, mas indique que a probabilidade matemática está favorável.
        Seja sério, científico, mas com um tom místico.
        """

        try:
            # Chama a API do Google
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"O Oráculo tenta falar, mas há ruído no sinal... (Erro API: {str(e)})"
