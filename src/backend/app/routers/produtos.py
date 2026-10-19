# ============================================================
# IMPORTAÇÕES
# ============================================================

# APIRouter:
# permite organizar as rotas relacionadas aos produtos.
#
# Depends:
# permite solicitar dependências, como a conexão com o banco.
#
# HTTPException:
# permite retornar erros HTTP personalizados.
#
# status:
# fornece códigos HTTP prontos, como 201 e 404.
#
# UploadFile:
# representa o arquivo enviado pelo navegador.
#
# File:
# informa ao FastAPI que receberemos um arquivo
# utilizando multipart/form-data.

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

# select é utilizado para realizar consultas
# utilizando o SQLAlchemy 2.x.
from sqlalchemy import select

# Session representa uma sessão/conexão com o banco.
from sqlalchemy.orm import Session

# Path permite trabalhar com caminhos e pastas.
from pathlib import Path

# uuid será utilizado para gerar nomes únicos
# para as imagens dos produtos.
import uuid


# ============================================================
# IMPORTAÇÕES INTERNAS DA WEBLUE
# ============================================================

# get_database fornece uma sessão do banco MySQL
# para cada requisição realizada na API.
from ..database import get_database

# Importa o model Produto.
from ..models.produto import Produto
from ..services.admin_security import verificar_token_admin

# Importa os schemas utilizados para validar
# os dados recebidos pela API.
from ..schemas.produto import (
    CriarProdutoRequest,
    AtualizarProdutoRequest,
)
# ============================================================
# CRIAÇÃO DO ROUTER
# ============================================================

# Todas as rotas deste arquivo começarão com:
#
# /produtos
#
# Exemplo:
#
# POST /produtos
# GET  /produtos
router = APIRouter(
    tags=["Produtos"]
)

seguranca_admin = HTTPBearer()


def exigir_admin_autenticado(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca_admin)
) -> int:
    admin_id = verificar_token_admin(credenciais.credentials)

    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token administrativo inválido ou expirado."
        )

    return admin_id


# ============================================================
# CADASTRAR PRODUTO
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo produto"
)
def cadastrar_produto(
    dados: CriarProdutoRequest,
    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):

    """
    Cadastra um novo produto no banco de dados.

    Fluxo:

    1. Recebe os dados.
    2. Valida os dados com Pydantic.
    3. Cria um objeto Produto.
    4. Salva no MySQL.
    5. Retorna o produto cadastrado.
    """


    # ========================================================
    # NORMALIZAÇÃO DOS DADOS
    # ========================================================

    # strip() remove espaços desnecessários
    # no começo e no final dos textos.
    #
    # Exemplo:
    #
    # "  Sérum Facial  "
    #
    # passa a ser:
    #
    # "Sérum Facial"

    nome = dados.nome.strip()

    descricao = dados.descricao.strip()

    categoria = dados.categoria.strip()

    marca = dados.marca.strip()


    # ========================================================
    # VALIDAÇÃO ADICIONAL
    # ========================================================

    # O Pydantic verifica o tamanho da string antes
    # da execução desta função.
    #
    # Porém uma entrada contendo somente espaços poderia
    # passar pela validação de tamanho.
    #
    # Depois do strip(), verificamos novamente.

    if len(nome) < 2:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O nome do produto é inválido."
        )


    if len(descricao) < 5:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A descrição do produto é inválida."
        )


    if len(categoria) < 2:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A categoria do produto é inválida."
        )


    if len(marca) < 2:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A marca do produto é inválida."
        )


    # ========================================================
    # CRIAÇÃO DO PRODUTO
    # ========================================================

    # Criamos um objeto Produto utilizando os dados
    # que chegaram pela API.
    novo_produto = Produto(

        nome=nome,

        descricao=descricao,

        preco=dados.preco,

        estoque=dados.estoque,

        categoria=categoria,

        marca=marca,

        imagem_url=(
            dados.imagem_url.strip()
            if dados.imagem_url
            else None
        ),

        # Todo novo produto começa ativo.
        status="ATIVO"
    )


    # ========================================================
    # SALVAR NO BANCO
    # ========================================================

    # Adiciona o produto à sessão do SQLAlchemy.
    database.add(
        novo_produto
    )


    # Confirma a operação no MySQL.
    database.commit()


    # Atualiza o objeto Python com os dados
    # gerados pelo banco.
    #
    # Por exemplo:
    #
    # id
    # data_criacao
    # data_atualizacao
    database.refresh(
        novo_produto
    )


    # ========================================================
    # RESPOSTA
    # ========================================================

    return {

        "mensagem":
            "Produto cadastrado com sucesso.",

        "produto": {

            "id":
                novo_produto.id,

            "nome":
                novo_produto.nome,

            "descricao":
                novo_produto.descricao,

            # Decimal não deve ser convertido para float
            # internamente para cálculos financeiros.
            #
            # Aqui utilizamos str somente na resposta
            # para apresentar o valor de maneira previsível.
            "preco":
                str(novo_produto.preco),

            "estoque":
                novo_produto.estoque,

            "categoria":
                novo_produto.categoria,

            "marca":
                novo_produto.marca,

            "imagem_url":
                novo_produto.imagem_url,

            "status":
                novo_produto.status,

            "data_criacao":
                novo_produto.data_criacao,

            "data_atualizacao":
                novo_produto.data_atualizacao
        }
    }


