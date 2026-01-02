# ==============================================================================
# 🧬 FRACTAL LEARNER - MEMÓRIA REGENERATIVA
# ARQUIVO OBRIGATÓRIO: fractal_learner.py
# ==============================================================================
import json
import os

class FractalLearner:
    def __init__(self):
        self.arquivo_memoria = "fractal_memory.json"
        
        # Pesos Padrão (O ponto de partida da IA)
        self.pesos_padrao = {
            "Markov": 0.40,   # 40% Inércia
            "Fractal": 0.30,  # 30% Equilíbrio/Caos
            "Gauss": 0.30     # 30% Estatística Normal
        }
        
        self.memoria = self.carregar_memoria()

    def carregar_memoria(self):
        """Carrega a inteligência salva ou cria nova."""
        if os.path.exists(self.arquivo_memoria):
            try:
                with open(self.arquivo_memoria, 'r') as f:
                    return json.load(f)
            except:
                return self.pesos_padrao
        return self.pesos_padrao

    def salvar_memoria(self):
        """Grava a evolução no disco."""
        try:
            with open(self.arquivo_memoria, 'w') as f:
                json.dump(self.memoria, f)
        except: pass 

    def regenerar_pesos(self, estrategia_vencedora_backtest):
        """
        Ajusta a inteligência baseada no sucesso recente.
        """
        taxa_aprendizado = 0.05 
        
        chave_map = ""
        if "Markov" in estrategia_vencedora_backtest: chave_map = "Markov"
        elif "Fractal" in estrategia_vencedora_backtest: chave_map = "Fractal"
        elif "Gauss" in estrategia_vencedora_backtest: chave_map = "Gauss"
        
        if chave_map:
            self.memoria[chave_map] += taxa_aprendizado
            
            # Reequilibra os pesos para a soma ser 1.0
            restante = 1.0 - self.memoria[chave_map]
            outras_chaves = [k for k in self.memoria if k != chave_map]
            
            for k in outras_chaves:
                self.memoria[k] = restante / len(outras_chaves)
            
            self.salvar_memoria()
            return True, chave_map
            
        return False, None

    def get_pesos(self):
        return self.memoria
