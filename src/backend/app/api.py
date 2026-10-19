# ============================================================
# WEBLUE
# ROUTER PRINCIPAL DA API
# ============================================================
#
# Este arquivo centraliza todos os routers da aplicação.
#
# Todas as rotas do BACKEND utilizarão o prefixo:
#
# /api
#
# Exemplos:
#
# /api/clientes
# /api/auth/login
# /api/perfil
# /api/produtos
# /api/admin/auth/login
#
# As páginas do frontend NÃO são afetadas.
#
# Exemplos:
#
# /home.html
# /login
# /cliente
# /admin-produtos.html
#
# ============================================================


# ============================================================
# IMPORTAÇÃO DO FASTAPI
# ============================================================

from fastapi import APIRouter


# ============================================================
# IMPORTAÇÃO DOS ROUTERS
# ============================================================


# ------------------------------------------------------------
# CLIENTES
# ------------------------------------------------------------

from .routers.clientes import (
    router as clientes_router
)


# ------------------------------------------------------------
# LOGIN DO CLIENTE
# ------------------------------------------------------------

from .routers.login import (
    router as login_router
)


# ------------------------------------------------------------
# RECUPERAÇÃO DE SENHA
# ------------------------------------------------------------

from .routers.recuperacao_senha import (
    router as recuperacao_senha_router
)


# ------------------------------------------------------------
# PERFIL DO CLIENTE
# ------------------------------------------------------------

from .routers.perfil import (
    router as perfil_router
)


# ------------------------------------------------------------
# PRODUTOS
# ------------------------------------------------------------

from .routers.produtos import (
    router as produtos_router
)

# ------------------------------------------------------------
# PEDIDOS E VENDAS
# ------------------------------------------------------------

from .routers.pedidos import (
    router as pedidos_router
)


# ------------------------------------------------------------
# AUTENTICAÇÃO DO ADMINISTRADOR
# ------------------------------------------------------------

from .routers.admin_auth import (
    router as admin_auth_router
)


# ============================================================
# ROUTER PRINCIPAL
# ============================================================

# Todos os routers registrados abaixo recebem
# automaticamente o prefixo "/api".
#
# Exemplo:
#
# O admin_auth_router possui:
#
# /admin/auth/login
#
# Como ele é incluído neste api_router,
# a rota final será:
#
# /api/admin/auth/login

api_router = APIRouter(
    prefix="/api"
)


# ============================================================
# REGISTRO DOS ROUTERS
# ============================================================


# ------------------------------------------------------------
# CLIENTES
# ------------------------------------------------------------

api_router.include_router(
    clientes_router,
    prefix="/clientes"
)


# ------------------------------------------------------------
# LOGIN DO CLIENTE
# ------------------------------------------------------------

api_router.include_router(
    login_router,
    prefix="/auth"
)


# ------------------------------------------------------------
# RECUPERAÇÃO DE SENHA
# ------------------------------------------------------------

api_router.include_router(
    recuperacao_senha_router,
    prefix="/auth"
)


# ------------------------------------------------------------
# PERFIL DO CLIENTE
# ------------------------------------------------------------

api_router.include_router(
    perfil_router,
    prefix="/perfil"
)


# ------------------------------------------------------------
# PRODUTOS
# ------------------------------------------------------------

api_router.include_router(
    produtos_router,
    prefix="/produtos"
)


# ------------------------------------------------------------
# PEDIDOS E VENDAS
# ------------------------------------------------------------

api_router.include_router(
    pedidos_router,
    prefix="/pedidos"
)


# ------------------------------------------------------------
# AUTENTICAÇÃO DO ADMINISTRADOR
# ------------------------------------------------------------

api_router.include_router(
    admin_auth_router,
    prefix="/admin/auth"
)