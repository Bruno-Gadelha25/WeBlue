from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..schemas.cliente import (
    ClienteCriacao,
    ClienteResposta,
    ClienteAtualizacao
)
from ..services.security import criar_hash_senha


router = APIRouter(
    tags=["Clientes"]
)


@router.post(
    "",
    response_model=ClienteResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo cliente"
)
def cadastrar_cliente(
    dados: ClienteCriacao,
    database: Session = Depends(get_database)
):
    consulta = select(Cliente).where(
        or_(
            Cliente.email == str(dados.email),
            Cliente.cpf == dados.cpf
        )
    )

    cliente_existente = database.scalar(consulta)

    if cliente_existente:
        if cliente_existente.email == str(dados.email):
            mensagem = "Este e-mail já está cadastrado."
        else:
            mensagem = "Este CPF já possui uma conta."

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensagem
        )

    novo_cliente = Cliente(
        nome_completo=dados.nome_completo,
        email=str(dados.email),
        cpf=dados.cpf,
        telefone=dados.telefone,
        senha_hash=criar_hash_senha(dados.senha),
        aceitou_termos_em=datetime.now(UTC).replace(tzinfo=None)
    )

    try:
        database.add(novo_cliente)
        database.commit()
        database.refresh(novo_cliente)

    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF ou e-mail já cadastrado."
        )

    return novo_cliente

