"""
Funções para interagir com a API da OpenAI
"""

import json
from openai import OpenAI


def openai_chat(openai_api_key, prompt, texto_pdf):
    """
    Função para interagir com a API da OpenAI para responder perguntas sobre os dados extraídos
    openai_api_key: chave de API da OpenAI
    prompt: texto de prompt para a API da OpenAI
    texto_pdf: texto extraído do PDF
    Retorna um dicionário com as respostas da OpenAI
    """

    client = OpenAI(api_key = openai_api_key)

    chat = client.chat.completions.create(
            model="gpt-4o", 
            temperature = 0,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": texto_pdf}])

    json_str = chat.choices[0].message.content

    # Converter a string JSON em um dicionário Python
    try:
        json_dict = json.loads(json_str)
    except json.decoder.JSONDecodeError as e:
        print(f"Erro de decodificação JSON: {e}")
        print(f"Conteúdo recebido: {json_str}")
        return {}

    return json_dict

