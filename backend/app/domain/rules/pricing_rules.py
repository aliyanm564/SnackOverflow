from backend.app.domain.models.orders import Order


def calculate_subtotal(order: Order, item_prices: dict) -> float:
   """Calculate order subtotal based on items."""
   return sum(item_prices.get(item, 0) for item in order.items)


def calculate_delivery_fee(order: Order, base_fee: float = 5.0) -> float:
   """Example: $1 per km + base fee."""
   if order.order_value is None:
       return base_fee
   return base_fee + 1.0 * getattr(order, "delivery_distance", 0)


def calculate_total(order: Order, item_prices: dict, tax_rate: float = 0.13, base_fee: float = 5.0) -> float:
   subtotal = calculate_subtotal(order, item_prices)
   delivery_fee = calculate_delivery_fee(order, base_fee)
   taxes = subtotal * tax_rate
   return subtotal + delivery_fee + taxes
