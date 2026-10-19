from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, ForeignKey, Numeric, text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class StatusPedido(str, Enum):
    """
    Estados possíveis de um pedido.
    """

    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    EM_SEPARACAO = "EM_SEPARACAO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


class Pedido(Base):
    """
    Pedido realizado por um cliente.
    """

    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    cliente_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("clientes.id"),
        nullable=False
    )

    status: Mapped[StatusPedido] = mapped_column(
        SQLAlchemyEnum(StatusPedido),
        nullable=False,
        server_default=StatusPedido.PENDENTE.value
    )

    valor_total: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP")
    )

    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="pedidos"
    )

    itens: Mapped[list["ItemPedido"]] = relationship(
        "ItemPedido",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )
