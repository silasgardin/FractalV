# fractal_learner.py
import json
import os

class FractalLearner:
    def __init__(self):
        self.arquivo_memoria = "fractal_memory.json"
        self.pesos_padrao = {"Markov": 0.40, "Fractal": 0.30, "IA": 0.30}
        self.memoria = self.carregar_memoria()

    def carregar_memoria(self):
        if os.path.exists(self.arquivo_memoria):
            try:
                with open(self.arquivo_memoria, 'r') as f: return json.load(f)
            except: return self.pesos_padrao.copy()
        return self.pesos_padrao.copy()

    def salvar_memoria(self):
        try:
            with open(self.arquivo_memoria, 'w') as f: json.dump(self.memoria, f)
        except: pass

    def regenerar_pesos(self, modelo_vencedor):
        # Mapeia o nome do modelo para a chave interna
        chave = ""
        if "Tendencia" in modelo_vencedor or "Markov" in modelo_vencedor: chave = "Markov"
        elif "Reversao" in modelo_vencedor or "Fractal" in modelo_vencedor: chave = "Fractal"
        elif "IA" in modelo_vencedor or "Preditiva" in modelo_vencedor: chave = "IA"
        
        if chave:
            self.memoria[chave] = min(0.90, self.memoria[chave] + 0.05)
            # Rebalanceia o resto
            restante = 1.0 - self.memoria[chave]
            outras = [k for k in self.memoria if k != chave]
            for k in outras: self.memoria[k] = restante / len(outras)
            self.salvar_memoria()
            return True
        return False

    def get_pesos(self):
        return self.memoria
