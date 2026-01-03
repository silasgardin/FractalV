import pandas as pd
import numpy as np

class OtimizadorFinanceiro:
    def __init__(self, link_csv_valores):
        self.url = link_csv_valores
        self.df_precos = None

    def carregar_dados(self):
        try:
            self.df_precos = pd.read_csv(self.url, decimal=",", thousands=".", on_bad_lines='skip')
            self.df_precos.dropna(subset=['Loteria'], inplace=True)
            if 'Preço Total (R$)' in self.df_precos.columns:
                self.df_precos['Preço Total (R$)'] = self.df_precos['Preço Total (R$)'].astype(str).apply(
                    lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.').strip()) if isinstance(x, str) else x
                )
            self.df_precos['Loteria_Key'] = self.df_precos['Loteria'].astype(str).str.upper().str.replace(' ', '_').str.replace('Á', 'A')
            return True
        except:
            return False

    def calcular_melhor_estrategia(self, jogo, orcamento):
        if self.df_precos is None:
            if not self.carregar_dados():
                return {"erro": "Erro crítico: Não foi possível ler a tabela de preços."}

        jogo_key = str(jogo).upper().replace(' ', '_')
        tabela = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key, na=False)].copy()
        
        if tabela.empty: return {"erro": f"Jogo '{jogo}' não encontrado na tabela."}

        tabela = tabela.sort_values(by='Preço Total (R$)', ascending=False)
        estrategia = {"jogo": jogo, "orcamento_inicial": orcamento, "carrinho": [], "sobra": 0}
        saldo = orcamento

        for _, row in tabela.iterrows():
            try:
                custo = float(row['Preço Total (R$)'])
                if custo <= 0: continue
                
                if saldo >= custo:
                    qtd = int(saldo // custo)
                    dezenas_val = int(float(row['Qtd. Dezenas']))
                    estrategia['carrinho'].append({
                        "qtd_volantes": qtd,
                        "dezenas": dezenas_val,
                        "custo_total": qtd * custo
                    })
                    saldo -= (qtd * custo)
            except: continue
        
        estrategia['sobra'] = round(saldo, 2)
        return estrategia

class MotorInferencia:
    """
    Cérebro Matemático V6.0 - Determinístico (Zero Oscilação)
    """
    
    @staticmethod
    def executar_backtest(df_completo, cols_dezenas):
        try:
            if len(df_completo) < 50: return "Padrão (Dados Insuficientes)", 0, {}
            
            alvo_real = set(df_completo.iloc[0][cols_dezenas].dropna().astype(int).values)
            df_treino = df_completo.iloc[1:].copy()
            qtd_alvo = len(alvo_real)
            
            # Seed fixo para backtest (garante consistência no teste)
            p_hurst = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Hurst", seed_offset=1)
            p_markov = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Markov", seed_offset=1)
            p_gauss = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Gauss", seed_offset=1)
            p_stoch = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Estocástico", seed_offset=1)
            
            scores = {
                "Hurst (Fractal)": len(alvo_real.intersection(p_hurst)),
                "Markov (Cadeias)": len(alvo_real.intersection(p_markov)),
                "Gauss (Normal)": len(alvo_real.intersection(p_gauss)),
                "Estocástico (Oscilador)": len(alvo_real.intersection(p_stoch))
            }
            
            melhor = max(scores, key=scores.get)
            return melhor, scores[melhor], scores
        except Exception as e:
            return "Padrão (Erro)", 0, {}

    @staticmethod
    def prever_proximo(modelo_vencedor, df_completo, cols_dezenas, qtd_numeros_gerar, fixos=[], excluidos=[], seed_index=0):
        """
        Gera números DETERMINÍSTICOS. 
        seed_index: Número do volante (1, 2, 3...) para garantir variação entre jogos, 
        mas consistência ao recalcular.
        """
        
        tipo = "Hurst"
        if "Markov" in modelo_vencedor: tipo = "Markov"
        elif "Gauss" in modelo_vencedor: tipo = "Gauss"
        elif "Estocástico" in modelo_vencedor: tipo = "Estocástico"
        
        vagas_abertas = qtd_numeros_gerar - len(fixos)
        if vagas_abertas <= 0: 
            return sorted(list(set(fixos))[:qtd_numeros_gerar])
        
        # Gera candidatos brutos usando Seed
        # Multiplicamos o seed_index para que o Jogo 1 seja bem diferente do Jogo 2
        candidatos_brutos = MotorInferencia._gerar_base(df_completo, cols_dezenas, qtd_numeros_gerar * 5, tipo, seed_offset=seed_index)
        
        candidatos_validos = [n for n in candidatos_brutos if n not in excluidos and n not in fixos]
        escolhidos = candidatos_validos[:vagas_abertas]
        
        # Fallback determinístico
        if len(escolhidos) < vagas_abertas:
            todas = df_completo.head(50)[cols_dezenas].values.flatten()
            todas = todas[~np.isnan(todas)]
            freq = pd.Series(todas).value_counts().index.tolist()
            extras = [n for n in freq if n not in excluidos and n not in fixos and n not in escolhidos]
            falta = vagas_abertas - len(escolhidos)
            escolhidos.extend(extras[:falta])
            
        resultado_final = list(set(escolhidos + fixos))
        return sorted(resultado_final)

    @staticmethod
    def _gerar_base(df, cols, qtd, tipo, seed_offset=0):
        """
        Geração controlada por Semente (Last Draw Hash).
        """
        # 1. Cria a Semente Mestra baseada no último sorteio (Imutável até novo sorteio)
        try:
            ultimo_sorteio_soma = int(df.iloc[0][cols].sum())
            master_seed = ultimo_sorteio_soma + (seed_offset * 1000) # Offset garante variação por bilhete
            np.random.seed(master_seed) # TRAVA O GERADOR
        except:
            np.random.seed(42 + seed_offset)

        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts()
        numeros_ordenados = freq.index.tolist() # Do mais quente para o mais frio
        
        # Lista base (Pool) de onde vamos tirar os números
        if tipo == "Hurst":
            somas = df[cols].sum(axis=1).head(60).values
            try:
                # Hurst calculation
                ts = np.array(somas)
                lags = range(2, 20)
                tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                h = poly[0] * 2.0
            except: h = 0.5
            
            # Em vez de sample aleatório, pegamos "fatias" do pool, 
            # mas usamos shuffle com seed para variar se precisarmos de muitos números
            if h > 0.55: # Tendência (Top)
                pool = numeros_ordenados[:qtd*3]
            elif h < 0.45: # Reversão (Bottom)
                pool = numeros_ordenados[-qtd*3:]
            else: # Random Walk
                pool = numeros_ordenados[:] 
            
            # Aqui está o segredo: Shuffle determinístico
            pool_lista = list(pool)
            np.random.shuffle(pool_lista)
            return set([int(x) for x in pool_lista[:qtd]])

        elif tipo == "Markov":
            ultimo_sorteio = set(df.iloc[0][cols].dropna().values)
            candidatos = []
            for i in range(1, min(100, len(df)-1)):
                jogo_passado = set(df.iloc[i][cols].dropna().values)
                if len(ultimo_sorteio.intersection(jogo_passado)) >= 2:
                    candidatos.extend(df.iloc[i-1][cols].dropna().values)
            
            if candidatos:
                # Ordena estritamente por contagem
                top = pd.Series(candidatos).value_counts().index.tolist()
                # Se precisar variar, pega um chunk maior e embaralha com seed
                pool = top[:qtd*2]
                np.random.shuffle(pool)
                return set([int(x) for x in pool[:qtd]])
            else:
                pool = numeros_ordenados[:qtd*3]
                np.random.shuffle(pool)
                return set([int(x) for x in pool[:qtd]])

        elif tipo == "Gauss":
            somas = df[cols].sum(axis=1)
            media = somas.mean()
            # Tenta achar combinação deterministicamente usando seed no sample
            pool = numeros_ordenados[:qtd*4]
            
            melhor_comb = set(pool[:qtd])
            menor_diff = float('inf')
            
            for _ in range(50): # 50 tentativas fixas
                samp = np.random.choice(pool, qtd, replace=False)
                diff = abs(sum(samp) - media)
                if diff < menor_diff:
                    menor_diff = diff
                    melhor_comb = set(samp)
                if diff < (media * 0.05): break
            
            return set([int(x) for x in melhor_comb])

        elif tipo == "Estocástico":
            candidatos = []
            for num in numeros_ordenados:
                recente = (df.head(10)[cols].values == num).sum()
                if recente <= 1: candidatos.append(num)
            
            if len(candidatos) < qtd: candidatos.extend(numeros_ordenados)
            
            pool = candidates = candidatos[:qtd*2]
            np.random.shuffle(pool)
            return set([int(x) for x in pool[:qtd]])
            
        return set([int(x) for x in numeros_ordenados[:qtd]])
