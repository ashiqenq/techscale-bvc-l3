# TechScale: Business logic layer
# Pricing rules and order validation only — no database or HTTP imports here.
# If a change is driven by a pricing policy or business rule, it belongs here.
# If it is driven by a schema change or HTTP contract, it belongs elsewhere.


# TODO 1: Add a function to validate the order quantity.
# Reject quantities that are zero or negative, and any quantity above 1000.
# Raise a descriptive ValueError for each invalid case; return True if valid.

def validate_order(quantity: int) -> bool:
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    if quantity > 1000:
        raise ValueError("Cannot order more than 1000 units")
    return True


# TODO 2: Add a function to calculate the total order price.
# TechScale uses three price tiers based on product ID:
#   product_id < 100   → $9.99 per unit
#   product_id < 200   → $24.99 per unit
#   product_id >= 200  → $49.99 per unit
# Reject non-positive product IDs with a ValueError.
# Return the total rounded to 2 decimal places.

def calculate_price(product_id: int, quantity: int) -> float:
    if product_id <= 0:
        raise ValueError("Product ID must be positive")
    validate_order(quantity)
    if product_id < 100:
        unit_price = 9.99
    elif product_id < 200:
        unit_price = 24.99
    else:
        unit_price = 49.99
    return round(quantity * unit_price, 2)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== validate_order ===")
    print(validate_order(5))           # True
    try:
        validate_order(-1)
    except ValueError as e:
        print(f"Caught: {e}")
    try:
        validate_order(1500)
    except ValueError as e:
        print(f"Caught: {e}")

    print("\n=== calculate_price ===")
    print(calculate_price(50, 3))      # 29.97  (3 x 9.99)
    print(calculate_price(150, 2))     # 49.98  (2 x 24.99)
    print(calculate_price(250, 1))     # 49.99  (1 x 49.99)
    try:
        calculate_price(-5, 1)
    except ValueError as e:
        print(f"Caught: {e}")
