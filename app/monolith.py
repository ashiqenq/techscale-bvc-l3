# TechScale - Monolithic Order Handler (reference only, do not modify)
#
# This file shows the CURRENT implementation before refactoring.
# All three concerns are mixed inside each route function:
#   1. HTTP-level concerns  -- input parsing, error responses
#   2. Business logic       -- pricing rules, validation rules
#   3. Database access      -- raw SQL, connection management per request
#
# Problems this creates:
#   High coupling:   the route handler depends directly on the DB schema;
#                    a column rename requires editing every route function.
#   Low cohesion:    each function has three unrelated reasons to change.
#   Untestable:      pricing logic cannot be unit-tested without a live DB.
#   Wasteful:        a new DB connection is opened and closed on every request.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pyodbc

router = APIRouter()

# Connection string duplicated wherever DB access is needed
_DB_CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=mentorskool.database.windows.net;"
    "DATABASE=mskl-masterclass;"
    "UID=mskllearnlogin;"
    "PWD=!@#sw2aq1;"
    "Encrypt=yes;TrustServerCertificate=no;"
)


class OrderCreate(BaseModel):
    customer_id: str
    product_id: int
    quantity: int


@router.post("/orders/monolith")
def create_order(order: OrderCreate):
    # HTTP validation mixed with business rules
    if order.quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be positive")
    if order.quantity > 1000:
        raise HTTPException(status_code=422, detail="Cannot order more than 1000 units")

    # Pricing logic inline inside the route handler
    if order.product_id < 100:
        price = round(order.quantity * 9.99, 2)
    elif order.product_id < 200:
        price = round(order.quantity * 24.99, 2)
    else:
        price = round(order.quantity * 49.99, 2)

    # Raw DB access with a new connection opened per request
    try:
        conn = pyodbc.connect(_DB_CONN_STR, timeout=30)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT TOP 1 customer_id FROM CUSTOMERS WHERE customer_id = ?",
            order.customer_id,
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Customer not found")
        conn.close()
    except pyodbc.Error as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")

    return {"total_price": price, "status": "pending"}


@router.get("/orders/monolith/top")
def get_top_orders():
    # DB connection string duplicated again
    try:
        conn = pyodbc.connect(_DB_CONN_STR, timeout=30)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT TOP 5
                o.order_id,
                c.customer_name,
                SUM(op.payment_value) AS total_value
            FROM ORDERS o
            JOIN CUSTOMERS c ON o.customer_id = c.customer_id
            JOIN ORDER_PAYMENTS op ON o.order_id = op.order_id
            GROUP BY o.order_id, c.customer_name
            ORDER BY total_value DESC
            """,
        )
        rows = cursor.fetchall()
        conn.close()
    except pyodbc.Error as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")

    return [
        {"order_id": r[0], "customer_name": r[1], "total_value": round(float(r[2]), 2)}
        for r in rows
    ]
