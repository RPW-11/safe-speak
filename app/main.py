from fastapi import FastAPI
from app.core.config import settings


class AppCreator:
    def __init__(self):
        self.app = FastAPI(
            title=settings.PROJECT_NAME,
            description=settings.PROJECT_DESCRIPTION,
            version=settings.PROJECT_VERSION,
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
        )

        @self.app.get("/")
        def root():
            return {"message": "Welcome to the malicious message detector API"}

    def create_app(self):
        return self.app
    

app_creator = AppCreator()
app = app_creator.create_app()