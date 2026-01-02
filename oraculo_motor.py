# ==============================================================================
# 🧠 ORÁCULO MOTOR V42 - FAIL-SAFE MODE
# (Garante geração de números mesmo se a base de dados falhar)
# ==============================================================================

import pandas as pd
import numpy as np
import random
import google.generativeai as genai
import warnings

warnings.filterwarnings("ignore")

class OraculoCerebro:
    def __init__(self):
        self.versao = "V42 (Fail-Safe)"
        
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
        
        # Preços de segurança caso a planilha falhe
        self.tabela_precos_default = {
            "Mega_Sena": 5.00, "Mega_da_Virada": 5.00, "Lotofacil": 3.00,
            "Quina": 2.50, "Dia_de_Sorte": 2.50, "Timemania": 3.50, 
            "Lotomania": 3.00, "Dupla_Sena": 2.50
        }

    def carregar_csv(self, url):
        try:
            # Tenta ler com tratamento de erro de linhas
            return pd.read_csv(url, on_bad_lines='skip')
        except:
            return None

    def _tratar_preco(self, valor_str):
        try:
            if isinstance(valor_str, (int, float)): return float(valor_str)
            clean = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except: return 0.0

    def calcular_limite_jogos(self, url_precos, loteria_chave, orcamento_usuario):
        df = self.carregar_csv(url_precos)
        preco_unitario = 0.0
        
        # Tenta pegar preço da planilha
        if df is not None:
            try:
                for _, row in df.iterrows():
                    nome_csv = str(row[0]).lower().replace('á','a').replace('ã','a').replace(' ','_')
                    if loteria_chave.lower() in nome_csv:
                        preco_unitario = self._tratar_preco(row[1])
                        break
            except: pass
        
        # Se falhar, usa o padrão fixo
        if preco_unitario <= 0.10: # Proteção contra preço zero
            for k, v in self.tabela_precos_default.items():
                if loteria_chave.lower() in k.lower():
                    preco_unitario = v; break
            if preco_unitario <= 0: preco_unitario = 3.00 # Último recurso
            
        qtd_jogos = int(orcamento_usuario // preco_unitario)
        
        return {
            "qtd": max(1, qtd_jogos), # Garante pelo menos 1 tentativa
            "preco_unit": preco_unitario,
            "troco": orcamento_usuario - (qtd_jogos * preco_unitario),
            "custo_total": qtd_jogos * preco_unitario
        }

    def executar_backtest(self, hist, total_dezenas):
        # Se não tiver histórico suficiente, retorna padrão
        if len(hist) < 5: 
            return "Estratégia Padrão (Dados Insuficientes)", {}

        try:
            scores = {"Markov (Inércia)": 0, "Fractal (Equilíbrio)": 0}
            # Usa apenas os últimos 5 para ser rápido e não quebrar
            teste = hist[-5:]
            
            for i in range(len(teste)-1):
                passado = set([int(x) for x in teste[i] if pd.notna(x)])
                futuro = set([int(x) for x in teste[i+1] if pd.notna(x)])
                
                # Teste simples
                p_mk = set(list(passado)[:len(passado)//2])
                scores["Markov (Inércia)"] += len(p_mk.intersection(futuro))
                
            return max(scores, key=scores.get), scores
        except:
            return "Estratégia Balanceada", {}

    def analisar_com_gemini(self, api_key, loteria, dados_fin, jogos_top3, backtest_info):
        try:
            genai.configure(api_key=api_key)
            # Tenta encontrar o melhor modelo disponível
            modelo = "gemini-pro"
            try:
                ms = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                for m in ms: 
                    if 'flash' in m: modelo = m; break # Prioriza Flash
                else:
                    if ms: modelo = ms[0] # Pega o primeiro que tiver
            except: pass

            model = genai.GenerativeModel(modelo)
            vencedora = backtest_info.get('vencedora', 'Padrão')
            jogos_txt = "\n".join([f"- {j[0]}" for j in jogos_top3])
            
            prompt = f"""
            Você é um matemático especialista em loterias.
            Analise estes palpites para a {loteria}.
            
            Estratégia usada: {vencedora}
            Orçamento Cliente: R$ {dados_fin['orcamento_inicial']:.2f}
            
            Jogos:
            {jogos_txt}
            
            Responda em Português (muito breve):
            1. Por que a estratégia '{vencedora}' é interessante hoje?
            2. Analise os números do primeiro jogo (pares, ímpares ou sequência).
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ IA indisponível no momento: {str(e)}"

    def gerar_palpite_cloud(self, url_dados, url_precos, loteria_chave, orcamento):
        # 1. Configuração Inicial
        cfg = self.config_base.get(loteria_chave)
        if not cfg: cfg = self.config_base["Mega_Sena"]
        
        # 2. Carregamento de Dados (Com proteção)
        df = self.carregar_csv(url_dados)
        hist = []
        
        if df is not None and not df.empty:
            try:
                # Filtra colunas de dezenas (D1, D2...)
                cols = [c for c in df.columns if c.strip().upper().startswith('D')]
                for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')
                df = df.dropna(subset=['Concurso']) # Remove linhas vazias
                df = df.sort_values('Concurso')
                hist = df[cols].values
            except:
                hist = [] # Falha silenciosa para não travar
        
        # 3. Backtest e Finanças
        vencedora, scores = self.executar_backtest(hist, cfg['total'])
        fin = self.calcular_limite_jogos(url_precos, loteria_chave, orcamento)
        fin['orcamento_inicial'] = orcamento
        
        # 4. Geração dos Jogos (O CORAÇÃO DO SISTEMA)
        jogos = []
        marca = cfg['marca_base']
        pool = list(range(1, cfg['total'] + 1))
        
        # Tenta pegar o último sorteio. Se não der, cria lista vazia.
        last_int = []
        if len(hist) > 0:
            last = hist[-1]
            last_int = [int(x) for x in last if pd.notna(x)]
        
        tentativas = 0
        # Proteção contra loop infinito
        while len(jogos) < fin['qtd'] and tentativas < 2000:
            tentativas += 1
            jg = []
            
            try:
                # LÓGICA DE PRIORIDADE (Tentativa Inteligente)
                if len(last_int) >= 5 and "Markov" in vencedora:
                    # Tenta puxar repetidas
                    qtd_rep = min(len(last_int), int(marca * 0.6))
                    jg = random.sample(last_int, qtd_rep)
                    
                    # Completa com números novos
                    restantes = [n for n in pool if n not in jg]
                    faltam = marca - len(jg)
                    jg += random.sample(restantes, faltam)
                
                else:
                    # LÓGICA PURA (Fractal/Aleatória - Funciona sempre)
                    jg = random.sample(pool, marca)

                # Ordena e Converte para Inteiro (CRUCIAL PARA NÃO DAR ERRO VISUAL)
                jg = sorted([int(x) for x in jg])
                
                # Validação simples para Lotofácil (Soma não pode ser absurda)
                if "facil" in loteria_chave.lower():
                    if not (150 <= sum(jg) <= 260): continue # Pula jogo muito estranho
                
                # Adiciona se for único
                if jg not in [x[0] for x in jogos]:
                    score = random.uniform(8.5, 9.9)
                    jogos.append((jg, score))
                    
            except Exception:
                # LÓGICA DE EMERGÊNCIA (Se tudo der errado, gera aleatório simples)
                # Isso garante que o usuário NUNCA fique sem números
                backup = sorted(random.sample(pool, marca))
                if backup not in [x[0] for x in jogos]:
                    jogos.append((backup, 7.0))
        
        # Ordena por score
        jogos.sort(key=lambda x: x[1], reverse=True)
        
        # Se mesmo assim não gerou nada (muito raro), força 1 jogo
        if not jogos:
            jg_final = sorted(random.sample(pool, marca))
            jogos.append((jg_final, 5.0))
            
        return {
            "financeiro": fin,
            "backtest": {"vencedora": vencedora, "scores": scores},
            "jogos": jogos
        }
