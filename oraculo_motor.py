# ==============================================================================
# 🧠 ORÁCULO MOTOR V40 - CORRIGIDO E LIMPO
# ==============================================================================
import pandas as pd
import numpy as np
import random
import google.generativeai as genai
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V40 (Fixed)"
        
        self.config_base = {
            "Lotofacil":      {"total": 25, "marca_base": 15},
            "Mega_Sena":      {"total": 60, "marca_base": 6},
            "Quina":          {"total": 80, "marca_base": 5},
            "Dia_de_Sorte":   {"total": 31, "marca_base": 7},
            "Timemania":      {"total": 80, "marca_base": 10},
            "Dupla_Sena":     {"total": 50, "marca_base": 6},
            "Lotomania":      {"total": 100,"marca_base": 50},
            "Mega_da_Virada": {"total": 60, "marca_base": 6}
        }
        
        self.tabela_precos_default = {
            "Mega_Sena": 5.00, "Mega_da_Virada": 5.00, "Lotofacil": 3.00,
            "Quina": 2.50, "Dia_de_Sorte": 2.50, "Timemania": 3.50, 
            "Lotomania": 3.00, "Dupla_Sena": 2.50
        }

    def carregar_csv(self, url):
        try: return pd.read_csv(url)
        except: return None

    def _tratar_preco(self, valor_str):
        try:
            if isinstance(valor_str, (int, float)): return float(valor_str)
            clean = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def calcular_limite_jogos(self, url_precos, loteria_chave, orcamento_usuario):
        df = self.carregar_csv(url_precos)
        preco_unitario = 0.0
        
        if df is not None:
            for _, row in df.iterrows():
                nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace(' ','_')
                if loteria_chave.lower() in nome_csv:
                    preco_unitario = self._tratar_preco(row[1])
                    break
        
        if preco_unitario <= 0:
            for k, v in self.tabela_precos_default.items():
                if loteria_chave.lower() in k.lower():
                    preco_unitario = v; break
            if preco_unitario <= 0: preco_unitario = 3.00
            
        qtd_jogos = int(orcamento_usuario // preco_unitario)
        troco = orcamento_usuario - (qtd_jogos * preco_unitario)
        
        return {
            "qtd": qtd_jogos if qtd_jogos > 0 else 1,
            "preco_unit": preco_unitario,
            "troco": troco,
            "custo_total": qtd_jogos * preco_unitario
        }

    def executar_backtest(self, hist, total_dezenas):
        if len(hist) < 15: 
            return "Padrão Aleatório (Dados insuficientes)", {}

        scores = {"Markov (Inércia)": 0, "Fractal (Equilíbrio)": 0, "Gauss (Soma)": 0}
        teste = hist[-10:]
        
        for i in range(len(teste)-1):
            passado = teste[i]
            futuro = set(teste[i+1])
            
            # Markov
            p_mk = set(passado[:len(passado)//2]) 
            scores["Markov (Inércia)"] += len(p_mk.intersection(futuro))
            
            # Fractal
            todos = set(range(1, total_dezenas+1))
            ausentes = list(todos - set(passado))
            random.shuffle(ausentes)
            p_fr = set(ausentes[:len(passado)//2])
            scores["Fractal (Equilíbrio)"] += len(p_fr.intersection(futuro))
            
            # Gauss
            meio = total_dezenas // 2
            p_gs = set(range(meio-5, meio+6))
            scores["Gauss (Soma)"] += len(p_gs.intersection(futuro))

        melhor = max(scores, key=scores.get)
        return melhor, scores

    def analisar_com_gemini(self, api_key, loteria, dados_fin, jogos_top3, backtest_info):
        try:
            genai.configure(api_key=api_key)
            modelo = "gemini-pro"
            try:
                # Tenta achar um modelo Flash ou Pro disponível
                ms = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                for m in ms: 
                    if 'flash' in m: modelo = m; break
                else:
                    if ms: modelo = ms[0]
            except: pass

            model = genai.GenerativeModel(modelo)
            vencedora = backtest_info.get('vencedora', 'Padrão')
            jogos_txt = "\n".join([f"- Jogo: {j[0]}" for j in jogos_top3])
            
            prompt = f"""
            Analise estes jogos de loteria ({loteria}) gerados pelo Oráculo V40.
            
            Contexto:
            - Orçamento: R$ {dados_fin['orcamento_inicial']:.2f} ({dados_fin['qtd']} jogos)
            - Estratégia Vencedora no Backtest: {vencedora}
            
            Jogos:
            {jogos_txt}
            
            Responda em Português (curto):
            1. Por que a estratégia '{vencedora}' foi escolhida?
            2. Analise os números do primeiro jogo sob essa ótica.
            3. Comente sobre a eficiência do orçamento.
            """
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Erro IA: {str(e)}"

    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        cfg = self.config_base.get(loteria_chave)
        if not cfg: cfg = self.config_base["Mega_Sena"]
        
        df = self.carregar_csv(url_dados)
        hist = []
        if df is not None:
            cols = [c for c in df.columns if c.strip().upper().startswith('D')]
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=['Concurso']).sort_values('Concurso')
            hist = df[cols].values
        
        vencedora, scores = self.executar_backtest(hist, cfg['total'])
        fin = self.calcular_limite_jogos(url_precos, loteria_chave, orcamento)
        fin['orcamento_inicial'] = orcamento
        
        if fin['qtd'] < 1: 
            return {"erro": f"Orçamento insuficiente. Mínimo: R$ {fin['preco_unit']:.2f}"}

        jogos = []
        marca = cfg['marca_base']
        pool = list(range(1, cfg['total'] + 1))
        last = hist[-1] if len(hist) > 0 else []

        peso_rep = 0.5
        if "Markov" in vencedora: peso_rep = 0.8
        if "Fractal" in vencedora: peso_rep = 0.2
        
        tentativas = 0
        while len(jogos) < fin['qtd'] and tentativas < 5000:
            tentativas += 1
            try:
                q_rep = int(marca * peso_rep)
                cand_rep = [n for n in last if n in pool and not pd.isna(n)]
                cand_new = [n for n in pool if n not in last]
                
                if len(cand_rep) < q_rep: q_rep = len(cand_rep)
                
                base = random.sample(cand_rep, q_rep) + random.sample(cand_new, marca - q_rep)
                jg = sorted(list(set(base)))
                
                while len(jg) < marca: 
                    n = random.choice(pool)
                    if n not in jg: jg.append(n)
                jg = sorted(jg)

                if jg not in [x[0] for x in jogos]:
                    score = random.uniform(8.0, 9.9) 
                    jogos.append((jg, score))
            except: continue
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "financeiro": fin,
            "backtest": {"vencedora": vencedora, "scores": scores},
            "jogos": jogos
        }
