# ============================================================
# WEBLUE - SCHEMAS DO ADMINISTRADOR
# ============================================================
#
# Este arquivo define os dados que entram e saem
# da API de autenticação do administrador.
#
# Os schemas são responsáveis pela validação dos dados
# recebidos pelo FastAPI.
# ============================================================


from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ============================================================
# LOGIN DO ADMINISTRADOR
# ============================================================

class AdministradorLogin(BaseModel):

    # E-mail utilizado para acessar
    # o painel administrativo.
    email: EmailStr

    # Senha informada pelo administrador.
    #
    # A senha precisa possuir pelo menos
    # 8 caracteres.
    senha: str = Field(
        ...,
        min_length=8,
        max_length=128
    )


# ============================================================
# DADOS PÚBLICOS DO ADMINISTRADOR
# ============================================================

class AdministradorResposta(BaseModel):

    # Permite criar este schema diretamente
    # a partir de um objeto SQLAlchemy.
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    nome: str

    email: EmailStr

    ativo: bool


# ============================================================
# RESPOSTA DO LOGIN
# ============================================================

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


class AdministradorLoginResposta(BaseModel):

    # Mensagem apresentada depois
    # que o login for realizado.
    mensagem: str

    # JWT que será utilizado para acessar
    # as funções protegidas do administrador.
    access_token: str

    # Refresh token usado para rotação de sessão.
    refresh_token: str

    # Tipo padrão de autenticação JWT.
    token_type: str = "bearer"

    # Informações básicas do administrador.
    administrador: AdministradorResposta