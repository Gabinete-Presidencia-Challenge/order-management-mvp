from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.session import engine
from app.models import order as order_models
from app.api.endpoints import orders
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (Alembic handles migrations in production)
    order_models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Orders Service",
    description="Order management microservice",
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

app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "orders-service"}
