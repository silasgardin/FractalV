import pandas as pd
import numpy as np
from scipy.stats import norm

class OtimizadorFinanceiro:
    """Gerencia o orçamento e a distribuição de apostas (Financial Management)"""
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

        # Ordena: Prioridade para jogos caros (Desdobramentos - Maior chance matemática)
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
    O Cérebro Matemático que compete modelos entre si.
    Modelos: Markov, Hurst, Gauss, Estocástico.
    """
    
    @staticmethod
    def executar_backtest(df_completo, cols_dezenas):
        """
        Testa qual modelo teria acertado mais no último sorteio.
        """
        try:
            # Separa: Histórico (Passado) vs Alvo (Último sorteio real)
            # df_treino = tudo menos a primeira linha (que é o último sorteio)
            # df_teste = primeira linha (o resultado que queremos prever no backtest)
            if len(df_completo) < 50: return "Padrão (Dados Insuficientes)", 0
            
            alvo_real = set(df_completo.iloc[0][cols_dezenas].dropna().astype(int).values)
            df_treino = df_completo.iloc[1:].copy()
            
            # --- MODELO 1: HURST (Tendência/Reversão) ---
            palpite_hurst = MotorInferencia._gerar_palpite_hurst(df_treino, cols_dezenas, len(alvo_real))
            acertos_hurst = len(alvo_real.intersection(palpite_hurst))
            
            # --- MODELO 2: MARKOV (Transição) ---
            palpite_markov = MotorInferencia._gerar_palpite_markov(df_treino, cols_dezenas, len(alvo_real))
            acertos_markov = len(alvo_real.intersection(palpite_markov))
            
            # --- MODELO 3: GAUSS (Distribuição Normal da Soma) ---
            palpite_gauss = MotorInferencia._gerar_palpite_gauss(df_treino, cols_dezenas, len(alvo_real))
            acertos_gauss = len(alvo_real.intersection(palpite_gauss))
            
            # --- MODELO 4: ESTOCÁSTICO (Oscilador) ---
            palpite_stoch = MotorInferencia._gerar_palpite_estocastico(df_treino, cols_dezenas, len(alvo_real))
            acertos_stoch = len(alvo_real.intersection(palpite_stoch))
            
            # Competição
            scores = {
                "Hurst (Fractal)": acertos_hurst,
                "Markov (Cadeias)": acertos_markov,
                "Gauss (Normal)": acertos_gauss,
                "Estocástico (Oscilador)": acertos_stoch
            }
            
            melhor_modelo = max(scores, key=scores.get)
            melhor_score = scores[melhor_modelo]
            
            return melhor_modelo, melhor_score, scores
        except Exception as e:
            # print(f"Erro Backtest: {e}")
            return "Padrão (Erro)", 0, {}

    @staticmethod
    def prever_proximo(modelo_vencedor, df_completo, cols_dezenas, qtd_numeros_gerar):
        """Gera os números para o PRÓXIMO sorteio usando o modelo vencedor"""
        if "Hurst" in modelo_vencedor:
            return MotorInferencia._gerar_palpite_hurst(df_completo, cols_dezenas, qtd_numeros_gerar)
        elif "Markov" in modelo_vencedor:
            return MotorInferencia._gerar_palpite_markov(df_completo, cols_dezenas, qtd_numeros_gerar)
        elif "Gauss" in modelo_vencedor:
            return MotorInferencia._gerar_palpite_gauss(df_completo, cols_dezenas, qtd_numeros_gerar)
        elif "Estocástico" in modelo_vencedor:
            return MotorInferencia._gerar_palpite_estocastico(df_completo, cols_dezenas, qtd_numeros_gerar)
        else:
            # Fallback: Frequência Simples
            todas = df_completo.head(50)[cols_dezenas].values.flatten()
            todas = todas[~np.isnan(todas)]
            freq = pd.Series(todas).value_counts()
            top = freq.head(qtd_numeros_gerar).index.tolist()
            return sorted([int(x) for x in top])

    # --- LÓGICAS INTERNAS DOS MODELOS ---
    
    @staticmethod
    def _gerar_palpite_hurst(df, cols, qtd):
        # Calcula Hurst da Soma
        somas = df[cols].sum(axis=1).head(60).values
        hurst = MotorFractal.calcular_hurst(somas)
        
        todas = df.head(50)[cols].values.flatten()
        freq = pd.Series(todas[~np.isnan(todas)]).value_counts()
        numeros = freq.index.tolist()
        
        if hurst > 0.55: # Tendência (Pega Quentes)
            escolhidos = numeros[:qtd]
        elif hurst < 0.45: # Reversão (Pega Frios/Atrasados)
            escolhidos = numeros[-qtd:]
        else: # Aleatório
            import random
            escolhidos = random.sample(numeros[:qtd*2], qtd) # Sorteia entre os top 2x
            
        return set([int(x) for x in escolhidos])

    @staticmethod
    def _gerar_palpite_markov(df, cols, qtd):
        # Lógica: Quais números saíram após os números do último sorteio (linha 0 do df de treino)
        ultimo_sorteio = set(df.iloc[0][cols].dropna().values)
        candidatos = []
        
        for i in range(1, len(df)-1):
            jogo_passado = set(df.iloc[i][cols].dropna().values)
            # Se o jogo passado se parece com o último (interseção > 3)
            if len(ultimo_sorteio.intersection(jogo_passado)) >= 2:
                # Pega o resultado SEGUINTE (que aconteceu depois dele)
                candidatos.extend(df.iloc[i-1][cols].dropna().values)
        
        if not candidatos:
            # Fallback se não achar padrão
            return MotorInferencia._gerar_palpite_hurst(df, cols, qtd)
            
        contagem = pd.Series(candidatos).value_counts()
        top = contagem.head(qtd).index.tolist()
        return set([int(x) for x in top])

    @staticmethod
    def _gerar_palpite_gauss(df, cols, qtd):
        # Lógica: Gerar jogo cuja SOMA esteja próxima da média histórica (Topo do Sino de Gauss)
        somas = df[cols].sum(axis=1)
        media_ideal = somas.mean()
        
        todas = df.head(50)[cols].values.flatten()
        freq = pd.Series(todas[~np.isnan(todas)]).value_counts()
        disponiveis = freq.index.tolist()
        
        # Tenta montar um jogo greedy que se aproxime da média
        escolhidos = []
        soma_atual = 0
        
        # Pega números aleatórios ponderados pela frequência até atingir a soma
        import random
        attempts = 0
        while attempts < 100:
            candidatos = random.sample(disponiveis[:qtd*3], qtd)
            if abs(sum(candidatos) - media_ideal) < (media_ideal * 0.1): # Margem de 10%
                return set([int(x) for x in candidatos])
            attempts += 1
            
        return set([int(x) for x in disponiveis[:qtd]]) # Fallback

    @staticmethod
    def _gerar_palpite_estocastico(df, cols, qtd):
        # Lógica: (Último - Min) / (Max - Min). Se < 0.2 (Oversold), deve sair.
        todas = df.head(100)[cols].values.flatten()
        freq = pd.Series(todas[~np.isnan(todas)]).value_counts()
        
        candidatos_fortes = []
        for num in freq.index:
            # Simula um oscilador simples de frequência recente vs total
            freq_recente = (df.head(10)[cols].values == num).sum()
            freq_total = freq[num] / 10.0 # Normaliza
            
            # Se apareceu pouco recentemente mas tem histórico alto (Oversold)
            if freq_recente <= 1 and freq_total > 2:
                candidatos_fortes.append(num)
                
        if len(candidatos_fortes) < qtd:
            mais_frequentes = freq.index.tolist()
            falta = qtd - len(candidatos_fortes)
            candidatos_fortes.extend([x for x in mais_frequentes if x not in candidatos_fortes][:falta])
            
        return set([int(x) for x in candidatos_fortes[:qtd]])

class MotorFractal:
    @staticmethod
    def calcular_hurst(serie_numerica):
        try:
            ts = np.array(serie_numerica)
            lags = range(2, 20)
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0] * 2.0
        except: return 0.5
