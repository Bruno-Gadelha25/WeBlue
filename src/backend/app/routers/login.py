from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..schemas.login import LoginEntrada, LoginResposta, LogoutRequest, RefreshTokenRequest
from ..services.security import (
    clear_attempts,
    criar_refresh_token_cliente,
    criar_token_acesso,
    extrair_jti,
    is_rate_limited,
    register_failed_attempt,
    revogar_token,
    verificar_refresh_token_cliente,
    verificar_senha,
)


router = APIRouter(
    tags=["Autenticação"]
)


@router.post(
    "/login",
    response_model=LoginResposta,
    status_code=status.HTTP_200_OK,
    summary="Realizar login do cliente"
)
def realizar_login(
    request: Request,
    dados: LoginEntrada,
    database: Session = Depends(get_database)
):
    permitido, retry_after = is_rate_limited(
        request,
        str(dados.email),
        prefix="login_cliente",
        max_attempts=5,
        window_seconds=900,
    )

    if not permitido:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de login. Tente novamente em {retry_after} segundos."
        )

    # Procura o cliente pelo e-mail
    consulta = select(Cliente).where(
        Cliente.email == str(dados.email)
    )

    cliente = database.scalar(consulta)

    senha_valida = (
        cliente is not None and verificar_senha(
            dados.senha,
            cliente.senha_hash
        )
    )

    if not senha_valida:
        register_failed_attempt(
            request,
            str(dados.email),
            prefix="login_cliente"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    # Verifica se a conta está bloqueada
    if cliente.status == "BLOQUEADA":
        register_failed_attempt(
            request,
            str(dados.email),
            prefix="login_cliente"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta está bloqueada."
        )

    # Verifica se a conta está inativa
    if cliente.status == "INATIVA":
        register_failed_attempt(
            request,
            str(dados.email),
            prefix="login_cliente"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta está inativa."
        )

    clear_attempts(request, str(dados.email), prefix="login_cliente")

    # Gera o JWT
    # Se "lembrar" for True, o token terá duração maior
    access_token = criar_token_acesso(
        cliente_id=cliente.id,
        lembrar=dados.lembrar
    )
    refresh_token, refresh_jti = criar_refresh_token_cliente(cliente.id)

    # Retorna o token e os dados básicos do cliente
    return {
        "mensagem": "Login realizado com sucesso.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "cliente": {
            "id": cliente.id,
            "nome_completo": cliente.nome_completo,
            "email": cliente.email,
            "status": cliente.status
        }
    }


@router.post("/refresh")
def refresh_cliente(
    request: Request,
    dados: RefreshTokenRequest,
    database: Session = Depends(get_database)
):
    refresh_token = dados.refresh_token
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token ausente."
        )

    cliente_id = verificar_refresh_token_cliente(refresh_token)
    if cliente_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou revogado."
        )

    cliente = database.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    jti_antigo = extrair_jti(refresh_token)
    revogar_token(jti_antigo)

    novo_access_token = criar_token_acesso(cliente_id=cliente.id, lembrar=False)
    novo_refresh_token, _ = criar_refresh_token_cliente(cliente.id)

    return {
        "access_token": novo_access_token,
        "refresh_token": novo_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout_cliente(
    request: Request,
    dados: LogoutRequest,
    database: Session = Depends(get_database)
):
    access_token = dados.access_token
    refresh_token = dados.refresh_token

    if access_token:
        revogar_token(extrair_jti(access_token))
    if refresh_token:
        revogar_token(extrair_jti(refresh_token))

    return {"mensagem": "Logout realizado com sucesso."}