from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routes import router as v1_router
from app.core.handlers import add_exception_handlers


class AppCreator:
    def __init__(self):
        self.app = FastAPI(
            title=settings.PROJECT_NAME,
            description=settings.PROJECT_DESCRIPTION,
            version=settings.PROJECT_VERSION,
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
        )
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=settings.CORS_ALLOWED_METHODS,
            allow_headers=settings.CORS_ALLOWED_HEADERS,
        )
        
        self.app.include_router(v1_router, prefix=settings.API_V1_STR, tags=["v1"])

        @self.app.get("/", tags=["Root"])
        async def root():
            return {"detail": "Welcome to the malicious message detector API"}

    def create_app(self):
        return self.app
    

app_creator = AppCreator()
app = app_creator.create_app()
add_exception_handlers(app)