# ============================================================
# LISTAR PRODUTOS
# ============================================================

@router.get(
    "/catalogo",
    summary="Listar catálogo público de produtos"
)
def listar_catalogo_publico(
    database: Session = Depends(get_database),
):
    """Retorna somente os produtos ativos para a vitrine da loja."""

    consulta = (
        select(Produto)
        .where(Produto.status == "ATIVO")
        .order_by(Produto.id)
    )

    produtos = database.scalars(consulta).all()
    lista_produtos = []

    for produto in produtos:
        lista_produtos.append({
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "preco": str(produto.preco),
            "estoque": produto.estoque,
            "categoria": produto.categoria,
            "marca": produto.marca,
            "imagem_url": produto.imagem_url,
            "status": produto.status,
            "data_criacao": produto.data_criacao,
            "data_atualizacao": produto.data_atualizacao,
        })

    return {
        "total": len(lista_produtos),
        "produtos": lista_produtos,
    }


@router.get(
    "",
    summary="Listar produtos"
)
def listar_produtos(
    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):

    """
    Retorna todos os produtos cadastrados.

    Nesta primeira versão também retornaremos produtos
    inativos.

    Depois podemos adicionar filtros como:

    /produtos?categoria=Skincare
    /produtos?marca=Weblue
    /produtos?status=ATIVO
    """


    # ========================================================
    # CONSULTA
    # ========================================================

    # Criamos:
    #
    # SELECT * FROM produtos
    #
    # ordenando pelo ID do produto.
    consulta = (
        select(Produto)
        .order_by(Produto.id)
    )


    # Executa a consulta.
    resultado = database.scalars(
        consulta
    )


    # Converte o resultado em uma lista.
    produtos = resultado.all()


    # ========================================================
    # PREPARAR RESPOSTA
    # ========================================================

    lista_produtos = []


    # Percorremos cada produto encontrado no banco.
    for produto in produtos:

        lista_produtos.append({

            "id":
                produto.id,

            "nome":
                produto.nome,

            "descricao":
                produto.descricao,

            "preco":
                str(produto.preco),

            "estoque":
                produto.estoque,

            "categoria":
                produto.categoria,

            "marca":
                produto.marca,

            "imagem_url":
                produto.imagem_url,

            "status":
                produto.status,

            "data_criacao":
                produto.data_criacao,

            "data_atualizacao":
                produto.data_atualizacao
        })


    # ========================================================
    # RESPOSTA
    # ========================================================

    return {

        # Quantidade de produtos encontrados.
        "total":
            len(lista_produtos),

        # Lista com os produtos.
        "produtos":
            lista_produtos
    }

# ============================================================
# BUSCAR PRODUTO POR ID
# ============================================================

