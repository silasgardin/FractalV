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
        except: return False

    def calcular_melhor_estrategia(self, jogo, orcamento):
        if self.df_precos is None:
            if not self.carregar_dados(): return {"erro": "Erro crítico: Tabela de preços indisponível."}

        jogo_key = str(jogo).upper().replace(' ', '_')
        tabela = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key, na=False)].copy()
        if tabela.empty: return {"erro": f"Jogo '{jogo}' não encontrado."}

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
                    estrategia['carrinho'].append({"qtd_volantes": qtd, "dezenas": dezenas_val, "custo_total": qtd * custo})
                    saldo -= (qtd * custo)
            except: continue
        estrategia['sobra'] = round(saldo, 2)
        return estrategia

class MotorInferencia:
    """
    Cérebro Matemático V7.0 - Deep Backtest (Janela Deslizante)
    """
    
    @staticmethod
    def executar_backtest_profundo(df_completo, cols_dezenas, profundidade=12):
        """
        Testa os modelos nos últimos 'profundidade' jogos e retorna o campeão da temporada.
        """
        try:
            if len(df_completo) < (profundidade + 50): 
                return "Hurst (Padrão)", 0, {} # Falta de dados históricos
            
            # Placar Geral Acumulado
            placar_geral = {
                "Hurst": 0,
                "Markov": 0,
                "Gauss": 0,
                "Estocástico": 0
            }
            
            # Loop reverso: Testa do jogo T-1 até T-12
            # Isso simula como se estivéssemos no passado tentando acertar aquele jogo
            for i in range(profundidade):
                # O alvo é o jogo i (sendo 0 o último, 1 o penúltimo...)
                alvo_real = set(df_completo.iloc[i][cols_dezenas].dropna().astype(int).values)
                qtd_alvo = len(alvo_real)
                
                # O treino é tudo o que veio DEPOIS do alvo (na tabela, índices maiores = passado)
                df_treino = df_completo.iloc[i+1:].copy()
                
                # Gera previsões para aquele dia específico
                # Usamos seed fixo para garantir consistência no teste
                p_hurst = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Hurst", seed_offset=i)
                p_markov = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Markov", seed_offset=i)
                p_gauss = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Gauss", seed_offset=i)
                p_stoch = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Estocástico", seed_offset=i)
                
                # Pontuação: Simples soma de acertos
                placar_geral["Hurst"] += len(alvo_real.intersection(p_hurst))
                placar_geral["Markov"] += len(alvo_real.intersection(p_markov))
                placar_geral["Gauss"] += len(alvo_real.intersection(p_gauss))
                placar_geral["Estocástico"] += len(alvo_real.intersection(p_stoch))
            
            melhor_modelo = max(placar_geral, key=placar_geral.get)
            
            # Formata o placar para exibição
            stats_view = {k: f"{v} acertos (últimos {profundidade} jogos)" for k, v in placar_geral.items()}
            
            return melhor_modelo, placar_geral[melhor_modelo], placar_geral
        except Exception as e:
            return "Hurst", 0, {}

    @staticmethod
    def prever_proximo(modelo_vencedor, df_completo, cols_dezenas, qtd_numeros_gerar, fixos=[], excluidos=[], seed_index=0):
        # Mapeamento de nomes
        tipo = "Hurst"
        if "Markov" in modelo_vencedor: tipo = "Markov"
        elif "Gauss" in modelo_vencedor: tipo = "Gauss"
        elif "Estocástico" in modelo_vencedor: tipo = "Estocástico"
        
        vagas_abertas = qtd_numeros_gerar - len(fixos)
        if vagas_abertas <= 0: return sorted(list(set(fixos))[:qtd_numeros_gerar])
        
        # Gera candidatos brutos (com excesso para filtragem)
        candidatos_brutos = MotorInferencia._gerar_base(df_completo, cols_dezenas, qtd_numeros_gerar * 5, tipo, seed_offset=seed_index)
        
        candidatos_validos = [n for n in candidatos_brutos if n not in excluidos and n not in fixos]
        escolhidos = candidatos_validos[:vagas_abertas]
        
        if len(escolhidos) < vagas_abertas:
            todas = df_completo.head(50)[cols_dezenas].values.flatten()
            todas = todas[~np.isnan(todas)]
            freq = pd.Series(todas).value_counts().index.tolist()
            extras = [n for n in freq if n not in excluidos and n not in fixos and n not in escolhidos]
            escolhidos.extend(extras[:vagas_abertas - len(escolhidos)])
            
        resultado_final = list(set(escolhidos + fixos))
        return sorted(resultado_final)

    @staticmethod
    def _gerar_base(df, cols, qtd, tipo, seed_offset=0):
        # Semente Determinística baseada na soma do último resultado conhecido naquele contexto
        try:
            seed_val = int(df.iloc[0][cols].sum()) + (seed_offset * 777)
            np.random.seed(seed_val)
        except: np.random.seed(42)

        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts()
        numeros_ordenados = freq.index.tolist()
        
        if tipo == "Hurst":
            somas = df[cols].sum(axis=1).head(60).values
            try:
                ts = np.array(somas)
                lags = range(2, 20)
                tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                h = poly[0] * 2.0
            except: h = 0.5
            
            pool = numeros_ordenados[:qtd*3] if h > 0.55 else (numeros_ordenados[-qtd*3:] if h < 0.45 else numeros_ordenados[:])
            pool_lista = list(pool)
            np.random.shuffle(pool_lista)
            return set(pool_lista[:qtd])

        elif tipo == "Markov":
            ultimo_sorteio = set(df.iloc[0][cols].dropna().values)
            candidatos = []
            for i in range(1, min(100, len(df)-1)):
                jogo_passado = set(df.iloc[i][cols].dropna().values)
                if len(ultimo_sorteio.intersection(jogo_passado)) >= 2:
                    candidatos.extend(df.iloc[i-1][cols].dropna().values)
            
            if candidatos:
                top = pd.Series(candidatos).value_counts().index.tolist()
                pool = top[:qtd*2]
                np.random.shuffle(pool)
                return set(pool[:qtd])
            else:
                pool = numeros_ordenados[:qtd*3]
                np.random.shuffle(pool)
                return set(pool[:qtd])

        elif tipo == "Gauss":
            somas = df[cols].sum(axis=1)
            media = somas.mean()
            pool = numeros_ordenados[:qtd*4]
            melhor_comb = set(pool[:qtd])
            menor_diff = float('inf')
            for _ in range(50):
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
            return set(pool[:qtd])
            
        return set(numeros_ordenados[:qtd])

class MotorFractal:
    pass
