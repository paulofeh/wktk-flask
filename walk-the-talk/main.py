"""
Este script contém funções para baixar, extrair e processar dados do Formulário de Referência (FRE) a partir do repositório de dados abertos da CVM (Comissão de Valores Mobiliários), bem como para extrair texto de arquivos PDF e interagir com a API da OpenAI para responder perguntas sobre os dados extraídos.
Autor: Paulo Fehlauer
Data: 2024-04-01
Versão: 0.1
Realizado como parte do projeto de conclusão do primeiro certificado do Master em Jornalismo de Dados, Automação e Data Storytelling do Insper.
"""

# Bibliotecas padrão do Python
import os
from datetime import datetime

# Bibliotecas de terceiros
from pymongo import MongoClient
from dotenv import load_dotenv

# Bibliotecas locais
from modules.processa_zip import lista_arquivos_zip, csv_para_dict
from modules.processa_xml import extrai_xml, tentar_parsear_xml, extrair_dados
from modules.processa_pdf import extrair_pdf_de_xml, pdf_para_string
from modules.consulta_gpt import openai_chat
from modules.ajusta_dados import ajustar_dados, date_to_datetime
from modules.download_cvm import busca_zip_cvm, busca_zip_relatorio


# VARIÁVEIS DE AMBIENTE
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
openai_api_key = os.getenv("OPENAI_API_KEY")
uri = os.getenv("MONGODB_URI")


# PROMPTS PARA A OPENAI

orientacoes = """
O seu papel nesta conversa é o de um analista especializado na pauta ESG a quem foi designada a tarefa de sumarizar questionários respondidos por empresas de capital aberto. Tais questionários estão relacionados ao seguinte contexto: "A Resolução nº 59 da Comissão de Valores Mobiliários (CVM) estabelece um novo regime de divulgação para o Formulário de Referência (FRE), principalmente no que diz respeito a informações sobre temáticas ambientais, sociais e de governança corporativa (ESG, ou ASG na sigla em Português). O modelo “pratique ou explique” adotado atende a uma demanda crescente de investidores quanto a transparência sobre tais temas." O texto enviado contém partes de um questionário e a empresa pode responder cada pergunta separadamente ou todas em um só bloco. Baseado na leitura do texto, responda as perguntas abaixo conforme instruções e retorne as respostas em formato JSON conforme as chaves apresentadas.

"""

diretrizes = """
Para todas as perguntas acima, siga sempre essas diretrizes: Sua resposta deve ser precisa, completa e baseada em trechos do questionário de forma a permitir verificação. Se não tiver certeza de uma resposta, deixe-a vazia. Não especule nem invente respostas. Seja cético em relação às informações divulgadas, reconhecendo que representam a visão da empresa e podem ser exageradamente otimistas. Mantenha suas respostas em formato JSON utilizando apenas as chaves mencionadas. Dê preferência a compromissos e afirmações concretas e mensuráveis, apresentadas por meio de dados.
"""

