# ============================================================
# WEBLUE - SEGURANÇA DO ADMINISTRADOR
# ============================================================
#
# Este arquivo cuida exclusivamente da segurança
# relacionada aos administradores.
#
# Responsabilidades:
#
# 1. Criar hash da senha do administrador.
# 2. Verificar a senha no momento do login.
# 3. Criar JWT administrativo.
# 4. Validar JWT administrativo.
#
# IMPORTANTE:
#
# O token administrativo utiliza:
#
# "tipo": "admin"
#
# Dessa forma, um token normal de cliente não poderá
# ser utilizado para acessar rotas administrativas.
# ============================================================


# ============================================================
# IMPORTAÇÕES
# ============================================================

import uuid
from datetime import (
    datetime,
    timedelta,
    timezone,
)

# A Weblue já utiliza PyJWT no security.py dos clientes.
# Portanto, mantemos a mesma biblioteca aqui.
import jwt

# Biblioteca utilizada pelo projeto para gerar
# e verificar hashes de senha.
from pwdlib import PasswordHash

# Configurações gerais da aplicação.
from ..config import settings

JWT_ISSUER = "weblue"

_REVOKED_JTIS: set[str] = set()

REFRESH_TOKEN_DIAS = 7


# ============================================================
# CONFIGURAÇÃO DO HASH DE SENHA
# ============================================================

# Utiliza a configuração recomendada pelo pwdlib.
#
# É o mesmo padrão utilizado na autenticação dos clientes.
password_hash = PasswordHash.recommended()


# ============================================================
# CONFIGURAÇÃO JWT
# ============================================================

# Chave secreta utilizada para assinar os tokens.
SECRET_KEY = settings.jwt_secret_key

# Algoritmo utilizado para gerar e validar o JWT.
ALGORITHM = settings.jwt_algorithm

# Tempo padrão de duração do token.
TEMPO_TOKEN_MINUTOS = settings.jwt_expire_minutes


# ============================================================
# CRIAR HASH DA SENHA DO ADMINISTRADOR
# ============================================================

def criar_hash_senha_admin(
    senha: str
) -> str:
    """
    Recebe a senha original do administrador
    e gera um hash seguro.

    A senha original nunca deve ser armazenada
    diretamente no banco de dados.
    """

    return password_hash.hash(senha)


# ============================================================
# VERIFICAR SENHA DO ADMINISTRADOR
# ============================================================

def verificar_senha_admin(
    senha: str,
    senha_hash: str
) -> bool:
    """
    Compara a senha informada no login
    com o hash armazenado no banco.

    Retorna:
        True  -> senha correta
        False -> senha incorreta
    """

    try:

        return password_hash.verify(
            senha,
            senha_hash
        )

    except Exception:

        # Caso exista algum problema durante
        # a verificação, o acesso é negado.
        return False


# ============================================================
# CRIAR TOKEN JWT DO ADMINISTRADOR
# ============================================================

def criar_token_admin(
    administrador_id: int,
    jti: str | None = None
) -> str:
    """
    Cria um JWT exclusivo para o administrador.

    O token contém:

    sub  -> ID do administrador
    tipo -> identifica que é um token administrativo
    iat  -> momento de criação
    exp  -> momento de expiração
    """

    agora = datetime.now(
        timezone.utc
    )

    expiracao = agora + timedelta(
        minutes=TEMPO_TOKEN_MINUTOS
    )

    dados_token = {
        "sub": str(administrador_id),
        "tipo": "admin",
        "iss": JWT_ISSUER,
        "iat": int(agora.timestamp()),
        "nbf": int(agora.timestamp()),
        "exp": int(expiracao.timestamp()),
        "jti": jti or str(uuid.uuid4()),
    }


    # ========================================================
    # GERAR TOKEN
    # ========================================================

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


    return token


def criar_refresh_token_admin(administrador_id: int) -> tuple[str, str]:
    """Cria um refresh token para o administrador."""

    agora = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    expiracao = agora + timedelta(days=REFRESH_TOKEN_DIAS)
    dados_token = {
        "sub": str(administrador_id),
        "tipo": "admin_refresh",
        "iss": JWT_ISSUER,
        "iat": int(agora.timestamp()),
        "nbf": int(agora.timestamp()),
        "exp": int(expiracao.timestamp()),
        "jti": jti,
    }
    token = jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


def extrair_jti(token: str) -> str | None:
    """Extrai o identificador do token sem validar assinatura ou expiração."""

    try:
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
            },
        )
        return payload.get("jti")
    except Exception:
        return None


def revogar_token(jti: str | None) -> None:
    if jti:
        _REVOKED_JTIS.add(jti)


def token_foi_revogado(jti: str | None) -> bool:
    return bool(jti and jti in _REVOKED_JTIS)


# ============================================================
# VERIFICAR TOKEN JWT DO ADMINISTRADOR
# ============================================================

def verificar_token_admin(
    token: str
) -> int | None:
    """
    Valida um token administrativo.

    Se o token for válido:
        retorna o ID do administrador.

    Se o token for inválido ou expirado:
        retorna None.

    Tokens de clientes também serão recusados,
    porque eles não possuem "tipo": "admin".
    """

    try:
        dados_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            options={
                "require": ["sub", "tipo", "iat", "exp", "iss", "nbf", "jti"],
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
            }
        )

        tipo_token = dados_token.get("tipo")
        if tipo_token != "admin":
            return None

        jti = dados_token.get("jti")
        if token_foi_revogado(jti):
            return None

        administrador_id = dados_token.get("sub")
        if administrador_id is None:
            return None

        return int(administrador_id)

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError
    ):
        return None


def verificar_refresh_token_admin(token: str) -> int | None:
    """Valida refresh token do administrador e rejeita tokens revogados."""

    try:
        dados_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            options={
                "require": ["sub", "tipo", "iat", "exp", "iss", "nbf", "jti"],
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
            },
        )

        if dados_token.get("tipo") != "admin_refresh":
            return None

        jti = dados_token.get("jti")
        if token_foi_revogado(jti):
            return None

        administrador_id = dados_token.get("sub")
        if administrador_id is None:
            return None

        return int(administrador_id)
    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError,
    ):
        return None