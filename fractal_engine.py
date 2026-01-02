# fractal_engine.py
import pandas as pd
import numpy as np
import xgboost as xgb
import random
import warnings
import meus_links
from fractal_learner import FractalLearner

warnings.filterwarnings("ignore")

class FractalVCerebro:
    def __init__(self):
        self.sistema = "FractalV"
        self.versao = "5.0 (Neural Link)"
        
        # Inicia a Memória
        self.learner = FractalLearner()
        pesos_vivos = self.learner.get_pesos_formatados()

        self.mapa_links = {
            "Lotofacil": "Lotofácil",
            "Mega_Sena": "Mega Sena",
            "Quina": "Quina",
            "Dia_de_Sorte": "Dia de Sorte"
        }

        self.config_base = {
            "Lotofacil":      {"total": 25, "marca": 15},
            "Mega_Sena":      {"total": 60, "marca": 6},
            "Quina":          {"total": 80, "marca": 5},
            "Dia_de_Sorte":   {"total": 31, "marca": 7},
        }
        
        # Catálogo com APRENDIZADO VIVO
        self.modelos_catalogo = {
            "Aprendizado_Vivo":   {"w_mk": pesos_vivos['w_mk'], "w_fr": pesos_vivos['w_fr'], "w_ia": pesos_vivos['w_ia'], "desc": "Evolução contínua baseada em resultados"},
            "Tendencia_Linear":   {"w_mk": 0.6, "w_ia": 0.3, "w_fr": 0.1, "desc": "Segue repetições (Markov Dominante)"},
            "Reversao_Fractal":   {"w_mk": 0.1, "w_ia": 0.3, "w_fr": 0.6, "desc": "Caça anomalias/Gaps (Z-Score)"},
            "Hibrido_Balanceado": {"w_mk": 0.3, "w_ia": 0.4, "w_fr": 0.3, "desc": "Equilíbrio entre Fluxo e Caos"},
            "IA_Preditiva":       {"w_mk": 0.0, "w_ia": 1.0, "w_fr": 0.0, "desc": "Apenas Machine Learning (XGBoost)"}
        }

    def carregar_base(self, loteria_chave):
        nome_no_link = self.mapa_links.get(loteria_chave)
        if not nome_no_link: return None, None
        
        url = meus_links.URLS.get(nome_no_link)
        
        try:
            df = pd.read_csv(url)
            cols = [c for c in df.columns if c.strip().upper().startswith('D') or c.strip().upper().startswith('B')]
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            if 'Concurso' in df.columns:
                df = df.dropna(subset=['Concurso'])
                df = df.sort_values(by='Concurso', ascending=True).reset_index(drop=True)
            return df, cols
        except Exception as e:
            return None, None
        
    def _core_markov(self, hist, total):
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
            if atraso_atual == 0: prob = max(prob, 0.45) 
            scores[d] = prob
        return scores

    def calibrar_sistema(self, loteria_chave, janela_analise=10):
        cfg = self.config_base.get(loteria_chave)
        if not cfg: return "Hibrido_Balanceado", 0.0
        
        df, cols = self.carregar_base(loteria_chave) 
        if df is None or len(df) < janela_analise + 50: 
            return "Hibrido_Balanceado", 0.0

        hist_full = df[cols].values
        placar = {k: 0 for k in self.modelos_catalogo.keys()}
        
        # Backtest
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
        
        # APRENDIZADO: Atualiza a memória com o vencedor
        self.learner.regenerar_pesos(melhor_modelo)
        
        # Atualiza catálogo interno para refletir o aprendizado imediato
        self.modelos_catalogo["Aprendizado_Vivo"].update(self.learner.get_pesos_formatados())

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
        df, cols = self.carregar_base(loteria_chave)
        hist = df[cols].values
        
        s_mk = self._core_markov(hist, cfg['total'])
        s_ia = self._core_xgboost(hist, cfg['total'])
        s_fr = self._core_fractal(hist, cfg['total'])
        
        final = {d: (s_mk[d]*pesos['w_mk'] + s_ia[d]*pesos['w_ia'] + s_fr[d]*pesos['w_fr']) 
                 for d in range(1, cfg['total']+1)}
        
        ranking = sorted(final.items(), key=lambda x: x[1], reverse=True)
        pool_elite = [x[0] for x in ranking[:int(cfg['total']*0.65)]]
        
        if "Reversao" in modelo_nome:
            zebras = sorted(s_fr.items(), key=lambda x: x[1], reverse=True)
            for z in zebras[:3]:
                if z[0] not in pool_elite: pool_elite.append(z[0])

        qtd_jogos = max(1, int(orcamento // 3.00))
        jogos = []
        
        attempts = 0
        while len(jogos) < qtd_jogos and attempts < 1000:
            attempts += 1
            try: jg = sorted(random.sample(pool_elite, cfg['marca']))
            except: jg = sorted(list(range(1, cfg['marca']+1)))
            
            if jg not in [x[0] for x in jogos]:
                f = sum([final[n] for n in jg])
                jogos.append((jg, f))
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "modelo_utilizado": modelo_nome,
            "jogos": jogos,
            "total_investido": qtd_jogos * 3.00,
            "troco": orcamento - (qtd_jogos * 3.00)
        }
