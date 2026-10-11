import sqlite3
import os

# Define o caminho do banco de dados na raiz do projeto
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'banco_testes.db')

def inicializar_banco():
    """Cria a tabela de produtos caso ela não exista."""
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        );
    """)
    conexao.commit()
    conexao.close()

def dict_factory(cursor, row):
    """Transforma as linhas do banco em dicionários limpos (Ex: {'preco': 299.90})"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def executar_query(query, valores=None, ler_dados=False):
    """Executa os comandos SQL no nosso banco simulado."""
    inicializar_banco() # Garante que a tabela existe
    
    # Adapta a sintaxe do MySQL (%s) para a sintaxe do SQLite (?)
    if query:
        query = query.replace('%s', '?')
        
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = dict_factory # Aplica o conversor limpo
    cursor = conexao.cursor()
    
    try:
        if valores:
            cursor.execute(query, valores)
        else:
            cursor.execute(query)
            
        if ler_dados:
            return cursor.fetchall() # Retorna a lista de dicionários perfeita
        
        conexao.commit()
    finally:
        conexao.close()
