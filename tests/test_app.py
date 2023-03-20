from typing import Any
from unittest.mock import MagicMock

from starlette.testclient import TestClient


def test_app_basic(db_mock: MagicMock, test_client: TestClient) -> None:
    async def query_stub(query: str) -> Any:
        assert query == "SELECT 1"
        return 1
    
    db_mock.query.side_effect = query_stub

    resp = test_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"result": 1}

    assert db_mock.query.call_args == [("SELECT 1",)]
