import pandas as pd
import numpy as np

class OtimizadorFinanceiro:
    def __init__(self, link_csv_valores):
        self.url = link_csv_valores
        self.df_precos = None

    def carregar_dados(self):
        try:
            # 1. Leitura robusta: Pula linhas ruins e usa padrão brasileiro
            self.df_precos = pd.read_csv(self.url, decimal=",", thousands=".", on_bad_lines='skip')
            
            # 2. LIMPEZA CRÍTICA: Remove linhas onde a coluna 'Loteria' está vazia
            # Isso resolve o erro "ValueError" causado por linhas em branco no final do arquivo
            self.df_precos.dropna(subset=['Loteria'], inplace=True)
            
            # 3. Tratamento de Moeda (R$)
            if 'Preço Total (R$)' in self.df_precos.columns:
                self.df_precos['Preço Total (R$)'] = self.df_precos['Preço Total (R$)'].astype(str).apply(
                    lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.').strip()) if isinstance(x, str) else x
                )
            
            # 4. Cria Chave de Busca (Maiúscula e sem acentos)
            # O .astype(str) garante que não trave mesmo se tiver número no meio do texto
            self.df_precos['Loteria_Key'] = self.df_precos['Loteria'].astype(str).str.upper().str.replace(' ', '_').str.replace('Á', 'A')
            
            return True
        except Exception as e:
            # Em produção, retornamos False para o app tratar
            return False

    def calcular_melhor_estrategia(self, jogo, orcamento):
        # Garante carregamento
        if self.df_precos is None:
            if not self.carregar_dados():
                return {"erro": "Erro crítico: Não foi possível ler a tabela de preços (Vlr_jogo.csv)."}

        # Prepara chave de busca
        jogo_key = str(jogo).upper().replace(' ', '_')
        
        # 5. FILTRO BLINDADO
        # na=False diz: "Se a linha tiver erro/vazio, ignore-a, não trave o app"
        tabela = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key, na=False)].copy()
        
        if tabela.empty:
            return {"erro": f"Jogo '{jogo}' não encontrado na tabela de preços."}

        # Ordena: Prioridade para jogos caros (Desdobramentos)
        tabela = tabela.sort_values(by='Preço Total (R$)', ascending=False)

        estrategia = {
            "jogo": jogo,
            "orcamento_inicial": orcamento,
            "carrinho": [],
            "sobra": 0
        }

        saldo = orcamento

        # Lógica de "Enchimento de Carrinho"
        for _, row in tabela.iterrows():
            try:
                custo = float(row['Preço Total (R$)'])
                if custo <= 0: continue # Evita loop infinito se custo for 0
                
                if saldo >= custo:
                    qtd = int(saldo // custo)
                    
                    # Tenta pegar a quantidade de dezenas de forma segura
                    try:
                        dezenas_val = int(float(row['Qtd. Dezenas']))
                    except:
                        dezenas_val = 0
                        
                    estrategia['carrinho'].append({
                        "qtd_volantes": qtd,
                        "dezenas": dezenas_val,
                        "custo_total": qtd * custo,
                        "probabilidade": row.get('Probabilidade (1 em...)', 'N/A')
                    })
                    
                    saldo -= (qtd * custo)
            except:
                continue # Pula linha se houver erro de dado nela
        
        estrategia['sobra'] = round(saldo, 2)
        return estrategia

class MotorFractal:
    @staticmethod
    def diagnosticar_tendencia(serie_dados):
        """
        Calcula o Expoente de Hurst para definir se estamos em Tendência ou Reversão.
        """
        try:
            if len(serie_dados) < 10:
                return 0.5, "DADOS INSUFICIENTES", "Histórico muito curto."

            # R/S Analysis Simplificada
            ts = np.array(serie_dados)
            lags = range(2, 20)
            
            # Cálculo da volatilidade em diferentes escalas (tau)
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            
            if len(tau) < 2: return 0.5, "ERRO MATEMÁTICO", "Série inválida."
            
            # Regressão linear para achar o coeficiente H
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            hurst = poly[0] * 2.0
            
            # Classificação
            if hurst > 0.55:
                return hurst, "TENDÊNCIA FRACTAL 📈", "O mercado tem memória positiva. Aposte na repetição."
            elif hurst < 0.45:
                return hurst, "REVERSÃO À MÉDIA 📉", "O mercado está esticado. Aposte na correção (contrário)."
            else:
                return hurst, "ALEATORIEDADE PURA 🎲", "Sem padrão claro. Seja conservador."
        except:
            return 0.5, "ERRO NO CÁLCULO", "Falha na execução matemática."
