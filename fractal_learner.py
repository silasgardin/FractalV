# ==============================================================================
# 🧬 FRACTAL LEARNER - NOME DO ARQUIVO: fractal_learner.py
# ==============================================================================
import json
import os

class FractalLearner:
    def __init__(self):
        self.arquivo_memoria = "fractal_memory.json"
        self.pesos_padrao = {"Markov": 0.40, "Fractal": 0.30, "Gauss": 0.30}
        self.memoria = self.carregar_memoria()

    def carregar_memoria(self):
        if os.path.exists(self.arquivo_memoria):
            try:
                with open(self.arquivo_memoria, 'r') as f: return json.load(f)
            except: return self.pesos_padrao
        return self.pesos_padrao

    def salvar_memoria(self):
        try:
            with open(self.arquivo_memoria, 'w') as f: json.dump(self.memoria, f)
        except: pass

    def regenerar_pesos(self, estrategia_vencedora_backtest):
        taxa_aprendizado = 0.05
        chave_map = ""
        if "Markov" in estrategia_vencedora_backtest: chave_map = "Markov"
        elif "Fractal" in estrategia_vencedora_backtest: chave_map = "Fractal"
        elif "Gauss" in estrategia_vencedora_backtest: chave_map = "Gauss"
        
        if chave_map:
            self.memoria[chave_map] += taxa_aprendizado
            restante = 1.0 - self.memoria[chave_map]
            outras = [k for k in self.memoria if k != chave_map]
            for k in outras: self.memoria[k] = restante / len(outras)
            self.salvar_memoria()
            return True, chave_map
        return False, None

    def get_pesos(self): return self.memoria