@router.get(
    "/{produto_id}",
    summary="Buscar produto por ID"
)
def buscar_produto_por_id(
    produto_id: int,
    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):

    """
    Busca um produto específico utilizando o seu ID.

    Exemplo:

    GET /produtos/1

    Fluxo:

    1. Recebe o ID pela URL.
    2. Procura o produto no banco de dados.
    3. Se o produto não existir, retorna erro 404.
    4. Se existir, retorna os dados do produto.
    """


    # ========================================================
    # BUSCAR PRODUTO
    # ========================================================

    # Criamos uma consulta equivalente a:
    #
    # SELECT * FROM produtos
    # WHERE id = produto_id
    #
    # Exemplo:
    #
    # GET /produtos/1
    #
    # procura o produto cujo ID é 1.
    consulta = select(Produto).where(
        Produto.id == produto_id
    )


    # Executamos a consulta no banco.
    #
    # scalar_one_or_none() pode retornar:
    #
    # Produto -> quando encontrou o registro.
    # None    -> quando não encontrou.
    produto = database.execute(
        consulta
    ).scalar_one_or_none()


    # ========================================================
    # VERIFICAR SE O PRODUTO EXISTE
    # ========================================================

    # Caso nenhum produto tenha sido encontrado,
    # retornamos o código HTTP 404.
    if produto is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )


    # ========================================================
    # RESPOSTA
    # ========================================================

    # Se chegamos até aqui, significa que o produto existe.
    #
    # Retornamos todos os dados necessários para o frontend.
    return {

        "produto": {

            "id":
                produto.id,

            "nome":
                produto.nome,

            "descricao":
                produto.descricao,

            # O preço é Decimal no banco.
            #
            # Transformamos em string apenas para manter
            # o mesmo padrão utilizado nas outras rotas.
            "preco":
                str(produto.preco),

            "estoque":
                produto.estoque,

            "categoria":
                produto.categoria,

            "marca":
                produto.marca,

            "imagem_url":
                produto.imagem_url,

            "status":
                produto.status,

            "data_criacao":
                produto.data_criacao,

            "data_atualizacao":
                produto.data_atualizacao
        }
    }# ============================================================
# ATUALIZAR PRODUTO
# ============================================================

