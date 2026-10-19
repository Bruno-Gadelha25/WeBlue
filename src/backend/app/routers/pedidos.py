# ============================================================
# ROTAS DO FLUXO DE VENDAS
# ============================================================
#
# Este router centraliza o ciclo de vendas do Weblue:
#
# 1. Carrinho / checkout
# 2. Simulação de pagamento
# 3. Registro do pedido
# 4. Histórico do cliente
# 5. Controle de estoque
#
# O projeto já possui os models Pedido, ItemPedido e Produto,
# então reutilizamos essa base para evitar duplicação.
# ============================================================

import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..models.item_pedido import ItemPedido
from ..models.pedido import Pedido, StatusPedido
from ..models.produto import Produto
from ..schemas.pedido import CheckoutRequest
from ..services.admin_security import verificar_token_admin
from ..services.security import criar_hash_senha

router = APIRouter(tags=["Pedidos e Vendas"])
seguranca_admin = HTTPBearer()


def exigir_admin_autenticado(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca_admin),
) -> int:
    admin_id = verificar_token_admin(credenciais.credentials)
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token administrativo inválido ou expirado.",
        )
    return admin_id


def _normalizar_telefone(telefone: str | None) -> str:
    if not telefone:
        return ""
    return "".join(ch for ch in telefone if ch.isdigit())[:11]


def _gerar_cpf_guest(email: str, telefone: str | None) -> str:
    base = f"guest:{(email or '').strip().lower()}:{_normalizar_telefone(telefone) or 'sem-telefone'}"
    valor = int(uuid.uuid5(uuid.NAMESPACE_DNS, base).hex[:12], 16) % 10**11
    return str(valor).zfill(11)


def simular_pagamento(metodo_pagamento: str, numero_cartao: str | None) -> bool:
    """Simula o resultado do pagamento sem depender de gateway real."""

    # PIX geralmente é aprovado imediatamente em um fluxo simples.
    if metodo_pagamento == "PIX":
        return True

    # Cabe ao cartão validar informações mínimas do número.
    if not numero_cartao:
        return False

    numeros = "".join(ch for ch in numero_cartao if ch.isdigit())

    if len(numeros) < 13:
        return False

    # Também simulamos um cenário simples de rejeição.
    # Caso o número tenha todos os dígitos repetidos,
    # a transação é recusada.
    return not all(digito == numeros[0] for digito in numeros)


@router.post(
    "/checkout",
    status_code=status.HTTP_200_OK,
    summary="Finalizar compra e registrar pedido",
)
def finalizar_compra(
    dados: CheckoutRequest,
    database: Session = Depends(get_database),
):
    """Valida o carrinho, confirma a venda e atualiza o estoque."""

    if not dados.itens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O carrinho está vazio.",
        )

    # Caso o cliente tenha sido informado por e-mail,
    # buscamos o cadastro existente no banco.
    cliente = None
    if dados.cliente_id is not None:
        cliente = database.get(Cliente, dados.cliente_id)

    if cliente is None and dados.email:
        cliente = database.scalar(
            select(Cliente).where(Cliente.email == str(dados.email).strip().lower())
        )

    telefone_normalizado = _normalizar_telefone(dados.telefone)
    if cliente is None and telefone_normalizado:
        cliente = database.scalar(
            select(Cliente).where(Cliente.telefone == telefone_normalizado)
        )

    # Se o cliente ainda não existe, aceitamos uma compra simples
    # utilizando dados básicos do checkout para não bloquear o fluxo.
    if cliente is None:
        nome_cliente = (dados.nome or "Cliente Weblue").strip()
        email_cliente = (dados.email or "cliente@weblue.local").strip().lower()

        proximo_cliente_id = (database.scalar(select(func.max(Cliente.id))) or 0) + 1
        cpf_guest = _gerar_cpf_guest(email_cliente, telefone_normalizado)
        while database.scalar(select(Cliente).where(Cliente.cpf == cpf_guest)) is not None:
            cpf_guest = _gerar_cpf_guest(f"{email_cliente}:{uuid.uuid4().hex}", telefone_normalizado)

        cliente = Cliente(
            id=proximo_cliente_id,
            nome_completo=nome_cliente,
            email=email_cliente,
            cpf=cpf_guest,
            telefone=telefone_normalizado or "00000000000",
            senha_hash=criar_hash_senha(f"guest-{uuid.uuid4().hex}"),
            status="ATIVA",
            aceitou_termos_em=datetime.utcnow(),
        )
        database.add(cliente)
        database.flush()

    # Repassamos a ordem de compra conforme carrinho.
    total_pedido = Decimal("0.00")
    itens_do_pedido = []

    for item in dados.itens:
        produto = database.get(Produto, item.produto_id)
        if produto is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto {item.produto_id} não encontrado.",
            )

        if produto.estoque < item.quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Produto '{produto.nome}' não possui estoque suficiente. "
                    f"Disponível: {produto.estoque}"
                ),
            )

        subtotal = Decimal(str(produto.preco)) * item.quantidade
        total_pedido += subtotal
        itens_do_pedido.append(
            {
                "produto": produto,
                "quantidade": item.quantidade,
                "subtotal": subtotal,
            }
        )

    # Simulamos a aprovação do pagamento antes de registrar o pedido.
    pagamento_aprovado = simular_pagamento(
        dados.metodo_pagamento,
        dados.numero_cartao,
    )

    if not pagamento_aprovado:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Pagamento recusado. Verifique os dados do pagamento e tente novamente.",
        )

    proximo_pedido_id = (database.scalar(select(func.max(Pedido.id))) or 0) + 1

    pedido = Pedido(
        id=proximo_pedido_id,
        cliente_id=cliente.id,
        status=StatusPedido.PAGO,
        valor_total=total_pedido,
    )
    database.add(pedido)
    database.flush()

    for item in itens_do_pedido:
        produto = item["produto"]
        quantidade = item["quantidade"]
        subtotal = item["subtotal"]

        produto.estoque -= quantidade

        proximo_item_pedido_id = (database.scalar(select(func.max(ItemPedido.id))) or 0) + 1
        item_pedido = ItemPedido(
            id=proximo_item_pedido_id,
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=Decimal(str(produto.preco)),
            subtotal=subtotal,
        )
        database.add(item_pedido)

    database.commit()
    database.refresh(pedido)

    return {
        "mensagem": "Pedido registrado com sucesso.",
        "pedido": {
            "id": pedido.id,
            "status": pedido.status.value,
            "valor_total": str(pedido.valor_total),
            "metodo_pagamento": dados.metodo_pagamento,
            "endereco": dados.endereco,
            "criado_em": pedido.criado_em.isoformat() if pedido.criado_em else None,
            "itens": [
                {
                    "produto_id": item["produto"].id,
                    "nome": item["produto"].nome,
                    "quantidade": item["quantidade"],
                    "subtotal": str(item["subtotal"]),
                }
                for item in itens_do_pedido
            ],
        },
    }


