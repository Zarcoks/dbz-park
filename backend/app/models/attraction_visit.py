"""Current presence: one row per visitor inside the attraction right now.

Written on entry, deleted on exit, so the table is at any moment the list of who is in.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attraction import Attraction
    from app.models.ticket import Ticket


class AttractionVisit(Base):
    __tablename__ = "attraction_visit"
    __table_args__ = (
        UniqueConstraint("attraction_id", "ticket_id", name="uq_visit_ticket_per_attraction"),
        {"comment": "Current presence: one row per visitor inside the attraction right now."},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    attraction_id: Mapped[int] = mapped_column(
        ForeignKey("attraction.id", ondelete="CASCADE"), index=True
    )
    ticket_id: Mapped[int] = mapped_column(ForeignKey("ticket.id", ondelete="CASCADE"), index=True)
    entered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    attraction: Mapped["Attraction"] = relationship(back_populates="visits")
    ticket: Mapped["Ticket"] = relationship(back_populates="visits")

    def __repr__(self) -> str:
        return f"<AttractionVisit attraction={self.attraction_id} ticket={self.ticket_id}>"
