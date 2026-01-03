import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

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
            if not self.carregar_dados(): return {"erro": "Erro crítico: Tabela indisponível."}

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
    Cérebro Matemático V9.0 - Big Pool Strategy (Correção de Repetição)
    """
    
    @staticmethod
    def executar_backtest_profundo(df_completo, cols_dezenas, profundidade=12):
        try:
            if len(df_completo) < (profundidade + 50): 
                return "Hurst (Padrão)", 0, {}
            
            placar = {"IA (Random Forest)": 0, "Hurst (Fractal)": 0, "Markov (Cadeias)": 0, "Gauss (Normal)": 0}
            
            for i in range(profundidade):
                alvo = set(df_completo.iloc[i][cols_dezenas].dropna().astype(int).values)
                qtd = len(alvo)
                df_treino = df_completo.iloc[i+1:].copy()
                
                # Para backtest, usamos seed fixo (i) para reprodutibilidade
                p_ia = MotorInferencia.gerar_aposta_final("IA", df_treino, cols_dezenas, qtd, seed_mix=i)
                p_hurst = MotorInferencia.gerar_aposta_final("Hurst", df_treino, cols_dezenas, qtd, seed_mix=i)
                p_markov = MotorInferencia.gerar_aposta_final("Markov", df_treino, cols_dezenas, qtd, seed_mix=i)
                p_gauss = MotorInferencia.gerar_aposta_final("Gauss", df_treino, cols_dezenas, qtd, seed_mix=i)
                
                placar["IA (Random Forest)"] += len(alvo.intersection(p_ia))
                placar["Hurst (Fractal)"] += len(alvo.intersection(p_hurst))
                placar["Markov (Cadeias)"] += len(alvo.intersection(p_markov))
                placar["Gauss (Normal)"] += len(alvo.intersection(p_gauss))
            
            melhor = max(placar, key=placar.get)
            return melhor, placar[melhor], placar
        except Exception as e:
            return "Hurst (Padrão)", 0, {}

    @staticmethod
    def prever_proximo(modelo_vencedor, df_completo, cols_dezenas, qtd_numeros_gerar, fixos=[], excluidos=[], seed_index=0):
        # Wrapper simples que chama a função de geração final
        return MotorInferencia.gerar_aposta_final(
            modelo_vencedor, df_completo, cols_dezenas, qtd_numeros_gerar, 
            fixos, excluidos, seed_mix=seed_index
        )

    @staticmethod
    def gerar_aposta_final(modelo_nome, df, cols, qtd_alvo, fixos=[], excluidos=[], seed_mix=0):
        """
        Gera uma aposta única e variada.
        1. Obtém um RANKING longo do modelo (ex: 40-50 números).
        2. Filtra fixos/excluídos.
        3. Sorteia deterministicamente os necessários desse ranking.
        """
        
        # 1. Identifica o modelo
        tipo = "Hurst"
        if "IA" in modelo_nome: tipo = "IA"
        elif "Markov" in modelo_nome: tipo = "Markov"
        elif "Gauss" in modelo_nome: tipo = "Gauss"
        
        vagas = qtd_alvo - len(fixos)
        if vagas <= 0: return sorted(list(set(fixos))[:qtd_alvo])
        
        # 2. Obtém RANKING LONGO (Pool)
        # Pedimos muito mais números (ex: 3x a meta) para ter variedade
        tamanho_pool = max(qtd_alvo * 3, 40)
        ranking = MotorInferencia._obter_ranking(tipo, df, cols, tamanho_pool)
        
        # 3. Filtra
        candidatos = [n for n in ranking if n not in excluidos and n not in fixos]
        
        # 4. Seleção Estocástica Determinística
        # Aqui está o segredo: Usamos o seed_mix (número do jogo) para embaralhar o ranking
        try:
            # Seed única por jogo e por sorteio
            seed_val = int(df.iloc[0][cols].sum()) + (seed_mix * 9999)
            rng = np.random.default_rng(seed_val)
            
            # Pega os Top X candidatos (Elite) para sortear entre eles
            # Ex: Se preciso de 15, pego os top 25 do ranking e sorteio 15.
            # Isso garante qualidade (estão no topo) mas com variedade.
            corte_elite = min(len(candidatos), vagas + 10) 
            elite_pool = candidatos[:corte_elite]
            
            # Embaralha a elite e pega os necessários
            escolhidos = list(rng.choice(elite_pool, size=vagas, replace=False))
            
        except:
            # Fallback
            escolhidos = candidates[:vagas]
            
        # 5. Complemento (se faltar)
        if len(escolhidos) < vagas:
            todas = df.head(50)[cols].values.flatten()
            todas = todas[~np.isnan(todas)]
            freq = pd.Series(todas).value_counts().index.tolist()
            extras = [n for n in freq if n not in excluidos and n not in fixos and n not in escolhidos]
            escolhidos.extend(extras[:vagas - len(escolhidos)])
            
        final = list(set(escolhidos + fixos))
        return sorted(final)

    @staticmethod
    def _obter_ranking(tipo, df, cols, qtd_pool):
        """
        Retorna uma lista ORDENADA de candidatos (do melhor para o pior),
        sem fazer sorteios. Apenas matemática pura.
        """
        # Base de frequência (fallback universal)
        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts()
        ranking_freq = freq.index.tolist()
        
        if tipo == "IA":
            try:
                data = df[cols].dropna().values.astype(int)
                if len(data) < 20: return ranking_freq
                
                # Prepara dados para IA
                data = data[::-1] # Cronológico
                X, y = [], []
                win = 5
                for i in range(len(data) - win):
                    X.append(data[i:i+win].flatten())
                    y.append(data[i+win])
                
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                model.fit(X, y)
                
                # Previsão
                last = data[-win:].flatten().reshape(1, -1)
                pred = model.predict(last)[0]
                
                # Ordena predição por "certeza" (valor numérico)
                # Na regressão, valores inteiros repetidos indicam força
                scores = {}
                for val in pred:
                    n = int(round(val))
                    if n > 0: scores[n] = scores.get(n, 0) + 1
                
                # Ordena pelo score da IA
                ranking_ia = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
                
                # Completa com frequencia
                for n in ranking_freq:
                    if n not in ranking_ia: ranking_ia.append(n)
                
                return ranking_ia[:qtd_pool]
            except:
                return ranking_freq

        elif tipo == "Hurst":
            somas = df[cols].sum(axis=1).head(60).values
            try:
                ts = np.array(somas)
                lags = range(2, 20)
                tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                h = poly[0] * 2.0
            except: h = 0.5
            
            # Se tendência (>0.55), ranking normal. Se reversão (<0.45), inverte.
            if h < 0.45: return ranking_freq[::-1][:qtd_pool]
            return ranking_freq[:qtd_pool]

        elif tipo == "Markov":
            ultimo = set(df.iloc[0][cols].dropna().values)
            candidatos = []
            for i in range(1, min(100, len(df)-1)):
                passado = set(df.iloc[i][cols].dropna().values)
                if len(ultimo.intersection(passado)) >= 2:
                    candidatos.extend(df.iloc[i-1][cols].dropna().values)
            
            if candidatos:
                ranking_mk = pd.Series(candidatos).value_counts().index.tolist()
                # Completa com freq
                full = ranking_mk + [x for x in ranking_freq if x not in ranking_mk]
                return full[:qtd_pool]
            return ranking_freq[:qtd_pool]

        elif tipo == "Gauss":
            # Gauss prioriza números que ajustam a média
            # Retornamos ranking de frequência, o filtro Gaussiano é complexo para ranking linear
            # Então usamos a base estatística
            return ranking_freq[:qtd_pool]
            
        return ranking_freq[:qtd_pool]

class MotorFractal:
    pass
