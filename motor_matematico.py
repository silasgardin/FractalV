import pandas as pd
import numpy as np

class OtimizadorFinanceiro:
    def __init__(self, link_csv_valores):
        """
        Inicializa lendo a tabela de preços diretamente do link CSV ou arquivo local.
        """
        # Carrega o CSV (simulando a leitura do link que você configurou no links_planilhas.py)
        # Na prática, usamos pd.read_csv(link_csv_valores)
        # Aqui, vou assumir que o dataframe já entra limpo ou carregado
        self.df_precos = None
        self.url = link_csv_valores

    def carregar_dados(self):
        try:
            # Tenta ler do link (ou arquivo local para testes)
            # Configuração específica para o formato brasileiro de números (milhar=. decimal=,)
            df = pd.read_csv(self.url, decimal=",", thousands=".")
            
            # Limpeza e Padronização
            # Remove "R$ ", pontos de milhar e troca vírgula por ponto para converter em FLOAT
            df['Preço Total (R$)'] = df['Preço Total (R$)'].astype(str).apply(
                lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
            )
            
            # Padronizar nomes das loterias (tudo maiúsculo e sem acento para facilitar busca)
            df['Loteria_Key'] = df['Loteria'].str.upper().str.replace(' ', '_').str.replace('Á', 'A')
            
            self.df_precos = df
            return True
        except Exception as e:
            print(f"Erro ao carregar tabela de valores: {e}")
            return False

    def calcular_melhor_estrategia(self, jogo, orcamento):
        """
        Define como gastar o orçamento:
        1. Tenta o jogo com MAIOR quantidade de dezenas possível (Desdobramento).
        2. Usa o troco para fazer jogos simples.
        """
        if self.df_precos is None:
            self.carregar_dados()

        # Filtra a tabela apenas para o jogo solicitado (ex: MEGA_SENA)
        jogo_key = jogo.upper().replace(' ', '_')
        tabela_jogo = self.df_precos[self.df_precos['Loteria_Key'].str.contains(jogo_key)].copy()
        
        if tabela_jogo.empty:
            return {"erro": f"Jogo {jogo} não encontrado na tabela de preços."}

        # Ordena por preço (do maior para o menor)
        tabela_jogo = tabela_jogo.sort_values(by='Preço Total (R$)', ascending=False)

        estrategia = {
            "jogo": jogo,
            "orcamento_inicial": orcamento,
            "carrinho": [],
            "sobra": 0
        }

        saldo = orcamento

        # Passo 1: Busca o maior jogo "bomba" possível (Desdobramento)
        # Ex: Se tenho R$ 50,00, ele vai tentar pegar o jogo de 7 dezenas (R$ 42,00) primeiro.
        for _, row in tabela_jogo.iterrows():
            custo = row['Preço Total (R$)']
            qtd_dezenas = row['Qtd. Dezenas']
            
            if saldo >= custo:
                # Quantos jogos desse tipo cabem? (Geralmente priorizamos 1 forte)
                qtd_comprar = int(saldo // custo)
                
                # Adiciona ao carrinho
                estrategia['carrinho'].append({
                    "tipo": "Aposta Especial" if qtd_dezenas > tabela_jogo['Qtd. Dezenas'].min() else "Aposta Simples",
                    "qtd_dezenas": int(qtd_dezenas),
                    "quantidade_volantes": qtd_comprar,
                    "custo_unitario": custo,
                    "custo_total": qtd_comprar * custo,
                    "probabilidade_teorica": row['Probabilidade (1 em...)']
                })
                
                saldo -= (qtd_comprar * custo)
        
        estrategia['sobra'] = round(saldo, 2)
        return estrategia

# --- MÓDULO MATEMÁTICO (HURST & FRACTAL) ---

class MotorFractal:
    @staticmethod
    def calcular_hurst(serie_numerica):
        """
        Calcula o Expoente de Hurst para definir se usamos tendência ou reversão.
        Entrada: Lista ou Array de resultados (somas ou dezenas específicas).
        """
        try:
            ts = np.array(serie_numerica)
            lags = range(2, 20)
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            hurst = poly[0] * 2.0 
            return hurst
        except:
            return 0.5 # Retorno neutro em caso de erro (dados insuficientes)

# --- EXECUÇÃO DE EXEMPLO (Simulação) ---
if __name__ == "__main__":
    # Simulação de uso
    # 1. Instancia o otimizador com o link (aqui simulado com o arquivo local)
    otimizador = OtimizadorFinanceiro("src/Oraculo_DB_Master - Vlr_jogo.csv") # Em produção, usar link WEB
    
    # 2. Usuário define: Quero gastar R$ 50,00 na Mega Sena
    resultado = otimizador.calcular_melhor_estrategia("MEGA_SENA", 50.00)
    
    print(f"--- ESTRATÉGIA FINANCEIRA PARA {resultado['jogo']} ---")
    print(f"Orçamento: R$ {resultado['orcamento_inicial']}")
    for item in resultado['carrinho']:
        print(f"-> {item['quantidade_volantes']}x Jogos de {item['qtd_dezenas']} dezenas")
        print(f"   Custo: R$ {item['custo_total']} | Tipo: {item['tipo']}")
    print(f"Troco: R$ {resultado['sobra']}")
