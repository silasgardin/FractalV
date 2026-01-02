# ==============================================================================
# 🔌 FRACTAL CONNECTOR - CAMADA DE DADOS ORÁCULO V
# ARQUIVO: fractal_connector.py
# ==============================================================================
import pandas as pd
import meus_links # Sua base de dados (Oráculo V)

class FractalConnector:
    def __init__(self):
        self.urls = meus_links.URLS
        self.url_precos = meus_links.LINK_PRECOS
        
        # Mapa de nomes para garantir que o sistema encontre a chave certa
        self.mapa_nomes = {
            "Lotofácil": "Lotofácil", "Lotofacil": "Lotofácil",
            "Mega Sena": "Mega Sena", "Mega_Sena": "Mega Sena",
            "Quina": "Quina",
            "Dia de Sorte": "Dia de Sorte", "Dia_de_Sorte": "Dia de Sorte",
            "Timemania": "Timemania",
            "Dupla Sena": "Dupla Sena", "Dupla_Sena": "Dupla Sena",
            "Lotomania": "Lotomania",
            "Mega da Virada": "Mega da Virada", "Mega_da_Virada": "Mega da Virada"
        }

    def _tratar_valor(self, valor):
        """Converte strings de moeda em float"""
        try:
            if isinstance(valor, (int, float)): return float(valor)
            clean = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def get_preco(self, loteria_nome):
        """Busca o preço atualizado na planilha de preços"""
        preco_padrao = 3.00
        try:
            df = pd.read_csv(self.url_precos, on_bad_lines='skip')
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
        Retorna:
        1. Matriz numpy com todos os resultados (histórico).
        2. ID do último concurso (para a semente).
        """
        chave = self.mapa_nomes.get(loteria_nome, loteria_nome)
        url = self.urls.get(chave)
        
        if not url: return None, 0
        
        try:
            df = pd.read_csv(url, on_bad_lines='skip')
            
            # Limpeza automática das colunas de dezenas (D1, D2, Bola1, etc)
            cols = [c for c in df.columns if str(c).strip().upper().startswith('D') or 'bola' in str(c).lower()]
            
            # Garante que são números
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            df = df.dropna(subset=['Concurso']).sort_values('Concurso')
            
            # Retorna apenas os valores das bolas e o último concurso
            historico = df[cols].values
            ultimo_conc = int(df['Concurso'].iloc[-1])
            
            return historico, ultimo_conc
        except Exception as e:
            print(f"Erro ao baixar dados do Oráculo V: {e}")
            return None, 0
