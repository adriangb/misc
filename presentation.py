# pyright: basic

# example
import uvicorn
from fastapi import FastAPI

app = FastAPI()
uvicorn.run(app)


# structure of an ASGI app

async def app(scope, receive, send):
    ...

# applications as objects
class App:
    async def __call__(self, scope, receive, send):
        ...

    def add_middleware(self):
        ...


# asgi scope object

{
    "type": "http",
    "path": "/users/1234",
    "headers": [(b"Authorization", b"Bearer MyToken")]
}

# asgi receive callback

async def receive():
    return {
        "type": "http.request",
        "body": b"some data",
        "more_body": False,
    }


async def send(message):
    ...

await send(
    {
        "type": "http.response.start",
        "status_code": 200,
        "headers": [(b"content-type", b"application/json")]
    }
)

# basic echo app

async def echo_app(scope, receive, send):
    assert scope["type"] == "http"
    assert scope["method"] == "POST"

    body = bytearray()
    more_body = True
    while more_body:
        msg = await receive()
        body.extend(await msg["body"])
        more_body = msg.get("more_body", False)
    
    await send({"type": "http.response.start", "status_code": 200, "headers": []})
    await send({"type": "http.response.body", "body": body})

# streaming echo app

async def echo_app(scope, receive, send):
    assert scope["type"] == "http"
    assert scope["method"] == "POST"

    await send({"type": "http.response.start", "status_code": 200, "headers": []})

    more_body = True
    while more_body:
        msg = await receive()
        more_body = msg.get("more_body", False)
        await send({"type": "http.response.body", "body": msg["body"], "more_body": True})

    await send({"type": "http.response.body", "body": b"", "more_body": False})

# server stub

async def echo_app(scope, receive, send):
    ...

scope = {
    "type": "http",
    "path": "/users/1233",
    "method": "POST",
}

async def receive():
    return {"type": "http.request.body", "body": b"abc"}


async def send(msg):
    print(msg)


await echo_app(scope, receive, send)

# middleware
class Middleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, scope, receive, send):
        return self.app(scope, receive, send)

async def app(scope, receive, send):
    raise NotImplementedError

app = Middleware(app)

# Starlette & middleware
from typing import Awaitable, Callable, List
from starlette.types import ASGIApp

class Starlette:
    def __init__(self, middlewares: List[Callable[[ASGIApp], ASGIApp]]):
        real_app = self
        for middleware in reversed(middlewares):
            real_app = middleware(real_app)
        self.real_app = real_app

    async def __call__(self, scope, receive, send):
        await self.real_app(scope, receive, send)

# modifying scope

from starlette.datastructures import Headers
from starlette.responses import Response

class AuthMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        headers = Headers(scope["headers"])
        if "authorization" not in headers:
            await Response(status_code=401)
            return
        # do authorization
        await self.app(scope, receive, send)

# modifying the incoming data

class UnGzipMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        decompressor = UnGzipper()

        async def wrapped_rcv():
            msg = await receive()
            msg["body"] = decompressor.decompress(msg["body"])
            return msg

        await self.app(scope, wrapped_rcv, send)

# modifying outgoing data

class GzipMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        compressor = Gzipper()

        async def wrapped_send(msg):
            msg["body"] = compressor.compress(msg["body"])
            await send(msg)

        await self.app(scope, receive, wrapped_send)


# storing state - bad

class GzipMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        self.compressor = Gzipper()

        async def wrapped_send(msg):
            msg["body"] = self.compressor.compress(msg["body"])
            await send(msg)

        await self.app(scope, receive, wrapped_send)

# storing state - per request
import anyio

class ConnectionTaskGroupMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "lifespan":
            async with anyio.create_task_group() as tg:
                scope["state"]["connection_tasks"] = tg
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)


# storing state - per lifespan
import anyio

class LifespanTaskGroupMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            async with anyio.create_task_group() as tg:
                scope["state"]["lifespan_tasks"] = tg
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

# helper function
from functools import partial

def add_background_task(scope, task, *args, **kwargs) -> None:
    scope["state"]["lifespan_tasks"].start_soon(partial(*args, **kwargs))

from starlette.requests import Request

async def endpoint(request: Request):
    async def my_task(x: int) -> None:
        print(x + 1)
    add_background_task(request["scope"], my_task, x=2)
    ...

# doesn't propagate lifespans
class AppNeedsLifespan:
    started = False
    async def __call__(
        self, scope, receive, send
    ):
        if scope["type"] == "lifespan":
            self.started = True
            ...
        else:
            assert self.started
            ...


# lifespan middleware

from contextlib import asynccontextmanager
from typing import AsyncIterator

from starlette.testclient import TestClient
from starlette.types import ASGIApp, Scope, Send, Receive

from asgi_lifespan_middleware import LifespanMiddleware

@asynccontextmanager
async def lifespan(
    # you'll get the wrapped app injected
    app: ASGIApp,
) -> AsyncIterator[None]:
    print("setup")
    yield
    print("teardown")


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    raise NotImplementedError


wrapped_app = LifespanMiddleware(
    app,
    lifespan=lifespan,
)

# asgi-background

from asgi_background import (
    BackgroundTaskMiddleware, BackgroundTasks
)
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

async def task(num: int) -> None:
    await anyio.sleep(1)
    print(num)

async def endpoint(request: Request) -> Response:
    tasks = BackgroundTasks(request.scope)
    await tasks.add_task(task, 1)
    return Response()

app = Starlette(
    routes=[Route("/", endpoint)],
    middleware=[Middleware(BackgroundTaskMiddleware)]
)


# control the event loop
from fastapi import FastAPI

from app.routes import routes  # a list of routes/routers

class UsersRepo:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    async def get_users(self, name: str):
        ...

def create_app(users_repo: UsersRepo) -> FastAPI:
    app = FastAPI(routes=routes)
    # need a coroutine wrapper for prod
    app.dependency_overrides[UsersRepo] = lambda: users_repo
    return app

async def main() -> None:
    async with asyncpg.create_pool(...) as pool:
        users_repo = UsersRepo(pool)
        app = create_app(users_repo)
        server_config = uvicorn.Config(app, port=80)
        server = uvicorn.Server(server_config)
        await server.serve()

if __name__ == "__main__":
    anyio.run(main)
