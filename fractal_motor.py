# ==============================================================================
# 🧠 FRACTAL MOTOR V3.0 - DETERMINISTIC CORE
# ==============================================================================
import pandas as pd
import numpy as np
import random
import google.generativeai as genai
import warnings
import fractal_learner

warnings.filterwarnings("ignore")

class FractalCerebro:
    def __init__(self):
        self.versao = "FractalV 3.0 (Deterministic)"
        self.learner = fractal_learner.FractalLearner()
        
        self.config_base = {
            "Lotofacil": {"total": 25, "marca_base": 15}, "Mega_Sena": {"total": 60, "marca_base": 6},
            "Quina": {"total": 80, "marca_base": 5}, "Dia_de_Sorte": {"total": 31, "marca_base": 7},
            "Timemania": {"total": 80, "marca_base": 10}, "Dupla_Sena": {"total": 50, "marca_base": 6},
            "Lotomania": {"total": 100,"marca_base": 50}, "Mega_da_Virada": {"total": 60, "marca_base": 6}
        }

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
                # Lógica simplificada de pontuação
                scores["Markov"] += len(passado.intersection(futuro))
                ausentes = set(range(1, total_dezenas+1)) - passado
                scores["Fractal"] += len(ausentes.intersection(futuro))
        except: pass
        
        vencedora = max(scores, key=scores.get)
        aprendeu, quem = self.learner.regenerar_pesos(vencedora)
        return vencedora, scores, aprendeu

    # --- NOVIDADE: RECEBE O MODELO ESCOLHIDO PELO USUÁRIO ---
    def analisar_com_gemini(self, api_key, modelo_escolhido, loteria, dados_fin, jogos_top3, backtest_info):
        try:
            genai.configure(api_key=api_key)
            
            # Usa estritamente o modelo que o usuário mandou
            model = genai.GenerativeModel(modelo_escolhido)
            
            vencedora = backtest_info.get('vencedora', 'Padrão')
            pesos = self.learner.get_pesos()
            
            prompt = f"""
            Atue como o Sistema FractalV.
            Analise estes palpites para {loteria}.
            
            1. Modelo Matemático Ativo: {vencedora} (Baseado no último Backtest).
            2. Estado Neural: Markov({pesos['Markov']:.2f}) | Fractal({pesos['Fractal']:.2f}).
            3. Jogos Gerados:
            {jogos_top3[0][0]}
            
            Responda em Português:
            - Por que manteve/mudou a estratégia em relação ao concurso anterior?
            - Qual a probabilidade teórica baseada na inércia dos números?
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e: return f"⚠️ Erro na IA ({modelo_escolhido}): {str(e)}"

    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        cfg = self.config_base.get(loteria_chave, self.config_base["Mega_Sena"])
        
        df = self.carregar_csv(url_dados)
        hist = []
        last_concurso_id = 0 # Identificador para a Semente
        
        if df is not None:
            try:
                cols = [c for c in df.columns if c.strip().upper().startswith('D')]
                for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
                df = df.dropna(subset=['Concurso']).sort_values('Concurso')
                hist = df[cols].values
                # Pega o número do último concurso para travar a decisão
                last_concurso_id = int(df['Concurso'].iloc[-1])
            except: pass

        # Backtest
        vencedora, scores, aprendeu = self.executar_backtest(hist, cfg['total'])
        fin = self.calcular_limite_jogos(url_precos, loteria_chave, orcamento)
        fin['orcamento_inicial'] = orcamento
        pesos_vivos = self.learner.get_pesos()

        # --- ESTABILIDADE DETERMINÍSTICA (A DECISÃO FIRME) ---
        # Criamos uma semente única baseada na Loteria + Último Resultado + Estratégia Vencedora
        # Se nada disso mudar, os números gerados serão IDÊNTICOS (Inércia de Decisão)
        seed_val = f"{loteria_chave}_{last_concurso_id}_{vencedora}_{fin['qtd']}"
        random.seed(seed_val) 
        # -----------------------------------------------------

        jogos = []
        marca = cfg['marca_base']
        pool = list(range(1, cfg['total'] + 1))
        
        last_draw = []
        if len(hist) > 0:
            last_draw = [int(x) for x in hist[-1] if pd.notna(x)]

        # Geração com Seed Travada
        tentativas = 0
        while len(jogos) < fin['qtd'] and tentativas < 2000:
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
                    # O score também será determinístico agora
                    score = random.uniform(8.0, 9.9) + (0.1 if aprendeu else 0)
                    jogos.append((jg, score))
            except: continue
            
        if not jogos:
            jg = sorted(random.sample(pool, marca))
            jogos.append((jg, 5.0))

        jogos.sort(key=lambda x: x[1], reverse=True)
        
        # IMPORTANTE: Destravar o random para não afetar outras partes do sistema se necessário
        random.seed(None) 
        
        return {
            "financeiro": fin, 
            "backtest": {"vencedora": vencedora, "scores": scores, "aprendeu": aprendeu, "pesos_atuais": pesos_vivos, "ultimo_concurso": last_concurso_id}, 
            "jogos": jogos
        }
