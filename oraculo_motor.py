# oraculo_motor.py - Versão Cloud V32 (Fixed for Streamlit)
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import random
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V32 (Cloud Advisor)"
        self.config_base = {
            "Lotofacil":      {"total": 25, "marca": 15},
            "Mega_Sena":      {"total": 60, "marca": 6},
            "Quina":          {"total": 80, "marca": 5},
            "Dia_de_Sorte":   {"total": 31, "marca": 7},
            "Timemania":      {"total": 80, "marca": 10},
            "Dupla_Sena":     {"total": 50, "marca": 6},
            "Lotomania":      {"total": 100,"marca": 50}
        }

    def carregar_base_cloud(self, url_csv):
        try:
            # Lê direto da URL do Google Sheets (formato CSV)
            df = pd.read_csv(url_csv)
            cols = [c for c in df.columns if c.strip().upper().startswith('D')]
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            # Limpeza básica
            if 'Concurso' in df.columns:
                df = df.dropna(subset=['Concurso'])
                df = df.sort_values(by='Concurso', ascending=True).reset_index(drop=True)
            return df, cols
        except Exception as e:
            return None, None

    # --- MOTORES MATEMÁTICOS ---
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
        
        last = hist[-1]
        scores = {}
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

    # --- CONSULTORIA E GERAÇÃO ---
    def gerar_palpite_cloud(self, url_dados, loteria_chave, preco_aposta, orcamento):
        cfg = self.config_base.get(loteria_chave)
        if not cfg: return {"erro": f"Loteria {loteria_chave} não suportada"}
        
        # 1. Carrega Dados da Nuvem
        df, cols = self.carregar_base_cloud(url_dados)
        if df is None: return {"erro": "Falha ao ler planilha do Google Sheets. Verifique o link."}
        
        # 2. Consultoria Financeira
        qtd_jogos = int(orcamento // preco_aposta)
        troco = orcamento % preco_aposta
        if qtd_jogos < 1: return {"erro": f"Orçamento insuficiente. Mínimo: R$ {preco_aposta:.2f}"}
        
        estrategia = "Tiro de Precisão" if qtd_jogos <= 5 else ("Cercamento Tático" if qtd_jogos <= 20 else "Hedge Massivo")
        
        # 3. Processamento Matemático
        hist = df[cols].values
        s_mk = self._core_markov(hist, cfg['total'])
        s_ia = self._core_xgboost(hist, cfg['total'])
        s_fr = self._core_fractal(hist, cfg['total'])
        
        w_mk, w_ia, w_fr = 0.3, 0.5, 0.2
        if loteria_chave == "Lotofacil": w_mk = 0.4
        
        def z(d):
            v = list(d.values()); m, s = np.mean(v), np.std(v)
            return {k: (val-m)/s if s>0 else 0 for k,val in d.items()}
            
        z_mk, z_ia, z_fr = z(s_mk), z(s_ia), z(s_fr)
        final = {d: (z_mk[d]*w_mk + z_ia[d]*w_ia + z_fr[d]*w_fr) for d in range(1, cfg['total']+1)}
        
        ranking = sorted(final.items(), key=lambda x: x[1], reverse=True)
        pool_elite = [x[0] for x in ranking[:int(cfg['total']*0.65)]]
        
        jogos = []
        tentativas = 0
        while len(jogos) < qtd_jogos and tentativas < 5000:
            tentativas += 1
            try: jg = sorted(random.sample(pool_elite, cfg['marca']))
            except: jg = sorted(list(range(1, cfg['marca']+1)))
            
            if jg not in [x[0] for x in jogos]:
                f = sum([final[n] for n in jg])
                jogos.append((jg, f))
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "financeiro": {
                "estrategia": estrategia,
                "qtd": qtd_jogos,
                "troco": troco,
                "conselho": f"Gerar {qtd_jogos} jogos focando nos melhores scores."
            },
            "jogos": jogos
        }
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        return {"financeiro": info_fin, "jogos": jogos, "motor": "V32 Cloud"}
