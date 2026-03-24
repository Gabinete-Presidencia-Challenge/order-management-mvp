from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Orders Service"
    DATABASE_URL: str = "postgresql://orders_user:orders_pass@orders-db:5432/orders_db"
    #DATABASE_URL: str = "postgresql://orders_user:orders_pass@localhost:5432/orders_db"

    SECRET_KEY: str = "orders-service-secret-key-change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]

    class Config:
        env_file = ".env"


settings = Settings()
