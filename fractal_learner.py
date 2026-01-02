# fractal_learner.py
import json
import os

class FractalLearner:
    def __init__(self):
        self.arquivo_memoria = "fractal_memory.json"
        # Mapeando os nomes para as chaves que o Engine usa (w_mk, w_fr, w_ia)
        self.pesos_padrao = {"Markov": 0.40, "Fractal": 0.30, "IA": 0.30} 
        self.memoria = self.carregar_memoria()

    def carregar_memoria(self):
        if os.path.exists(self.arquivo_memoria):
            try:
                with open(self.arquivo_memoria, 'r') as f: 
                    return json.load(f)
            except: 
                return self.pesos_padrao.copy()
        return self.pesos_padrao.copy()

    def salvar_memoria(self):
        try:
            with open(self.arquivo_memoria, 'w') as f: 
                json.dump(self.memoria, f)
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")

    def regenerar_pesos(self, tipo_vencedor):
        # tipo_vencedor deve ser: 'Tendencia_Linear', 'Reversao_Fractal', etc.
        
        chave = ""
        # Traduz o Modelo Vencedor para o Peso que deve aumentar
        if "Tendencia" in tipo_vencedor: chave = "Markov"
        elif "Reversao" in tipo_vencedor: chave = "Fractal"
        elif "IA" in tipo_vencedor: chave = "IA"
        
        taxa = 0.02 # Taxa de aprendizado (Learning Rate)
        
        if chave:
            self.memoria[chave] = min(0.90, self.memoria[chave] + taxa)
            
            # Rebalanceia os outros para a soma dar sempre 1.0 (100%)
            restante = 1.0 - self.memoria[chave]
            outras = [k for k in self.memoria if k != chave]
            for k in outras: 
                self.memoria[k] = restante / len(outras)
            
            self.salvar_memoria()
            return True, chave, self.memoria
            
        return False, None, self.memoria
    
    def get_pesos_formatados(self):
        # Retorna no formato que o Engine entende (w_mk, w_fr, w_ia)
        return {
            "w_mk": self.memoria["Markov"],
            "w_fr": self.memoria["Fractal"],
            "w_ia": self.memoria["IA"]
        }
