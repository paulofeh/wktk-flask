from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()  
uri = os.getenv("MONGODB_URI")

# Conectar ao MongoDB
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True).mjd_fehlauer
collection = db['cvm']

app = Flask(__name__)

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



if __name__ == '__main__':
    app.run(debug=True)
