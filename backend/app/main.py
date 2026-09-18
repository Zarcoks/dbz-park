"""The FastAPI app, mounted under /api — what the front calls.

In dev the Vite proxy forwards /api here without rewriting the path
(see `frontend/vite.config.js`).
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.config import get_settings
from app.routers import attractions, auth, console, queue, tickets

settings = get_settings()

API_PREFIX = "/api"

app = FastAPI(
    title="Dragon Ball Park API",
    version="0.1.0",
    summary="Contract in ../API.md: two answers only, 200 and 400.",
    docs_url=f"{API_PREFIX}/docs",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# Only useful for a front deployed elsewhere: in dev the Vite proxy shares the origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def malformed_request(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Translates FastAPI's `422` into the `400` the contract allows.

    Keeps a message a visitor can read, rather than the raw list of Pydantic errors.
    """
    first = exc.errors()[0]
    field = ".".join(str(part) for part in first["loc"] if part not in ("body", "query", "path"))
    detail = f"Champ « {field} » invalide : {first['msg']}" if field else "Requête mal formée."
    return JSONResponse(status_code=400, content={"detail": detail})


@app.get(f"{API_PREFIX}/health/", tags=["health"])
async def health() -> dict[str, str]:
    """Is the server answering, without touching the database."""
    return {"status": "ok"}


for router in (
    auth.router,
    tickets.router,
    tickets.user_router,
    attractions.router,
    queue.router,
    console.router,
):
    app.include_router(router, prefix=API_PREFIX)
