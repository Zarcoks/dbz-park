"""The contract allows two answers only: `200` and `400`.

Every refusal goes through `ApiError`, which produces the `{"detail": "..."}` body the
front prints as is. That message is the only information sent, so it must tell the
visitor what to do and never reveal what they are not entitled to know.
"""

from typing import NoReturn

from fastapi import HTTPException

# Messages shared by several routes: one place to check nothing leaks.
NOT_AUTHENTICATED = "Connectez-vous pour accéder à cette page."
NOT_STAFF = NOT_AUTHENTICATED  # deliberately identical
UNKNOWN_TICKET = "Ce billet est introuvable."
UNKNOWN_ENTRY = "Cette place est introuvable."


class ApiError(HTTPException):
    """The only error of the project: `raise ApiError("…")` → 400 + detail."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=400, detail=detail)


def todo(route: str) -> NoReturn:
    """Marks a handler not written yet.

    Answers `501`, deliberately outside the contract, so "refused" (400) and "not done
    yet" are never confused. These calls disappear as routes get implemented.
    """
    raise HTTPException(status_code=501, detail=f"{route} n'est pas encore implémenté.")
