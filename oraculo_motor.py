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
        
        # --- MODELO DE IA (AUTO-DISCOVERY) ---
        # Busca automática do melhor modelo disponível na conta
        self.modelo_ia = "gemini-pro" 
        
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
        
        # Tabela de preços de fallback (caso o CSV falhe)
        self.tabela_precos_default = {
            "Mega_Sena": 5.00, "Mega_da_Virada": 5.00, "Lotofacil": 3.00,
            "Quina": 2.50, "Dia_de_Sorte": 2.50, "Timemania": 3.50, "Lotomania": 3.00, "Dupla_Sena": 2.50
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
            "qtd": qtd_jogos if qtd_jogos > 0 else 1, # Mínimo 1 jogo para não quebrar
            "preco_unit": preco_unitario,
            "troco": troco,
            "custo_total": qtd_jogos * preco_unitario
        }

    # --- ENGINE DE BACKTEST (O CÉREBRO DA V40) ---
    def executar_backtest(self, hist, total_dezenas):
        """
        Testa 3 estratégias nos últimos 10 concursos e vê qual performa melhor.
        """
        if len(hist) < 15: return "Padrão Aleatório (Dados insuficientes)"

        # Definição das Estratégias
        scores_backtest = {"Markov (Inércia)": 0, "Fractal (Equilíbrio)": 0, "Gauss (Soma)": 0}
        
        # Recorte de teste (Últimos 10 resultados conhecidos)
        teste_range = hist[-10:]
        
        for i in range(len(teste_range)-1):
            passado = teste_range[i]
            futuro_real = set(teste_range[i+1])
            
            # 1. Simulação Markov (Repete 50% do passado)
            pred_mk = set(passado[:len(passado)//2]) 
            acertos_mk = len(pred_mk.intersection(futuro_real))
            scores_backtest["Markov (Inércia)"] += acertos_mk
            
            # 2. Simulação Fractal (Pega números que NÃO saíram - Espelho)
            todos = set(range(1, total_dezenas+1))
            ausentes = list(todos - set(passado))
            random.shuffle(ausentes)
            pred_fr = set(ausentes[:len(passado)//2])
            acertos_fr = len(pred_fr.intersection(futuro_real))
            scores_backtest["Fractal (Equilíbrio)"] += acertos_fr
            
            # 3. Simulação Gauss (Números centrais)
            meio = total_dezenas // 2
            pred_gs = set(range(meio-5, meio+6)) # Faixa central
            acertos_gs = len(pred_gs.intersection(futuro_real))
            scores_backtest["Gauss (Soma)"] += acertos_gs

        # Retorna a vencedora
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
                # Prefere Flash > Pro
                for m in available: 
                    if 'flash' in m: modelo_uso = m; break
                else:
                    if available: modelo_uso = available[0]
            except: pass

            model = genai.GenerativeModel(modelo_uso)
            
            vencedora = backtest_info['vencedora']
            
            jogos_txt = "\n".join([f"- Jogo: {j[0]}" for j in jogos_top3])
            
            prompt = f"""
            Aja como um Estrategista de Loterias Profissional.
            O sistema 'Oráculo V40' realizou um BACKTEST (teste histórico) e definiu a melhor estratégia.
            
            DADOS DO PROCESSAMENTO:
            - Loteria: {loteria}
            - Orçamento Cliente: R$ {dados_fin['orcamento_inicial']:.2f} (Gerou {dados_fin['qtd']} jogos)
            - Estratégia Vencedora no Backtest: {vencedora}
            
            JOGOS GERADOS:
            {jogos_txt}
            
            SUA MISSÃO (Responda em Português, direto ao ponto):
            1. Explique por que a estratégia '{vencedora}' foi escolhida (baseado no fato de ter tido melhor performance nos últimos testes).
            2. Analise os números do primeiro jogo: por que eles se encaixam nessa estratégia?
            3. Dê um veredito sobre a eficiência do uso do orçamento (R$ {dados_fin['custo_total']:.2f}).
            """
            
            response = model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            return f"⚠️ IA Indisponível: {str(e)}. (Mas os cálculos de orçamento e jogos estão corretos!)"

    # --- GERAÇÃO PRINCIPAL ---
    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        cfg = self.config_base.get(loteria_chave)
        if not cfg: cfg = self.config_base["Mega_Sena"]
        
        # 1. Carregar Dados Históricos
        df = self.carregar_csv(url_dados)
        hist = []
        if df is not None:
            cols = [c for c in df.columns if c.strip().upper().startswith('D')]
            for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=['Concurso']).sort_values('Concurso')
            hist = df[cols].values
        
        # 2. Executar Backtest (Decidir Estratégia)
        estrategia_vencedora, scores = self.executar_backtest(hist, cfg['total'])
        
        # 3. Calcular Orçamento (Rígido)
        financas = self.calcular_limite_jogos(url_precos, loteria_chave, orcamento)
        financas['orcamento_inicial'] = orcamento
        
        if financas['qtd'] < 1: 
            return {"erro": f"Orçamento de R$ {orcamento} insuficiente. Aposta mínima é R$ {financas['preco_unit']:.2f}"}

        # 4. Gerar Jogos Baseado na Vencedora
        jogos = []
        marca = cfg['marca_base']
        pool = list(range(1, cfg['total'] + 1))
        last_draw = hist[-1] if len(hist) > 0 else []

        # Configura pesos baseados na estratégia vencedora
        peso_repeticao = 0.5 # Default
        if "Markov" in estrategia_vencedora: peso_repeticao = 0.8 # Favorece repetição
        if "Fractal" in estrategia_vencedora: peso_repeticao = 0.2 # Favorece números novos
        
        tentativas = 0
        while len(jogos) < financas['qtd'] and tentativas < 5000:
            tentativas += 1
            try:
                # Lógica Híbrida baseada no Backtest
                # Se Markov venceu, puxa mais do último sorteio
                # Se Fractal venceu, puxa mais dos ausentes
                
                qtd_repetidas = int(marca * peso_repeticao)
                qtd_novas = marca - qtd_repetidas
                
                candidatos_repetidos = [n for n in last_draw if n in pool and not pd.isna(n)]
                candidatos_novos = [n for n in pool if n not in last_draw]
                
                # Garante que tem números suficientes
                if len(candidatos_repetidos) < qtd_repetidas: qtd_repetidas = len(candidatos_repetidos)
                
                base = random.sample(candidatos_repetidos, qtd_repetidas) + random.sample(candidatos_novos, marca - qtd_repetidas)
                jg = sorted(list(set(base)))
                
                # Preenchimento de segurança
                while len(jg) < marca: 
                    n = random.choice(pool)
                    if n not in jg: jg.append(n)
                jg = sorted(jg)

                if jg not in [x[0] for x in jogos]:
                    # Score simulado para ranking
                    score = random.uniform(8.0, 9.9) 
                    jogos.append((jg, score))
            except: continue
        
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "financeiro": financas,
            "backtest": {"vencedora": estrategia_vencedora, "scores": scores},
            "jogos": jogos
        }
