import pandas as pd
import numpy as np

class OtimizadorFinanceiro:
    def __init__(self, link_csv_valores):
        self.url = link_csv_valores
        self.df_precos = None

    def carregar_dados(self):
        try:
            # Tenta ler do link (ignora linhas ruins e ajusta decimais BR)
            self.df_precos = pd.read_csv(self.url, decimal=",", thousands=".", on_bad_lines='skip')
            
            # Limpeza de moeda e conversão
            if 'Preço Total (R$)' in self.df_precos.columns:
                self.df_precos['Preço Total (R$)'] = self.df_precos['Preço Total (R$)'].astype(str).apply(
                    lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
                )
            self.df_precos['Loteria_Key'] = self.df_precos['Loteria'].str.upper().str.replace(' ', '_').str.replace('Á', 'A')
            return True
        except Exception as e:
            return False

    def calcular_melhor_estrategia(self, jogo, orcamento):
        if self.df_precos is None:
            if not self.carregar_dados():
                return {"erro": "Falha ao conectar com tabela de preços."}

        jogo_key = jogo.upper().replace(' ', '_')
        tabela = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key)].copy()
        
        if tabela.empty:
            return {"erro": f"Jogo {jogo} não configurado na tabela de preços."}

        # Ordena do maior preço para o menor (Tenta desdobramento primeiro)
        tabela = tabela.sort_values(by='Preço Total (R$)', ascending=False)

        estrategia = {"jogo": jogo, "orcamento": orcamento, "carrinho": [], "sobra": 0}
        saldo = orcamento

        for _, row in tabela.iterrows():
            custo = row['Preço Total (R$)']
            if saldo >= custo:
                qtd = int(saldo // custo)
                estrategia['carrinho'].append({
                    "qtd_volantes": qtd,
                    "dezenas": int(row['Qtd. Dezenas']),
                    "custo_total": qtd * custo,
                    "probabilidade": row['Probabilidade (1 em...)']
                })
                saldo -= (qtd * custo)
        
        estrategia['sobra'] = round(saldo, 2)
        return estrategia

class MotorFractal:
    @staticmethod
    def diagnosticar_tendencia(serie_dados):
        """
        Executa o Backtest Matemático imediato (Hurst) e define a estratégia.
        Retorna: (Valor Hurst, Nome da Estratégia, Recomendação Técnica)
        """
        try:
            # Cálculo Simplificado de Hurst
            ts = np.array(serie_dados)
            lags = range(2, 20)
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            hurst = poly[0] * 2.0
            
            # Lógica de Decisão Automática
            if hurst > 0.6:
                return hurst, "TENDÊNCIA FRACTAL (Seguir)", "O Backtest indica persistência. Aposte na repetição de padrões recentes."
            elif hurst < 0.4:
                return hurst, "REVERSÃO À MÉDIA (Corrigir)", "O Backtest indica estresse elástico. Aposte contra os últimos números."
            else:
                return hurst, "ESTATÍSTICA PURA (Conservador)", "Série em Random Walk. Use médias móveis e evite riscos."
        except:
            return 0.5, "DADOS INSUFICIENTES", "Não foi possível calcular o fractal."
