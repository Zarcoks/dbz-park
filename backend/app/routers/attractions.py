"""Attractions, and joining a queue."""

from fastapi import APIRouter, Response

from app.db import SessionDep
from app.dependencies import CurrentUser
from app.errors import todo
from app.schemas.attractions import AttractionCardOut

router = APIRouter(prefix="/attractions", tags=["attractions"])


@router.get("/", response_model=list[AttractionCardOut])
async def list_attractions(user: CurrentUser, session: SessionDep):
    """The catalogue: the attractions themselves, and nothing about this visitor.

    `people_inside` is a counter carried by the attraction, not a count made here.
    """
    todo("GET /attractions/")


@router.post("/{attraction_id}/queue/join/")
async def join_queue(attraction_id: int, user: CurrentUser, session: SessionDep) -> Response:
    """Takes a place in the queue.

    The back picks the visitor's best ticket itself: super saiyan, then saiyan, then normal.
    """
    todo("POST /attractions/{id}/queue/join/")
