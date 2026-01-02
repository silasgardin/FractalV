# ==============================================================================
# 🧠 FRACTAL MOTOR V3.5 - REBRANDING FINAL & ENTROPY CORE
# ARQUIVO: fractal_motor.py
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
        self.versao = "FractalV 3.5 (Entropy Core)"
        self.learner = fractal_learner.FractalLearner()
        
        self.config_base = {
            "Lotofacil": {"total": 25, "marca_base": 15}, "Mega_Sena": {"total": 60, "marca_base": 6},
            "Quina": {"total": 80, "marca_base": 5}, "Dia_de_Sorte": {"total": 31, "marca_base": 7},
            "Timemania": {"total": 80, "marca_base": 10}, "Dupla_Sena": {"total": 50, "marca_base": 6},
            "Lotomania": {"total": 100,"marca_base": 50}, "Mega_da_Virada": {"total": 60, "marca_base": 6}
        }

    # --- O CORAÇÃO DA ENTROPIA (AEF) ---
    def _calcular_entropia_real(self, jogo, total_dezenas):
        """
        Calcula o grau de CAOS do jogo (0.0 a 1.0).
        Usa Shannon (Informação) + Desvio Padrão (Dispersão).
        """
        try:
            jogo = sorted(jogo)
            if len(jogo) < 2: return 0.5
            
            # 1. Dispersão (O quão longe os números estão uns dos outros)
            gaps = np.diff(jogo)
            std_gaps = np.std(gaps)
            fator_espalhamento = 1.0 / (1.0 + std_gaps) 

            # 2. Entropia de Shannon (Equilíbrio Par/Ímpar)
            pares = len([n for n in jogo if n % 2 == 0])
            ratio = pares / len(jogo)
            if ratio == 0 or ratio == 1: shannon_parity = 0
            else:
                shannon_parity = - (ratio * math.log2(ratio) + (1-ratio) * math.log2(1-ratio))

            # 3. Gravidade (Distância da Média ideal)
            soma_real = sum(jogo)
            soma_ideal = (len(jogo) * (total_dezenas + 1)) / 2
            distancia_soma = abs(soma_real - soma_ideal)
            fator_soma = 1.0 - (distancia_soma / soma_ideal)

            # Fórmula Final Ponderada
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
        return vencedora, scores
