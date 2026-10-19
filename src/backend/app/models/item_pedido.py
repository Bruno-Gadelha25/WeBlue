from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ItemPedido(Base):
    """
    Produto pertencente a um pedido.
    """

    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    pedido_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("pedidos.id"),
        nullable=False
    )

    produto_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("produtos.id"),
        nullable=False
    )

    quantidade: Mapped[int] = mapped_column(
        nullable=False
    )

    preco_unitario: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    pedido = relationship(
        "Pedido",
        back_populates="itens"
    )

    produto = relationship(
        "Produto"
    )