from app.domain.models.order import Order

def calculate_subtotal(order: Order) -> float:
    """
    Calculate the subtotal of an order by summing the price of each item multiplied by its quantity.
    """
    return sum(item.price * item.quantity for item in order.items)


def calculate_delivery_fee(order: Order) -> float:
    """
    Calculate the delivery fee based on the distance and a fixed rate.
    For example, let's assume a fixed rate of $0.5 per kilometer.
    """
    fixed_rate = 0.5
    if order.order_value is None:
        return 5.0  # Base fee for orders without a specified value
    
    return order.delivery_distance * fixed_rate

def calculate_total(order: Order) -> float:
    """
    Calculate the total cost of an order by adding the subtotal and delivery fee.
    """
    subtotal = calculate_subtotal(order)
    delivery_fee = calculate_delivery_fee(order)
    taxes = subtotal * 0.12  # find tax rate
    return subtotal + delivery_fee + taxes

