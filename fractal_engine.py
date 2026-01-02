# fractal_engine.py
import numpy as np
import xgboost as xgb
import random
import warnings
from fractal_learner import FractalLearner
from fractal_connector import FractalConnector # <--- Usa o conector novo

warnings.filterwarnings("ignore")

class FractalVCerebro:
    def __init__(self):
        self.sistema = "FractalV"
        self.versao = "5.1 (Data Fusion)"
        
        self.learner = FractalLearner()
        pesos_vivos = self.learner.get_pesos_formatados()
        
        # Instancia o conector para carregar dados# ==============================================================================
# 🧠 FRACTAL MOTOR V3.3 - ENTROPY CORE
# ==============================================================================
import pandas as pd
import numpy as np
import random
import google.generativeai as genai
import warnings
import fractal_learner
import math

warnings.filterwarnings("ignore")

class FractalCerebro:
    def __init__(self):
        self.versao = "FractalV 3.3 (Entropy Core)"
        self.learner = fractal_learner.FractalLearner()
        
        self.config_base = {
            "Lotofacil": {"total": 25, "marca_base": 15}, "Mega_Sena": {"total": 60, "marca_base": 6},
            "Quina": {"total": 80, "marca_base": 5}, "Dia_de_Sorte": {"total": 31, "marca_base": 7},
            "Timemania": {"total": 80, "marca_base": 10}, "Dupla_Sena": {"total": 50, "marca_base": 6},
            "Lotomania": {"total": 100,"marca_base": 50}, "Mega_da_Virada": {"total": 60, "marca_base": 6}
        }

    # --- NOVO MOTOR DE CÁLCULO DE ENTROPIA REAL ---
    def _calcular_entropia_real(self, jogo, total_dezenas):
        """
        Calcula a 'Entropia Interna' do jogo baseada em 3 fatores:
        1. Espalhamento (Desvio Padrão das distâncias).
        2. Equilíbrio de Paridade (Entropia de Shannon binária).
        3. Centro de Gravidade (Distância da Soma Média).
        Retorna um float entre 0.0 (Ordem Total) e 1.0 (Caos Fractal).
        """
        try:
            jogo = sorted(jogo)
            if len(jogo) < 2: return 0.5
            
            # 1. Análise de Gaps (Espalhamento)
            gaps = np.diff(jogo)
            std_gaps = np.std(gaps)
            # Normalização grosseira: quanto menor o desvio, mais "regular" (entropia baixa)
            fator_espalhamento = 1.0 / (1.0 + std_gaps) 

            # 2. Equilíbrio Par/Ímpar (Shannon)
            pares = len([n for n in jogo if n % 2 == 0])
            ratio = pares / len(jogo)
            if ratio == 0 or ratio == 1: shannon_parity = 0
            else:
                # Fórmula de Entropia de Shannon Binária
                shannon_parity = - (ratio * math.log2(ratio) + (1-ratio) * math.log2(1-ratio))

            # 3. Centro de Gravidade (Soma)
            soma_real = sum(jogo)
            soma_ideal = (len(jogo) * (total_dezenas + 1)) / 2
            distancia_soma = abs(soma_real - soma_ideal)
            fator_soma = 1.0 - (distancia_soma / soma_ideal) # 1.0 se for perfeito na média

            # ENTROPIA FINAL PONDERADA (Pesos Intrínsecos do FractalV)
            # Damos mais peso ao Shannon (Equilíbrio) e Espalhamento
            entropia_final = (shannon_parity * 0.5) + ((1 - fator_espalhamento) * 0.3) + (fator_soma * 0.2)
            
            return max(0.0, min(1.0, entropia_final))
            
        except: return 0.5

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
        if len(hist) < 5: return "Padrão Fractal", {}, False
        scores = {"Markov": 0, "Fractal": 0, "Gauss": 0}
        try:
            teste = hist[-5:]
            for i in range(len(teste)-1):
                passado = set([int(x) for x in teste[i] if pd.notna(x)])
                futuro = set([int(x) for x in teste[i+1] if pd.notna(x)])
                
                scores["Markov"] += len(passado.intersection(futuro))
                ausentes = set(range(1, total_dezenas+1)) - passado
                scores["Fractal"] += len(ausentes.intersection(futuro))
                
                meio = total_dezenas // 2
                gauss_zone = set(range(meio-5, meio+6))
                scores["Gauss"] += len(gauss_zone.intersection(futuro))
        except: pass
        
        vencedora = max(scores, key=scores.get)
        aprendeu, quem = self.learner.regenerar_pesos(vencedora)
        return vencedora, scores, aprendeu

    def analisar_com_gemini(self, api_key, modelo_escolhido, loteria, dados_fin, jogos_top3, backtest_info):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(modelo_escolhido)
            
            vencedora = backtest_info.get('vencedora', 'Padrão')
            pesos = self.learner.get_pesos()
            
            # Pega a Entropia calculada do primeiro jogo
            entropia_calc = jogos_top3[0][2] # Índice 2 agora é a entropia
            
            prompt = f"""
            Atue como o Núcleo FractalV (V3.3).
            Analise estes dados de loteria ({loteria}).
            
            DADOS TÉCNICOS CALCULADOS:
            1. Estratégia Vencedora (Backtest): {vencedora}
            2. Índice de Entropia Fractal (Calculado): {entropia_calc:.4f} (Escala 0.0 a 1.0)
            3. Jogo Gerado: {jogos_top3[0][0]}
            
            Responda em Português:
            - O que o valor de Entropia {entropia_calc:.4f} diz sobre este jogo? (Está equilibrado ou arriscado?)
            - Como a estratégia '{vencedora}' foi aplicada aqui?
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e: return f"⚠️ Erro IA: {str(e)}"

    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        cfg = self.config_base.get(loteria_chave, self.config_base["Mega_Sena"])
        
        df = self.carregar_csv(url_dados)
        hist = []
        last_concurso_id = 0
        if df is not None:
            try:
                cols = [c for c in df.columns if c.strip().upper().startswith('D')]
                for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
                df = df.dropna(subset=['Concurso']).sort_values('Concurso')
                hist = df[cols].values
                last_concurso_id = int(df['Concurso'].iloc[-1])
            except: pass

        vencedora, scores, aprendeu = self.executar_backtest(hist, cfg['total'])
        fin = self.calcular_limite_jogos(url_precos, loteria_chave, orcamento)
        fin['orcamento_inicial'] = orcamento
        pesos_vivos = self.learner.get_pesos()

        seed_val = f"FractalV3.3_{loteria_chave}_{last_concurso_id}_{vencedora}_{fin['qtd']}"
        random.seed(seed_val) 
        
        jogos = []
        marca = cfg['marca_base']
        pool = list(range(1, cfg['total'] + 1))
        last_draw = [int(x) for x in hist[-1] if pd.notna(x)] if len(hist) > 0 else []

        tentativas = 0
        while len(jogos) < fin['qtd'] and tentativas < 3000:
            tentativas += 1
            try:
                fator_markov = pesos_vivos.get("Markov", 0.4)
                
                if len(last_draw) > 5:
                    q_rep = int(marca * fator_markov)
                    jg = random.sample(last_draw, min(len(last_draw), q_rep))
                    restantes = [n for n in pool if n not in jg]
                    jg += random.sample(restantes, marca - len(jg))
                else:
                    jg = random.sample(pool, marca)
                
                jg = sorted([int(n) for n in jg])
                
                if jg not in [x[0] for x in jogos]:
                    # CÁLCULO DA ENTROPIA REAL
                    entropia = self._calcular_entropia_real(jg, cfg['total'])
                    
                    # Filtro de Qualidade Fractal: Só aceita jogos com entropia saudável
                    # (Nem muito ordenado, nem caos total)
                    if entropia < 0.35 or entropia > 0.95:
                        continue 
                        
                    # Score baseado na Entropia + Aprendizado
                    score = (entropia * 10) + (0.5 if aprendeu else 0)
                    
                    # Tupla: (Numeros, Score, Entropia)
                    jogos.append((jg, score, entropia))
            except: continue
            
        if not jogos:
            jg = sorted(random.sample(pool, marca))
            jogos.append((jg, 5.0, 0.5)) # Fallback

        jogos.sort(key=lambda x: x[1], reverse=True)
        random.seed(None) 
        
        return {
            "financeiro": fin, 
            "backtest": {"vencedora": vencedora, "scores": scores, "aprendeu": aprendeu, "pesos_atuais": pesos_vivos, "ultimo_concurso": last_concurso_id}, 
            "jogos": jogos
        }
        self.conector = FractalConnector()

        self.config_base = {
            "Lotofacil":      {"total": 25, "marca": 15},
            "Mega_Sena":      {"total": 60, "marca": 6},
            "Quina":          {"total": 80, "marca": 5},
            "Dia_de_Sorte":   {"total": 31, "marca": 7},
        }
        
        self.modelos_catalogo = {
            "Aprendizado_Vivo":   {"w_mk": pesos_vivos['w_mk'], "w_fr": pesos_vivos['w_fr'], "w_ia": pesos_vivos['w_ia'], "desc": "Evolução contínua baseada em resultados"},
            "Tendencia_Linear":   {"w_mk": 0.6, "w_ia": 0.3, "w_fr": 0.1, "desc": "Segue repetições (Markov Dominante)"},
            "Reversao_Fractal":   {"w_mk": 0.1, "w_ia": 0.3, "w_fr": 0.6, "desc": "Caça anomalias/Gaps (Z-Score)"},
            "Hibrido_Balanceado": {"w_mk": 0.3, "w_ia": 0.4, "w_fr": 0.3, "desc": "Equilíbrio entre Fluxo e Caos"},
            "IA_Preditiva":       {"w_mk": 0.0, "w_ia": 1.0, "w_fr": 0.0, "desc": "Apenas Machine Learning (XGBoost)"}
        }

    def _core_markov(self, hist, total):
        # (Código Markov Mantido igual)
        if len(hist) < 2: return {d:0 for d in range(1, total+1)}
        matriz = np.zeros((total + 1, total + 1))
        recorte = hist[-100:] 
        for i in range(len(recorte)-1):
            for u in recorte[i]:
                if np.isnan(u): continue
                for v in recorte[i+1]:
                    if np.isnan(v): continue
                    try: matriz[int(u)][int(v)] += 1
                    except: pass
        row_sums = matriz.sum(axis=1)
        row_sums[row_sums==0] = 1
        probs = matriz / row_sums[:, None]
        last = hist[-1]
        scores = {}
        for d in range(1, total+1):
            s = 0; c = 0
            for n in last:
                if not np.isnan(n): 
                    try: s += probs[int(n)][d]; c += 1
                    except: pass
            scores[d] = s/c if c > 0 else 0
        return scores

    def _core_xgboost(self, hist, total):
        # (Código XGBoost Mantido igual - simplificado para brevidade)
        if len(hist) < 10: return {d:0.5 for d in range(1, total+1)}
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
        # (Código Fractal Mantido igual)
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
                else: current_delay[d] += 1
        for d in range(1, total+1):
            gaps = gaps_history[d]
            atraso_atual = current_delay[d]
            if len(gaps) < 2: scores[d] = 0.5; continue
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
        
        # USA O CONECTOR PARA PEGAR DADOS FRESCOS
        hist_full, ultimo_id = self.conector.get_historico(loteria_chave)
        
        if hist_full is None or len(hist_full) < janela_analise + 50: 
            return "Hibrido_Balanceado", 0.0

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
        
        # Aprendizado
        self.learner.regenerar_pesos(melhor_modelo)
        self.modelos_catalogo["Aprendizado_Vivo"].update(self.learner.get_pesos_formatados())

        return melhor_modelo, media_acertos, ultimo_id

    def info_card(self, loteria_chave):
        modelo_vencedor, acertos_medios, ultimo_id = self.calibrar_sistema(loteria_chave)
        desc_modelo = self.modelos_catalogo[modelo_vencedor]['desc']
        
        # Pega preço atualizado
        preco = self.conector.get_preco(loteria_chave)
        
        return {
            "loteria": loteria_chave,
            "modelo_ativo": modelo_vencedor,
            "descricao": desc_modelo,
            "performance_recente": f"{acertos_medios:.1f} (Méd. 10 jogos)",
            "preco_aposta": preco,
            "ultimo_concurso": ultimo_id
        }

    def processar_jogos(self, loteria_chave, orcamento):
        modelo_nome, _, _ = self.calibrar_sistema(loteria_chave)
        pesos = self.modelos_catalogo[modelo_nome]
        
        cfg = self.config_base.get(loteria_chave)
        # USA O CONECTOR
        hist, _ = self.conector.get_historico(loteria_chave)
        
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
        
        preco_aposta = self.conector.get_preco(loteria_chave)
        qtd_jogos = max(1, int(orcamento // preco_aposta))
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
            "total_investido": qtd_jogos * preco_aposta,
            "troco": orcamento - (qtd_jogos * preco_aposta)
        }
