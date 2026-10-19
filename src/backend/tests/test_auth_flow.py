from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import api_router
from app.database import get_database
from app.models.administrador import Administrador
from app.models.cliente import Cliente
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.services.admin_security import criar_hash_senha_admin
from app.services.security import criar_hash_senha


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
def database_session():
    Cliente.__table__.create(bind=engine, checkfirst=True)
    Administrador.__table__.create(bind=engine, checkfirst=True)
    Produto.__table__.create(bind=engine, checkfirst=True)

    session = TestingSessionLocal()
    try:
        session.query(Cliente).delete()
        session.query(Administrador).delete()
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture()
def client_app():
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


def test_cliente_login_profile_flow(database_session, client_app):
    senha = "SenhaForte123"
    cliente = Cliente(
        id=1,
        nome_completo="Ana Souza",
        email="ana@weblue.com",
        cpf="12345678901",
        telefone="11999999999",
        senha_hash=criar_hash_senha(senha),
        status="ATIVA",
        aceitou_termos_em=datetime.utcnow(),
    )
    database_session.add(cliente)
    database_session.commit()
    database_session.refresh(cliente)

    response = client_app.post(
        "/api/auth/login",
        json={"email": cliente.email, "senha": senha, "lembrar": False},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cliente"]["email"] == cliente.email
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"

    token = payload["access_token"]
    perfil_response = client_app.get(
        "/api/perfil",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert perfil_response.status_code == 200
    perfil = perfil_response.json()
    assert perfil["email"] == cliente.email
    assert perfil["status"] == "ATIVA"

    update_response = client_app.put(
        "/api/perfil",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome_completo": "Ana Pereira",
            "email": "ana.nova@weblue.com",
            "telefone": "11888888888",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["cliente"]["email"] == "ana.nova@weblue.com"
    assert updated["cliente"]["nome_completo"] == "Ana Pereira"


def test_admin_login_returns_public_data(database_session, client_app):
    senha = "SenhaAdmin123"
    administrador = Administrador(
        id=1,
        nome="Admin Central",
        email="admin@weblue.com",
        senha_hash=criar_hash_senha_admin(senha),
        ativo=True,
    )
    database_session.add(administrador)
    database_session.commit()
    database_session.refresh(administrador)

    response = client_app.post(
        "/api/admin/auth/login",
        json={"email": administrador.email, "senha": senha},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["administrador"]["email"] == administrador.email
    assert payload["administrador"]["nome"] == administrador.nome
    assert "senha_hash" not in payload["administrador"]
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"


def test_admin_products_require_valid_token(database_session, client_app):
    senha = "SenhaAdmin123"
    administrador = Administrador(
        id=1,
        nome="Admin Central",
        email="admin@weblue.com",
        senha_hash=criar_hash_senha_admin(senha),
        ativo=True,
    )
    database_session.add(administrador)
    database_session.commit()
    database_session.refresh(administrador)

    resposta_sem_token = client_app.get("/api/produtos")
    assert resposta_sem_token.status_code == 401

    resposta_login = client_app.post(
        "/api/admin/auth/login",
        json={"email": administrador.email, "senha": senha},
    )
    assert resposta_login.status_code == 200
    token = resposta_login.json()["access_token"]

    resposta_com_token = client_app.get(
        "/api/produtos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta_com_token.status_code == 200
    assert "produtos" in resposta_com_token.json()
