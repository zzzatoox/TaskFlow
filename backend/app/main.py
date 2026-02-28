from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from .database import engine
from .models.users import Base

from .dependencies import SessionDep
from .routers.users import router as user_router
from .routers.auth import router as auth_router
from .routers.tasks import router as tasks_router
from .routers.priorities import router as priorities_router
from .routers.statuses import router as statuses_router


app = FastAPI()

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(priorities_router)
app.include_router(statuses_router)


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
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
