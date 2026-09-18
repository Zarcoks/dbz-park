from datetime import datetime

from pydantic import BaseModel

from app.schemas.tickets import TicketOut


class VisitOut(BaseModel):
    """The visitor is inside the attraction right now."""

    ticket: TicketOut
    entered_at: datetime


class QueueEntryOut(BaseModel):
    """The place the visitor holds in the queue."""

    id: int
    ticket: TicketOut
    joined_at: datetime
    is_ready: bool
    ready_at: datetime | None
    max_seconds_allowing_ready: int
    # Computed by the back, not by the front.
    ready_expired: bool


class AttractionCardOut(BaseModel):
    """An attraction, plus what *this* visitor has going on there.

    The four cases are exclusive, read in this order by the front:
    `visit` → called `entry` → expired `entry` → waiting `entry` → `ticket`.
    """

    id: int
    name: str
    photo_url: str
    max_people: int
    people_inside: int
    avg_duration: str

    visit: VisitOut | None = None
    entry: QueueEntryOut | None = None
    position: int | None = None
    ticket: TicketOut | None = None


class PositionOut(BaseModel):
    """How many people are ahead, this place included: 1 means next in line."""

    position: int
