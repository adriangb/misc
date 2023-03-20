from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from typing_extensions import LiteralString

class Connection:
    async def query(self, query: LiteralString) -> Any:
        raise NotImplementedError

@asynccontextmanager
async def connect() -> AsyncIterator[Connection]:
    yield Connection()
