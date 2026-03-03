from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from .database import engine
from .models.users import Base

from .dependencies import SessionDep
from .routers.users import router as user_router
from .routers.auth import router as auth_router
from .routers.tasks import router as tasks_router
from .routers.priorities import router as priorities_router
from .routers.statuses import router as statuses_router
from backend.app.utils.custom_exceptions import DomainException


app = FastAPI()


@app.exception_handler(DomainException)
async def validation_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        content={"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers
    )


@app.exception_handler(Exception)
async def unexcpected_exception_handler(request: Request, exc: Exception):
    print(f"Unexcpected error: {exc}")
    return JSONResponse(content={"detail": "Internal server error"}, status_code=500)


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
