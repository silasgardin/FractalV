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

    def obter_preco_minimo(self, jogo):
        if self.df_precos is None:
            if not self.carregar_dados(): return 5.0
        try:
            jogo_key = str(jogo).upper().replace(' ', '_')
            tabela = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key, na=False)]
            if tabela.empty: return 5.0
            return float(tabela['Preço Total (R$)'].min())
        except: return 5.0

    def calcular_melhor_estrategia(self, jogo, orcamento, modo="POTENCIA"):
        """
        modo: "POTENCIA" (Foco em desdobramento) ou "EQUILIBRIO" (Misto)
        """
        if self.df_precos is None:
            if not self.carregar_dados(): return {"erro": "Erro crítico: Tabela indisponível."}

        jogo_key = str(jogo).upper().replace(' ', '_')
        tabela = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key, na=False)].copy()
        if tabela.empty: return {"erro": f"Jogo '{jogo}' não encontrado."}

        estrategia = {"jogo": jogo, "orcamento_inicial": orcamento, "carrinho": [], "sobra": 0}
        
        # --- LÓGICA DE EQUILÍBRIO (HÍBRIDA) ---
        if modo == "EQUILIBRIO":
            # 60% para Potência, 40% para Volume
            orcamento_power = orcamento * 0.60
            saldo_atual = orcamento
            
            # FASE 1: Potência (Jogo Forte)
            tabela_power = tabela.sort_values(by='Preço Total (R$)', ascending=False)
            for _, row in tabela_power.iterrows():
                custo = float(row['Preço Total (R$)'])
                if custo <= 0: continue
                
                if orcamento_power >= custo:
                    qtd = int(orcamento_power // custo)
                    if qtd > 0:
                        qtd = max(1, qtd)
                        dezenas_val = int(float(row['Qtd. Dezenas']))
                        estrategia['carrinho'].append({"qtd_volantes": qtd, "dezenas": dezenas_val, "custo_total": qtd * custo})
                        saldo_atual -= (qtd * custo)
                        break 
            
            # FASE 2: Volume com o troco (Jogos Baratos)
            tabela_cob = tabela.sort_values(by='Preço Total (R$)', ascending=True)
            try:
                row = tabela_cob.iloc[0]
                custo = float(row['Preço Total (R$)'])
                dezenas_val = int(float(row['Qtd. Dezenas']))
                
                if saldo_atual >= custo:
                    qtd = int(saldo_atual // custo)
                    if qtd > 0:
                        estrategia['carrinho'].append({
                            "qtd_volantes": qtd, 
                            "dezenas": dezenas_val, 
                            "custo_total": qtd * custo
                        })
                        saldo_atual -= (qtd * custo)
            except: pass
            
            estrategia['sobra'] = round(saldo_atual, 2)
            return estrategia

        # --- LÓGICA DE POTÊNCIA (PADRÃO / ELSE) ---
        else:
            tabela = tabela.sort_values(by='Preço Total (R$)', ascending=False)
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
        return MotorInferencia.gerar_aposta_final(modelo_vencedor, df_completo, cols_dezenas, qtd_numeros_gerar, fixos, excluidos, seed_mix=seed_index)

    @staticmethod
    def gerar_aposta_final(modelo_nome, df, cols, qtd_alvo, fixos=[], excluidos=[], seed_mix=0):
        tipo = "Hurst"
        if "IA" in modelo_nome: tipo = "IA"
        elif "Markov" in modelo_nome: tipo = "Markov"
        elif "Gauss" in modelo_nome: tipo = "Gauss"
        vagas = qtd_alvo - len(fixos)
        if vagas <= 0: return sorted(list(set(fixos))[:qtd_alvo])
        tamanho_pool = max(qtd_alvo * 3, 40)
        ranking = MotorInferencia._obter_ranking(tipo, df, cols, tamanho_pool)
        candidatos = [n for n in ranking if n not in excluidos and n not in fixos]
        try:
            seed_val = int(df.iloc[0][cols].sum()) + (seed_mix * 9999)
            rng = np.random.default_rng(seed_val)
            corte_elite = min(len(candidatos), vagas + 10) 
            elite_pool = candidatos[:corte_elite]
            escolhidos = list(rng.choice(elite_pool, size=vagas, replace=False))
        except: escolhidos = candidates[:vagas]
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
        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts()
        ranking_freq = freq.index.tolist()
        if tipo == "IA":
            try:
                data = df[cols].dropna().values.astype(int)
                if len(data) < 20: return ranking_freq
                data = data[::-1] 
                X, y = [], []
                win = 5
                for i in range(len(data) - win):
                    X.append(data[i:i+win].flatten())
                    y.append(data[i+win])
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                model.fit(X, y)
                last = data[-win:].flatten().reshape(1, -1)
                pred = model.predict(last)[0]
                scores = {}
                for val in pred:
                    n = int(round(val))
                    if n > 0: scores[n] = scores.get(n, 0) + 1
                ranking_ia = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
                for n in ranking_freq:
                    if n not in ranking_ia: ranking_ia.append(n)
                return ranking_ia[:qtd_pool]
            except: return ranking_freq
        elif tipo == "Hurst":
            somas = df[cols].sum(axis=1).head(60).values
            try:
                ts = np.array(somas)
                lags = range(2, 20)
                tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                h = poly[0] * 2.0
            except: h = 0.5
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
                full = ranking_mk + [x for x in ranking_freq if x not in ranking_mk]
                return full[:qtd_pool]
            return ranking_freq[:qtd_pool]
        elif tipo == "Gauss": return ranking_freq[:qtd_pool]
        return ranking_freq[:qtd_pool]

class MotorFractal:
    pass
