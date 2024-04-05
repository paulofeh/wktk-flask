def gerar_pictogramas_por_orgao(dados_orgao, emojis):
    """
    Gera pictogramas a partir dos dados de um órgão, usando emojis fornecidos.
    Retorna um dicionário de pictogramas por órgão administrativo.
    """
    pictogramas = {}
    for orgao in dados_orgao:
        if orgao.get('NaoSeAplica', 'false') == 'false':
            pictograma = ""
            for categoria, valor in orgao.items():
                if categoria in emojis and valor.isdigit():
                    pictograma += (emojis[categoria] + " ") * int(valor)
            if pictograma:  # Garante que não adicionaremos órgãos vazios
                pictogramas[orgao['OrgaoAdministracao']] = pictograma
    return pictogramas


def calcular_totais_e_proporcoes(dados_orgao):
    """
    Calcula totais e proporções a partir dos dados do órgão.
    Retorna uma lista de dicionários com descrição, total e proporções.
    """
    resultados = []
    for orgao in dados_orgao:
        totais = {chave: int(valor.replace('.', '')) for chave, valor in orgao.items() if chave not in ['DescricaoInformacao', 'NaoSeAplica'] and valor.replace('.', '').isdigit()}
        total_geral = sum(totais.values())
        proporcoes = {chave: valor / total_geral for chave, valor in totais.items() if total_geral > 0}
        resultados.append({
            'descricao': orgao['DescricaoInformacao'],
            'total': total_geral,
            'proporcoes': proporcoes,
            'totais': totais  # Inclui os totais individuais de cada subgrupo
        })
    return resultados

def obter_e_gerar_pictogramas(documento, caminho, funcao_geradora, emojis):
    """
    Extrai os dados do documento usando o caminho fornecido, e gera pictogramas.
    Retorna None se os dados não estiverem disponíveis ou forem inválidos.
    """
    dados = documento
    for chave in caminho:
        if isinstance(dados, dict) and chave in dados and dados[chave]:
            dados = dados[chave]
        else:
            return None  # Dados ausentes ou inválidos
    return funcao_geradora(dados, emojis)


def gerar_pictogramas_proporcionais(dados_orgao, emojis, max_emojis=100):
    """
    Gera pictogramas proporcionais a partir dos dados de um órgão, usando emojis fornecidos.
    Retorna um dicionário de pictogramas por órgão administrativo.
    """
    pictogramas = {}
    dados_proporcoes = calcular_totais_e_proporcoes(dados_orgao)
    for dado in dados_proporcoes:
        pictograma = ""
        detalhes = {}  # Novo dicionário para armazenar os totais de cada subgrupo
        for categoria, proporcao in dado['proporcoes'].items():
            num_emojis = round(proporcao * max_emojis)
            pictograma += (emojis.get(categoria, '❔') + " ") * num_emojis
            detalhes[categoria] = dado['totais'][categoria]  # Adiciona o total de cada categoria aos detalhes
        if pictograma:
            pictogramas[dado['descricao']] = {
                'pictograma': pictograma.strip(),
                'total': dado['total'],
                'detalhes': detalhes
            }
    return pictogramas