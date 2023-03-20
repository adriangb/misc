import contextlib
from typing import AsyncIterator, TypedDict

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import Lifespan

from app.db import connect, Connection


class State(TypedDict):
    conn: Connection


@contextlib.asynccontextmanager
async def lifespan(_: Starlette) -> AsyncIterator[State]:
    async with connect() as conn:
        yield {"conn": conn}


async def hello(request: Request) -> Response:
    state: State = request["state"]
    res = await state["conn"].query("SELECT 1")
    return JSONResponse({"result": res})


def build_app(lifespan: Lifespan[Starlette] = lifespan) -> Starlette:
    return Starlette(
        lifespan=lifespan,
        routes=[Route("/", hello)]
    )
