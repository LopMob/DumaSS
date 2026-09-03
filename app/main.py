from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import crud
from app.config import get_settings
from app.database import Base, engine
from app.routers import commissions, deputies, meetings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Учёт депутатов, комиссий, заседаний, председателей и посещаемости.",
    version="0.1.0",
)

# Для ЛР1 таблицы создаются автоматически при старте (create_all).
# В следующих лабораторных работах схема управляется миграциями Alembic (make migrate).
Base.metadata.create_all(bind=engine)

app.include_router(deputies.router)
app.include_router(commissions.router)
app.include_router(meetings.router)


@app.get("/health", tags=["Служебное"])
def health():
    """Служебный адрес проверки работоспособности сервиса и БД."""
    try:
        with engine.connect():
            db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "environment": settings.environment,
        "database": "ok" if db_ok else "unavailable",
    }


@app.exception_handler(crud.NotFoundError)
def not_found_handler(request: Request, exc: crud.NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(crud.ConflictError)
def conflict_handler(request: Request, exc: crud.ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(crud.QuorumError)
def quorum_handler(request: Request, exc: crud.QuorumError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
def validation_handler(request: Request, exc: RequestValidationError):
    # Единый формат ответа на некорректные запросы (422).
    return JSONResponse(
        status_code=422,
        content={"detail": "Некорректные данные запроса", "errors": exc.errors()},
    )
