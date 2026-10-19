# ============================================================
# IMPORTAÇÕES
# ============================================================

# Decimal será utilizado para representar valores monetários.
#
# É mais adequado do que float para preços,
# pois evita problemas de precisão com centavos.
from decimal import Decimal


# BaseModel:
# classe base utilizada para criar schemas no Pydantic.
#
# Field:
# permite criar regras de validação para os campos.
from pydantic import (
    BaseModel,
    Field
)


# ============================================================
# SCHEMA PARA CADASTRAR PRODUTO
# ============================================================

class CriarProdutoRequest(BaseModel):

    """
    Representa os dados necessários para cadastrar
    um novo produto na Weblue.

    Este schema é utilizado em:

    POST /produtos
    """


    # ========================================================
    # NOME
    # ========================================================

    # Nome comercial do produto.
    #
    # Regras:
    #
    # mínimo: 2 caracteres
    # máximo: 150 caracteres
    nome: str = Field(
        min_length=2,
        max_length=150
    )


    # ========================================================
    # DESCRIÇÃO
    # ========================================================

    # Descrição apresentada ao cliente.
    #
    # Exigimos pelo menos 5 caracteres.
    descricao: str = Field(
        min_length=5
    )


    # ========================================================
    # PREÇO
    # ========================================================

    # Valor de venda do produto.
    #
    # Decimal é utilizado para evitar problemas
    # de precisão com valores monetários.
    #
    # gt=0:
    # o preço deve ser maior que zero.
    #
    # max_digits=10:
    # permite no máximo 10 dígitos.
    #
    # decimal_places=2:
    # permite duas casas decimais.
    preco: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2
    )


    # ========================================================
    # ESTOQUE
    # ========================================================

    # Quantidade disponível do produto.
    #
    # ge=0 significa:
    #
    # maior ou igual a zero.
    #
    # Portanto:
    #
    # 0  -> permitido
    # 10 -> permitido
    # -1 -> não permitido
    estoque: int = Field(
        ge=0
    )


    # ========================================================
    # CATEGORIA
    # ========================================================

    # Categoria do produto.
    #
    # Exemplos:
    #
    # Skincare
    # Maquiagem
    # Cabelos
    categoria: str = Field(
        min_length=2,
        max_length=100
    )


    # ========================================================
    # MARCA
    # ========================================================

    # Marca ou fabricante.
    marca: str = Field(
        min_length=2,
        max_length=100
    )


    # ========================================================
    # IMAGEM
    # ========================================================

    # URL da imagem principal do produto.
    #
    # É opcional porque inicialmente podemos cadastrar
    # um produto sem imagem.
    imagem_url: str | None = Field(
        default=None,
        max_length=500
    )


# ============================================================
# SCHEMA PARA ATUALIZAR PRODUTO
# ============================================================

class AtualizarProdutoRequest(BaseModel):

    """
    Representa os dados permitidos durante
    a atualização de um produto.

    Este schema é utilizado em:

    PUT /produtos/{produto_id}

    Todos os campos são opcionais porque podemos
    atualizar somente uma parte do produto.

    Exemplo:

    {
        "preco": 64.90,
        "estoque": 30
    }

    Nesse caso somente preço e estoque serão alterados.
    """


    # ========================================================
    # NOME
    # ========================================================

    nome: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )


    # ========================================================
    # DESCRIÇÃO
    # ========================================================

    descricao: str | None = Field(
        default=None,
        min_length=5
    )


    # ========================================================
    # PREÇO
    # ========================================================

    preco: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2
    )


    # ========================================================
    # ESTOQUE
    # ========================================================

    estoque: int | None = Field(
        default=None,
        ge=0
    )


    # ========================================================
    # CATEGORIA
    # ========================================================

    categoria: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )


    # ========================================================
    # MARCA
    # ========================================================

    marca: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )


    # ========================================================
    # IMAGEM
    # ========================================================

    # Também permitimos None para que futuramente
    # seja possível remover a imagem do produto.
    imagem_url: str | None = Field(
        default=None,
        max_length=500
    )


    # ========================================================
    # STATUS
    # ========================================================

    # Permite alterar o estado do produto.
    #
    # A validação dos valores:
    #
    # ATIVO
    # INATIVO
    #
    # será realizada no router.
    status: str | None = Field(
        default=None,
        max_length=20
    )
    