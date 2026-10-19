from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente

from ..schemas.recuperacao_senha import (
    SolicitarRecuperacaoRequest,
    RedefinirSenhaRequest
)

from ..services.security import (
    clear_attempts,
    criar_hash_senha,
    criar_token_recuperacao,
    is_rate_limited,
    register_failed_attempt,
    verificar_token_recuperacao,
)


router = APIRouter(
    tags=["Autenticação"]
)


# ==========================================
# ETAPA 1 - SOLICITAR RECUPERAÇÃO
# ==========================================

@router.post(
    "/solicitar-recuperacao",
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperação de senha"
)
def solicitar_recuperacao(
    request: Request,
    dados: SolicitarRecuperacaoRequest,
    database: Session = Depends(get_database)
):

    email = str(dados.email)

    permitido, retry_after = is_rate_limited(
        request,
        email,
        prefix="recuperacao_cliente",
        max_attempts=3,
        window_seconds=900,
    )

    if not permitido:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de recuperação. Tente novamente em {retry_after} segundos."
        )

    consulta = select(Cliente).where(
        Cliente.email == email
    )

    cliente = database.scalar(consulta)

    if cliente is None:
        register_failed_attempt(request, email, prefix="recuperacao_cliente")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    criar_token_recuperacao(
        cliente.email
    )
    clear_attempts(request, email, prefix="recuperacao_cliente")

    return {
        "mensagem": (
            "Se o e-mail estiver cadastrado, "
            "um link de recuperação foi enviado. "
            "Use o token recebido por e-mail para redefinir a senha."
        )
    }


# ==========================================
# ETAPA 2 - REDEFINIR SENHA
# ==========================================

@router.post(
    "/redefinir-senha",
    status_code=status.HTTP_200_OK,
    summary="Redefinir senha do cliente"
)
def redefinir_senha(
    dados: RedefinirSenhaRequest,
    database: Session = Depends(get_database)
):

    email = str(dados.email)

    # Verifica se o token é válido
    token_valido = verificar_token_recuperacao(
        dados.token,
        email
    )

    if not token_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )

    # Procura o cliente no banco
    consulta = select(Cliente).where(
        Cliente.email == email
    )

    cliente = database.scalar(consulta)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    # Cria o hash da nova senha
    cliente.senha_hash = criar_hash_senha(
        dados.nova_senha
    )

    # Salva a nova senha no MySQL
    database.commit()
    database.refresh(cliente)

    return {
        "mensagem": (
            "Senha alterada com sucesso. "
            "Você já pode realizar o login."
        )
    }