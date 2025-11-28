from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 1. CONFIGURAÇÃO
load_dotenv()
app = Flask(__name__)

# CORS: Permite acesso do seu site no Firebase e Localhost
CORS(app, resources={r"/api/*": {"origins": [
    "https://guia-ibira.web.app",
    "https://guia-ibira.firebaseapp.com",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]}})

# 2. CONEXÃO SUPABASE
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("ERRO: Verifique variáveis de ambiente")
    exit(1)

supabase: Client = create_client(url, key)

# 3. ROTAS

@app.route('/')
def home():
    return "Servidor Guia Ibirá Online! 🚀"

# LISTA: Pega todos os itens (plural)
@app.route('/api/items/<tabela>', methods=['GET'])
def get_items(tabela):
    try:
        response = supabase.table(tabela).select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# DETALHE: Pega UM item específico (singular) - A ROTA QUE FALTA
@app.route('/api/item/<tabela>/<id>', methods=['GET'])
def get_item_detail(tabela, id):
    try:
        # Busca apenas 1 item pelo ID
        response = supabase.table(tabela).select("*").eq('id', id).execute()
        
        # Verifica se encontrou algo
        if len(response.data) > 0:
            return jsonify(response.data[0]), 200
        else:
            return jsonify({"erro": "Item não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# AVALIAÇÕES: Resumo
@app.route('/api/avaliacoes/resumo/<tabela>', methods=['GET'])
def get_resumo_avaliacoes(tabela):
    try:
        response = supabase.table('avaliacoes')\
            .select('item_id, nota')\
            .eq('tabela_item', tabela)\
            .execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# AVALIAÇÕES: Detalhe
@app.route('/api/avaliacoes/detalhe/<tabela>/<item_id>', methods=['GET'])
def get_detalhe_avaliacoes(tabela, item_id):
    try:
        response = supabase.table('avaliacoes')\
            .select('*')\
            .eq('tabela_item', tabela)\
            .eq('item_id', item_id)\
            .order('created_at', desc=True)\
            .execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# NOVA AVALIAÇÃO
@app.route('/api/avaliar', methods=['POST'])
def nova_avaliacao():
    dados = request.json
    if not dados.get('item_id') or not dados.get('nota'):
        return jsonify({"erro": "Dados incompletos"}), 400
    try:
        response = supabase.table('avaliacoes').insert(dados).execute()
        return jsonify({"mensagem": "Sucesso!", "dados": response.data}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# BUSCA
@app.route('/api/busca', methods=['GET'])
def buscar():
    termo = request.args.get('q')
    if not termo:
        return jsonify([]), 200
    try:
        response = supabase.rpc('search_items', {'search_term': termo}).execute()
        return jsonify(response.data), 200
    except Exception as e:
        print(f"Erro busca: {e}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)