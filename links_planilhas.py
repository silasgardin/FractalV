# Arquivo: src/links_planilhas.py

"""
FRACTALV - Mapeamento de Dados (Via Web CSV)
Este arquivo contém os links diretos de exportação CSV das abas do Google Sheets.
Isso permite leitura rápida sem necessidade de credenciais de API complexas.
"""

# Dicionário de Links (Substitua as URLs abaixo pelos links que você gerou)
LINKS_CSV = {
    # Abas de Resultados
    "MEGA_SENA": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=936546416&single=true&output=csv",
    "LOTOFACIL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1063211255&single=true&output=csv",
    "QUINA": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=676865658&single=true&output=csv",
    "LOTOMANIA": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=848764653&single=true&output=csv",
    "TIMEMANIA": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1575649264&single=true&output=csv",
    "DIA_DE_SORTE": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1059501941&single=true&output=csv",
    "DUPLA_SENA": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=676865658&single=true&output=csv",
    
    # Aba de Controle Financeiro (Essencial para o Orçamento Inteligente)
    "VALORES": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHPmYqIsBMWIzdMlnuKfPDI5BI4UG_WMEdMP6OwUeojDThvp0fI6J7fywO_T7ynVsk30-JuhJJQng6/pub?gid=1620341582&single=true&output=csv"
}

# Configurações de Leitura
# Define como o Pandas deve interpretar os dados
PARAMS_LEITURA = {
    "sep": ",",          # Separador padrão de CSV do Google
    "encoding": "utf-8", # Codificação padrão
    "thousands": ".",    # Tratamento para números brasileiros (milhar)
    "decimal": ","       # Tratamento para números brasileiros (decimal)
}