@router.get(
    "/me",
    summary="Listar pedidos do cliente",
)
def listar_pedidos_cliente(
    email: str | None = Query(default=None),
    cliente_id: int | None = Query(default=None),
    database: Session = Depends(get_database),
):
    """Retorna o histórico de pedidos do cliente informado."""

    filtro_cliente = None

    if cliente_id is not None:
        filtro_cliente = Cliente.id == cliente_id
    elif email:
        filtro_cliente = Cliente.email == str(email).strip().lower()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe cliente_id ou e-mail para consultar o histórico.",
        )

    cliente = database.scalar(select(Cliente).where(filtro_cliente))
    if cliente is None:
        return {"total": 0, "pedidos": []}

    pedidos = (
        database.execute(
            select(Pedido)
            .where(Pedido.cliente_id == cliente.id)
            .order_by(Pedido.criado_em.desc())
        )
        .scalars()
        .all()
    )

    resposta = []
    for pedido in pedidos:
        itens = []
        for item in pedido.itens:
            itens.append(
                {
                    "produto_id": item.produto_id,
                    "nome": item.produto.nome if item.produto else "Produto",
                    "quantidade": item.quantidade,
                    "subtotal": str(item.subtotal),
                }
            )

        resposta.append(
            {
                "id": pedido.id,
                "status": pedido.status.value,
                "valor_total": str(pedido.valor_total),
                "criado_em": pedido.criado_em.isoformat() if pedido.criado_em else None,
                "itens": itens,
            }
        )

    return {"total": len(resposta), "pedidos": resposta}


@router.get(
    "",
    summary="Listar todos os pedidos",
)
def listar_pedidos(
    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):
    """Lista pedidos do sistema para uso administrativo ou consulta simples."""

    pedidos = (
        database.execute(
            select(Pedido)
            .order_by(Pedido.criado_em.desc())
        )
        .scalars()
        .all()
    )

    resposta = []
    for pedido in pedidos:
        resposta.append(
            {
                "id": pedido.id,
                "cliente_id": pedido.cliente_id,
                "status": pedido.status.value,
                "valor_total": str(pedido.valor_total),
                "criado_em": pedido.criado_em.isoformat() if pedido.criado_em else None,
                "itens": [
                    {
                        "produto_id": item.produto_id,
                        "nome": item.produto.nome if item.produto else "Produto",
                        "quantidade": item.quantidade,
                        "subtotal": str(item.subtotal),
                    }
                    for item in pedido.itens
                ],
            }
        )

    return {"total": len(resposta), "pedidos": resposta}


@router.get(
    "/estoque",
    summary="Consultar disponibilidade de estoque",
)
def consultar_estoque(
    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):
    """Retorna os produtos com quantidade disponível em estoque."""

    produtos = database.execute(
        select(Produto).order_by(Produto.id)
    ).scalars().all()

    return {
        "total": len(produtos),
        "produtos": [
            {
                "id": produto.id,
                "nome": produto.nome,
                "estoque": produto.estoque,
                "status": produto.status,
                "preco": str(produto.preco),
                "categoria": produto.categoria,
            }
            for produto in produtos
        ],
    }
