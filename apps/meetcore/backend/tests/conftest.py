"""Test fixtures and configuration."""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from core.db import Base
import core.db as db_module


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create temp file-based DB for each test."""
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    db_module.async_session_factory = original_factory
    await engine.dispose()
    os.unlink(db_path)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_meeting_id() -> str:
    return "test_meeting_001"
