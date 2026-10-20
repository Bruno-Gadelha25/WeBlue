# ============================================================
# IMPORTAÇÕES PADRÃO DO PYTHON
# ============================================================

# Permite executar ações quando a aplicação inicia
# e quando ela é encerrada.
from contextlib import asynccontextmanager

# Facilita a construção dos caminhos das pastas.
from pathlib import Path


# ============================================================
# IMPORTAÇÕES DO FASTAPI
# ============================================================

# FastAPI:
# cria a aplicação.
#
# HTTPException:
# permite retornar erros HTTP personalizados.
#
# status:
# fornece constantes de códigos HTTP.
from fastapi import (
    FastAPI,
    HTTPException,
    status,
)

# Middleware responsável pelo CORS.
from fastapi.middleware.cors import CORSMiddleware

# Permite retornar arquivos HTML.
from fastapi.responses import FileResponse

# Permite disponibilizar CSS, JavaScript e imagens.
from fastapi.staticfiles import StaticFiles


# ============================================================
# SQLALCHEMY
# ============================================================

# Permite executar comandos SQL simples.
#
# Neste projeto é utilizado no healthcheck do banco.
from sqlalchemy import text


# ============================================================
# BANCO DE DADOS
# ============================================================

# Base:
# classe principal dos models SQLAlchemy.
#
# engine:
# conexão principal com o MySQL.
from .database import (
    Base,
    engine,
)


# ============================================================
# MODELS
# ============================================================

# IMPORTANTE:
#
# Os models precisam ser importados antes de:
#
# Base.metadata.create_all(...)
#
# Dessa forma o SQLAlchemy conhece as tabelas
# que fazem parte do projeto.


# Model da tabela clientes.
from .models.cliente import Cliente

# Model da tabela produtos.
from .models.produto import Produto

# Model da tabela administradores.
from .models.administrador import Administrador

# Modelos das tabelas de pedidos.
from .models.item_pedido import ItemPedido
from .models.pedido import Pedido


# ============================================================
# ROUTER PRINCIPAL DA API
# ============================================================

# Todos os routers da Weblue agora ficam centralizados
# no arquivo:
#
# src/backend/app/api.py
#
# Portanto, o main.py não precisa mais importar
# clientes_router, login_router, produtos_router etc.
from .api import api_router

# ============================================================
# CAMINHO DO FRONTEND
# ============================================================

# Este arquivo está em:
#
# src/backend/app/main.py
#
# parents[2] leva até:
#
# src/
#
# Depois acrescentamos "frontend".
#
# Resultado:
#
# src/frontend/
FRONTEND_DIR = (
    Path(__file__).resolve().parents[2]
    / "frontend"
)


# ============================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Cria automaticamente as tabelas que ainda
    # não existem no banco.
    #
    # Como os modelos foram importados acima,
    # o SQLAlchemy conhece:
    #
    # clientes
    # produtos
    # pedidos
    # itens_pedido
    Base.metadata.create_all(
        bind=engine
    )

    # A aplicação continua sua inicialização.
    yield


# ============================================================
# CRIAÇÃO DO FASTAPI
# ============================================================

app = FastAPI(

    # Nome apresentado no Swagger.
    title="API Weblue",

    # Descrição apresentada na documentação.
    description=(
        "API do e-commerce de cosméticos Weblue."
    ),

    # Versão atual da API.
    version="1.0.0",

    # Define o ciclo de vida da aplicação.
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    # Endereços que podem acessar a API.
    allow_origins=[

        # Live Server.
        "http://127.0.0.1:5500",
        "http://localhost:5500",

        # FastAPI local.
        "http://127.0.0.1:8000",
        "http://localhost:8000",

        # Aplicação publicada no Railway.
        "https://weblue-production.up.railway.app",
    ],

    # Atualmente a autenticação utiliza JWT
    # pelo cabeçalho Authorization,
    # e não cookies.
    allow_credentials=False,

    # Métodos HTTP permitidos.
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],

    # Permite os cabeçalhos necessários.
    allow_headers=["*"],
)


# ============================================================
# ROTAS DA API
# ============================================================

# Agora todas as rotas são registradas através
# de um único router principal.
#
# O api_router está definido em:
#
# src/backend/app/api.py
#
# IMPORTANTE:
#
# Nesta etapa ainda não adicionamos prefix="/api".
#
# Portanto as URLs existentes continuam funcionando:
#
# /clientes
# /auth/login
# /auth/recuperar-senha
# /perfil
# /produtos
#
# Assim reorganizamos o backend sem quebrar
# o frontend atual.

app.include_router(
    api_router
)


# ============================================================
# ARQUIVOS ESTÁTICOS
# ============================================================

# Disponibiliza os arquivos CSS através de:
#
# /css/arquivo.css
app.mount(
    "/css",
    StaticFiles(
        directory=FRONTEND_DIR / "css"
    ),
    name="css",
)


# Disponibiliza os arquivos JavaScript através de:
#
# /js/arquivo.js
app.mount(
    "/js",
    StaticFiles(
        directory=FRONTEND_DIR / "js"
    ),
    name="js",
)


# Disponibiliza as imagens através de:
#
# /img/arquivo.png
app.mount(
    "/img",
    StaticFiles(
        directory=FRONTEND_DIR / "img"
    ),
    name="img",
)


# ============================================================
# PÁGINAS DO FRONTEND
# ============================================================


# ============================================================
# PÁGINA INICIAL
# ============================================================

@app.get(
    "/",
    include_in_schema=False,
)
def pagina_inicial():

    # Retorna a página inicial da Weblue.
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ============================================================
# INDEX.HTML
# ============================================================

