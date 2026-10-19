# ============================================================
# WEBLUE - AUTENTICAÇÃO DO ADMINISTRADOR
# ============================================================
#
# Este router é responsável pelo login administrativo.
#
# Fluxo:
#
# 1. Recebe e-mail e senha.
# 2. Procura o administrador no banco.
# 3. Verifica se a conta está ativa.
# 4. Confere a senha com o hash armazenado.
# 5. Gera um JWT exclusivo de administrador.
# 6. Retorna os dados do administrador autenticado.
# ============================================================


# ============================================================
# FASTAPI
# ============================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)


# ============================================================
# SQLALCHEMY
# ============================================================

from sqlalchemy.orm import Session


# ============================================================
# BANCO DE DADOS
# ============================================================
#
# O projeto Weblue utiliza get_database().
#
# Essa função cria uma sessão com o banco MySQL
# e fecha a conexão automaticamente ao final da requisição.
# ============================================================

from ..database import get_database


# ============================================================
# MODEL
# ============================================================

from ..models.administrador import Administrador


# ============================================================
# SCHEMAS
# ============================================================

from ..schemas.administrador import (
    AdministradorLogin,
    AdministradorLoginResposta,
    AdministradorResposta,
    LogoutRequest,
    RefreshTokenRequest,
)


# ============================================================
# SEGURANÇA
# ============================================================

from ..services.admin_security import (
    criar_refresh_token_admin,
    criar_token_admin,
    extrair_jti,
    revogar_token,
    verificar_refresh_token_admin,
    verificar_senha_admin,
)
from ..services.security import (
    clear_attempts,
    is_rate_limited,
    register_failed_attempt,
)


# ============================================================
# ROUTER
# ============================================================
#
# Como este router será registrado no api_router,
# que já possui prefix="/api",
#
# a rota final será:
#
# POST /api/admin/auth/login
# ============================================================

router = APIRouter(
    tags=["Admin - Autenticação"]
)


# ============================================================
# LOGIN DO ADMINISTRADOR
# ============================================================

@router.post(
    "/login",
    response_model=AdministradorLoginResposta,
    status_code=status.HTTP_200_OK,
    summary="Realizar login do administrador"
)
def login_administrador(
    request: Request,
    dados: AdministradorLogin,
    db: Session = Depends(get_database)
):
    email = dados.email.strip().lower()

    permitido, retry_after = is_rate_limited(
        request,
        email,
        prefix="login_admin",
        max_attempts=5,
        window_seconds=900,
    )

    if not permitido:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de login. Tente novamente em {retry_after} segundos."
        )

    administrador = (
        db.query(Administrador)
        .filter(
            Administrador.email == email
        )
        .first()
    )

    if administrador is None:
        register_failed_attempt(request, email, prefix="login_admin")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not administrador.ativo:
        register_failed_attempt(request, email, prefix="login_admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso administrativo desativado."
        )

    senha_correta = verificar_senha_admin(
        dados.senha,
        administrador.senha_hash
    )

    if not senha_correta:
        register_failed_attempt(request, email, prefix="login_admin")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    clear_attempts(request, email, prefix="login_admin")

    access_token = criar_token_admin(
        administrador.id
    )
    refresh_token, _ = criar_refresh_token_admin(administrador.id)

    administrador_publico = (
        AdministradorResposta.model_validate(
            administrador
        ).model_dump()
    )

    return {
        "mensagem":
            "Login administrativo realizado com sucesso.",

        "access_token":
            access_token,
        "refresh_token":
            refresh_token,
        "token_type":
            "bearer",

        "administrador":
            administrador_publico
    }


@router.post("/refresh")
def refresh_administrador(
    request: Request,
    dados: RefreshTokenRequest,
    db: Session = Depends(get_database)
):
    refresh_token = dados.refresh_token
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token ausente."
        )

    administrador_id = verificar_refresh_token_admin(refresh_token)
    if administrador_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou revogado."
        )

    administrador = db.get(Administrador, administrador_id)
    if administrador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrador não encontrado."
        )

    revogar_token(extrair_jti(refresh_token))
    novo_access_token = criar_token_admin(administrador.id)
    novo_refresh_token, _ = criar_refresh_token_admin(administrador.id)

    return {
        "access_token": novo_access_token,
        "refresh_token": novo_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout_administrador(
    request: Request,
    dados: LogoutRequest,
    db: Session = Depends(get_database)
):
    access_token = dados.access_token
    refresh_token = dados.refresh_token

    if access_token:
        revogar_token(extrair_jti(access_token))
    if refresh_token:
        revogar_token(extrair_jti(refresh_token))

    return {"mensagem": "Logout realizado com sucesso."}