prompt_asg = """
1 A empresa divulga informações ASG em relatório anual ou em documento específico para esta finalidade? (chave 'divulga_esg', responda True, False ou vazio)
2 Qual a URL informada para o acesso do relatório ou documento? (chave 'url_relatorio', responda com uma lista de URLs válidas ou deixe a lista vazia)
3 A empresa considera uma matriz de materialidade ou indicadores-chave de desempenho ASG? (chave 'matriz_material', responda True, False ou vazio) 
4 Caso a resposta acima seja positiva, quais indicadores de desempenho ASG são mencionados? (chave 'matriz_indicadores', responda com uma lista de indicadores ou deixe a lista vazia)
5 A empresa leva em consideração os Objetivos de Desenvolvimento Sustentável (ODS) estabelecidos pela ONU? (chave 'ods', responda True, False ou vazio)
6 Caso a resposta seja positiva, quais os ODS mencionados no texto? (chave 'lista_ods', responda com uma lista numérica a partir das seguintes opções: 1 Erradicação da Pobreza; 2 Fome Zero e Agricultura Sustentável; 3 Saúde e Bem-Estar; 4 Educação de Qualidade; 5 Igualdade de Gênero; 6 Água Limpa e Saneamento; 7 Energia Limpa e Acessível; 8 Trabalho Decente e Crescimento Econômico; 9 Indústria, Inovação e Infraestrutura; 10 Redução das Desigualdades; 11 Cidades e Comunidades Sustentáveis; 12 Consumo e Produção Responsáveis; 13 Ação Contra a Mudança Global do Clima; 14 Vida na Água; 15 Vida Terrestre; 16 Paz, Justiça e Instituições Eficazes; 17 Parcerias e Meios de Implementação)
7 A empresa considera recomendações da Força-Tarefa para Divulgações Financeiras Relacionadas às Mudanças Climáticas (TCFD)? (chave 'tcfd', responda True, False ou vazio)
8 A empresa divulga inventários de emissão de gases do efeito estufa (GEE)? (chave 'divulga_gee', responda True, False ou vazio)
9 Caso a resposta seja positiva, quais os escopos informados? (chave 'escopos_gee', responda com uma lista numérica a partir das seguintes opções: 1 Emissões diretas de gases do efeito estufa; 2 Emissões indiretas associadas à eletricidade, calor ou vapor adquiridos; 3 Outras emissões indiretas que ocorrem nas atividades da empresa, mas fora de seu controle direto)
10 Caso a empresa divulgue inventários de emissão de GEE, qual a URL informada para acesso a esses inventários? (chave 'url_gee', responda com uma lista de URLs válidas ou deixe a lista vazia)
11 Caso a empresa mencione compromissos relativos a questões de Gênero, Raça e Diversidade, resuma-os em uma lista de até 5 itens ou retorne uma lista vazia (chave 'lista_diversidade')
12 Caso a empresa mencione compromissos relacionados à redução de emissões de GEE e mitigação das mudanças climáticas, resuma-os em uma lista de até 5 itens ou retorne uma lista vazia (chave 'lista_mitigacao')
13 O item (i) do questionário pede que a empresa explique a não adoção de cada uma das práticas acima, quando for o caso. Resuma em até 200 tokens as explicações fornecidas pela empresa, caso existam, ou deixe a resposta vazia (chave 'explique').

"""

prompt_historico = """
1 Data de fundação da empresa (chave 'data_fundacao', formato datetime, ou deixe a chave vazia)
2 Resumo do histórico da empresa (chave 'resumo_historico', resumindo em até 200 tokens os principais pontos do histórico da empresa)

"""

prompt_atividades = """
1 Principais atividades desenvolvidas pela empresa e/ou suas controladas (chave "lista_atividades", formato lista de strings, ou deixe a lista vazia).

"""

prompt_efeitos = """
1 Considerando apenas o item (b) deste questionário (principais aspectos relacionados ao cumprimento das obrigações legais e regulatórias ligadas a questões ambientais e sociais pelo emissor), resuma em até 200 tokens os principais pontos da resposta da empresa (chave 'efeitos_regulacao').

"""

prompt_oportunidades = """
1 Considerando apenas o item (d) deste questionário (oportunidades inseridas no plano de negócios do emissor relacionadas a questões ASG), resuma em até 200 tokens os principais pontos da resposta da empresa (chave 'oportunidades').

"""


# CONEXÃO COM O MONGODB

# Conecta ao banco de dados do projeto no MongoDB
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True).mjd_fehlauer

# Conecta à coleção do projeto no banco de dados
collection = db.cvm_relatorios


# EXECUÇÃO DO ALGORITMO

# Define o ano de interesse
ano = 2024

# Busca o ZIP do ano de interesse na CVM
cvm_sucesso, cvm_zip = busca_zip_cvm(ano)

# Se o download do ZIP foi bem sucedido, continua com o processamento
if cvm_sucesso:

    # Lista os arquivos dentro do ZIP
    lista_relatorios = lista_arquivos_zip(cvm_zip)

    # O primeiro arquivo da lista é o CSV com os dados de interesse
    # Extrai os dados desse CSV para um dicionário
    relatorios = csv_para_dict(cvm_zip, lista_relatorios[0], ano)
    print(f"Encontrados {len(relatorios)} registros no CSV.")

