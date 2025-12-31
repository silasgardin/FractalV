# oraculo_motor.py - V33 Dynamic Pricing
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import random
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V33 (Dynamic Pricing)"
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
        
        # Multiplicadores Combinatórios (Regra Matemática Imutável)
        # Ex: Jogar 7 numeros na Mega custa 7x o preço base. Jogar 8 custa 28x.
        self.multiplicadores = {
            "Mega_Sena":      {6: 1, 7: 7, 8: 28, 9: 84, 10: 210},
            "Mega_da_Virada": {6: 1, 7: 7, 8: 28, 9: 84},
            "Lotofacil":      {15: 1, 16: 16, 17: 136, 18: 816},
            "Quina":          {5: 1, 6: 6, 7: 21, 8: 56, 9: 126},
            "Dia_de_Sorte":   {7: 1, 8: 8, 9: 36, 10: 120},
            "Dupla_Sena":     {6: 1, 7: 7, 8: 28, 9: 84},
            "Timemania":      {10: 1}, # Timemania é fixa
            "Lotomania":      {50: 1}  # Lotomania é fixa
        }

    def carregar_csv(self, url):
        try:
            df = pd.read_csv(url)
            return df
        except: return None

    def _tratar_preco(self, valor_str):
        """Converte 'R$ 6,00' para float 6.00"""
        try:
            if isinstance(valor_str, (int, float)): return float(valor_str)
            clean = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def atualizar_precos(self, url_precos, loteria_chave):
        """Busca o preço base na planilha e gera a tabela de combos"""
        df = self.carregar_csv(url_precos)
        preco_base = 0.0
        
        # Padrão Fallback (caso a planilha falhe)
        fallback = 3.00
        
        if df is not None:
            # Procura a linha da loteria (ex: 'Mega Sena')
            for _, row in df.iterrows():
                nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace(' ','_')
                chave_busca = loteria_chave.lower()
                
                # Matching flexível (ex: 'mega_sena' encontra 'mega_sena' ou 'mega')
                if chave_busca in nome_csv or nome_csv in chave_busca:
                    preco_base = self._tratar_preco(row[1])
                    break
        
        if preco_base <= 0: preco_base = fallback
        
        # Gera tabela de preços reais (Base x Multiplicador)
        tabela_atualizada = {}
        
        # Encontra a chave de multiplicadores correta
        chave_mult = None
        for k in self.multiplicadores.keys():
            if k.lower() in loteria_chave.lower(): chave_mult = k; break
            
        if chave_mult:
            mults = self.multiplicadores[chave_mult]
            tabela_atualizada = {qtd: (fator * preco_base) for qtd, fator in mults.items()}
        else:
            # Se não tiver multiplicador (ex: Loteria nova), assume aposta simples
            base = self.config_base.get(loteria_chave, {}).get('marca_base', 6)
            tabela_atualizada = {base: preco_base}
            
        return tabela_atualizada, preco_base

    # ... [MÉTODOS MATEMÁTICOS _core_markov, _core_xgboost, _core_fractal MANTIDOS IGUAIS] ...
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
            model = GradientBoostingClassifier(n_estimators=30, max_depth=3)
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

    def otimizar_orcamento_dinamico(self, tabela_precos, orcamento):
        """Define estratégia com base nos preços ATUALIZADOS da planilha"""
        base_dezenas = min(tabela_precos.keys())
        melhor_escolha = base_dezenas
        qtd_final = int(orcamento // tabela_precos[base_dezenas])
        
        # Tenta upgrade para combo
        for dezenas in sorted(tabela_precos.keys(), reverse=True):
            preco = tabela_precos[dezenas]
            qtd_possivel = int(orcamento // preco)
            
            if qtd_possivel >= 1:
                # Regra de Segurança: Só faz combo se der pra fazer minimo de jogos
                min_jogos = 1
                if dezenas > base_dezenas: min_jogos = 2 # Combo pede pelo menos 2 jogos
                
                if qtd_possivel >= min_jogos:
                    melhor_escolha = dezenas
                    qtd_final = qtd_possivel
                    break
        
        custo = tabela_precos[melhor_escolha]
        troco = orcamento - (qtd_final * custo)
        tipo = "Combo" if melhor_escolha > base_dezenas else "Simples"
        
        return {"tipo": tipo, "dezenas": melhor_escolha, "qtd": qtd_final, "troco": troco}

    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        # 1. Config e Carga
        cfg = self.config_base.get(loteria_chave)
        if not cfg:
             for k, v in self.config_base.items():
                if loteria_chave.lower() in k.lower(): cfg = v; loteria_chave = k; break
        
        df = self.carregar_csv(url_dados)
        if df is None: return {"erro": "Erro leitura dados."}
        
        # Tratamento Colunas
        cols = [c for c in df.columns if c.strip().upper().startswith('D')]
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
        if 'Concurso' in df.columns: df = df.dropna(subset=['Concurso']).sort_values('Concurso')

        # 2. Atualização de Preços (INTEGRAÇÃO VLR_JOGO.CSV)
        tabela_atualizada, preco_base = self.atualizar_precos(url_precos, loteria_chave)
        
        # 3. Planejamento Financeiro
        plano = self.otimizar_orcamento_dinamico(tabela_atualizada, orcamento)
        if plano['qtd'] < 1: 
             return {"erro": f"Orçamento insuficiente. Aposta mínima: R$ {tabela_atualizada[min(tabela_atualizada.keys())]:.2f}"}

        # 4. Matemática Fractal V33
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
        
        jogos = []
        marca = plano['dezenas']
        tentativas = 0
        
        while len(jogos) < plano['qtd'] and tentativas < 5000:
            tentativas += 1
            try: jg = sorted(random.sample(pool_elite, marca))
            except: jg = sorted(list(range(1, marca+1)))
            
            if jg not in [x[0] for x in jogos]:
                f = sum([final[n] for n in jg])
                jogos.append((jg, f))
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "financeiro": {
                "estrategia": f"{plano['tipo']} ({marca} dz)",
                "qtd": plano['qtd'],
                "troco": plano['troco'],
                "preco_base": preco_base,
                "conselho": f"Com R$ {orcamento:.2f} e a aposta base a R$ {preco_base:.2f}, o melhor é fazer {plano['qtd']} jogos de {marca} dezenas."
            },
            "jogos": jogos
        }
