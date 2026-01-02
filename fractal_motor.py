# ==============================================================================
# 🧠 FRACTAL-V MOTOR (V44) - CORE INTELLIGENCE
# ==============================================================================
import pandas as pd
import numpy as np
import random
import google.generativeai as genai
import warnings

warnings.filterwarnings("ignore")

class FractalCerebro: # Renomeado de OraculoCerebro
    def __init__(self):
        self.versao = "FractalV 1.0 (Genesis)"
        self.config_base = {
            "Lotofacil": {"total": 25, "marca_base": 15}, "Mega_Sena": {"total": 60, "marca_base": 6},
            "Quina": {"total": 80, "marca_base": 5}, "Dia_de_Sorte": {"total": 31, "marca_base": 7},
            "Timemania": {"total": 80, "marca_base": 10}, "Dupla_Sena": {"total": 50, "marca_base": 6},
            "Lotomania": {"total": 100,"marca_base": 50}, "Mega_da_Virada": {"total": 60, "marca_base": 6}
        }
        self.tabela_precos_default = {
            "Mega_Sena": 6.00, "Mega_da_Virada": 6.00, "Lotofacil": 3.50,
            "Quina": 3.00, "Dia_de_Sorte": 2.50, "Timemania": 3.50, "Lotomania": 3.00, "Dupla_Sena": 3.00
        }

    def carregar_csv(self, url):
        try: return pd.read_csv(url, on_bad_lines='skip')
        except: return None

    def _tratar_preco(self, valor_str):
        try:
            if isinstance(valor_str, (int, float)): return float(valor_str)
            clean = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def calcular_limite_jogos(self, url_precos, loteria_chave, orcamento_usuario):
        preco_unitario = 3.00 
        try:
            df = self.carregar_csv(url_precos)
            if df is not None:
                for _, row in df.iterrows():
                    if loteria_chave.lower() in str(row[0]).lower().replace(' ','_'):
                        val = self._tratar_preco(row[1])
                        if val > 0: preco_unitario = val; break
        except: pass

        qtd_jogos = int(orcamento_usuario // preco_unitario)
        return {"qtd": max(1, qtd_jogos), "preco_unit": preco_unitario, "troco": orcamento_usuario - (qtd_jogos * preco_unitario), "custo_total": qtd_jogos * preco_unitario}

    def executar_backtest(self, hist, total_dezenas):
        if len(hist) < 5: return "Padrão Fractal (Dados Insuficientes)", {}
        
        scores = {"Markov (Inércia)": 0, "Fractal (Equilíbrio)": 0}
        try:
            teste = hist[-5:]
            for i in range(len(teste)-1):
                passado = set([int(x) for x in teste[i] if pd.notna(x)])
                futuro = set([int(x) for x in teste[i+1] if pd.notna(x)])
                scores["Markov (Inércia)"] += len(passado.intersection(futuro))
        except: pass
        
        return max(scores, key=scores.get), scores

    def analisar_com_gemini(self, api_key, loteria, dados_fin, jogos_top3, backtest_info):
        try:
            genai.configure(api_key=api_key)
            modelo = "gemini-pro"
            try:
                ms = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                for m in ms: 
                    if 'flash' in m: modelo = m; break
                else: 
                    if ms: modelo = ms[0]
            except: pass

            model = genai.GenerativeModel(modelo)
            vencedora = backtest_info.get('vencedora', 'Padrão')
            jogos_txt = "\n".join([f"- {j[0]}" for j in jogos_top3])
            
            prompt = f"Analise estes palpites do sistema FractalV para a {loteria}.\nEstratégia: {vencedora}\nJogos:\n{jogos_txt}\n\nResponda em Português (curto):\n1. Por que a lógica '{vencedora}' se aplica aqui?\n2. Analise a distribuição do primeiro jogo."
            response = model.generate_content(prompt)
            return response.text
        except Exception as e: return f"⚠️ IA Off: {str(e)}"

    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        cfg = self.config_base.get(loteria_chave, self.config_base["Mega_Sena"])
        
        df = self.carregar_csv(url_dados)
        hist = []
        if df is not None:
            try:
                cols = [c for c in df.columns if c.strip().upper().startswith('D')]
                for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
                df = df.dropna(subset=['Concurso']).sort_values('Concurso')
                hist = df[cols].values
            except: pass

        vencedora, scores = self.executar_backtest(hist, cfg['total'])
        fin = self.calcular_limite_jogos(url_precos, loteria_chave, orcamento)
        fin['orcamento_inicial'] = orcamento

        jogos = []
        marca = cfg['marca_base']
        pool = list(range(1, cfg['total'] + 1))
        
        last_draw = []
        if len(hist) > 0:
            last_draw = [int(x) for x in hist[-1] if pd.notna(x)]

        tentativas = 0
        while len(jogos) < fin['qtd'] and tentativas < 1000:
            tentativas += 1
            try:
                if len(last_draw) > 5:
                    q_rep = int(marca * 0.6)
                    jg = random.sample(last_draw, min(len(last_draw), q_rep))
                    restantes = [n for n in pool if n not in jg]
                    jg += random.sample(restantes, marca - len(jg))
                else:
                    jg = random.sample(pool, marca)
                
                jg = sorted([int(n) for n in jg])
                
                if jg not in [x[0] for x in jogos]:
                    score = random.uniform(8.0, 9.9)
                    jogos.append((jg, score))
            except: continue
            
        if not jogos:
            jg = sorted(random.sample(pool, marca))
            jogos.append((jg, 5.0))

        jogos.sort(key=lambda x: x[1], reverse=True)
        return {"financeiro": fin, "backtest": {"vencedora": vencedora, "scores": scores}, "jogos": jogos}
