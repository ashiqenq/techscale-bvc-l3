# TechScale: HTTP routing layer
# Route handlers receive HTTP input, delegate to service/repository layers, and return responses.
# No pricing logic, validation rules, or SQL belongs in this file.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
import order_service
import order_repository

router = APIRouter()


class OrderCreate(BaseModel):
    customer_id: str
    product_id: int
    quantity: int


# TODO: Implement two route handlers.
#
# 1. POST /orders: accept an order request, validate the quantity via the service layer,
#    calculate the price via the service layer, and return the total price and status.
#    Surface any validation rejection as a 422 response.
#
# 2. GET /orders/top: fetch the top orders via the repository layer.
#    Return a 404 if no orders exist.

@router.post("/orders")
async def create_order(order: OrderCreate):
    try:
        order_service.validate_order(order.quantity)
        total_price = order_service.calculate_price(order.product_id, order.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"total_price": total_price, "status": "pending"}


@router.get("/orders/top")
async def get_top_orders():
    try:
        orders = await run_in_threadpool(order_repository.get_top_orders)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders
