from fastapi import FastAPI
from .database import engine
from .models.users import Base

from .dependecies import SessionDep
from .routers.users import router as user_router


app = FastAPI()

app.include_router(user_router)


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.post("/setup-database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return {"message": "Database setup completed"}


@app.get("/health")
async def health_check(session: SessionDep):
    from sqlalchemy import text

    try:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        return {"status": "healthy", "check": value}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
