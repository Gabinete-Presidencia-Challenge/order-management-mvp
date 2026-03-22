from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.session import engine
from app.models import user as user_models
from app.api.endpoints import users, auth
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    user_models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Users Service",
    description="User management and authentication microservice",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "users-service"}
