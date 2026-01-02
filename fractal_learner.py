# ==============================================================================
# 🧬 FRACTAL LEARNER - MEMÓRIA REGENERATIVA
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

    def regenerar_pesos(self, estrategia_vencedora):
        taxa = 0.05
        chave = ""
        if "Markov" in estrategia_vencedora: chave = "Markov"
        elif "Fractal" in estrategia_vencedora: chave = "Fractal"
        elif "Gauss" in estrategia_vencedora: chave = "Gauss"
        
        if chave:
            self.memoria[chave] += taxa
            restante = 1.0 - self.memoria[chave]
            outras = [k for k in self.memoria if k != chave]
            for k in outras: self.memoria[k] = restante / len(outras)
            self.salvar_memoria()
            return True, chave
        return False, None

    def get_pesos(self): return self.memoria
