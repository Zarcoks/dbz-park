"""A ticket: a unique `numero`, a `role` fixed at purchase, and a holder that stays
`null` until somebody claims it. No payment state — a ticket is usable as soon as it
exists, which is why no column here mentions money.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attraction_visit import AttractionVisit
    from app.models.queue_entry import QueueEntry
    from app.models.user import User


class TicketRole(str, enum.Enum):
    """The three fares. Declaration order is priority order, and Postgres sorts an enum
    that way: a plain `ORDER BY role` yields the best ticket first, no `CASE WHEN`.
    """

    super_sayan = "super_sayan"
    sayan = "sayan"
    normal = "normal"

    @property
    def display(self) -> str:
        return {"super_sayan": "Super Saiyan", "sayan": "Saiyan", "normal": "Normal"}[self.value]


# Best fare first, for anything that has to pick a ticket on the visitor's behalf.
ROLE_PRIORITY: list[TicketRole] = [TicketRole.super_sayan, TicketRole.sayan, TicketRole.normal]


class Ticket(Base):
    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    numero: Mapped[str] = mapped_column(String(32), unique=True)
    role: Mapped[TicketRole] = mapped_column(
        Enum(TicketRole, name="ticket_role", values_callable=lambda e: [m.value for m in e]),
        default=TicketRole.normal,
        server_default=TicketRole.normal.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User | None"] = relationship(back_populates="tickets")
    queue_entries: Mapped[list["QueueEntry"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    visits: Mapped[list["AttractionVisit"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )

    @property
    def role_display(self) -> str:
        return self.role.display

    def __repr__(self) -> str:
        return f"<Ticket {self.numero} ({self.role.value})>"
