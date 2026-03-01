from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .database import engine
from .models.users import Base

from .dependencies import SessionDep
from .routers.users import router as user_router
from .routers.auth import router as auth_router
from .routers.tasks import router as tasks_router
from .routers.priorities import router as priorities_router
from .routers.statuses import router as statuses_router
from backend.app.utils.custom_exceptions import (
    ConflictException,
    DomainException,
    NotFoundException,
    ValidationException,
    InternalServerException,
    UnauthorizedException,
    ForbiddenException,
)


app = FastAPI()

ERROR_MAP = {
    DomainException: 400,
    ValidationException: 400,
    UnauthorizedException: 401,
    ForbiddenException: 403,
    NotFoundException: 404,
    ConflictException: 409,
    InternalServerException: 500,
}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input",
            "details": exc.errors(),
        }
    }
    return JSONResponse(content=payload, status_code=422)


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    payload = {
        "error": {
            "code": exc.code or type(exc).__name__,
            "message": exc.message,
        }
    }
    return JSONResponse(content=payload, status_code=404)


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    payload = {
        "error": {
            "code": exc.code or type(exc).__name__,
            "message": exc.message,
        }
    }
    return JSONResponse(content=payload, status_code=400)


@app.exception_handler(ConflictException)
async def conflict_exception_handler(request: Request, exc: ConflictException):
    payload = {
        "error": {
            "code": exc.code or type(exc).__name__,
            "message": exc.message,
        }
    }
    return JSONResponse(content=payload, status_code=409)


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    status_code = ERROR_MAP.get(type(exc), 500)
    payload = {
        "error": {
            "code": exc.code or type(exc).__name__,
            "message": exc.message,
            "request_id": request.state.request_id
            if hasattr(request.state, "request_id")
            else None,
        }
    }
    return JSONResponse(content=payload, status_code=status_code)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    payload = {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": str(exc),
        }
    }
    return JSONResponse(content=payload, status_code=500)


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
