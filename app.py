"""
O projeto lupa(ESG) é uma aplicação web que permite a busca e visualização de informações sobre a pauta ESG de empresas listadas na CVM (Comissão de Valores Mobiliários). 
Autor: Paulo Fehlauer
Data: 2024-04-11
Versão: 0.1
Licença: MIT

Este arquivo contém o código principal da aplicação web, construída com Flask e TailwindCSS.
"""


# Importa bibliotecas
from flask import Flask, render_template, request, jsonify, abort
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Importa funções para geração de pictogramas
from pictogramas import gerar_pictogramas_por_orgao, gerar_pictogramas_proporcionais, calcular_totais_e_proporcoes, obter_e_gerar_pictogramas

# Carrega variáveis de ambiente
load_dotenv()  
uri = os.getenv("MONGODB_URI")

# Conecta ao MongoDB
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True).mjd_fehlauer
collection = db['cvm_relatorios']


# Variáveis a serem passadas para os templates
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


# Definições e rotas do Flask
app = Flask(__name__)

# Função para injetar metadados do site nos templates
@app.context_processor
def inject_site_metadata():
    return dict(
        site_title="lupa(ESG)",
        site_subtitle="Ambiente, Sociedade e Governança na ponta dos dados",
        site_meta_description="Plataforma que busca e organiza informações públicas fornecidas por empresas brasileiras sobre práticas relacionadas à pauta ESG - Ambiental, Social e Governança."
        )

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


@app.route('/empresa/<int:codigo_cvm>')
def empresa(codigo_cvm):
    documentos_empresa = list(collection.find({"Codigo_CVM": codigo_cvm}).sort("Data_Referencia", -1))
    if not documentos_empresa:
        abort(404)

    contexto = {'documentos': documentos_empresa}

    # Função auxiliar para verificar e obter dados de um caminho de chaves
    def obter_dados(documento, caminho):
        atual = documento
        for chave in caminho:
            if isinstance(atual, dict) and chave in atual:
                atual = atual[chave]
            else:
                return None
        if isinstance(atual, list) and all(isinstance(item, dict) for item in atual):
            return atual
        else:
            return None

    caminhos_pictogramas = [
        (
            'DescricaoCaracteristicasOrgaosAdmECF', 
            'DescricaoCorRaca', 
            'XmlFormularioReferenciaDadosFREFormularioAssembleiaGeralEAdmDescricaoCaracteristicasOrgaosAdmECFCorRaca', 
            gerar_pictogramas_por_orgao, 
            emojis_cor_raca,
            'pictogramas_cor_raca'
        ),
        (
            'DescricaoCaracteristicasOrgaosAdmECF', 
            'DescricaoGenero', 
            'XmlFormularioReferenciaDadosFREFormularioAssembleiaGeralEAdmDescricaoCaracteristicasOrgaosAdmECFGenero', 
            gerar_pictogramas_por_orgao, 
            emojis_genero,
            'pictogramas_genero'
        ),
        (
            'DescricaoRHEmissor', 
            'DescricaoCorRaca', 
            'XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorCorRaca', 
            gerar_pictogramas_proporcionais, 
            emojis_cor_raca,
            'pictogramas_rh_cor_raca'
        ),
        (
            'DescricaoRHEmissor', 
            'DescricaoGenero', 
            'XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorGenero', 
            gerar_pictogramas_proporcionais, 
            emojis_genero,
            'pictogramas_rh_genero'
        ),
        (
            'DescricaoRHEmissor', 
            'DescricaoFaixaEtaria', 
            'XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorFaixaEtaria', 
            gerar_pictogramas_proporcionais, 
            emojis_faixa_etaria,
            'pictogramas_rh_idade'
        ),
        (
            'DescricaoRHEmissor', 
            'DescricaoLocalizacaoGeografica', 
            'XmlFormularioReferenciaDadosFREFormularioRecursosHumanosDescricaoRHEmissorLocalizacaoGeografica', 
            gerar_pictogramas_proporcionais, 
            emojis_regiao,
            'pictogramas_rh_regiao'
        ),
    ]

    for caminho in caminhos_pictogramas:
        chave_dados, chave_dados_intermediario, chave_final, funcao_geradora, emojis, chave_template = caminho
        dados_pictogramas = obter_dados(documentos_empresa[0], [chave_dados, chave_dados_intermediario, chave_final])
        if dados_pictogramas:
            contexto[chave_template] = funcao_geradora(dados_pictogramas, emojis)

    return render_template('empresa.html', **contexto, ods_descricao=ods_descricao, escopos=escopos)


if __name__ == '__main__':
    app.run(debug=True)


