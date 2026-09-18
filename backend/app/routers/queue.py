"""Places held in a queue: position, withdrawal, validation."""

from fastapi import APIRouter, Response

from app.db import SessionDep
from app.dependencies import CurrentUser
from app.errors import todo
from app.schemas.attractions import PositionOut

router = APIRouter(prefix="/queue", tags=["queue"])


@router.get("/{entry_id}/position/", response_model=PositionOut)
async def queue_position(entry_id: int, user: CurrentUser, session: SessionDep):
    """How many people are ahead, this place included, recomputed on each call.

    A position tells how busy a queue is, so it is readable by its holder only: someone
    else's place answers exactly like a place that does not exist.
    """
    todo("GET /queue/{id}/position/")


@router.post("/{entry_id}/leave/")
async def leave_queue(entry_id: int, user: CurrentUser, session: SessionDep) -> Response:
    """Voluntary withdrawal: the place disappears and the queue moves up."""
    todo("POST /queue/{id}/leave/")


@router.post("/{entry_id}/validate/")
async def validate_queue_entry(entry_id: int, user: CurrentUser, session: SessionDep) -> Response:
    """The visitor shows up after being called.

    The place is deleted and a visit takes over, in the same transaction.
    """
    todo("POST /queue/{id}/validate/")
