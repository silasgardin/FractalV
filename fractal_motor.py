# ==============================================================================
# 🧠 FRACTAL MOTOR V3.3 - ENTROPY CORE
# NOME DO ARQUIVO OBRIGATÓRIO: fractal_motor.py
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

    # --- CÁLCULO DE ENTROPIA REAL ---
    def _calcular_entropia_real(self, jogo, total_dezenas):
        try:
            jogo = sorted(jogo)
            if len(jogo) < 2: return 0.5
            
            # 1. Espalhamento (Desvio Padrão)
            gaps = np.diff(jogo)
            std_gaps = np.std(gaps)
            fator_espalhamento = 1.0 / (1.0 + std_gaps) 

            # 2. Paridade (Shannon)
            pares = len([n for n in jogo if n % 2 == 0])
            ratio = pares / len(jogo)
            if ratio == 0 or ratio == 1: shannon_parity = 0
            else:
                shannon_parity = - (ratio * math.log2(ratio) + (1-ratio) * math.log2(1-ratio))

            # 3. Soma
            soma_real = sum(jogo)
            soma_ideal = (len(jogo) * (total_dezenas + 1)) / 2
            distancia_soma = abs(soma_real - soma_ideal)
            fator_soma = 1.0 - (distancia_soma / soma_ideal)

            # Peso Fractal
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
            entropia_calc = jogos_top3[0][2]
            
            prompt = f"""
            Atue como o Núcleo FractalV (V3.3).
            Analise estes dados de loteria ({loteria}).
            
            DADOS TÉCNICOS:
            1. Estratégia Vencedora: {vencedora}
            2. Índice de Entropia Fractal: {entropia_calc:.4f} (Escala 0.0 a 1.0)
            3. Jogo Gerado: {jogos_top3[0][0]}
            
            Responda em Português:
            - O que o valor de Entropia {entropia_calc:.4f} diz sobre este jogo? (Equilibrado ou Arriscado?)
            - Como a estratégia '{vencedora}' foi aplicada?
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
                    entropia = self._calcular_entropia_real(jg, cfg['total'])
                    if entropia < 0.35 or entropia > 0.95: continue 
                    
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
            "backtest": {"vencedora": vencedora, "scores": scores, "aprendeu": aprendeu, "pesos_atuais": pesos_vivos, "ultimo_concurso": last_concurso_id}, 
            "jogos": jogos
        }