@router.put(
    "/{produto_id}",
    summary="Atualizar produto"
)
def atualizar_produto(
    produto_id: int,
    dados: AtualizarProdutoRequest,
    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):

    """
    Atualiza os dados de um produto existente.

    Exemplo:

    PUT /produtos/1

    É possível atualizar apenas os campos desejados.

    Exemplo:

    {
        "preco": 64.90,
        "estoque": 30
    }
    """


    # ========================================================
    # BUSCAR PRODUTO
    # ========================================================

    # Procura no banco o produto correspondente ao ID.
    #
    # Equivalente a:
    #
    # SELECT * FROM produtos
    # WHERE id = produto_id;
    consulta = select(Produto).where(
        Produto.id == produto_id
    )


    # Executa a consulta.
    #
    # Se encontrar, retorna o objeto Produto.
    #
    # Se não encontrar, retorna None.
    produto = database.execute(
        consulta
    ).scalar_one_or_none()


    # ========================================================
    # VERIFICAR SE O PRODUTO EXISTE
    # ========================================================

    if produto is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )


    # ========================================================
    # IDENTIFICAR CAMPOS ENVIADOS
    # ========================================================

    # exclude_unset=True é muito importante.
    #
    # Ele faz com que somente os campos realmente enviados
    # sejam considerados na atualização.
    #
    # Exemplo:
    #
    # {
    #     "preco": 64.90
    # }
    #
    # Somente o preço será alterado.
    dados_atualizacao = dados.model_dump(
        exclude_unset=True
    )


    # ========================================================
    # NORMALIZAR NOME
    # ========================================================

    if "nome" in dados_atualizacao:

        if dados_atualizacao["nome"] is None:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O nome do produto é inválido."
            )

        nome = dados_atualizacao["nome"].strip()

        if len(nome) < 2:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O nome do produto é inválido."
            )

        dados_atualizacao["nome"] = nome


    # ========================================================
    # NORMALIZAR DESCRIÇÃO
    # ========================================================

    if "descricao" in dados_atualizacao:

        if dados_atualizacao["descricao"] is None:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A descrição do produto é inválida."
            )

        descricao = dados_atualizacao["descricao"].strip()

        if len(descricao) < 5:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A descrição do produto é inválida."
            )

        dados_atualizacao["descricao"] = descricao


    # ========================================================
    # NORMALIZAR CATEGORIA
    # ========================================================

    if "categoria" in dados_atualizacao:

        if dados_atualizacao["categoria"] is None:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A categoria do produto é inválida."
            )

        categoria = dados_atualizacao["categoria"].strip()

        if len(categoria) < 2:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A categoria do produto é inválida."
            )

        dados_atualizacao["categoria"] = categoria


    # ========================================================
    # NORMALIZAR MARCA
    # ========================================================

    if "marca" in dados_atualizacao:

        if dados_atualizacao["marca"] is None:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A marca do produto é inválida."
            )

        marca = dados_atualizacao["marca"].strip()

        if len(marca) < 2:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A marca do produto é inválida."
            )

        dados_atualizacao["marca"] = marca


    # ========================================================
    # TRATAR IMAGEM
    # ========================================================

    if "imagem_url" in dados_atualizacao:

        imagem_url = dados_atualizacao["imagem_url"]

        # imagem_url pode ser None.
        #
        # Isso permite remover uma imagem existente.
        if imagem_url is not None:

            imagem_url = imagem_url.strip()

            dados_atualizacao["imagem_url"] = (
                imagem_url
                if imagem_url
                else None
            )


    # ========================================================
    # VALIDAR STATUS
    # ========================================================

    if "status" in dados_atualizacao:

        status_produto = dados_atualizacao["status"]

        # Se o campo status foi enviado,
        # não permitimos valor null.
        if status_produto is None:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O status do produto é inválido."
            )


        # Remove espaços e converte para maiúsculas.
        #
        # ativo -> ATIVO
        # Ativo -> ATIVO
        status_produto = status_produto.strip().upper()


        # Atualmente a Weblue trabalha com:
        #
        # ATIVO
        # INATIVO
        if status_produto not in [
            "ATIVO",
            "INATIVO"
        ]:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Status inválido. "
                    "Utilize ATIVO ou INATIVO."
                )
            )


        dados_atualizacao["status"] = status_produto


    # ========================================================
    # ATUALIZAR CAMPOS
    # ========================================================

    # Percorremos somente os campos enviados.
    #
    # setattr() altera dinamicamente o atributo
    # correspondente no objeto Produto.
    #
    # Exemplo:
    #
    # campo = "estoque"
    # valor = 30
    #
    # equivale a:
    #
    # produto.estoque = 30
    for campo, valor in dados_atualizacao.items():

        setattr(
            produto,
            campo,
            valor
        )


    # ========================================================
    # SALVAR NO MYSQL
    # ========================================================

    # Confirma as alterações no banco.
    database.commit()


    # Atualiza o objeto com os valores atuais
    # armazenados no MySQL.
    database.refresh(
        produto
    )


    # ========================================================
    # RESPOSTA
    # ========================================================

    return {

        "mensagem":
            "Produto atualizado com sucesso.",

        "produto": {

            "id":
                produto.id,

            "nome":
                produto.nome,

            "descricao":
                produto.descricao,

            "preco":
                str(produto.preco),

            "estoque":
                produto.estoque,

            "categoria":
                produto.categoria,

            "marca":
                produto.marca,

            "imagem_url":
                produto.imagem_url,

            "status":
                produto.status,

            "data_criacao":
                produto.data_criacao,

            "data_atualizacao":
                produto.data_atualizacao
        }
    }# ============================================================
# DESATIVAR PRODUTO
# ============================================================

