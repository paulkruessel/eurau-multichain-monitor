import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend import main


def test_get_connection_info_returns_rpc_status(monkeypatch):
    monkeypatch.setenv("BASE_RPC_URL", "https://rpc.example.com")

    class FakeProvider:
        def __init__(self, url):
            self.url = url

    class FakeWeb3:
        HTTPProvider = staticmethod(lambda url: FakeProvider(url))

        def __init__(self, provider):
            self.provider = provider

        def is_connected(self):
            return True

        @property
        def eth(self):
            return type("Eth", (), {"chain_id": 8453, "block_number": 1234})()

    monkeypatch.setattr(main, "Web3", FakeWeb3)

    result = asyncio.run(main.getConnectionInfo())

    assert result == {
        "connected": True,
        "chain_id": 8453,
        "block_number": 1234,
    }


def test_get_connection_info_raises_when_rpc_unavailable(monkeypatch):
    monkeypatch.setenv("BASE_RPC_URL", "https://rpc.example.com")

    class FakeProvider:
        def __init__(self, url):
            self.url = url

    class FakeWeb3:
        HTTPProvider = staticmethod(lambda url: FakeProvider(url))

        def __init__(self, provider):
            self.provider = provider

        def is_connected(self):
            return False

        @property
        def eth(self):
            return type("Eth", (), {"chain_id": 8453, "block_number": 1234})()

    monkeypatch.setattr(main, "Web3", FakeWeb3)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(main.getConnectionInfo())

    assert exc_info.value.status_code == 503
    assert "unavailable" in exc_info.value.detail.lower()


def test_get_connection_info_raises_when_chain_id_not_expected(monkeypatch):
    monkeypatch.setenv("BASE_RPC_URL", "https://rpc.example.com")

    class FakeProvider:
        def __init__(self, url):
            self.url = url

    class FakeWeb3:
        HTTPProvider = staticmethod(lambda url: FakeProvider(url))

        def __init__(self, provider):
            self.provider = provider

        def is_connected(self):
            return True

        @property
        def eth(self):
            return type("Eth", (), {"chain_id": 8454, "block_number": 1234})()

    monkeypatch.setattr(main, "Web3", FakeWeb3)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(main.getConnectionInfo())

    assert exc_info.value.status_code == 500
    assert "8453" in exc_info.value.detail


def test_get_connection_info_raises_when_base_rpc_url_missing(monkeypatch):
    monkeypatch.delenv("BASE_RPC_URL", raising=False)

    with pytest.raises(KeyError):
        asyncio.run(main.getConnectionInfo())
