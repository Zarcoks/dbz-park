from datetime import datetime

from pydantic import BaseModel

from app.schemas.tickets import TicketOut


class ConsoleAttractionOut(BaseModel):
    id: int
    name: str
    max_people: int


class ConsoleReadyOut(BaseModel):
    """A visitor who has been called, waiting on the admin's decision."""

    id: int
    username: str
    ticket: TicketOut
    ready_at: datetime | None
    max_seconds_allowing_ready: int
    ready_expired: bool


class ConsoleRowOut(BaseModel):
    """One row per attraction, including those where nobody is called (`ready: []`)."""

    attraction: ConsoleAttractionOut
    inside: int
    waiting: int
    ready: list[ConsoleReadyOut]
