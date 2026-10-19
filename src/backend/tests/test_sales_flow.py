# ============================================================
# TESTES DO FLUXO DE VENDAS
# ============================================================
#
# Os testes abaixo validam:
#
# 1. cadastro de pedido com estoque suficiente
# 2. rejeição de venda sem estoque
# 3. atualização de saldo após confirmação
# ============================================================

from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import api_router
from app.database import get_database
from app.models.cliente import Cliente
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto


SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def sales_database_session():
    Cliente.__table__.create(bind=engine, checkfirst=True)
    Produto.__table__.create(bind=engine, checkfirst=True)
    Pedido.__table__.create(bind=engine, checkfirst=True)
    ItemPedido.__table__.create(bind=engine, checkfirst=True)

    session = TestingSessionLocal()
    try:
        session.query(ItemPedido).delete()
        session.query(Pedido).delete()
        session.query(Cliente).delete()
        session.query(Produto).delete()
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture()
def sales_client_app():
    app = FastAPI()
    app.include_router(api_router)

    def override_get_database():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_guest_checkout_creates_customer_and_tracks_orders(sales_database_session, sales_client_app):
    produto = Produto(
        id=101,
        nome="Óleo Facial",
        descricao="Óleo leve para pele mista.",
        preco=59.90,
        estoque=4,
        categoria="Skincare",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add(produto)
    sales_database_session.commit()

    response = sales_client_app.post(
        "/api/pedidos/checkout",
        json={
            "nome": "Cliente Guest",
            "email": "guest@weblue.com",
            "telefone": "11977778888",
            "endereco": "Avenida do Sol, 150",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": 101, "quantidade": 2}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pedido"]["status"] == "PAGO"
    assert payload["pedido"]["valor_total"] == "119.80"

    cliente = sales_database_session.query(Cliente).filter(Cliente.email == "guest@weblue.com").one()
    assert cliente.senha_hash.startswith("$")
    assert cliente.telefone == "11977778888"

    historico = sales_client_app.get("/api/pedidos/me?email=guest@weblue.com")
    assert historico.status_code == 200
    assert historico.json()["total"] == 1

    sales_database_session.refresh(produto)
    assert produto.estoque == 2


def test_checkout_approves_sale_and_reduces_stock(sales_database_session, sales_client_app):
    produto = Produto(
        id=102,
        nome="Sérum Vitamina C",
        descricao="Sérum para brilho e luminosidade.",
        preco=49.90,
        estoque=5,
        categoria="Skincare",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add(produto)
    sales_database_session.commit()

    response = sales_client_app.post(
        "/api/pedidos/checkout",
        json={
            "nome": "Maria Souza",
            "email": "maria@weblue.com",
            "telefone": "11999999999",
            "endereco": "Rua das Flores, 123",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": 102, "quantidade": 2}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pedido"]["status"] == "PAGO"
    assert payload["pedido"]["valor_total"] == "99.80"

    sales_database_session.refresh(produto)
    assert produto.estoque == 3

    historico = sales_client_app.get("/api/pedidos/me?email=maria@weblue.com")
    assert historico.status_code == 200
    assert historico.json()["total"] == 1


def test_checkout_rejects_sale_without_stock(sales_database_session, sales_client_app):
    produto = Produto(
        id=103,
        nome="Creme Hidratante",
        descricao="Creme para pele seca.",
        preco=39.99,
        estoque=1,
        categoria="Corpo",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add(produto)
    sales_database_session.commit()

    response = sales_client_app.post(
        "/api/pedidos/checkout",
        json={
            "nome": "João Silva",
            "email": "joao@weblue.com",
            "telefone": "11888888888",
            "endereco": "Avenida Paulista, 99",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": 103, "quantidade": 2}],
        },
    )

    assert response.status_code == 400
    assert "estoque" in response.json()["detail"].lower()

    sales_database_session.refresh(produto)
    assert produto.estoque == 1
