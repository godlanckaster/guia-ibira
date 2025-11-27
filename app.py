from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 1. CONFIGURAÇÃO
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://guia-ibira.web.app", "http://localhost:5500"]}}) 

# 2. CONEXÃO SUPABASE
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("ERRO: Verifique seu arquivo .env")
    exit(1)

supabase: Client = create_client(url, key)

# 3. ROTAS

@app.route('/')
def home():
    return "Servidor Guia Ibirá Online! 🚀"

# Rota para pegar os itens (Restaurantes, Hoteis, etc)
@app.route('/api/items/<tabela>', methods=['GET'])
def get_items(tabela):
    try:
        # Busca todos os itens da tabela
        response = supabase.table(tabela).select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para pegar TODAS as notas de uma categoria (para calcular estrelas no Grid)
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

# Rota para pegar avaliações DETALHADAS de um item (para o Modal)
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

# Rota para SALVAR uma nova avaliação
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

# Rota de BUSCA (Chama a função RPC do Supabase)
@app.route('/api/busca', methods=['GET'])
def buscar():
    termo = request.args.get('q')
    if not termo:
        return jsonify([]), 200
    try:
        # Certifique-se de ter a função 'search_items' criada no seu Supabase
        response = supabase.rpc('search_items', {'search_term': termo}).execute()
        return jsonify(response.data), 200
    except Exception as e:
        print(f"Erro busca: {e}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':

    app.run(debug=True, port=5000)
