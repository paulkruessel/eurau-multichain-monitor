import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend import main


def test_read_con_info_from_env_returns_values(monkeypatch):
    monkeypatch.setattr(main.Path, "exists", lambda self: True)
    monkeypatch.setattr(main, "load_dotenv", lambda *_args, **_kwargs: None)
    monkeypatch.setenv("BASE_RPC_URL", "https://rpc.example.com")
    monkeypatch.setenv("EURAU_BASE_CONTRACT_ADDRESS", "0xabc123")

    assert main.readConInfoFromEnv() == (
        "https://rpc.example.com",
        "0xabc123",
    )


def test_read_con_info_from_env_raises_when_dotenv_missing(monkeypatch):
    monkeypatch.setattr(main.Path, "exists", lambda self: False)

    with pytest.raises(FileNotFoundError):
        main.readConInfoFromEnv()


def test_get_connection_info_returns_rpc_status(monkeypatch):
    monkeypatch.setattr(
        main,
        "readConInfoFromEnv",
        lambda: ("https://rpc.example.com", "0xabc123"),
    )

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
        "rpc_url": "https://rpc.example.com",
        "chain_id": 8453,
        "block_number": 1234,
    }


def test_get_connection_info_raises_when_rpc_unavailable(monkeypatch):
    monkeypatch.setattr(
        main,
        "readConInfoFromEnv",
        lambda: ("https://rpc.example.com", "0xabc123"),
    )

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
    monkeypatch.setattr(
        main,
        "readConInfoFromEnv",
        lambda: ("https://rpc.example.com", "0xabc123"),
    )

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


def test_get_connection_info_handles_missing_env_file(monkeypatch):
    def raise_missing_env():
        raise FileNotFoundError

    monkeypatch.setattr(main, "readConInfoFromEnv", raise_missing_env)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(main.getConnectionInfo())

    assert exc_info.value.status_code == 500
    assert "env" in exc_info.value.detail.lower()
