# Estrutura do projeto

## Tipo de projeto
- Projeto fullstack com backend em Python e frontend estático em HTML/CSS/JavaScript.
- O backend é servido por FastAPI e expõe a API REST e arquivos estáticos do frontend.
- O banco principal é MySQL, acessado via SQLAlchemy.

## Camadas e áreas funcionais
- Backend principal: `src/backend/app`
  - `main.py`: ponto de entrada da aplicação FastAPI, serve arquivos estáticos e registra rotas.
  - `api.py`: centraliza os routers da API em prefixo `/api`.
  - `database.py`: configuração de engine, sessão e Base do SQLAlchemy.
  - `config.py`: carregamento de variáveis de ambiente com Pydantic Settings.
  - `models/`: entidades ORM do sistema.
  - `routers/`: endpoints HTTP por domínio.
  - `services/`: segurança, hash de senha e geração/validação de JWT.
- Frontend estático: `src/frontend`
  - páginas HTML com scripts em `js/` e estilos em `css/`.
  - o frontend usa `fetch` para consumir a API REST do backend.

## Funções centrais observadas
- Autenticação de clientes: login e validação de JWT.
- Cadastro e perfil do cliente.
- Recuperação de senha com token temporário.
- Gestão de produtos e painel administrativo.
- Autenticação administrativa separada para login do administrador.

## Arquitetura funcional observada
- Frontend estático (HTML/CSS/JS)
  - navegadores e fetch API
- FastAPI
  - roteamento HTTP
  - validação via Pydantic
  - arquivos estáticos + páginas HTML
- SQLAlchemy + MySQL
  - persistência e modelos ORM

## Evidência do código
- Endpoints são registrados em `src/backend/app/api.py` e incluídos em `src/backend/app/main.py`.
- Entidades principais: `Cliente`, `Produto`, `Pedido`, `ItemPedido`, `Administrador`.
- A autenticação usa `pwdlib` + `PyJWT` na camada `services/security.py`.
