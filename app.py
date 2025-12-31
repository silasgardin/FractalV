# oraculo_motor.py - V33 Ultimate (Financial + Fractal + Filters)
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import random
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V33 (Ultimate Architect)"
        self.config_base = {
            "Lotofacil":      {"total": 25, "marca_base": 15},
            "Mega_Sena":      {"total": 60, "marca_base": 6},
            "Quina":          {"total": 80, "marca_base": 5},
            "Dia_de_Sorte":   {"total": 31, "marca_base": 7},
            "Timemania":      {"total": 80, "marca_base": 10},
            "Dupla_Sena":     {"total": 50, "marca_base": 6},
            "Lotomania":      {"total": 100,"marca_base": 50}
        }
        
        self.tabela_precos = {
            "Mega_Sena": {6: 5.00, 7: 35.00, 8: 140.00, 9: 420.00},
            "Lotofacil": {15: 3.00, 16: 48.00, 17: 408.00},
            "Quina": {5: 2.50, 6: 15.00, 7: 52.50, 8: 140.00},
            "Dia_de_Sorte": {7: 2.50, 8: 20.00, 9: 90.00},
            "Dupla_Sena": {6: 2.50, 7: 17.50, 8: 70.00}
        }

    def carregar_base_cloud(self, url_csv):
        try:
            df = pd.read_csv(url_csv)
            cols = [c for c in df.columns if c.strip().upper().startswith('D')]
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            if 'Concurso' in df.columns:
                df = df.dropna(subset=['Concurso'])
                df = df.sort_values(by='Concurso', ascending=True).reset_index(drop=True)
            return df, cols
        except: return None, None

    # --- MOTORES (MANTIDOS) ---
    def _core_markov(self, hist, total):
        matriz = np.zeros((total + 1, total + 1))
        recorte = hist[-100:]
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
        scores = {}
        recorte = hist[-50:]
        for d in range(1, total+1):
            series = [1 if d in row else 0 for row in recorte]
            if len(series) < 5: scores[d] = 0.5; continue
            flips = sum(1 for i in range(1, len(series)) if series[i] != series[i-1])
            flip_ratio = flips / (len(series) - 1)
            scores[d] = flip_ratio if series[-1] == 0 else 1.0 - flip_ratio
        return scores

    # --- NOVO: FILTROS DINÂMICOS (V30 RESGATADA) ---
    def _validar_jogo(self, jg, last_draw, loteria_chave):
        """Aplica filtros físicos dependendo do jogo."""
        soma = sum(jg)
        
        # 1. Filtro Soma (Gauss)
        if "facil" in loteria_chave.lower():
            # Lotofacil: Soma varia conforme qtd de dezenas
            media_esperada = len(jg) * 13 # media do numero 1 a 25 é 13
            margem = 30
            if not (media_esperada - margem <= soma <= media_esperada + margem): return False
            
            # Repetição (Crucial para Loto)
            rep = len(set(jg).intersection(set(last_draw)))
            # Se jogo for padrão (15), exige 8-11. Se for maior, aceita mais.
            min_rep = 8 + (len(jg) - 15)
            max_rep = 11 + (len(jg) - 15)
            if not (min_rep <= rep <= max_rep): return False

        elif "mega" in loteria_chave.lower():
            if not (140 <= soma <= 240): return False # Padrão Mega
            
            # Quadrantes
            q1 = len([n for n in jg if n <= 15])
            if q1 > (len(jg) / 2): return False # Muita aglomeração
            
        elif "dia" in loteria_chave.lower():
             if not (80 <= soma <= 150): return False

        return True

    def otimizar_orcamento(self, loteria_chave, orcamento):
        # ... (Mesma lógica V33 anterior) ...
        chave = None
        for k in self.tabela_precos.keys():
            if k.lower() in loteria_chave.lower(): chave = k; break
        if not chave:
            base = self.config_base.get(loteria_chave, {}).get('marca_base', 0) or 6
            preco = 3.00
            return {"tipo": "Simples", "dezenas": base, "qtd": int(orcamento//preco), "custo_unit": preco, "troco": orcamento%preco}

        opcoes = self.tabela_precos[chave]
        base_dezenas = min(opcoes.keys())
        melhor_escolha = base_dezenas
        qtd_final = int(orcamento // opcoes[base_dezenas])
        
        for dezenas in sorted(opcoes.keys(), reverse=True):
            preco = opcoes[dezenas]
            qtd_possivel = int(orcamento // preco)
            if qtd_possivel >= 1:
                fator_risco = 1
                if dezenas == base_dezenas + 1: fator_risco = 3
                if dezenas == base_dezenas + 2: fator_risco = 2
                if qtd_possivel >= fator_risco:
                    melhor_escolha = dezenas; qtd_final = qtd_possivel; break
        
        return {
            "tipo": "Combo" if melhor_escolha > base_dezenas else "Simples",
            "dezenas": melhor_escolha,
            "qtd": qtd_final,
            "custo_unit": opcoes[melhor_escolha],
            "troco": orcamento - (qtd_final * opcoes[melhor_escolha])
        }

    def gerar_palpite_cloud(self, url_dados, loteria_chave, preco_aposta_ignorado, orcamento):
        cfg = self.config_base.get(loteria_chave)
        if not cfg:
             for k, v in self.config_base.items():
                if loteria_chave.lower() in k.lower(): cfg = v; loteria_chave = k; break
        if not cfg: return {"erro": "Loteria não suportada"}

        df, cols = self.carregar_base_cloud(url_dados)
        if df is None: return {"erro": "Erro leitura Planilha"}

        plano = self.otimizar_orcamento(loteria_chave, orcamento)
        if plano['qtd'] < 1: return {"erro": "Orçamento insuficiente."}

        # Matemática
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
        
        # --- LÓGICA DE POOLS RESTAURADA (V29) ---
        ranking = sorted(final.items(), key=lambda x: x[1], reverse=True)
        
        # Elite: Top 60%
        corte_elite = int(cfg['total'] * 0.60)
        pool_elite = [x[0] for x in ranking[:corte_elite]]
        
        # Zebra: Bottom 40% (mas excluindo os 5 piores absolutos que nunca saem)
        pool_zebra = [x[0] for x in ranking[corte_elite:-5]] 
        if not pool_zebra: pool_zebra = [x[0] for x in ranking[corte_elite:]]

        jogos = []
        marca = plano['dezenas']
        
        # Define quantas zebras entram
        # Se for jogo combo (muitas dezenas), permite mais zebras
        qtd_zebras = 2
        if marca > cfg['marca_base'] + 1: qtd_zebras = 3
        if "facil" in loteria_chave.lower(): qtd_zebras = 3 if marca >= 16 else 2
        
        qtd_elite = marca - qtd_zebras
        last_draw = hist[-1]

        tentativas = 0
        while len(jogos) < plano['qtd'] and tentativas < 20000:
            tentativas += 1
            
            # Mistura Elite + Zebra (O Retorno do Caos)
            try:
                part_e = random.sample(pool_elite, qtd_elite)
                part_z = random.sample(pool_zebra, qtd_zebras)
                jg = sorted(list(set(part_e + part_z)))
            except:
                jg = sorted(random.sample(list(final.keys()), marca))
            
            # Completa se faltar (caso haja duplicatas na fusão, raro)
            while len(jg) < marca:
                jg.append(random.choice(pool_elite))
                jg = sorted(list(set(jg)))
            
            # Filtros Especialistas (V30)
            if self._validar_jogo(jg, last_draw, loteria_chave):
                if jg not in [x[0] for x in jogos]:
                    f = sum([final[n] for n in jg])
                    jogos.append((jg, f))
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "financeiro": {
                "estrategia": f"{plano['tipo']} ({marca} dz)",
                "qtd": plano['qtd'],
                "troco": plano['troco'],
                "conselho": f"V33 Ultimate: {plano['qtd']} jogos de {marca} dezenas (Com Filtros e Zebras)."
            },
            "jogos": jogos
        }
