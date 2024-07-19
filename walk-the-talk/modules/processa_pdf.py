"""
Funções para extrair e processar arquivos PDF.
"""

import os
import base64
import xml.etree.ElementTree as ET
from io import StringIO
import fitz


def extrair_pdf_de_xml(caminho_xml, codigo_cvm, tag_de_interesse):
    """
    Função para extrair o PDF de um XML
    caminho_xml: caminho do arquivo XML a ser processado
    codigo_cvm: código CVM da empresa
    tag_de_interesse: tag do XML que contém o PDF a ser extraído
    Retorna True se o PDF foi extraído com sucesso e False caso contrário
    Retorna o caminho do PDF extraído
    """

    # Define o caminho onde o arquivo ZIP será salvo
    caminho_local = os.path.join(os.getcwd(), 'arquivos_cvm\\')
    os.makedirs(caminho_local, exist_ok=True)

    try:
        # Abrir e ler o arquivo XML com a codificação 'cp1252'
        with open(caminho_xml, 'r', encoding='cp1252') as file:
            xml_content = file.read()

        # Parsear o XML
        tree = ET.parse(StringIO(xml_content))
        root = tree.getroot()

        # Encontrar a tag de interesse e extrair os dados do PDF
        tag_interesse_el = root.find(f'.//{tag_de_interesse}')
        if tag_interesse_el is not None:
            nome_arquivo_pdf_el = tag_interesse_el.find('NomeArquivoPdf')
            pdf_data_el = tag_interesse_el.find('ImagemObjetoArquivoPdf')

            # Verificar se as tags NomeArquivoPdf e ImagemObjetoArquivoPdf existem
            if nome_arquivo_pdf_el is not None and pdf_data_el is not None:
                nome_arquivo_pdf = nome_arquivo_pdf_el.text
                pdf_data = pdf_data_el.text
                pdf_bytes = base64.b64decode(pdf_data)

                nome_arquivo_saida = os.path.join(caminho_local, f"{codigo_cvm}_{tag_de_interesse}.pdf")
                with open(nome_arquivo_saida, 'wb') as pdf_file:
                    pdf_file.write(pdf_bytes)
                print(f"PDF extraído e salvo como {nome_arquivo_saida}")
                return True, nome_arquivo_saida
            else:
                # Se uma das subtags necessárias não for encontrada, imprime uma mensagem apropriada
                print(f"Subtag 'NomeArquivoPdf' ou 'ImagemObjetoArquivoPdf' não encontrada em <{tag_de_interesse}>.")
                return False, None
        else:
            print(f"Elemento <{tag_de_interesse}> não encontrado.")
            return False, None
    
    except UnicodeDecodeError as e:
        print(f"Erro de decodificação ao tentar ler o arquivo XML: {e}")
        return False, None
    except ET.ParseError as e:
        print(f"Erro ao parsear o XML: {e}")
        return False, None


def pdf_para_string(caminho_pdf, max_tokens=15000):
    """
    Função para extrair texto de um arquivo PDF, com um limite opcional de tokens.
    caminho_pdf: caminho do arquivo PDF a ser processado.
    max_tokens: número máximo de tokens que a função deve retornar.
    Retorna o texto extraído do PDF, limitado pelo número de tokens especificado.
    """

    # Abre o arquivo PDF
    pdf_document = fitz.open(caminho_pdf)

    # Inicializa a string de texto
    texto_pdf = ''
    contador_tokens = 0

    # Itera por todas as páginas do documento
    for pagina_num in range(pdf_document.page_count):
        pagina = pdf_document.load_page(pagina_num)
        texto_pagina = pagina.get_text()
        palavras_pagina = texto_pagina.split()
        
        # Adiciona palavras da página atual ao texto total, respeitando o limite de tokens
        for palavra in palavras_pagina:
            if contador_tokens + 1 <= max_tokens:
                texto_pdf += palavra + ' '
                contador_tokens += 1
            else:
                break  # Sai do loop se o limite de tokens for alcançado

        if contador_tokens >= max_tokens:
            break  # Interrompe a extração de texto das páginas seguintes se o limite for atingido

    return texto_pdf.strip()  # Retorna o texto extraído, removendo espaços extras no final
