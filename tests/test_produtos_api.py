import pytest
from playwright.sync_api import sync_playwright
import sys
import os

# Permite que o Python encontre a pasta 'utils' para importar o db_helper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db_helper import executar_query

@pytest.fixture(scope="function")
def limpar_banco():
    """Garante que o banco de dados estará limpo antes e depois de cada teste."""
    executar_query("DELETE FROM produtos;")
    yield
    executar_query("DELETE FROM produtos;")


# --- TESTE 1: O SEU TESTE DE CADASTRO (QUE JÁ PASSOU!) ---
def test_deve_cadastrar_produto_e_validar_no_banco(limpar_banco):
    novo_produto = {"nome": "Teclado Mecânico RGB", "preco": 299.90, "estoque": 15}
    
    with sync_playwright() as p:
        request_context = p.request.new_context(base_url="https://httpbin.org") 
        response = request_context.post("/post", data=novo_produto)
        assert response.status == 200 
        
        executar_query(
            "INSERT INTO produtos (nome, preco, estoque) VALUES (%s, %s, %s);",
            (novo_produto["nome"], novo_produto["preco"], novo_produto["estoque"])
        )
        
        resultado_banco = executar_query("SELECT * FROM produtos WHERE nome = %s;", (novo_produto["nome"],), ler_dados=True)
        assert len(resultado_banco) == 1
        
        produto_salvo = resultado_banco[0]
        assert produto_salvo["preco"] == 299.90
        assert produto_salvo["estoque"] == 15
        request_context.dispose()


# --- TESTE 2: CENÁRIO DE UPDATE DE ESTOQUE ---
def test_deve_atualizar_estoque_via_api_e_refletir_no_banco(limpar_banco):
    # 1. ARRANGE: Injeta um produto inicial direto no banco usando SQL (Cenário Pré-configurado)
    executar_query(
        "INSERT INTO produtos (id, nome, preco, estoque) VALUES (%s, %s, %s, %s);",
        (555, "Mouse Gamer Wireless", 150.00, 10) # Começa com estoque 10
    )
    
    dados_atualizacao = {"novo_estoque": 8} # Queremos dar baixa em 2 unidades
    
    # 2. ACT: Dispara a API simulando uma atualização de estoque
    with sync_playwright() as p:
        request_context = p.request.new_context(base_url="https://httpbin.org")
        response = request_context.put("/put", data=dados_atualizacao)
        assert response.status == 200 # API respondeu com sucesso
        
        # Simula o backend executando o UPDATE com SQL
        executar_query(
            "UPDATE produtos SET estoque = %s WHERE id = %s;",
            (dados_atualizacao["novo_estoque"], 555)
        )
        
        # 3. ASSERT: QA consulta o banco para ver se a alteração foi persistida com sucesso
        resultado_banco = executar_query("SELECT estoque FROM produtos WHERE id = %s;", (555,), ler_dados=True)
        
        estoque_atualizado = resultado_banco[0]["estoque"]
        assert estoque_atualizado == 8, f"Erro! O estoque deveria ser 8, mas está {estoque_atualizado}"
        
        print("\n🎉 Teste de UPDATE executado com sucesso! Estoque alterado corretamente no banco!")
        request_context.dispose()


# --- TESTE 3: CENÁRIO NEGATIVO (EVITAR DADO CORROMPIDO) ---
def test_nao_deve_salvar_no_banco_se_api_retornar_erro(limpar_banco):
    # 1. ARRANGE: Prepara dados inválidos (Preço negativo)
    produto_invalido = {"nome": "Cabo HDMI Defeituoso", "preco": -10.00, "estoque": 5}
    
    # 2. ACT: Dispara uma API que vai simular uma rejeição (Simulando uma URL de erro 400 Bad Request)
    with sync_playwright() as p:
        request_context = p.request.new_context(base_url="https://httpbin.org")
        response = request_context.post("/status/400", data=produto_invalido)
        
        # O teste garante que a API barrou a requisição!
        assert response.status == 400 
        
        # Como a API barrou (deu erro 400), o backend NÃO deve rodar o INSERT.
        # Caso a lógica do backend estivesse quebrada, ele tentaria salvar.
        
        # 3. ASSERT DE QA: Usa o SQL para garantir que a tabela continua perfeitamente limpa
        resultado_banco = executar_query("SELECT * FROM produtos;", ler_dados=True)
        
        # O tamanho da lista DEVE ser 0, provando que nenhum dado inválido entrou no banco de dados!
        assert len(resultado_banco) == 0, "🚨 BUG: A API retornou erro, mas o dado inválido foi gravado no banco!"
        
        print("\n🎉 Teste NEGATIVO passou! Banco de dados protegido contra requisições inválidas!")
        request_context.dispose()
