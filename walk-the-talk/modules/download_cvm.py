"""
Funções para download de arquivos ZIP da CVM
"""

import os
import requests
from requests import Session


def busca_zip_cvm(ano):
    """ 
    Busca o arquivo ZIP no repositório da CVM e salva-o em pasta dedicada no diretório corrente
    Retorna True caso o download tenha sido bem sucedido e False caso contrário
    Retorna o caminho do arquivo ZIP salvo
    """    

    # URL do repositório da CVM
    url_repo = 'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/'

    # URL do arquivo ZIP
    nome_zip_cvm = f'fre_cia_aberta_{ano}.zip'
    url_zip_cvm = url_repo + nome_zip_cvm

    # Define o caminho onde o arquivo ZIP será salvo
    caminho_local = os.path.join(os.getcwd(), 'arquivos_cvm\\')
    os.makedirs(caminho_local, exist_ok=True)

    # Faz o download do arquivo ZIP
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url_zip_cvm, headers=headers)

    if response.status_code == 200:
        caminho_zip = os.path.join(caminho_local, nome_zip_cvm)

        with open(caminho_zip, "wb") as file:
            file.write(response.content)
            
        print(f"ZIP {nome_zip_cvm} salvo com sucesso.")
        return True, caminho_zip
    else:
        print(f"Falha no download do ZIP {nome_zip_cvm}. Erro {response.status_code}.")
        return False, None
    

def busca_zip_relatorio(url, cod_cvm):
    """
    Busca o arquivo ZIP no repositório da CVM e salva em pasta dedicada no diretório corrente
    Retorna True caso o download tenha sido bem sucedido e False caso contrário
    """

    # Substitui 'http' por 'https' na URL
    url = url.replace("http://", "https://")

    # Define o caminho onde o arquivo ZIP será salvo
    caminho_local = os.path.join(os.getcwd(), 'arquivos_cvm\\')
    os.makedirs(caminho_local, exist_ok=True)

    # Faz o download do arquivo ZIP
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt,en-US;q=0.9,en;q=0.8,es;q=0.7,pt-BR;q=0.6,es-419;q=0.5",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": "_ga_81XRXPNHSK=GS1.3.1708735940.1.0.1708735940.0.0.0; _ga_H8QM8DH015=GS1.3.1710252799.2.0.1710252799.0.0.0; _ga_6KR6GSRJZZ=GS1.1.1711483988.5.1.1711484321.0.0.0; ASP.NET_SessionId=uj05yychuwi0jnps00faitsb; dtCookie=v_4_srv_27_sn_8592F9AFAEEA6AAD845CED4F835CD528_perc_100000_ol_0_mul_1_app-3Aca883f3beebf9526_1_rcs-3Acss_0; BIGipServerpool_www.rad.cvm.gov.br_443=1242043402.47873.0000; TS01f82b11=011d592ce16f3b33e2abc77a55c56b8a376b8e4ddc8cb9eddd60e14cd95a007180a2568ad8bdc586cd2e2e8e1398e0604fe76936ad; _gid=GA1.3.1681611676.1711654202; _ga_146QLVPQ44=GS1.3.1711654202.22.1.1711654291.0.0.0; rxVisitor=1711654304222UEIST157USV3PR06THKGSEMQ5GL26BGA; dtSa=-; _ga_1HWVQMZJJT=GS1.1.1711654355.3.1.1711654668.0.0.0; _ga=GA1.1.1244918504.1708717704; TS01a5fb2d=016e3b076ff953e4dd5561ccaaf1b9a51c4c976453ab1a3db435bda15004f971c22e1965d9cad26173216e4a7837b44cd7ab6a09a5; TS01871345=016e3b076fa0140e142e3a3cf2dced5da19cbd02bb899d7e0eb84e0a762f4bce6a6ba695b0447db437022a47d5c475ff0a763d79a9; rxvt=1711656772915|1711654304227; dtPC=27$454972132_578h-vIPANPKQLJHFSAVGPTRCQAPHHESAKKSGR-0e0",
        "Host": "www.rad.cvm.gov.br",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Microsoft Edge\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }

    # Utiliza sessions para manter a conexão aberta e evitar erros de timeout
    with Session() as session:
        session.headers.update(headers)
        response = session.get(url)

        # Se o download for bem sucedido, salva o arquivo ZIP
        if response.status_code == 200:
            caminho_zip = os.path.join(caminho_local, str(cod_cvm) + '.zip')

            with open(caminho_zip, "wb") as file:
                file.write(response.content)
                
            print(f"Relatório ZIP da empresa {cod_cvm} salvo com sucesso em {caminho_zip}.")
            return True, caminho_zip
        # Se o download falhar, exibe uma mensagem de erro
        else:
            print(f"Falha no download do relatório ZIP da empresa {cod_cvm}. Erro {response.status_code}.")
            return False, None