@app.get(
    "/index",
    include_in_schema=False,
)
@app.get(
    "/index.html",
    include_in_schema=False,
)
def pagina_index():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ============================================================
# HOME
# ============================================================

@app.get(
    "/home",
    include_in_schema=False,
)
@app.get(
    "/home.html",
    include_in_schema=False,
)
def pagina_home():

    """
    Retorna a página Home da Weblue.

    Arquivo utilizado:

    src/frontend/home.html
    """

    return FileResponse(
        FRONTEND_DIR / "home.html"
    )


# ============================================================
# CADASTRO
# ============================================================

@app.get(
    "/cadastro",
    include_in_schema=False,
)
@app.get(
    "/cadastro.html",
    include_in_schema=False,
)
def pagina_cadastro():

    # Retorna a página de cadastro.
    return FileResponse(
        FRONTEND_DIR / "cadastro.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.get(
    "/login",
    include_in_schema=False,
)
@app.get(
    "/login.html",
    include_in_schema=False,
)
def pagina_login():

    # Retorna a página de login.
    return FileResponse(
        FRONTEND_DIR / "login.html"
    )


# ============================================================
# RECUPERAÇÃO DE SENHA
# ============================================================

@app.get(
    "/recuperar-senha",
    include_in_schema=False,
)
@app.get(
    "/recuperar-senha.html",
    include_in_schema=False,
)
def pagina_recuperar_senha():

    # Retorna a página de recuperação de senha.
    return FileResponse(
        FRONTEND_DIR / "recuperar-senha.html"
    )


# ============================================================
# ÁREA DO CLIENTE
# ============================================================

@app.get(
    "/cliente",
    include_in_schema=False,
)
@app.get(
    "/cliente.html",
    include_in_schema=False,
)
def pagina_cliente():

    # Retorna a área do cliente.
    return FileResponse(
        FRONTEND_DIR / "cliente.html"
    )


# ============================================================
# CARRINHO DE COMPRAS
# ============================================================

@app.get(
    "/carrinho",
    include_in_schema=False,
)
@app.get(
    "/carrinho.html",
    include_in_schema=False,
)
def pagina_carrinho():
    return FileResponse(
        FRONTEND_DIR / "carrinho.html"
    )


# ============================================================
# CHECKOUT
# ============================================================

@app.get(
    "/checkout",
    include_in_schema=False,
)
@app.get(
    "/checkout.html",
    include_in_schema=False,
)
def pagina_checkout():
    return FileResponse(
        FRONTEND_DIR / "checkout.html"
    )


# ============================================================
# HISTÓRICO DE PEDIDOS
# ============================================================

@app.get(
    "/pedidos",
    include_in_schema=False,
)
@app.get(
    "/pedidos.html",
    include_in_schema=False,
)
def pagina_pedidos():
    return FileResponse(
        FRONTEND_DIR / "pedidos.html"
    )


# ============================================================
# PAINEL ADMINISTRATIVO DE PRODUTOS
# ============================================================

@app.get(
    "/admin-produtos",
    include_in_schema=False,
)
@app.get(
    "/admin-produtos.html",
    include_in_schema=False,
)
def pagina_admin_produtos():

    """
    Retorna a página administrativa de produtos.

    Arquivo utilizado:

    src/frontend/admin-produtos.html
    """

    return FileResponse(
        FRONTEND_DIR / "admin-produtos.html"
    )

# ============================================================
# DASHBOARD ADMINISTRATIVO
# ============================================================

@app.get(
    "/admin-dashboard",
    include_in_schema=False,
)
@app.get(
    "/admin-dashboard.html",
    include_in_schema=False,
)
def pagina_admin_dashboard():

    arquivo = FRONTEND_DIR / "admin-dashboard.html"

    if not arquivo.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Página dashboard não encontrada."
        )

    return FileResponse(arquivo)

# ============================================================
# PÁGINA - LOGIN ADMINISTRATIVO
# ============================================================

@app.get(
    "/admin-login",
    include_in_schema=False,
)
@app.get(
    "/admin-login.html",
    include_in_schema=False
)
def pagina_admin_login():
    """
    Retorna a página de login do administrador.
    """

    arquivo = FRONTEND_DIR / "admin-login.html"

    if not arquivo.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Página de login administrativo não encontrada."
        )

    return FileResponse(arquivo)

# ============================================================
# INFORMAÇÕES DA API
# ============================================================

@app.get(
    "/api",
    tags=["Informações"],
)
def informacoes_api():

    # Endpoint simples para verificar
    # se a API está respondendo.
    return {
        "sistema": "Weblue",
        "mensagem": "API funcionando com sucesso",
    }


# ============================================================
# MONITORAMENTO DA API
# ============================================================

@app.get(
    "/health",
    tags=["Monitoramento"],
)
def verificar_saude():

    # Indica que o FastAPI está funcionando.
    return {
        "status": "online"
    }


# ============================================================
# MONITORAMENTO DO BANCO DE DADOS
# ============================================================

@app.get(
    "/health/database",
    tags=["Monitoramento"],
)
def verificar_banco():

    try:

        # Abre uma conexão temporária
        # com o banco MySQL.
        with engine.connect() as connection:

            # Executa uma consulta simples.
            #
            # Se o MySQL responder ao SELECT 1,
            # consideramos a conexão funcionando.
            connection.execute(
                text("SELECT 1")
            )

        # Retorno em caso de sucesso.
        return {
            "status": "online",
            "banco": "MySQL",
            "database": "weblue",
        }

    except Exception:

        # Se houver problema de conexão,
        # retornamos HTTP 503.
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail="Banco de dados indisponível",
        )
