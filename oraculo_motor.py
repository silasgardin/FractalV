# ==============================================================================
# 🧠 ORÁCULO MOTOR V34 - AI POWERED ARCHITECT
# (Financial Intelligence + Fractal Logic + Expert Filters + Generative AI)
# ==============================================================================

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import random
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V34 (AI Powered Architect)"
        
        # Configurações de Jogo (Universo e Marcação Padrão)
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
        
        # Tabela de Preços para Apostas Múltiplas (Estimativa Base)
        self.multiplicadores = {
            "Mega_Sena":      {6: 1, 7: 7, 8: 28, 9: 84, 10: 210},
            "Mega_da_Virada": {6: 1, 7: 7, 8: 28, 9: 84},
            "Lotofacil":      {15: 1, 16: 16, 17: 136, 18: 816},
            "Quina":          {5: 1, 6: 6, 7: 21, 8: 56, 9: 126},
            "Dia_de_Sorte":   {7: 1, 8: 8, 9: 36, 10: 120},
            "Dupla_Sena":     {6: 1, 7: 7, 8: 28, 9: 84},
            "Timemania":      {10: 1}, 
            "Lotomania":      {50: 1}  
        }

    def carregar_csv(self, url):
        """Lê CSV diretamente da URL pública do Google Sheets"""
        try:
            df = pd.read_csv(url)
            return df
        except: return None

    def _tratar_preco(self, valor_str):
        """Converte 'R$ 6,00' para float 6.00"""
        try:
            if isinstance(valor_str, (int, float)): return float(valor_str)
            clean = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def atualizar_precos(self, url_precos, loteria_chave):
        """Busca o preço base na planilha e gera a tabela de combos"""
        df = self.carregar_csv(url_precos)
        preco_base = 0.0
        fallback = 3.00
        
        if df is not None:
            for _, row in df.iterrows():
                nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace(' ','_')
                chave_busca = loteria_chave.lower()
                if chave_busca in nome_csv or nome_csv in chave_busca:
                    preco_base = self._tratar_preco(row[1])
                    break
        
        if preco_base <= 0: preco_base = fallback
        
        chave_mult = None
        for k in self.multiplicadores.keys():
            if k.lower() in loteria_chave.lower(): chave_mult = k; break
            
        if chave_mult:
            mults = self.multiplicadores[chave_mult]
            tabela_atualizada = {qtd: (fator * preco_base) for qtd, fator in mults.items()}
        else:
            base = self.config_base.get(loteria_chave, {}).get('marca_base', 6)
            tabela_atualizada = {base: preco_base}
            
        return tabela_atualizada, preco_base

    # --- CAMADA 1: MOTORES MATEMÁTICOS ---
    
    def _core_markov(self, hist, total):
        matriz = np.zeros((total + 1, total + 1)); recorte = hist[-100:]
        for i in range(len(recorte)-1):
            for u in recorte[i]:
                if pd.isna(u): continue
                for v in recorte[i+1]:
                    if pd.isna(v): continue
                    matriz[int(u)][int(v)] += 1
        row_sums = matriz.sum(axis=1); row_sums[row_sums==0] = 1
        probs = matriz / row_sums[:, None]
        last = hist[-1]; scores = {}
        for d in range(1, total+1):
            s=0; c=0
            for n in last:
                if not pd.isna(n): s+=probs[int(n)][d]; c+=1
            scores[d] = s/c if c>0 else 0
        return scores

    def _core_xgboost(self, hist, total):
        X, y = [], []; atrasos = {d: 0 for d in range(1, total+1)}
        start = max(0, len(hist)-80)
        for i in range(start, len(hist)-1):
            p, c = hist[i], hist[i+1]
            for d in range(1, total+1):
                saiu = 1 if d in p else 0; atr = atrasos[d]
                if d in c or atr > 5: X.append([d, saiu, atr]); y.append(1 if d in c else 0)
                atrasos[d] = 0 if d in p else atras
