from contextlib import asynccontextmanager
from typing import  AsyncIterator, Iterator
from unittest.mock import MagicMock

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from app.app import State, build_app


@pytest.fixture
def db_mock() -> Iterator[MagicMock]:
    yield MagicMock()


@pytest.fixture
def test_client(db_mock: MagicMock) -> Iterator[TestClient]:
    @asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[State]:
        yield {"conn": db_mock}
    
    app = build_app(lifespan=lifespan)
    
    with TestClient(app) as client:
        yield client
