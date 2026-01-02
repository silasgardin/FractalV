# ==============================================================================
# 🧠 ORÁCULO MOTOR V40 - ADAPTIVE BACKTEST & BUDGET CONTROL
# ==============================================================================

import pandas as pd
import numpy as np
import random
import google.generativeai as genai
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V40 (Adaptive Backtest)"
        
        # --- CONFIGURAÇÕES TÉCNICAS ---
        self.config_base = {
            "Lotofacil":      {"total": 25, "marca_base": 15},
            "Mega_Sena":      {"total": 60, "marca_base": 6},
            "Quina":          {"total": 80, "marca_base": 5},
            "Dia_de_Sorte":   {"total": 31, "marca_base": 7},
            "Timemania":      {"total": 80, "marca_base": 10},
            "Dupla_Sena":     {"total": 50, "marca_base": 6},
            "Lotomania":      {"total": 100,"marca_base": 50},
            "Mega_da_Virada": {"total": 60, "marca_base": 6}
        }
        
        # Preços atualizados (Fallback caso o CSV falhe)
        self.tabela_precos_default = {
            "Mega_Sena": 6.00, "Mega_da_Virada": 6.00, "Lotofacil": 3.50,
            "Quina": 3.00, "Dia_de_Sorte": 2.50, "Timemania": 3.50, "Lotomania": 3.00, "Dupla_Sena": 3.00
        }

    def carregar_csv(self, url):
        try: return pd.read_csv(url)
        except: return None

    def _tratar_preco(self, valor_str):
        try:
            if isinstance(valor_str, (int, float)): return float(valor_str)
            clean = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    # --- NOVO SISTEMA DE ORÇAMENTO RÍGIDO ---
    def calcular_limite_jogos(self, url_precos, loteria_chave, orcamento_usuario):
        # 1. Tenta ler o preço atualizado do CSV
        df = self.carregar_csv(url_precos)
        preco_unitario = 0.0
        
        if df is not None:
            for _, row in df.iterrows():
                nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace(' ','_')
                if loteria_chave.lower() in nome_csv:
                    preco_unitario = self._tratar_preco(row[1])
                    break
        
        # 2. Se falhar, usa o default
        if preco_unitario <= 0:
            for k, v in self.tabela_precos_default.items():
                if loteria_chave.lower() in k.lower():
                    preco_unitario = v; break
            if preco_unitario <= 0: preco_unitario = 3.00 # Fallback final
            
        # 3. Cálculo Matemático do Orçamento
        qtd_jogos = int(orcamento_usuario // preco_unitario)
        troco = orcamento_usuario - (qtd_jogos * preco_unitario)
        
        return {
            "qtd": qtd_jogos if qtd_jogos > 0 else 1, # Mínimo 1 jogo
            "preco_unit": preco_unitario,
            "troco": troco,
            "custo_total": qtd_jogos * preco_unitario
        }

    # --- ENGINE DE BACKTEST (O CÉREBRO DA V40) ---
    def executar_backtest(self, hist, total_dezenas):
        """
        Testa 3 estratégias nos últimos 10 concursos e vê qual performa melhor.
        """
        if len(hist) < 15: return "Padrão Aleatório (Dados insuficientes)", {}

        scores_backtest = {"Markov (Inércia)": 0, "Fractal (Equilíbrio)": 0, "Gauss (Soma)": 0}
        teste_range = hist[-10:]
        
        for i in range(len(teste_range)-1):
            passado = teste_range[i]
            futuro_real = set(teste_range[i+1])
            
            # 1. Simulação Markov (Repete 50% do passado)
            pred_mk = set(passado[:len(passado)//2]) 
            acertos_mk = len(pred_mk.intersection(futuro_real))
            scores_backtest["Markov (Inércia)"] += acertos_mk
            
            # 2. Simulação Fractal (Pega números que NÃO saíram)
            todos = set(range(1, total_dezenas+1))
            ausentes = list(todos - set(passado))
            random.shuffle(ausentes)
            pred_fr = set(ausentes[:len(passado)//2])
            acertos_fr = len(pred_fr.intersection(futuro_real))
            scores_backtest["Fractal (Equilíbrio)"] += acertos_fr
            
            # 3. Simulação Gauss (Números centrais)
            meio = total_dezenas // 2
            pred_gs = set(range(meio-5, meio+6))
            acertos_gs = len(pred_gs.intersection(futuro_real))
            scores_backtest["Gauss (Soma)"] += acertos_gs

        melhor_estrategia = max(scores_backtest, key=scores_backtest.get)
        return melhor_estrategia, scores_backtest

    # --- INTEGRAÇÃO I.A. EXPLICATIVA ---
    def analisar_com_gemini(self, api_key, loteria, dados_fin, jogos_top3, backtest_info):
        try:
            genai.configure(api_key=api_key)
            
            # Auto-Discovery de Modelo
            modelo_uso = "gemini-pro"
            try:
                available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                for m in available: 
                    if 'flash' in m: modelo_uso = m; break
                else:
                    if available: modelo_uso = available[0]
            except: pass

            model = genai.GenerativeModel(modelo_uso)
            
            vencedora = backtest_info.get('venced