@router.delete(
    "/{produto_id}",
    summary="Desativar produto"
)
def desativar_produto(
    produto_id: int,
    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):

    """
    Desativa um produto existente.

    Exemplo:

    DELETE /produtos/1

    IMPORTANTE:

    O produto NÃO será apagado fisicamente do banco.

    Em vez disso, seu status será alterado:

    ATIVO -> INATIVO

    Essa estratégia é chamada de exclusão lógica.

    Ela permite preservar o histórico do produto e
    possibilita sua reativação posteriormente.

    Fluxo:

    1. Recebe o ID do produto pela URL.
    2. Procura o produto no banco.
    3. Se não existir, retorna erro 404.
    4. Verifica se ele já está inativo.
    5. Altera o status para INATIVO.
    6. Salva a alteração no MySQL.
    7. Retorna uma confirmação.
    """


    # ========================================================
    # BUSCAR PRODUTO
    # ========================================================

    # Criamos uma consulta equivalente a:
    #
    # SELECT * FROM produtos
    # WHERE id = produto_id;
    consulta = select(Produto).where(
        Produto.id == produto_id
    )


    # Executa a consulta no banco.
    #
    # Se encontrar:
    #
    # produto = objeto Produto
    #
    # Se não encontrar:
    #
    # produto = None
    produto = database.execute(
        consulta
    ).scalar_one_or_none()


    # ========================================================
    # VERIFICAR SE O PRODUTO EXISTE
    # ========================================================

    # Caso nenhum produto tenha sido encontrado,
    # retornamos HTTP 404.
    if produto is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )


    # ========================================================
    # VERIFICAR SE JÁ ESTÁ INATIVO
    # ========================================================

    # Evitamos executar uma atualização desnecessária
    # caso o produto já esteja desativado.
    if produto.status == "INATIVO":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O produto já está inativo."
        )


    # ========================================================
    # DESATIVAR PRODUTO
    # ========================================================

    # Não utilizamos:
    #
    # database.delete(produto)
    #
    # porque isso apagaria fisicamente o registro.
    #
    # Apenas alteramos o status.
    produto.status = "INATIVO"


    # ========================================================
    # SALVAR ALTERAÇÃO
    # ========================================================

    # Confirma a alteração no MySQL.
    database.commit()


    # Atualiza o objeto Python com os dados
    # atuais armazenados no banco.
    database.refresh(
        produto
    )


    # ========================================================
    # RESPOSTA
    # ========================================================

    return {

        "mensagem":
            "Produto desativado com sucesso.",

        "produto": {

            "id":
                produto.id,

            "nome":
                produto.nome,

            "status":
                produto.status,

            "data_atualizacao":
                produto.data_atualizacao
        }
    }
# ============================================================
# CONFIGURAÇÃO DO UPLOAD DE IMAGENS
# ============================================================

# Localiza automaticamente a pasta "src".
#
# Este arquivo está em:
#
# src/backend/app/routers/produtos.py
#
# parents[3] nos leva até:
#
# src/
SRC_DIR = Path(__file__).resolve().parents[3]


# Pasta onde serão armazenadas as imagens dos produtos.
#
# Resultado:
#
# src/frontend/img/produtos/
PRODUTOS_IMG_DIR = (
    SRC_DIR
    / "frontend"
    / "img"
    / "produtos"
)


# Garante que a pasta exista.
#
# Como você já criou a pasta manualmente,
# normalmente esta linha não precisará criar nada.
#
# Porém ela também protege o sistema caso a pasta
# seja apagada futuramente.
PRODUTOS_IMG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TIPOS DE IMAGEM PERMITIDOS
# ============================================================

# Trabalhamos com MIME type em vez de confiar apenas
# na extensão enviada pelo navegador.
TIPOS_IMAGEM_PERMITIDOS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


# ============================================================
# TAMANHO MÁXIMO
# ============================================================

# Limite:
#
# 5 MB
TAMANHO_MAXIMO_IMAGEM = (
    5 * 1024 * 1024
)


# ============================================================
# UPLOAD DA IMAGEM DO PRODUTO
# ============================================================

