from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Users Service"
    DATABASE_URL: str = "postgresql://users_user:users_pass@users-db:5433/users_db"
    #DATABASE_URL: str = "postgresql://users_user:users_pass@localhost:5432/users_db"
    SECRET_KEY: str = "users-service-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]

    class Config:
        env_file = ".env"


settings = Settings()
