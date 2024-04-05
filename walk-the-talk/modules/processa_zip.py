"""
Funções para processar arquivos ZIP
"""

import zipfile
import pandas as pd


def lista_arquivos_zip(nome_zip):
    """
    Abre o arquivo ZIP e retorna a lista de arquivos contidos nele
    """

    # Abre o arquivo ZIP
    with zipfile.ZipFile(nome_zip, 'r') as zip_ref:

        # Lista os arquivos contidos no ZIP
        lista_arquivos = zip_ref.namelist()

    # Retorna a lista de arquivos
    print(f'Lista de arquivos recuperada com sucesso. De {lista_arquivos[0]} a {lista_arquivos[-1]}')
    return lista_arquivos


def csv_para_dict(arquivo_zip, nome_arquivo, ano):
    """
    Extrai os dados de um CSV específico dentro do ZIP
    Formata os rótulos das colunas e os tipos de dados
    Filtra os dados para recuperar apenas a versão mais recente de cada empresa
    Retorna uma lista de dicionários com os dados para obtenção do XML de cada empresa
    """

    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        with zip_ref.open(nome_arquivo) as file:
            try:
                df = pd.read_csv(file, encoding='cp1252', sep=';', decimal=',')
                print(f"Arquivo {nome_arquivo} carregado com sucesso.")
                
                # Padroniza os rótulos das colunas
                if nome_arquivo == f'fre_cia_aberta_{ano}.csv':
                    rotulos_colunas = ['CNPJ_Companhia', 'Data_Referencia', 'Versao', 'Nome_Companhia', 'Codigo_CVM', 'Categoria_Doc', 'ID_Documento', 'Data_Recebimento', 'Link_Doc'] 
                    df = df.rename(columns=dict(zip(df.columns, rotulos_colunas)))

                # Padroniza os tipos de dados                
                for column in df.columns:
                    if 'Data' in column:
                        df[column] = pd.to_datetime(df[column]).dt.date
                    if 'Preco' in column or 'Valor' in column or 'Quantidade' in column:
                        df[column] = pd.to_numeric(df[column], errors='coerce')

                # Filtra para manter apenas a versão mais recente de cada empresa
                idx = df.groupby('CNPJ_Companhia')['Versao'].transform('max') == df['Versao']
                df_recente = df[idx]

                # Converte o DataFrame filtrado em dicionário para inserção no MongoDB
                registros_recentes = df_recente.to_dict('records')
                return registros_recentes

            except UnicodeDecodeError as e:
                print(f"Erro de decodificação: {e}")
                return None
            