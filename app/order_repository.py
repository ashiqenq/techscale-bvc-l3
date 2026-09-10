# TechScale: Data access layer
# Owns the database connection pool and all SQL queries.
# The service layer and routes must not import sqlalchemy or pyodbc directly.
#
# Cloud database behaviour to account for when configuring the pool:
#   pool_size     — persistent connections kept open at all times
#   max_overflow  — extra connections allowed above pool_size during traffic spikes
#   pool_pre_ping — verifies a pooled connection is still alive before using it;
#                   silently replaces any that Azure closed during an idle period
#   pool_recycle  — retires a connection after N seconds to prevent Azure's
#                   idle timeout from closing it underneath the pool

import urllib
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


# Database credentials (do not modify)
_params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=mentorskool.database.windows.net;"
    "DATABASE=mskl-masterclass;"
    "UID=mskllearnlogin;"
    "PWD=!@#sw2aq1;"
    "Encrypt=yes;TrustServerCertificate=no;"
)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={_params}"


# TODO 1: Create the SQLAlchemy engine with a connection pool.
# Configure it to handle high-concurrency traffic and Azure's idle-connection timeout.
# Use the pool settings documented above. After creating the engine, verify connectivity.

try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=1800,
    )
except ModuleNotFoundError as exc:
    if exc.name != "pyodbc":
        raise
    engine = None


# TODO 2: Add a function that returns the top 5 orders by total payment value.
# Join ORDERS, CUSTOMERS, and ORDER_PAYMENTS.
# Return dicts with order_id, customer_name, and total_value rounded to 2 decimals.

def get_top_orders():
    query = text(
        """
        SELECT TOP 5
            o.order_id,
            c.customer_name,
            SUM(op.payment_value) AS total_value
        FROM ORDERS AS o
        JOIN CUSTOMERS AS c ON c.customer_id = o.customer_id
        JOIN ORDER_PAYMENTS AS op ON op.order_id = o.order_id
        GROUP BY o.order_id, c.customer_name
        ORDER BY total_value DESC
        """
    )
    try:
        if engine is None:
            raise RuntimeError("pyodbc is required for database access")
        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()
    except (SQLAlchemyError, RuntimeError) as exc:
        raise RuntimeError(f"Database unavailable: {exc}") from exc
    return [
        {
            "order_id": row["order_id"],
            "customer_name": row["customer_name"],
            "total_value": round(float(row["total_value"]), 2),
        }
        for row in rows
    ]


# Entry point

if __name__ == "__main__":
    print("=== Connection pool test ===")
    # TODO 1 should print: [DB] Connection pool ready: (1,)
    try:
        if engine is None:
            raise RuntimeError("pyodbc is required for database access")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).fetchone()
            print(f"[DB] Connection pool ready: {result}")
    except (SQLAlchemyError, RuntimeError) as exc:
        print(f"[DB] Connection pool unavailable: {exc}")

    print("\n=== Top orders query ===")
    orders = get_top_orders()
    for o in orders:
        print(f"  {o['order_id']} | {o['customer_name']} | ${o['total_value']:.2f}")