# Itera sobre os registros do CSV
for registro in relatorios:

    # Busca no MongoDB considerando CNPJ_Companhia e Data_Referencia (apenas o ano)
    filtro = {
        'CNPJ_Companhia': registro['CNPJ_Companhia'],
        'Data_Referencia': {
            '$gte': datetime(registro['Data_Referencia'].year, 1, 1),
            '$lt': datetime(registro['Data_Referencia'].year + 1, 1, 1)
        }
    }
    empresa = collection.find_one(filtro)

    # Agora a comparação leva em conta também a Data_Referencia
    if empresa and empresa['Versao'] >= registro['Versao']:
        print(f"Empresa {registro['CNPJ_Companhia']} já tem versão {registro['Versao']} para o ano {registro['Data_Referencia'].year} no MongoDB.")
        continue

    # Se não existe um registro para o CNPJ_Companhia no ano especificado, ou a versão é inferior
    else:
        print(f"Empresa {registro['CNPJ_Companhia']} tem nova versão {registro['Versao']} para o a data de referência {registro['Data_Referencia']}.")

        # Dicionário com os dados a serem inseridos/atualizados no MongoDB
        dados_empresa = {
            'CNPJ_Companhia': registro['CNPJ_Companhia'],
            'Data_Referencia': date_to_datetime(registro['Data_Referencia']),
            'Versao': registro['Versao'],
            'Nome_Companhia': registro['Nome_Companhia'],
            'Codigo_CVM': registro['Codigo_CVM'],
            'ID_Documento': registro['ID_Documento'],
            'Data_Recebimento': date_to_datetime(registro['Data_Recebimento']),
        }

        # Busca o ZIP do relatório da empresa
        url_relatorio = registro['Link_Doc']
        cod_cvm = registro['Codigo_CVM']
        relatorio_sucesso, relatorio_zip = busca_zip_relatorio(url_relatorio, cod_cvm)

        if relatorio_sucesso:
                
            # Extrai o XML do ZIP do relatório
            xml_path = extrai_xml(relatorio_zip)

            if xml_path is not None:
                # Extrai os dados do XML
                tags_buscadas = ['DescricaoCaracteristicasOrgaosAdmECF', 'DescricaoRHEmissor']
                dados_xml = extrair_dados(xml_path, tags_buscadas)

                # Verifica se a extração retornou dados válidos antes de prosseguir
                if dados_xml:
                    # Ajusta os dados extraídos do XML
                    dados_ajustados = ajustar_dados(dados_xml)    

                    # Define os prompts específicos para cada tag de interesse
                    prompts_por_tag = {
                        'HistoricoEmissor': orientacoes + prompt_historico + diretrizes,
                        'AtividadesEmissorControladas': orientacoes + prompt_atividades + diretrizes,
                        'EfeitosRegulacaoEstatal': orientacoes + prompt_efeitos + diretrizes,
                        'InfoASG': orientacoes + prompt_asg + diretrizes,
                        'PlanoNegocios': orientacoes + prompt_oportunidades + diretrizes
                    }

                    # Define as tags de interesse para cada empresa
                    tags_de_interesse = [
                        'HistoricoEmissor',
                        'AtividadesEmissorControladas', 
                        'EfeitosRegulacaoEstatal',
                        'InfoASG',
                        'PlanoNegocios'
                        ]

                    # Dicionário para armazenar os dados da consulta à OpenAI
                    dados_openai = {}

                    for tag in tags_de_interesse:
                        pdf_sucesso, pdf_path = extrair_pdf_de_xml(xml_path, cod_cvm, tag)
                        if pdf_sucesso:
                            texto_pdf = pdf_para_string(pdf_path)
                            prompt = prompts_por_tag[tag]  # Acessa o prompt específico para a tag atual
                            respostas_openai = openai_chat(openai_api_key, prompt, texto_pdf)
                            dados_openai[tag] = respostas_openai
                            os.remove(pdf_path) # Apaga o arquivo PDF temporário

                    # Combina os dicionários para inserção/atualização no MongoDB
                    dados_db = {**dados_empresa, **dados_ajustados, **dados_openai}
                    
                    # Insere ou atualiza o registro no MongoDB
                    print(dados_db)
                    collection.update_one(filtro, {'$set': dados_db}, upsert=True)
                    print(f"Dados da empresa {registro['Nome_Companhia']} atualizados no MongoDB.")

                    # Apaga os arquivos temporários
                    os.remove(relatorio_zip)
                    os.remove(xml_path)
        else:
            print(f"Não foi possível extrair o XML do relatório da empresa {cod_cvm}.")

            # Apaga os arquivos temporários
            os.remove(relatorio_zip)

            continue

os.remove(cvm_zip)  # Apaga o arquivo ZIP temporário