from flask import Flask, render_template, request, jsonify, abort
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()  
uri = os.getenv("MONGODB_URI")


# Conectar ao MongoDB
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True).mjd_fehlauer
collection = db['cvm_relatorios']


# Definições do Flask
app = Flask(__name__)

@app.context_processor
def inject_site_metadata():
    return dict(
        site_title="lupa(ESG)",
        site_subtitle="Ambiente, Sociedade e Governança na ponta dos dados"
    )

# Funções auxiliares

# Função para criar pictogramas a partir dos dados de raça/cor e gênero de órgãos administrativos
def gerar_pictogramas_por_orgao(dados_orgao, emojis):
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

# Função para calcular totais e proporções de valores para número de funcionários
def calcular_totais_e_proporcoes(dados_orgao):
    resultados = []
    for orgao in dados_orgao:
        # Calcular o total somente se o valor for numérico (após remover os pontos) e não estiver na lista de exceções
        total = sum(int(valor.replace('.', '')) for chave, valor in orgao.items() if chave not in ['DescricaoInformacao', 'NaoSeAplica'] and valor.replace('.', '').isdigit())

        # Calcular as proporções da mesma forma, garantindo que os valores sejam numéricos e válidos
        proporcoes = {chave: int(valor.replace('.', '')) / total for chave, valor in orgao.items() if chave not in ['DescricaoInformacao', 'NaoSeAplica'] and valor.replace('.', '').isdigit() and total > 0}

        resultados.append({
            'descricao': orgao['DescricaoInformacao'],
            'total': total,
            'proporcoes': proporcoes
        })
    return resultados

# Função para gerar pictogramas proporcionais a partir dos dados dos funcionários
def gerar_pictogramas_proporcionais(dados_orgao, emojis, max_emojis=100):
    pictogramas = {}
    dados_proporcoes = calcular_totais_e_proporcoes(dados_orgao)
    for dado in dados_proporcoes:
        pictograma = ""
        for categoria, proporcao in dado['proporcoes'].items():
            num_emojis = round(proporcao * max_emojis)
            pictograma += (emojis.get(categoria, '❔') + " ") * num_emojis
        if pictograma:
            pictogramas[dado['descricao']] = {
                'pictograma': pictograma.strip(),
                'total': dado['total']
            }
    return pictogramas



# Variáveis que armazenam valores a serem passados para os templates
emojis_genero = {
    'Masculino': '🔵',
    'Feminino': '🔴',
    'NaoBinario': '🟣',
    'Outros': '⚪',  # Escolha um Emoji representativo
    'PrefereNaoResponder': '❔'
}

emojis_cor_raca = {
        'Amarelo': '🟨',
        'Branco': '⬜',
        'Preto': '⬛',
        'Pardo': '🟫',
        'Parda': '🟫',
        'Indigena': '🟥',
        'Outros': '🔵',  # Exemplo de cor para "Outros"
        'PrefereNaoResponder': '❔'
    }

emojis_faixa_etaria = {
    'FaixaAbaixo30': '🐣',
    'FaixaDe30a50': '🧑',
    'FaixaAcima50': '🧓'
}

emojis_regiao = {
    'Norte': '🟦',
    'Nordeste': '🟩',
    'CentroOeste': '🟨',
    'Sudeste': '🟪',
    'Sul': '🟥',
    'Exterior': '🌍'
}


ods_descricao = {
    1: "Erradicação da Pobreza",
    2: "Fome Zero e Agricultura Sustentável",
    3: "Saúde e Bem-Estar",
    4: "Educação de Qualidade",
    5: "Igualdade de Gênero",
    6: "Água Limpa e Saneamento",
    7: "Energia Acessível e Limpa",
    8: "Trabalho Decente e Crescimento Econômico",
    9: "Indústria, Inovação e Infraestrutura",
    10: "Redução das Desigualdades",
    11: "Cidades e Comunidades Sustentáveis",
    12: "Consumo e Produção Responsáveis",
    13: "Ação Contra a Mudança Global do Clima",
    14: "Vida na Água",
    15: "Vida Terrestre",
    16: "Paz, Justiça e Instituições Eficazes",
    17: "Parcerias e Meios de Implementação"
}

escopos = {
    1: "Emissões diretas de gases do efeito estufa",
    2: "Emissões indiretas associadas à eletricidade, calor ou vapor adquiridos",
    3: "Outras emissões indiretas que ocorrem nas atividades da empresa, mas fora de seu controle direto"
}


