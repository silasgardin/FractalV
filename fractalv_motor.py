# ==============================================================================
# 🌀 FRACTAL V - MOTOR ADAPTATIVO V4.1
# ==============================================================================
import pandas as pd
import numpy as np
import xgboost as xgb
import random
import warnings

warnings.filterwarnings("ignore")

class FractalVCerebro:
    def __init__(self):
        self.sistema = "FractalV"
        self.versao = "4.1 (Adaptive Hive)"
        
        # Configuração das Bases de Dados
        self.config_base = {
            "Lotofacil":      {"total": 25, "marca": 15, "csv": "Oraculo_DB_Master - Lotofacil.csv"},
            "Mega_Sena":      {"total": 60, "marca": 6,  "csv": "Oraculo_DB_Master - Mega_Sena.csv"},
            "Quina":          {"total": 80, "marca": 5,  "csv": "Oraculo_DB_Master - Quina.csv"},
            "Dia_de_Sorte":   {"total": 31, "marca": 7,  "csv": "Oraculo_DB_Master - Dia_de_Sorte.csv"},
        }
        
        # Catálogo de Algoritmos do FractalV
        self.modelos_catalogo = {
            "Tendencia_Linear":   {"w_mk": 0.6, "w_ia": 0.3, "w_fr": 0.1, "desc": "Segue repetições (Markov Dominante)"},
            "Reversao_Fractal":   {"w_mk": 0.1, "w_ia": 0.3, "w_fr": 0.6, "desc": "Caça anomalias/Gaps (Z-Score)"},
            "Hibrido_Balanceado": {"w_mk": 0.3, "w_ia": 0.4, "w_fr": 0.3, "desc": "Equilíbrio entre Fluxo e Caos"},
            "IA_Preditiva":       {"w_mk": 0.0, "w_ia": 1.0, "w_fr": 0.0, "desc": "Apenas Machine Learning (XGBoost)"}
        }

    def carregar_base(self, caminho_arquivo):
        try:
            try: df = pd.read_csv(caminho_arquivo)
            except: df = pd.read_csv(caminho_arquivo, encoding='latin1')
            cols = [c for c in df.columns if c.strip().upper().startswith('D')]
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            if 'Concurso' in df.columns:
                df = df.dropna(subset=['Concurso'])
                df = df.sort_values(by='Concurso', ascending=True).reset_index(drop=True)
            return df, cols
        except: return None, None
        
    def _core_markov(self, hist, total):
        # Lógica de Cadeias de Markov (Probabilidade de Transição)
        matriz = np.zeros((total + 1, total + 1))
        recorte = hist[-100:] 
        for i in range(len(recorte)-1):
            for u in recorte[i]:
                if pd.isna(u): continue
                for v in recorte[i+1]:
                    if pd.isna(v): continue
                    matriz[int(u)][int(v)] += 1
        row_sums = matriz.sum(axis=1)
        row_sums[row_sums==0] = 1
        probs = matriz / row_sums[:, None]
        last = hist[-1]
        scores = {}
        for d in range(1, total+1):
            s = 0; c = 0
            for n in last:
                if not pd.isna(n): s += probs[int(n)][d]; c += 1
            scores[d] = s/c if c > 0 else 0
        return scores

    def _core_xgboost(self, hist, total):
        # Lógica de Machine Learning (Classificação Binária)
        X, y = [], []
        atrasos = {d: 0 for d in range(1, total+1)}
        start = max(0, len(hist)-80)
        for i in range(start, len(hist)-1):
            p, c = hist[i], hist[i+1]
            for d in range(1, total+1):
                saiu = 1 if d in p else 0
                atr = atrasos[d]
                if d in c or atr > 5 or i%3==0:
                    X.append([d, saiu, atr])
                    y.append(1 if d in c else 0)
                atrasos[d] = 0 if d in p else atrasos[d]+1
        scores = {}
        try:
            model = xgb.XGBClassifier(n_estimators=50, max_depth=3, verbosity=0)
            model.fit(np.array(X), np.array(y))
            last = hist[-1]
            for d in range(1, total+1):
                saiu = 1 if d in last else 0
                atr = atrasos[d]
                scores[d] = model.predict_proba(np.array([[d, saiu, atr]]))[0][1]
        except: scores = {d: 0.5 for d in range(1, total+1)}
        return scores

    def _core_fractal(self, hist, total):
        # Lógica FractalV (Z-Score de Gaps Temporais)
        scores = {}
        recorte = hist[-100:]
        
        gaps_history = {d: [] for d in range(1, total+1)}
        current_delay = {d: 0 for d in range(1, total+1)}
        
        for row in recorte:
            row_set = set(row)
            for d in range(1, total+1):
                if d in row_set:
                    if current_delay[d] > 0: gaps_history[d].append(current_delay[d])
                    current_delay[d] = 0
                else:
                    current_delay[d] += 1
                    
        for d in range(1, total+1):
            gaps = gaps_history[d]
            atraso_atual = current_delay[d]
            if len(gaps) < 2:
                scores[d] = 0.5
                continue
            media_gap = np.mean(gaps)
            std_gap = np.std(gaps)
            if std_gap == 0: std_gap = 1
            
            z_score = (atraso_atual - media_gap) / std_gap
            prob = 1 / (1 + np.exp(-z_score)) 
            if atraso_atual == 0: prob = max(prob, 0.45) # Proteção Markoviana
            scores[d] = prob
        return scores

    # --- AUTO-ADAPTAÇÃO (O Cérebro do FractalV) ---
    def calibrar_sistema(self, loteria_chave, janela_analise=10):
        """
        Analisa os últimos jogos para decidir qual configuração matemática
        está perfomando melhor neste momento para esta loteria específica.
        """
        cfg = self.config_base.get(loteria_chave)
        if not cfg: return "Hibrido_Balanceado", 0.0
        
        df, cols = self.carregar_base(cfg['csv'])
        if df is None or len(df) < janela_analise + 50: 
            return "Hibrido_Balanceado", 0.0

        hist_full = df[cols].values
        placar = {k: 0 for k in self.modelos_catalogo.keys()}
        
        # Backtest Rápido
        for i in range(janela_analise):
            idx_teste = -(i + 1)
            target = set(hist_full[idx_teste])
            hist_treino = hist_full[:idx_teste]
            
            s_mk = self._core_markov(hist_treino, cfg['total'])
            s_ia = self._core_xgboost(hist_treino, cfg['total'])
            s_fr = self._core_fractal(hist_treino, cfg['total'])
            
            for nome_mod, pesos in self.modelos_catalogo.items():
                w_mk, w_ia, w_fr = pesos['w_mk'], pesos['w_ia'], pesos['w_fr']
                final = {d: (s_mk[d]*w_mk + s_ia[d]*w_ia + s_fr[d]*w_fr) for d in range(1, cfg['total']+1)}
                ranking = sorted(final.items(), key=lambda x: x[1], reverse=True)
                palpite_top = set([x[0] for x in ranking[:cfg['marca']]])
                acertos = len(palpite_top.intersection(target))
                placar[nome_mod] += acertos

        melhor_modelo = max(placar, key=placar.get)
        media_acertos = placar[melhor_modelo] / janela_analise
        return melhor_modelo, media_acertos

    def info_card(self, loteria_chave):
        modelo_vencedor, acertos_medios = self.calibrar_sistema(loteria_chave)
        desc_modelo = self.modelos_catalogo[modelo_vencedor]['desc']
        preco = 3.00
        if loteria_chave == "Mega_Sena": preco = 5.00
        elif loteria_chave == "Quina": preco = 2.50
        
        return {
            "loteria": loteria_chave,
            "modelo_ativo": modelo_vencedor,
            "descricao": desc_modelo,
            "performance_recente": f"{acertos_medios:.1f} (Méd. 10 jogos)",
            "preco_aposta": preco
        }

    def processar_jogos(self, loteria_chave, orcamento):
        modelo_nome, _ = self.calibrar_sistema(loteria_chave)
        pesos = self.modelos_catalogo[modelo_nome]
        
        cfg = self.config_base.get(loteria_chave)
        df, cols = self.carregar_base(cfg['csv'])
        hist = df[cols].values
        
        s_mk = self._core_markov(hist, cfg['total'])
        s_ia = self._core_xgboost(hist, cfg['total'])
        s_fr = self._core_fractal(hist, cfg['total'])
        
        final = {d: (s_mk[d]*pesos['w_mk'] + s_ia[d]*pesos['w_ia'] + s_fr[d]*pesos['w_fr']) 
                 for d in range(1, cfg['total']+1)}
        
        ranking = sorted(final.items(), key=lambda x: x[1], reverse=True)
        pool_elite = [x[0] for x in ranking[:int(cfg['total']*0.65)]]
        
        # Adiciona Zebras do Fractal se o modelo atual for Reversão
        if "Reversao" in modelo_nome:
            zebras = sorted(s_fr.items(), key=lambda x: x[1], reverse=True)
            for z in zebras[:3]:
                if z[0] not in pool_elite: pool_elite.append(z[0])

        qtd_jogos = max(1, int(orcamento // 3.00))
        jogos = []
        
        for _ in range(qtd_jogos * 50):
            if len(jogos) >= qtd_jogos: break
            try: jg = sorted(random.sample(pool_elite, cfg['marca']))
            except: jg = sorted(list(range(1, cfg['marca']+1)))
            if jg not in [x[0] for x in jogos]:
                f = sum([final[n] for n in jg])
                jogos.append((jg, f))
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "modelo_utilizado": modelo_nome,
            "jogos": jogos,
            "total_investido": qtd_jogos * 3.00, # Simplificado
            "troco": orcamento - (qtd_jogos * 3.00)
        }
