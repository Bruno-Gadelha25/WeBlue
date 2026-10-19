from pydantic import BaseModel, EmailStr, Field


class LoginEntrada(BaseModel):
    email: EmailStr

    senha: str = Field(
        min_length=8,
        max_length=128
    )

    lembrar: bool = False


class ClienteAutenticado(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    status: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


class LoginResposta(BaseModel):
    mensagem: str
    access_token: str
    refresh_token: str
    token_type: str
    cliente: ClienteAutenticado