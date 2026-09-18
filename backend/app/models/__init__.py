"""The five tables of the park.

Everything must be imported here: Alembic reads this module to know the target schema,
so a table missing from it would be missing from the migrations too.
"""

from app.models.attraction import Attraction
from app.models.attraction_visit import AttractionVisit
from app.models.base import Base
from app.models.queue_entry import QueueEntry
from app.models.ticket import ROLE_PRIORITY, Ticket, TicketRole
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Ticket",
    "TicketRole",
    "ROLE_PRIORITY",
    "Attraction",
    "QueueEntry",
    "AttractionVisit",
]
