import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.app.main import app
from backend.app.database import Base, get_async_session
from backend.app.config import settings

from httpx import AsyncClient, ASGITransport


BASE_URL = "http://test"


@pytest.fixture
async def test_engine():
    engine = create_async_engine(settings.test_db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_async_session] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac

    app.dependency_overrides.clear()
