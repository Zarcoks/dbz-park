"""The operations console, staff only.

`StaffUser` refuses a merely logged-in visitor with the same message as someone with no
token: nothing says the console exists.
"""

from fastapi import APIRouter, Response

from app.db import SessionDep
from app.dependencies import StaffUser
from app.errors import todo
from app.schemas.console import ConsoleRowOut

router = APIRouter(prefix="/console", tags=["console"])


@router.get("/", response_model=list[ConsoleRowOut])
async def console_rows(staff: StaffUser, session: SessionDep):
    """One row per attraction, including those where nobody is called."""
    todo("GET /console/")


@router.post("/entries/{entry_id}/accept/")
async def accept_entry(entry_id: int, staff: StaffUser, session: SessionDep) -> Response:
    """The visitor goes in.

    Unlike the visitor-side validation, an expired place can be accepted: the admin decides.
    """
    todo("POST /console/entries/{id}/accept/")


@router.post("/entries/{entry_id}/refuse/")
async def refuse_entry(entry_id: int, staff: StaffUser, session: SessionDep) -> Response:
    """The place is removed and the queue moves up."""
    todo("POST /console/entries/{id}/refuse/")
