from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db.session import get_db
from app.models.order import OrderStatus
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate, PaginatedOrders
from app.services import order_service

router = APIRouter()


@router.get("", response_model=PaginatedOrders)
def list_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """List all orders with optional status filter and pagination."""
    result = order_service.list_orders(db, status=status, page=page, page_size=page_size)
    return result


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order with items."""
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="An order must contain at least one item.",
        )
    return order_service.create_order(db, payload)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single order by ID, including items and status history."""
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update the status of an existing order."""
    order = order_service.update_order_status(db, order_id, payload)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: UUID, db: Session = Depends(get_db)):
    """Delete an order by ID."""
    deleted = order_service.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
