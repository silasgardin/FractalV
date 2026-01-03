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
            
            # --- CORREÇÃO DO ERRO ---
            # Remove linhas que estejam totalmente vazias ou sem nome de loteria
            self.df_precos.dropna(subset=['Loteria'], inplace=True)
            
            # Limpeza de moeda e conversão
            if 'Preço Total (R$)' in self.df_precos.columns:
                self.df_precos['Preço Total (R$)'] = self.df_precos['Preço Total (R$)'].astype(str).apply(
                    lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
                )
            
            # Cria a chave de busca (Maiúscula e sem espaços)
            self.df_precos['Loteria_Key'] = self.df_precos['Loteria'].str.upper().str.replace(' ', '_').str.replace('Á', 'A')
            return True
        except Exception as e:
            # print(f"Erro debug: {e}") # Descomente para ver erros no log
            return False

    def calcular_melhor_estrategia(self, jogo, orcamento):
        # Garante que os dados estão carregados
        if self.df_precos is None:
            if not self.carregar_dados():
                return {"erro": "Falha ao conectar com tabela de preços ou tabela vazia."}

        jogo_key = jogo.upper().replace(' ', '_')
        
        # --- CORREÇÃO DO ERRO ---
        # Adicionado na=False para ignorar falhas de leitura em linhas sujas
        tabela = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key, na=False)].copy()
        
        if tabela.empty:
            return {"erro": f"Jogo {jogo} não encontrado na tabela de preços (Verifique nomes no CSV)."}

        # Ordena do maior preço para o menor (Tenta desdobramento primeiro)
        tabela = tabela.sort_values(by='Preço Total (R$)', ascending=False)

        estrategia = {"jogo": jogo, "orcamento": orcamento, "carrinho": [], "sobra": 0}
        saldo = orcamento

        for _, row in tabela.iterrows():
            custo = row['Preço Total (R$)']
            # Proteção contra custo zero ou negativo
            if custo <= 0: continue
            
            if saldo >= custo:
                qtd = int(saldo // custo)
                
                # Tratamento para pegar a quantidade de dezenas (pode vir como int ou float)
                try:
                    q_dezenas = int(row['Qtd. Dezenas'])
                except:
                    q_dezenas = 0
                
                estrategia['carrinho'].append({
                    "qtd_volantes": qtd,
                    "dezenas": q_dezenas,
                    "custo_total": qtd * custo,
                    "probabilidade": row.get('Probabilidade (1 em...)', 'N/A')
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
            if len(serie_dados) < 10:
                return 0.5, "DADOS INSUFICIENTES", "Histórico curto demais."

            # Cálculo Simplificado de Hurst
            ts = np.array(serie_dados)
            lags = range(2, 20)
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            
            # Evita erro de divisão por zero ou log de zero
            if len(tau) < 2: return 0.5, "ERRO CÁLCULO", "Série inválida."
            
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            hurst = poly[0] * 2.0
            
            # Lógica de Decisão Automática
            if hurst > 0.55:
                return hurst, "TENDÊNCIA FRACTAL (Seguir)", "O Backtest indica persistência."
            elif hurst < 0.45:
                return hurst, "REVERSÃO À MÉDIA (Corrigir)", "O Backtest indica estresse elástico."
            else:
                return hurst, "ESTATÍSTICA PURA (Conservador)", "Série em Random Walk."
        except:
            return 0.5, "ERRO NO FRACTAL", "Não foi possível calcular."
