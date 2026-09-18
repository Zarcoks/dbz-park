"""Tickets.

Two listings, with different rights: `GET /tickets/` shows every ticket with its holder
and is staff-only — the single response of the API that ties a ticket to a name — while
`GET /user/<id>/tickets/` shows one visitor's, readable by that visitor or by staff.
A ticket is usable as soon as it exists: there is no payment step.
"""

from fastapi import APIRouter

from app.db import SessionDep
from app.dependencies import CurrentUser, StaffUser
from app.errors import todo
from app.schemas.tickets import TicketAdminOut, TicketAssignIn, TicketCreateIn, TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])

# One visitor's tickets live under the visitor: the address says whose they are.
user_router = APIRouter(prefix="/user", tags=["tickets"])


@router.get("/", response_model=list[TicketAdminOut])
async def list_all_tickets(staff: StaffUser, session: SessionDep):
    """Every ticket in the park, assigned or not, with its holder.

    Closed to visitors: everywhere else the API is built so nothing can be learnt about
    someone else's tickets, and this is the exception that must stay behind `is_staff`.
    """
    todo("GET /tickets/")


@user_router.get("/{user_id}/tickets/", response_model=list[TicketOut])
async def list_user_tickets(user_id: int, user: CurrentUser, session: SessionDep):
    """One visitor's tickets: themself, or a staff account.

    "not you" and "no such account" must share one message, or the route becomes a way
    to find out which accounts exist.
    """
    todo("GET /user/{id}/tickets/")


@router.post("/", response_model=TicketOut)
async def create_ticket(data: TicketCreateIn, user: CurrentUser, session: SessionDep):
    """Buys a ticket: the row is created, attached to the caller, usable right away."""
    todo("POST /tickets/")


@router.post("/assign/", response_model=TicketOut)
async def assign_ticket(data: TicketAssignIn, user: CurrentUser, session: SessionDep):
    """Claims a ticket bought elsewhere, from its number alone.

    Unknown number and already-taken number must give the exact same message: we never
    say who owns a ticket.
    """
    todo("POST /tickets/assign/")