@router.post(
    "/{produto_id}/imagem",
    status_code=status.HTTP_200_OK,
    summary="Enviar imagem do produto"
)
async def enviar_imagem_produto(
    produto_id: int,

    # File(...) informa ao FastAPI que o arquivo
    # chegará como multipart/form-data.
    imagem: UploadFile = File(...),

    database: Session = Depends(get_database),
    admin_id: int = Depends(exigir_admin_autenticado),
):

    """
    Envia uma imagem para um produto já cadastrado.

    Fluxo:

    1. Recebe o ID do produto.
    2. Procura o produto no MySQL.
    3. Recebe a imagem enviada pelo navegador.
    4. Valida formato.
    5. Valida tamanho.
    6. Gera um nome único.
    7. Salva em frontend/img/produtos.
    8. Atualiza imagem_url no banco.
    9. Retorna a nova URL.
    """


    # ========================================================
    # BUSCAR PRODUTO
    # ========================================================

    consulta = select(Produto).where(
        Produto.id == produto_id
    )

    produto = database.execute(
        consulta
    ).scalar_one_or_none()


    # ========================================================
    # VERIFICAR SE O PRODUTO EXISTE
    # ========================================================

    if produto is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )


    # ========================================================
    # VALIDAR FORMATO
    # ========================================================

    # Exemplos aceitos:
    #
    # image/jpeg
    # image/png
    # image/webp

    if imagem.content_type not in TIPOS_IMAGEM_PERMITIDOS:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Formato de imagem inválido. "
                "Utilize JPG, PNG ou WEBP."
            )
        )


    # Obtém a extensão correspondente ao MIME type.
    extensao = TIPOS_IMAGEM_PERMITIDOS[
        imagem.content_type
    ]


    # ========================================================
    # LER ARQUIVO
    # ========================================================

    conteudo = await imagem.read()


    # ========================================================
    # VERIFICAR ARQUIVO VAZIO
    # ========================================================

    if not conteudo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A imagem enviada está vazia."
        )


    # ========================================================
    # VALIDAR TAMANHO
    # ========================================================

    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A imagem é muito grande. "
                "O tamanho máximo permitido é 5 MB."
            )
        )


    # ========================================================
    # GERAR NOME ÚNICO
    # ========================================================

    # uuid evita que duas imagens tenham o mesmo nome.
    #
    # Exemplo:
    #
    # produto-2-a98f21...png

    nome_arquivo = (
        f"produto-{produto.id}-"
        f"{uuid.uuid4().hex}"
        f"{extensao}"
    )


    # Caminho físico onde o arquivo será salvo.
    caminho_arquivo = (
        PRODUTOS_IMG_DIR
        / nome_arquivo
    )


    # ========================================================
    # GUARDAR REFERÊNCIA DA IMAGEM ANTIGA
    # ========================================================

    # Precisamos guardar isso antes de atualizar o banco.
    #
    # Assim, se o produto já possuir uma imagem local,
    # poderemos removê-la depois que a nova imagem
    # for salva com sucesso.

    imagem_antiga = produto.imagem_url


    # ========================================================
    # SALVAR NOVA IMAGEM NO DISCO
    # ========================================================

    try:

        with caminho_arquivo.open("wb") as arquivo:

            arquivo.write(
                conteudo
            )

    except OSError:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Não foi possível salvar "
                "a imagem do produto."
            )
        )


    # ========================================================
    # CRIAR URL PÚBLICA
    # ========================================================

    # Como a pasta /img já é disponibilizada pelo FastAPI,
    # o navegador poderá acessar:
    #
    # /img/produtos/nome-da-imagem.png

    nova_imagem_url = (
        f"/img/produtos/{nome_arquivo}"
    )


    # ========================================================
    # ATUALIZAR PRODUTO
    # ========================================================

    produto.imagem_url = nova_imagem_url


    # ========================================================
    # SALVAR NO MYSQL
    # ========================================================

    try:

        database.commit()

        database.refresh(
            produto
        )

    except Exception:

        # Desfaz alterações pendentes no banco.
        database.rollback()


        # Se o banco falhar, removemos a imagem nova.
        #
        # Isso evita deixar arquivos que não pertencem
        # a nenhum produto.

        if caminho_arquivo.exists():

            try:

                caminho_arquivo.unlink()

            except OSError:

                pass


        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Não foi possível atualizar "
                "a imagem do produto."
            )
        )


    # ========================================================
    # REMOVER IMAGEM LOCAL ANTIGA
    # ========================================================

    # Fazemos isso SOMENTE depois que:
    #
    # - a nova imagem foi salva;
    # - o banco foi atualizado.
    #
    # Assim não perdemos a imagem antiga caso ocorra
    # algum problema durante o processo.

    if (
        imagem_antiga
        and imagem_antiga.startswith(
            "/img/produtos/"
        )
        and imagem_antiga != nova_imagem_url
    ):

        nome_imagem_antiga = Path(
            imagem_antiga
        ).name

        caminho_imagem_antiga = (
            PRODUTOS_IMG_DIR
            / nome_imagem_antiga
        )


        if caminho_imagem_antiga.exists():

            try:

                caminho_imagem_antiga.unlink()

            except OSError:

                # Se não for possível apagar a imagem antiga,
                # o upload novo continua válido.
                pass


    # ========================================================
    # RESPOSTA
    # ========================================================

    return {

        "mensagem":
            "Imagem do produto enviada com sucesso.",

        "produto": {

            "id":
                produto.id,

            "nome":
                produto.nome,

            "imagem_url":
                produto.imagem_url

        }

    }