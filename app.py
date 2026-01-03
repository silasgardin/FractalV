import pandas as pd
import numpy as np
from scipy.stats import norm

class OtimizadorFinanceiro:
    """Gerencia o orçamento e a distribuição de apostas"""
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
    O Cérebro Matemático com suporte a Filtros Manuais.
    """
    
    @staticmethod
    def executar_backtest(df_completo, cols_dezenas):
        """Testa qual modelo teria acertado mais no último sorteio."""
        try:
            if len(df_completo) < 50: return "Padrão (Dados Insuficientes)", 0, {}
            
            alvo_real = set(df_completo.iloc[0][cols_dezenas].dropna().astype(int).values)
            df_treino = df_completo.iloc[1:].copy()
            qtd_alvo = len(alvo_real)
            
            # Gera palpites SEM filtros para o teste puro
            p_hurst = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Hurst")
            p_markov = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Markov")
            p_gauss = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Gauss")
            p_stoch = MotorInferencia._gerar_base(df_treino, cols_dezenas, qtd_alvo, "Estocástico")
            
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
    def prever_proximo(modelo_vencedor, df_completo, cols_dezenas, qtd_numeros_gerar, fixos=[], excluidos=[]):
        """Gera números usando o modelo vencedor + Filtros do Usuário"""
        
        # 1. Identifica estratégia base
        tipo = "Hurst"
        if "Markov" in modelo_vencedor: tipo = "Markov"
        elif "Gauss" in modelo_vencedor: tipo = "Gauss"
        elif "Estocástico" in modelo_vencedor: tipo = "Estocástico"
        
        # 2. Calcula quantas vagas restam (Total - Fixos)
        vagas_abertas = qtd_numeros_gerar - len(fixos)
        if vagas_abertas <= 0: return sorted(list(set(fixos))[:qtd_numeros_gerar])
        
        # 3. Gera candidatos (pedimos mais para poder filtrar os excluídos depois)
        candidatos_brutos = MotorInferencia._gerar_base(df_completo, cols_dezenas, qtd_numeros_gerar * 3, tipo)
        
        # 4. Aplica Filtros (Remove Excluídos e Fixos já presentes)
        candidatos_validos = [n for n in candidatos_brutos if n not in excluidos and n not in fixos]
        
        # 5. Preenche as vagas
        escolhidos = candidatos_validos[:vagas_abertas]
        
        # Se faltar número (devido aos filtros agressivos), completa com aleatórios válidos
        if len(escolhidos) < vagas_abertas:
            todas = df_completo.head(50)[cols_dezenas].values.flatten()
            todas = todas[~np.isnan(todas)]
            freq = pd.Series(todas).value_counts().index.tolist()
            extras = [n for n in freq if n not in excluidos and n not in fixos and n not in escolhidos]
            escolhidos.extend(extras[:vagas_abertas - len(escolhidos)])
            
        resultado_final = list(set(escolhidos + fixos))
        return sorted(resultado_final)

    # --- MOTORES INTERNOS ---
    @staticmethod
    def _gerar_base(df, cols, qtd, tipo):
        # Lógica centralizada de geração
        todas = df.head(50)[cols].values.flatten()
        todas = todas[~np.isnan(todas)]
        freq = pd.Series(todas).value_counts()
        numeros = freq.index.tolist()
        
        if tipo == "Hurst":
            somas = df[cols].sum(axis=1).head(60).values
            try:
                # Cálculo Hurst rápido
                ts = np.array(somas)
                lags = range(2, 20)
                tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                h = poly[0] * 2.0
            except: h = 0.5
            
            if h > 0.55: return set([int(x) for x in numeros[:qtd]]) # Quentes
            elif h < 0.45: return set([int(x) for x in numeros[-qtd:]]) # Frios
            else: 
                import random
                return set([int(x) for x in random.sample(numeros[:qtd*2], qtd)])

        elif tipo == "Markov":
            ultimo_sorteio = set(df.iloc[0][cols].dropna().values)
            candidatos = []
            for i in range(1, min(100, len(df)-1)):
                jogo_passado = set(df.iloc[i][cols].dropna().values)
                if len(ultimo_sorteio.intersection(jogo_passado)) >= 2:
                    candidatos.extend(df.iloc[i-1][cols].dropna().values)
            
            if candidatos:
                top = pd.Series(candidatos).value_counts().head(qtd).index.tolist()
                return set([int(x) for x in top])
            else:
                return set([int(x) for x in numeros[:qtd]]) # Fallback

        elif tipo == "Gauss":
            somas = df[cols].sum(axis=1)
            media = somas.mean()
            import random
            # Tenta achar combinação perto da média
            for _ in range(50):
                samp = random.sample(numeros[:qtd*3], qtd)
                if abs(sum(samp) - media) < (media * 0.15):
                    return set([int(x) for x in samp])
            return set([int(x) for x in numeros[:qtd]])

        elif tipo == "Estocástico":
            # Oversold: Apareceu pouco recentemente mas é frequente no geral
            candidatos = []
            for num in numeros:
                recente = (df.head(10)[cols].values == num).sum()
                if recente <= 1: candidatos.append(num)
            
            if len(candidatos) < qtd: candidatos.extend(numeros)
            return set([int(x) for x in candidatos[:qtd]])
            
        return set([int(x) for x in numeros[:qtd]])

class MotorFractal:
    # Apenas helper para Hurst externo se precisar
    pass
