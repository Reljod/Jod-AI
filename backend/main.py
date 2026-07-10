from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Jod-AI"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="Jod-AI API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Welcome to Jod-AI API"}
