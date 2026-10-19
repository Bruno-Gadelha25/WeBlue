from datetime import datetime

from sqlalchemy import DateTime, Enum, String, text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    nome_completo: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True
    )

    cpf: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
        unique=True
    )

    telefone: Mapped[str] = mapped_column(
        String(11),
        nullable=False
    )

    senha_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum("ATIVA", "INATIVA", "BLOQUEADA"),
        nullable=False,
        server_default="ATIVA"
    )

    aceitou_termos_em: Mapped[datetime] = mapped_column(
        DateTime,
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

    pedidos: Mapped[list["Pedido"]] = relationship(
        "Pedido",
        back_populates="cliente"
    )