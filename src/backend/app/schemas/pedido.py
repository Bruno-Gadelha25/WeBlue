# ============================================================
# SCHEMAS DO FLUXO DE VENDAS
# ============================================================
#
# Este arquivo define os dados esperados pelo checkout,
# pelo histórico de pedidos e pela validação de estoque.
#
# Utilizamos Pydantic para manter a entrada da API consistente
# e evitar que o backend aceite dados inválidos.
# ============================================================

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ItemCarrinhoRequest(BaseModel):
    """Representa um produto adicionando ao carrinho."""

    produto_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class CheckoutRequest(BaseModel):
    """Dados enviados ao finalizar a compra."""

    cliente_id: int | None = None
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    telefone: str | None = Field(default=None, min_length=8, max_length=20)
    endereco: str = Field(min_length=5, max_length=250)
    metodo_pagamento: str = Field(default="PIX")
    numero_cartao: str | None = Field(default=None, max_length=40)
    itens: list[ItemCarrinhoRequest] = Field(min_length=1)

    @field_validator("metodo_pagamento")
    @classmethod
    def validar_metodo_pagamento(cls, valor: str) -> str:
        valor_normalizado = valor.strip().upper()
        if valor_normalizado not in {"PIX", "CARTAO"}:
            raise ValueError("O método de pagamento deve ser PIX ou CARTAO.")
        return valor_normalizado


class ResumoPedido(BaseModel):
    """Resumo do pedido gerado na compra."""

    id: int
    status: str
    valor_total: str
    metodo_pagamento: str
    endereco: str
    criado_em: str


class EstoqueResumo(BaseModel):
    """Resumo do estoque para a área administrativa ou cliente."""

    id: int
    nome: str
    estoque: int
    status: str
    preco: str
