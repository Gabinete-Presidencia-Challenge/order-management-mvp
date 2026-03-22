from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatusHistory, OrderStatus
from app.schemas.order import OrderCreate, OrderStatusUpdate


def get_order(db: Session, order_id: UUID) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()


def list_orders(
    db: Session,
    status: Optional[OrderStatus] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": orders}


def create_order(db: Session, payload: OrderCreate) -> Order:
    total = sum(item.unit_price * item.quantity for item in payload.items)
    order = Order(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        notes=payload.notes,
        total_amount=total,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.flush()  # get order.id before items insert

    for item_data in payload.items:
        item = OrderItem(
            order_id=order.id,
            product_name=item_data.product_name,
            product_sku=item_data.product_sku,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
        )
        db.add(item)

    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=None,
        new_status=OrderStatus.PENDING,
        changed_by="system",
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, order_id: UUID, payload: OrderStatusUpdate) -> Optional[Order]:
    order = get_order(db, order_id)
    if not order:
        return None
    previous = order.status
    order.status = payload.status
    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=previous,
        new_status=payload.status,
        changed_by=payload.changed_by or "api",
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order_id: UUID) -> bool:
    order = get_order(db, order_id)
    if not order:
        return False
    db.delete(order)
    db.commit()
    return True