# Rotas do Flask
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/busca')
def busca_empresas():
    query = request.args.get('q')
    if query and len(query) >= 3:
        regex_query = {"$regex": query, "$options": "i"}  # Define a regex query
        search_results = collection.find({
            "$or": [
                {"Nome_Companhia": regex_query},
                {"AtividadesEmissorControladas.lista_atividades": regex_query}
            ]
        })
        suggestions = [{"name": result['Nome_Companhia'], "slug": result.get('Codigo_CVM', '')} for result in search_results]
        return jsonify(suggestions)
    return jsonify([])


@app.route('/empresa/<int:codigo_cvm>')
def empresa(codigo_cvm):
    documentos_empresa = list(collection.find({"Codigo_CVM": codigo_cvm}).sort("Data_Referencia", -1))
    if documentos_empresa:
        
        dados_cor_raca = documentos_empresa[0]['DescricaoCaracteristicasOrgaosAdmECF']['DescricaoCorRaca']['XmlFormularioReferenciaDadosFREFormularioAssembleiaGeralEAdmDescricaoCaracteristicasOrgaosAdmECFCorRaca']
        pictogramas_cor_raca = gerar_pictogramas_por_orgao(dados_cor_raca, emojis_cor_raca)

        dados_genero = documentos_empresa[0]['DescricaoCaracteristicasOrgaosAdmECF']['DescricaoGenero']['XmlFormularioReferenciaDadosFREFormularioAssembleiaGeralEAdmDescricaoCaracteristicasOrgaosAdmECFGenero']
        pictogramas_genero = gerar_pictogramas_por_orgao(dados_genero, emojis_genero)

        dados_rh_cor_raca = documentos_empresa[0]['DescricaoRHEmissor']['DescricaoCorRaca']['XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorCorRaca']
        pictogramas_rh_cor_raca = gerar_pictogramas_proporcionais(dados_rh_cor_raca, emojis_cor_raca)

        dados_rh_genero = documentos_empresa[0]['DescricaoRHEmissor']['DescricaoGenero']['XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorGenero']
        pictogramas_rh_genero = gerar_pictogramas_proporcionais(dados_rh_genero, emojis_genero)

        dados_rh_idade = documentos_empresa[0]['DescricaoRHEmissor']['DescricaoFaixaEtaria']['XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorFaixaEtaria']
        pictogramas_rh_idade = gerar_pictogramas_proporcionais(dados_rh_idade, emojis_faixa_etaria)

        dados_rh_regiao = documentos_empresa[0]['DescricaoRHEmissor']['DescricaoLocalizacaoGeografica']['XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorLocalizacaoGeografica']
        pictogramas_rh_regiao = gerar_pictogramas_proporcionais(dados_rh_regiao, emojis_regiao)

        return render_template('empresa.html', documentos=documentos_empresa, pictogramas_cor_raca=pictogramas_cor_raca, pictogramas_genero=pictogramas_genero, ods_descricao=ods_descricao, escopos=escopos, pictogramas_rh_cor_raca=pictogramas_rh_cor_raca, pictogramas_rh_genero=pictogramas_rh_genero, pictogramas_rh_idade=pictogramas_rh_idade, pictogramas_rh_regiao=pictogramas_rh_regiao)

    else:
        abort(404)


@app.route('/lista-empresas')
def listar_empresas():
    # Supondo que cada empresa tem um documento representativo mais recente com seu nome e Código CVM
    empresas = list(collection.find().sort("Nome_Companhia", 1))
    return render_template('lista_empresas.html', empresas=empresas)


@app.route('/relatorios-esg')
def relatorios_esg():
    # Recupera todos os documentos da coleção
    documentos = list(collection.find({}))

    # Filtra os documentos para obter apenas aqueles com URL de relatório ESG
    empresas_com_url = sorted(
        [
            {
                'Nome': documento['Nome_Companhia'],
                'URLs': [
                    'https://' + url if not url.startswith('http://') and not url.startswith('https://') else url for url in documento['InfoASG'].get('url_relatorio', [])
                    ]
                    }
                    for documento in documentos if documento.get('InfoASG', {}).get('url_relatorio')
                    ],
                    key=lambda empresa: empresa['Nome']
                    )
    # Passa a lista filtrada para o template
    return render_template('relatorios.html', empresas=empresas_com_url)

if __name__ == '__main__':
    app.run(debug=True)
