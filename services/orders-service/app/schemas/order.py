from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_name: str
    product_sku: Optional[str] = None
    quantity: int = 1
    unit_price: float


class OrderItemOut(OrderItemCreate):
    id: UUID
    order_id: UUID

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    notes: Optional[str] = None
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    changed_by: Optional[str] = None


class OrderStatusHistoryOut(BaseModel):
    id: UUID
    previous_status: Optional[OrderStatus]
    new_status: OrderStatus
    changed_at: datetime
    changed_by: Optional[str]

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: UUID
    customer_name: str
    customer_email: str
    status: OrderStatus
    total_amount: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut] = []
    status_history: List[OrderStatusHistoryOut] = []

    class Config:
        from_attributes = True


class OrderListOut(BaseModel):
    id: UUID
    customer_name: str
    customer_email: str
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedOrders(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[OrderListOut]
