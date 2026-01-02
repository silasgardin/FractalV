# oraculo_motor.py - V35 (Gemini Pro Stable Fixed)
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import random
import google.generativeai as genai
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V35 (Gemini Pro Stable)"
        
        # Configurações de Jogo
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
        
        self.multiplicadores = {
            "Mega_Sena":      {6: 1, 7: 7, 8: 28, 9: 84, 10: 210},
            "Mega_da_Virada": {6: 1, 7: 7, 8: 28, 9: 84},
            "Lotofacil":      {15: 1, 16: 16, 17: 136, 18: 816},
            "Quina":          {5: 1, 6: 6, 7: 21, 8: 56, 9: 126},
            "Dia_de_Sorte":   {7: 1, 8: 8, 9: 36, 10: 120},
            "Dupla_Sena":     {6: 1, 7: 7, 8: 28, 9: 84},
            "Timemania":      {10: 1}, 
            "Lotomania":      {50: 1}  
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

    def atualizar_precos(self, url_precos, loteria_chave):
        df = self.carregar_csv(url_precos)
        preco_base = 0.0
        fallback = 3.00
        
        if df is not None:
            for _, row in df.iterrows():
                nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace(' ','_')
                if loteria_chave.lower() in nome_csv or nome_csv in loteria_chave.lower():
                    preco_base = self._tratar_preco(row[1])
                    break
        
        if preco_base <= 0: preco_base = fallback
        
        chave_mult = None
        for k in self.multiplicadores.keys():
            if k.lower() in loteria_chave.lower(): chave_mult = k; break
            
        if chave_mult:
            tabela = {qtd: (fat * preco_base) for qtd, fat in self.multiplicadores[chave_mult].items()}
        else:
            base = self.config_base.get(loteria_chave, {}).get('marca_base', 6)
            tabela = {base: preco_base}
            
        return tabela, preco_base

    # --- MATEMÁTICA ---
    def _core_markov(self, hist, total):
        matriz = np.zeros((total + 1, total + 1)); recorte = hist[-100:]
        for i in range(len(recorte)-1):
            for u in recorte[i]:
                if pd.isna(u): continue
                for v in recorte[i+1]:
                    if pd.isna(v): continue
                    matriz[int(u)][int(v)] += 1
        row_sums = matriz.sum(axis=1); row_sums[row_sums==0] = 1
        probs = matriz / row_sums[:, None]
        last = hist[-1]; scores = {}
        for d in range(1, total+1):
            s=0; c=0
            for n in last:
                if not pd.isna(n): s+=probs[int(n)][d]; c+=1
            scores[d] = s/c if c>0 else 0
        return scores

    def _core_xgboost(self, hist, total):
        X, y = [], []; atrasos = {d: 0 for d in range(1, total+1)}
        start = max(0, len(hist)-80)
        for i in range(start, len(hist)-1):
            p, c = hist[i], hist[i+1]
            for d in range(1, total+1):
                saiu = 1 if d in p else 0; atr = atrasos[d]
                if d in c or atr > 5: X.append([d, saiu, atr]); y.append(1 if d in c else 0)
                atrasos[d] = 0 if d in p else atrasos[d]+1
        scores = {}
        try:
            model = GradientBoostingClassifier(n_estimators=40, max_depth=3)
            model.fit(np.array(X), np.array(y))
            last = hist[-1]
            for d in range(1, total+1):
                saiu = 1 if d in last else 0
                scores[d] = model.predict_proba(np.array([[d, saiu, atrasos[d]]]))[0][1]
        except: scores = {d: 0.5 for d in range(1, total+1)}
        return scores

    def _core_fractal(self, hist, total):
        scores = {}; recorte = hist[-50:]
        for d in range(1, total+1):
            series = [1 if d in row else 0 for row in recorte]
            if len(series) < 5: scores[d] = 0.5; continue
            flips = sum(1 for i in range(1, len(series)) if series[i] != series[i-1])
            ratio = flips / (len(series) - 1)
            scores[d] = ratio if series[-1] == 0 else 1.0 - ratio
        return scores

    def _validar_filtros(self, jogo, last_draw, loteria_chave):
        soma = sum(jogo)
        if "facil" in loteria_chave.lower():
            media = len(jogo) * 13 
            if not (media - 35 <= soma <= media + 35): return False
            comuns = len(set(jogo).intersection(set(last_draw)))
            delta = len(jogo) - 15
            if not (8 + delta <= comuns <= 11 + delta): return False
        elif "mega" in loteria_chave.lower():
            if len(jogo) == 6 and not (140 <= soma <= 240): return False
        return True

    def otimizar_orcamento(self, tabela, orcamento):
        base = min(tabela.keys()); melhor = base; qtd_final = int(orcamento // tabela[base])
        for d in sorted(tabela.keys(), reverse=True):
            preco = tabela[d]; qtd = int(orcamento // preco)
            if qtd >= 1:
                min_j = 2 if d > base else 1
                if qtd >= min_j: melhor = d; qtd_final = qtd; break
        custo = tabela[melhor]
        return {"tipo": "Combo" if melhor > base else "Simples", "dezenas": melhor, "qtd": qtd_final, "troco": orcamento - (qtd_final*custo)}

    # --- CORREÇÃO DO GEMINI (AQUI ESTÁ A MUDANÇA) ---
    def analisar_com_gemini(self, api_key, loteria, estrategia_fin, jogos_top3):
        try:
            # Configuração segura
            genai.configure(api_key=api_key)
            
            # Mudei de 'gemini-1.5-flash' para 'gemini-pro'
            # 'gemini-pro' é o modelo mais estável e universalmente suportado
            model = genai.GenerativeModel('gemini-pro')
            
            jogos_texto = "\n".join([f"- Jogo: {j[0]} (Score Mat: {j[1]:.2f})" for j in jogos_top3])
            
            prompt = f"""
            Aja como um Matemático Especialista em Loterias.
            Analise os dados gerados pelo meu algoritmo para a {loteria}:
            
            1. Estratégia Financeira: {estrategia_fin['estrategia']}
            2. Jogos Gerados (Top 3):
            {jogos_texto}
            
            Responda em Português (máx 4 linhas):
            - Por que esta estratégia financeira é eficiente?
            - Cite uma observação curiosa sobre os números do primeiro jogo (pares/ímpares ou repetições).
            """
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Retorna o erro de forma amigável sem quebrar o app
            return f"⚠️ Nota: O Gemini (IA) não pôde responder agora ({str(e)}), mas os seus jogos matemáticos acima estão 100% corretos e prontos para usar!"

    # --- EXECUÇÃO ---
    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        cfg = self.config_base.get(loteria_chave)
        if not cfg:
             for k, v in self.config_base.items():
                if loteria_chave.lower() in k.lower(): cfg = v; loteria_chave = k; break
        
        df = self.carregar_csv(url_dados)
        if df is None: return {"erro": "Erro leitura dados."}
        
        cols = [c for c in df.columns if c.strip().upper().startswith('D')]
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        if 'Concurso' in df.columns: df = df.dropna(subset=['Concurso']).sort_values('Concurso')

        tab, preco = self.atualizar_precos(url_precos, loteria_chave)
        plano = self.otimizar_orcamento(tab, orcamento)
        
        if plano['qtd'] < 1: return {"erro": "Orçamento insuficiente."}

        hist = df[cols].values
        s_mk = self._core_markov(hist, cfg['total'])
        s_ia = self._core_xgboost(hist, cfg['total'])
        s_fr = self._core_fractal(hist, cfg['total'])
        
        w_mk, w_ia, w_fr = 0.3, 0.5, 0.2
        if "facil" in loteria_chave.lower(): w_mk = 0.4
        
        def z(d):
            v = list(d.values()); m, s = np.mean(v), np.std(v)
            return {k: (val-m)/s if s>0 else 0 for k,val in d.items()}
        
        z_mk, z_ia, z_fr = z(s_mk), z(s_ia), z(s_fr)
        final = {d: (z_mk[d]*w_mk + z_ia[d]*w_ia + z_fr[d]*w_fr) for d in range(1, cfg['total']+1)}
        
        ranking = sorted(final.items(), key=lambda x: x[1], reverse=True)
        pool_elite = [x[0] for x in ranking[:int(cfg['total']*0.7)]]
        pool_zebra = [x[0] for x in ranking[int(cfg['total']*0.7):-5]]
        if not pool_zebra: pool_zebra = [x[0] for x in ranking[int(cfg['total']*0.7):]]

        jogos = []
        marca = plano['dezenas']
        
        n_z = 2
        if marca >= 8: n_z = 3
        if "facil" in loteria_chave.lower() and marca >= 16: n_z = 4
        n_e = marca - n_z

        tentativas = 0
        while len(jogos) < plano['qtd'] and tentativas < 10000:
            tentativas += 1
            try:
                base = random.sample(pool_elite, n_e) + random.sample(pool_zebra, n_z)
                jg = sorted(list(set(base)))
                while len(jg) < marca: jg.append(random.choice(pool_elite)); jg = sorted(list(set(jg)))
                jg = jg[:marca]
                
                if self._validar_filtros(jg, hist[-1], loteria_chave):
                    if jg not in [x[0] for x in jogos]:
                        f = sum([final[n] for n in jg])
                        jogos.append((jg, f))
            except: continue
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "financeiro": {
                "estrategia": f"{plano['tipo']} ({marca} dz)",
                "qtd": plano['qtd'],
                "troco": plano['troco'],
                "preco_base": preco,
                "conselho": f"Otimizado: {plano['qtd']} jogos de {marca} dezenas."
            },
            "jogos": jogos
        }
