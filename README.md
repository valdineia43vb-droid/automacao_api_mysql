# 🚀 Automação de Testes de API Web com Playwright e Validação SQL

Este projeto demonstra a implementação de uma arquitetura robusta de **Garantia de Qualidade (QA)** focada em testes automatizados de API utilizando **Python**, **Playwright** e **SQL** para validações ponta a ponta (End-to-End).

A suíte de testes adota o padrão de teste de caixa-cinza, garantindo não apenas que as respostas das requisições HTTP estejam corretas (status codes), mas que as transações de dados sejam persistidas com integridade diretamente nas tabelas do banco de dados.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Framework de Testes:** Pytest
* **Automação de API:** Playwright (APIRequestContext)
* **Banco de Dados:** SQLite (Simulando queries ANSI SQL padrão para MySQL)
* **Gerenciador de Contexto:** Hooks de Setup/Teardown automatizados para massa de dados limpa

## 🎯 Cenários Automatizados

O projeto cobre fluxos essenciais de manipulação de dados utilizando operações lógicas e comandos SQL estruturados:

1. **Validação de Cadastro (Persistência DML):** Dispara um payload de criação via API e executa uma query `SELECT` com parâmetros dinâmicos para assegurar a gravação íntegra do preço e estoque no banco.
2. **Atualização de Estoque (Mutação de Estado):** Pré-configura um cenário inserindo um registro via SQL, consome o endpoint correspondente e valida a alteração real do saldo via comando `UPDATE`.
3. **Cenário Negativo (Integridade de Dados):** Envia dados corrompidos para a API, garante o retorno de um erro controlado (`400 Bad Request`) e valida via SQL que o banco de dados permaneceu protegido e sem registros inválidos.
