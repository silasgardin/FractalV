# ==============================================================================
# 🧠 FRACTAL MOTOR V4.0 - PURE MATH CORE
# ARQUIVO: fractal_motor.py
# ==============================================================================
import numpy as np
import random
import google.generativeai as genai
import warnings
import fractal_learner
import math
import pandas as pd # Apenas para manipulação de dados interna se precisar

warnings.filterwarnings("ignore")

class FractalCerebro:
    def __init__(self):
        self.versao = "FractalV 4.0 (Pure Math)"
        self.learner = fractal_learner.FractalLearner()
        
        self.config_base = {
            "Lotofacil": {"total": 25, "marca_base": 15}, "Mega_Sena": {"total": 60, "marca_base": 6},
            "Quina": {"total": 80, "marca_base": 5}, "Lotomania": {"total": 100,"marca_base": 50},
            "Dupla_Sena": {"total": 50, "marca_base": 6}, "Dia_de_Sorte": {"total": 31, "marca_base": 7},
            "Timemania": {"total": 80, "marca_base": 10}, "Mega_da_Virada": {"total": 60, "marca_base": 6}
        }

    def _calcular_entropia_real(self, jogo, total_dezenas):
        # ... (CÓDIGO DE ENTROPIA PERMANECE IGUAL AO ANTERIOR) ...
        try:
            jogo = sorted(jogo)
            if len(jogo) < 2: return 0.5
            if len(jogo) > 20: fator_espalhamento = 0.5 
            else:
                gaps = np.diff(jogo)
                std_gaps = np.std(gaps)
                fator_espalhamento = 1.0 / (1.0 + std_gaps) 
            pares = len([n for n in jogo if n % 2 == 0])
            ratio = pares / len(jogo)
            if ratio == 0 or ratio == 1: shannon_parity = 0
            else: shannon_parity = - (ratio * math.log2(ratio) + (1-ratio) * math.log2(1-ratio))
            soma_real = sum(jogo)
            soma_ideal = (len(jogo) * (total_dezenas + 1)) / 2
            distancia_soma = abs(soma_real - soma_ideal)
            fator_soma = 1.0 - (distancia_soma / soma_ideal)
            entropia_final = (shannon_parity * 0.5) + ((1 - fator_espalhamento) * 0.3) + (fator_soma * 0.2)
            return max(0.0, min(1.0, entropia_final))
        except: return 0.5

    def executar_backtest(self, hist, total_dezenas):
        if hist is None or len(hist) < 5: return "Padrão Fractal", {}, False
        scores = {"Markov": 0, "Fractal": 0, "Gauss": 0}
        try:
            teste = hist[-5:]
            for i in range(len(teste)-1):
                passado = set([int(x) for x in teste[i] if not np.isnan(x)])
                futuro = set([int(x) for x in teste[i+1] if not np.isnan(x)])
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

    def analisar_com_gemini(self, api_key, modelo, loteria, dados_fin, jogos_top3, meta):
        # ... (CÓDIGO GEMINI PERMANECE IGUAL) ...
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(modelo)
            vencedora = meta.get('vencedora', 'Padrão')
            entropia_calc = jogos_top3[0][2]
            prompt = f"Você é FractalV 4.0. Analise para {loteria}. Estratégia: {vencedora}. Entropia: {entropia_calc:.4f}. Jogo: {jogos_top3[0][0]}. Responda curto: A entropia é boa? Por que essa estratégia?"
            return model.generate_content(prompt).text
        except Exception as e: return f"⚠️ Erro IA: {str(e)}"

    # AGORA RECEBE OS DADOS JÁ CARREGADOS, NÃO A URL
    def processar_nucleo(self, historico, ultimo_concurso_id, preco_jogo, loteria_chave, orcamento):
        key_norm = loteria_chave.replace(' ','_').replace('á','a').replace('ç','c')
        cfg = self.config_base.get(key_norm, self.config_base["Mega_Sena"])
        
        # Backtest
        vencedora, scores, aprendeu = self.executar_backtest(historico, cfg['total'])
        
        # Financeiro
        qtd_jogos = int(orcamento // preco_jogo)
        qtd_jogos = max(1, qtd_jogos)
        fin = {
            "qtd": qtd_jogos,
            "preco_unit": preco_jogo,
            "troco": orcamento - (qtd_jogos * preco_jogo),
            "custo_total": qtd_jogos * preco_jogo
        }

        # Pesos
        pesos_vivos = self.learner.get_pesos()

        # Semente
        seed_val = f"FV4.0_{loteria_chave}_{ultimo_concurso_id}_{vencedora}_{qtd_jogos}"
        random.seed(seed_val)

        jogos = []
        marca = cfg['marca_base']
        pool = list(range(1, cfg['total'] + 1))
        
        last_draw = []
        if historico is not None and len(historico) > 0:
            last_draw = [int(x) for x in historico[-1] if not np.isnan(x)]

        tentativas = 0
        while len(jogos) < qtd_jogos and tentativas < 3000:
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
                    entropia = self._calcular_entropia_real(jg, cfg['total'])
                    limite_min = 0.35 if marca < 20 else 0.20
                    if entropia < limite_min or entropia > 0.98: continue
                    
                    score = (entropia * 10) + (0.5 if aprendeu else 0)
                    jogos.append((jg, score, entropia))
            except: continue
        
        if not jogos:
            jg = sorted(random.sample(pool, marca))
            jogos.append((jg, 5.0, 0.5))

        jogos.sort(key=lambda x: x[1], reverse=True)
        random.seed(None)
        
        return {
            "financeiro": fin,
            "backtest": {"vencedora": vencedora, "scores": scores, "aprendeu": aprendeu, "pesos_atuais": pesos_vivos, "ultimo_concurso": ultimo_concurso_id},
            "jogos": jogos
        }
