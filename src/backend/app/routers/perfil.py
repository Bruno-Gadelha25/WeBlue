# ============================================================
# IMPORTAÇÕES DO FASTAPI
# ============================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

# HTTPBearer é responsável por capturar o token enviado
# no cabeçalho Authorization.
#
# Exemplo:
# Authorization: Bearer eyJhbGciOi...
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)


# ============================================================
# IMPORTAÇÕES DO SQLALCHEMY
# ============================================================

# select é utilizado para realizar consultas no banco.
from sqlalchemy import select

# Session representa a sessão de comunicação com o banco.
from sqlalchemy.orm import Session


# ============================================================
# IMPORTAÇÕES DO PROJETO
# ============================================================

# Função responsável por fornecer uma sessão do banco
# de dados para cada requisição.
from ..database import get_database

# Modelo Cliente, que representa a tabela de clientes
# no banco de dados.
from ..models.cliente import Cliente

# Schema utilizado para validar os dados enviados pelo
# cliente quando ele editar o próprio perfil.
from ..schemas.perfil import AtualizarPerfilRequest

# Função responsável por verificar o JWT e retornar
# o ID do cliente autenticado.
from ..services.security import verificar_token_acesso


# ============================================================
# CONFIGURAÇÃO DO ROUTER
# ============================================================

# Todas as rotas deste arquivo começam com /perfil.
#
# Portanto:
#
# @router.get("")
#
# representa:
#
# GET /perfil
#
# E:
#
# @router.put("")
#
# representa:
#
# PUT /perfil
router = APIRouter(
    tags=["Perfil"]
)


# ============================================================
# SEGURANÇA
# ============================================================

# HTTPBearer informa ao FastAPI que as rotas abaixo
# esperam receber:
#
# Authorization: Bearer TOKEN
seguranca = HTTPBearer()


# ============================================================
# GET /perfil
# CONSULTAR PERFIL DO CLIENTE AUTENTICADO
# ============================================================

@router.get(
    "",
    summary="Consultar perfil do cliente"
)
def consultar_perfil(

    # Captura as credenciais enviadas pelo navegador.
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca),

    # Abre uma sessão com o banco de dados.
    database: Session = Depends(get_database)

):

    # ========================================================
    # 1. PEGAR TOKEN
    # ========================================================

    # HTTPBearer separa automaticamente a palavra "Bearer"
    # do token.
    #
    # Portanto, aqui recebemos somente o JWT.
    token = credenciais.credentials


    # ========================================================
    # 2. VALIDAR TOKEN
    # ========================================================

    # verificar_token_acesso() valida o JWT.
    #
    # Se estiver correto, esperamos receber o ID do cliente.
    cliente_id = verificar_token_acesso(token)


    # Se não foi possível recuperar um cliente pelo token,
    # consideramos que ele é inválido ou expirou.
    if cliente_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )


    # ========================================================
    # 3. PROCURAR CLIENTE NO BANCO
    # ========================================================

    # Equivalente aproximadamente a:
    #
    # SELECT *
    # FROM clientes
    # WHERE id = cliente_id;
    consulta = select(Cliente).where(
        Cliente.id == cliente_id
    )


    # Executa a consulta e retorna o cliente encontrado.
    cliente = database.scalar(consulta)


    # ========================================================
    # 4. VERIFICAR SE O CLIENTE EXISTE
    # ========================================================

    if cliente is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )


    # ========================================================
    # 5. VERIFICAR STATUS DA CONTA
    # ========================================================

    # Somente contas com status ATIVA podem acessar
    # normalmente a área do cliente.
    if cliente.status != "ATIVA":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta sem permissão de acesso."
        )


    # ========================================================
    # 6. RETORNAR DADOS DO CLIENTE
    # ========================================================

    # Não retornamos senha_hash nem outras informações
    # sensíveis.
    return {

        "id": cliente.id,

        "nome_completo": cliente.nome_completo,

        "email": cliente.email,

        "cpf": cliente.cpf,

        "telefone": cliente.telefone,

        "status": cliente.status
    }


# ============================================================
# PUT /perfil
# ATUALIZAR PERFIL DO CLIENTE AUTENTICADO
# ============================================================

@router.put(
    "",
    summary="Atualizar perfil do cliente"
)
def atualizar_perfil(

    # O FastAPI recebe o JSON enviado pelo frontend
    # e valida utilizando AtualizarPerfilRequest.
    dados: AtualizarPerfilRequest,

    # Token JWT enviado no cabeçalho Authorization.
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca),

    # Sessão com o banco de dados.
    database: Session = Depends(get_database)

):

    # ========================================================
    # 1. PEGAR TOKEN
    # ========================================================

    token = credenciais.credentials


    # ========================================================
    # 2. VALIDAR TOKEN
    # ========================================================

    cliente_id = verificar_token_acesso(token)


    if cliente_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )


    # ========================================================
    # 3. BUSCAR O CLIENTE AUTENTICADO
    # ========================================================

    consulta = select(Cliente).where(
        Cliente.id == cliente_id
    )

    cliente = database.scalar(consulta)


    # ========================================================
    # 4. VERIFICAR SE O CLIENTE EXISTE
    # ========================================================

    if cliente is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )


    # ========================================================
    # 5. VERIFICAR STATUS DA CONTA
    # ========================================================

    if cliente.status != "ATIVA":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta sem permissão de acesso."
        )


    # ========================================================
    # 6. NORMALIZAR O E-MAIL
    # ========================================================

    # Remove espaços extras e transforma o e-mail
    # em letras minúsculas.
    email_normalizado = str(dados.email).strip().lower()


    # ========================================================
    # 7. VERIFICAR SE O NOVO E-MAIL JÁ ESTÁ EM USO
    # ========================================================

    # Procuramos outro cliente que tenha o e-mail informado.
    #
    # O trecho:
    #
    # Cliente.id != cliente.id
    #
    # é importante para não considerar o próprio cliente
    # como um conflito.
    consulta_email = select(Cliente).where(
        Cliente.email == email_normalizado,
        Cliente.id != cliente.id
    )


    email_existente = database.scalar(
        consulta_email
    )


    # Se outro cliente já utiliza o endereço informado,
    # impedimos a alteração.
    if email_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado."
        )


    # ========================================================
    # 8. ATUALIZAR OS DADOS
    # ========================================================

    # Nome completo.
    cliente.nome_completo = dados.nome_completo.strip()

    # E-mail já normalizado.
    cliente.email = email_normalizado

    # Telefone.
    cliente.telefone = dados.telefone.strip()


    # O CPF NÃO é alterado aqui.
    #
    # Também não permitimos alterar:
    #
    # - ID
    # - status
    # - senha_hash
    #
    # por meio desta rota.


    # ========================================================
    # 9. SALVAR ALTERAÇÕES NO BANCO
    # ========================================================

    # Confirma as alterações no MySQL.
    database.commit()


    # Atualiza o objeto "cliente" com os dados que ficaram
    # efetivamente armazenados no banco.
    database.refresh(cliente)


    # ========================================================
    # 10. RETORNAR RESULTADO
    # ========================================================

    return {

        "mensagem": "Perfil atualizado com sucesso.",

        "cliente": {

            "id": cliente.id,

            "nome_completo": cliente.nome_completo,

            "email": cliente.email,

            "cpf": cliente.cpf,

            "telefone": cliente.telefone,

            "status": cliente.status
        }
    }