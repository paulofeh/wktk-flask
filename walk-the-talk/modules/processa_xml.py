"""
Funções para processar arquivos XML
"""

import os
import zipfile
import xml.etree.ElementTree as ET


def extrai_xml(caminho_zip):
    """
    Extrai o arquivo XML de um ZIP
    Retorna o caminho do arquivo XML extraído
    O arquivo XML extraído é salvo em pasta dedicada no diretório corrente
    """
    
    # Define o caminho onde o arquivo ZIP será salvo
    caminho_local = os.path.join(os.getcwd(), 'arquivos_cvm\\')
    os.makedirs(caminho_local, exist_ok=True)

    # Abre o arquivo ZIP
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        # Lista os arquivos contidos no ZIP
        lista_arquivos = zip_ref.namelist()
        
        # Filtra para encontrar o arquivo XML de interesse
        try:
            arquivo_xml_interesse = [arquivo for arquivo in lista_arquivos if 'FRE' in arquivo][0]
        
            # Extrai o arquivo XML de interesse
            zip_ref.extract(arquivo_xml_interesse, caminho_local)

            # Caminho completo para o arquivo XML extraído
            arquivo_xml_path = os.path.join(caminho_local, arquivo_xml_interesse)
            print(f"Arquivo XML extraído com sucesso em {arquivo_xml_path}.")
            return arquivo_xml_path
        
        except IndexError:
            print("Nenhum arquivo XML de interesse ('FRE') encontrado no ZIP.")
            return None  


def tentar_parsear_xml(caminho, encodings):
    for encoding in encodings:
        try:
            with open(caminho, 'r', encoding=encoding) as file:
                tree = ET.parse(file)
                return tree.getroot()  # Se conseguir parsear, retorna o root
        except (ET.ParseError, UnicodeDecodeError) as e:
            print(f"Tentativa de leitura com {encoding} falhou: {e}")
    # Se todas as tentativas falharem, retorna None
    print("Não foi possível parsear o XML com as codificações fornecidas.")
    return None


def extrair_dados(xml_path, tags_buscadas):
    """
    Função para extrair dados e replicar a estrutura de um elemento XML para as tags especificadas
    xml_path: caminho do arquivo XML a ser processado
    tags_buscadas: Lista de tags que estamos buscando no XML
    Retorna dicionário contendo os dados encontrados
    """

    # Dicionário para armazenar os dados extraídos
    dados = {}

    encodings = ['cp1252', 'utf-8', 'utf-16']
    root = tentar_parsear_xml(xml_path, encodings)

    if root is None:
        print("Não foi possível obter a raiz do XML.")
        return dados
    
    else:
        
        # Função recursiva para processar cada elemento
        def processar_elemento(el):
            # Se o elemento é uma das tags buscadas, captura tudo sob ele
            if el.tag in tags_buscadas:
                return {el.tag: capturar_estrutura_aninhada(el)}
            # Caso contrário, continua a busca nos elementos filhos
            else:
                for filho in el:
                    resultado = processar_elemento(filho)
                    if resultado:
                        # Se já existe a chave e é uma lista, adiciona. Se não, transforma em lista.
                        if filho.tag in dados:
                            if isinstance(dados[filho.tag], list):
                                dados[filho.tag].append(resultado[filho.tag])
                            else:
                                dados[filho.tag] = [dados[filho.tag], resultado[filho.tag]]
                        else:
                            dados.update(resultado)

        def capturar_estrutura_aninhada(el):
            # Se não tem filhos, retorna o texto do elemento
            if not list(el):
                return el.text.strip() if el.text else ''
            # Se tem filhos, cria um dicionário para sua estrutura aninhada
            subdados = {}
            for filho in el:
                resultado_filho = capturar_estrutura_aninhada(filho)
                # Mesmo tratamento para possíveis múltiplos filhos com a mesma tag
                if filho.tag in subdados:
                    if isinstance(subdados[filho.tag], list):
                        subdados[filho.tag].append(resultado_filho)
                    else:
                        subdados[filho.tag] = [subdados[filho.tag], resultado_filho]
                else:
                    subdados[filho.tag] = resultado_filho
            return subdados

        # Inicia o processamento a partir do elemento raiz
        resultado_raiz = processar_elemento(root)
        if resultado_raiz:
            dados.update(resultado_raiz)

        return dados

