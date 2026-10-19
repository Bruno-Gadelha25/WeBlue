# ============================================================
# IMPORTAÇÕES
# ============================================================

# datetime será utilizado para registrar automaticamente
# quando o produto foi criado e quando foi atualizado.
from datetime import datetime


# Decimal é recomendado para valores monetários.
#
# Evitamos utilizar float para preços porque números
# decimais em ponto flutuante podem gerar problemas
# de precisão.
from decimal import Decimal


# Tipos utilizados para definir as colunas da tabela.
from sqlalchemy import (
    String,
    Text,
    Numeric,
    Integer,
    DateTime
)
from sqlalchemy.dialects.mysql import BIGINT


# Recursos do SQLAlchemy 2.x utilizados para declarar
# os atributos do modelo.
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)


# Base utilizada pelos modelos da Weblue.
#
# IMPORTANTE:
# Estamos assumindo que "Base" está definida em database.py.
from ..database import Base


# ============================================================
# MODELO PRODUTO
# ============================================================

class Produto(Base):

    """
    Representa um produto disponível na Weblue.

    Cada objeto Produto corresponde a um registro
    da tabela "produtos" no banco de dados.
    """


    # ========================================================
    # NOME DA TABELA
    # ========================================================

    __tablename__ = "produtos"


    # ========================================================
    # ID
    # ========================================================

    # Identificador único do produto.
    #
    # primary_key=True:
    # transforma esta coluna na chave primária.
    #
    # autoincrement=True:
    # faz o banco gerar automaticamente:
    #
    # 1, 2, 3, 4...
    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )


    # ========================================================
    # NOME DO PRODUTO
    # ========================================================

    # Nome apresentado ao cliente.
    #
    # Exemplo:
    #
    # "Sérum Facial Vitamina C"
    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )


    # ========================================================
    # DESCRIÇÃO
    # ========================================================

    # Descrição completa do produto.
    #
    # Utilizamos Text porque uma descrição pode
    # ser maior que um campo String convencional.
    descricao: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )


    # ========================================================
    # PREÇO
    # ========================================================

    # Valor de venda do produto.
    #
    # Numeric(10, 2) permite valores como:
    #
    # 49.90
    # 129.99
    # 1250.00
    #
    # Utilizamos Decimal no Python para preservar
    # corretamente os centavos.
    preco: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=10,
            scale=2
        ),
        nullable=False
    )


    # ========================================================
    # ESTOQUE
    # ========================================================

    # Quantidade disponível para venda.
    #
    # Exemplo:
    #
    # estoque = 25
    estoque: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )


    # ========================================================
    # CATEGORIA
    # ========================================================

    # Categoria utilizada para organizar os produtos.
    #
    # Exemplos:
    #
    # "Skincare"
    # "Maquiagem"
    # "Cabelos"
    # "Corpo"
    categoria: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


    # ========================================================
    # MARCA
    # ========================================================

    # Marca/fabricante do produto.
    #
    # Exemplo:
    #
    # "Weblue"
    # "Principia"
    # "Nivea"
    marca: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


    # ========================================================
    # IMAGEM
    # ========================================================

    # Endereço da imagem principal do produto.
    #
    # Inicialmente vamos armazenar uma URL/caminho.
    #
    # Exemplos:
    #
    # /img/produtos/serum-vitamina-c.webp
    #
    # ou uma URL externa.
    #
    # Depois podemos evoluir isso para um sistema
    # próprio de upload de imagens.
    imagem_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )


    # ========================================================
    # STATUS
    # ========================================================

    # Define se o produto está disponível no catálogo.
    #
    # Inicialmente utilizaremos:
    #
    # ATIVO
    # INATIVO
    #
    # Isso é melhor do que apagar imediatamente um
    # produto do banco, porque futuramente pedidos
    # antigos poderão continuar referenciando esse produto.
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ATIVO"
    )


    # ========================================================
    # DATA DE CRIAÇÃO
    # ========================================================

    # Registra quando o produto foi cadastrado.
    #
    # default=datetime.now:
    # o valor é criado automaticamente quando um novo
    # produto é inserido.
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now
    )


    # ========================================================
    # DATA DE ATUALIZAÇÃO
    # ========================================================

    # Registra quando o produto foi modificado.
    #
    # default=datetime.now:
    # define o valor inicial.
    #
    # onupdate=datetime.now:
    # atualiza automaticamente quando o registro
    # sofre uma alteração pelo SQLAlchemy.
    data_atualizacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now
    )