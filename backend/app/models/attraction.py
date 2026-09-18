"""An attraction of the park."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attraction_visit import AttractionVisit
    from app.models.queue_entry import QueueEntry


class Attraction(Base):
    __tablename__ = "attraction"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    max_people: Mapped[int] = mapped_column(Integer)

    # An integer rather than an interval: the front reads it as is.
    avg_duration: Mapped[int] = mapped_column(
        Integer, default=120, server_default=text("120"), comment="one ride, in seconds"
    )

    # A counter, not a count: whoever writes an entry or an exit must move it too.
    people_inside: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        comment="counter kept in step with attraction_visit, not a count",
    )

    queue_entries: Mapped[list["QueueEntry"]] = relationship(
        back_populates="attraction", cascade="all, delete-orphan"
    )
    visits: Mapped[list["AttractionVisit"]] = relationship(
        back_populates="attraction", cascade="all, delete-orphan"
    )

    @property
    def is_full(self) -> bool:
        return self.people_inside >= self.max_people

    def __repr__(self) -> str:
        return f"<Attraction {self.name}>"
