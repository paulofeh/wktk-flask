from flask import Flask, render_template, request, jsonify, abort
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()  
uri = os.getenv("MONGODB_URI")


# Conectar ao MongoDB
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True).mjd_fehlauer
collection = db['cvm']


# Definições do Flask
app = Flask(__name__)

@app.context_processor
def inject_site_metadata():
    return dict(
        site_title="Walk the Talk",
        site_subtitle="O que as empresas dizem que fazem - e o que realmente fazem - em relação à pauta ESG"
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
        'Indigena': '🟥',
        'Outros': '🔵',  # Exemplo de cor para "Outros"
        'PrefereNaoResponder': '❔'
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
    return render_template('index.html')

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

        return render_template('empresa.html', documentos=documentos_empresa, pictogramas_cor_raca=pictogramas_cor_raca, pictogramas_genero=pictogramas_genero, ods_descricao=ods_descricao, escopos=escopos)

    else:
        abort(404)


@app.route('/lista-empresas')
def listar_empresas():
    # Supondo que cada empresa tem um documento representativo mais recente com seu nome e Código CVM
    empresas = list(collection.find().sort("Nome_Companhia", 1))
    return render_template('lista_empresas.html', empresas=empresas)


if __name__ == '__main__':
    app.run(debug=True)
