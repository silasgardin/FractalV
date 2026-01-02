# ==============================================================================
# 🔌 FRACTAL CONNECTOR - CORREÇÃO DE LEITURA (LAST GAME FIX)
# ARQUIVO: fractal_connector.py
# ==============================================================================
import pandas as pd
import meus_links

class FractalConnector:
    def __init__(self):
        self.urls = meus_links.URLS
        self.url_precos = meus_links.LINK_PRECOS
        
        self.mapa_nomes = {
            "Lotofácil": "Lotofácil", "Lotofacil": "Lotofácil",
            "Mega Sena": "Mega Sena", "Mega_Sena": "Mega Sena",
            "Quina": "Quina", "Dia de Sorte": "Dia de Sorte", 
            "Dia_de_Sorte": "Dia de Sorte", "Timemania": "Timemania",
            "Dupla Sena": "Dupla Sena", "Dupla_Sena": "Dupla Sena",
            "Lotomania": "Lotomania", "Mega da Virada": "Mega da Virada", 
            "Mega_da_Virada": "Mega da Virada"
        }

    def _tratar_valor(self, valor):
        try:
            if isinstance(valor, (int, float)): return float(valor)
            clean = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def get_preco(self, loteria_nome):
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
        chave = self.mapa_nomes.get(loteria_nome, loteria_nome)
        url = self.urls.get(chave)
        
        if not url: return None, 0
        
        try:
            # 1. Lê o CSV
            df = pd.read_csv(url, on_bad_lines='skip')
            
            # 2. Identifica colunas (Concurso e Bolas)
            # Normaliza o nome das colunas para evitar erros de maiúsculas/minúsculas
            df.columns = [c.strip() for c in df.columns]
            
            # Procura coluna de Concurso
            col_concurso = None
            for c in df.columns:
                if 'concurso' in c.lower():
                    col_concurso = c
                    break
            
            if not col_concurso:
                # Tenta pegar a primeira coluna se não achar o nome "Concurso"
                col_concurso = df.columns[0]

            # 3. LIMPEZA CRÍTICA: Força "Concurso" a ser Numérico e Remove Vazios
            df[col_concurso] = pd.to_numeric(df[col_concurso], errors='coerce')
            df = df.dropna(subset=[col_concurso]) # Remove linhas onde concurso é NaN
            df = df[df[col_concurso] > 0] # Garante que é maior que zero
            
            # 4. ORDENAÇÃO MATEMÁTICA (Garante que o último é o maior número)
            df = df.sort_values(by=col_concurso, ascending=True)

            # 5. Pega as colunas de dezenas (Bolas)
            cols_dezenas = [c for c in df.columns if str(c).strip().upper().startswith('D') or 'bola' in str(c).lower()]
            
            # Garante que as dezenas também são números
            for c in cols_dezenas: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            # 6. Retorna Dados
            historico = df[cols_dezenas].values
            ultimo_conc_id = int(df[col_concurso].iloc[-1]) # Pega o último da lista ordenada
            
            return historico, ultimo_conc_id
            
        except Exception as e:
            print(f"Erro Conector: {e}")
            return None, 0
