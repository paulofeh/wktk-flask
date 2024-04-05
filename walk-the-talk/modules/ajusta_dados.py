"""
Funções para ajustar os dados extraídos, convertendo tipos de dados e formatos.
"""

from datetime import date, datetime


def date_to_datetime(data):
    """Converte um objeto datetime.date para datetime.datetime."""
    if isinstance(data, date) and not isinstance(data, datetime):
        # Converte data para datetime no início do dia (meia-noite)
        return datetime.combine(data, datetime.min.time())
    return data


def ajustar_dados(dados):
    """
    Função para ajustar os dados extraídos, convertendo tipos de dados e formatos.
    Retorna dicionário com os dados ajustados.
    """
    for chave, valor in dados.items():
        if isinstance(valor, dict):
            # Faz a chamada recursiva para dicionários aninhados
            dados[chave] = ajustar_dados(valor)
        elif isinstance(valor, list):
            # Processa cada item da lista, aplicando ajustes recursivamente
            dados[chave] = [ajustar_dados(item) if isinstance(item, dict) else item for item in valor]
        else:
            # Converte strings numéricas para int ou float
            if isinstance(valor, str):
                if valor.isdigit():
                    dados[chave] = int(valor)
                else:
                    try:
                        dados[chave] = float(valor)
                    except ValueError:
                        # Trata campos vazios, substituindo por 0
                        dados[chave] = 0 if valor == '' else valor
            # Converte datas para datetime.datetime se necessário
            dados[chave] = date_to_datetime(valor)
    return dados




