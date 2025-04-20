from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppExceptionBase

def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppExceptionBase)
    async def app_exception_handler(request: Request, exc: AppExceptionBase):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()[0]['msg']},
        )