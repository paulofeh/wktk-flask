from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# VARIÁVEIS DE AMBIENTE
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
uri = os.getenv("MONGODB_URI")

# Conectar ao MongoDB
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True).mjd_fehlauer
collection = db['cvm']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/busca_empresas')
def busca_empresas():
    query = request.args.get('q')  # Obtém a query de busca da URL
    if query:
        # Busca no MongoDB usando a query; ajuste este comando conforme necessário
        search_results = collection.find({"Nome_Companhia": {"$regex": query, "$options": "i"}})
        suggestions = [result['Nome_Companhia'] for result in search_results]
        return jsonify(suggestions)
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)