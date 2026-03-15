from dataclasses import dataclass

from backend.app.application.exceptions import NotFoundError
from backend.app.domain.models.orders import Order
from backend.app.domain.models.user import User
from backend.app.domain.rules.pricing_rules import (
    calculate_delivery_fee,
    calculate_subtotal,
    calculate_total,
)
from backend.app.infrastructure.repositories.menu_repository import MenuRepository
from backend.app.infrastructure.repositories.order_repository import OrderRepository


@dataclass(frozen=True)
class PriceBreakdown:
    subtotal: float
    delivery_fee: float
    taxes: float
    loyalty_discount: float
    grand_total: float

class PricingService:

    DEFAULT_TAX_RATE = 0.13
    DEFAULT_BASE_DELIVERY_FEE = 5.0
    LOYALTY_DISCOUNT_RATE = 0.05

    def __init__(
        self,
        order_repository: OrderRepository,
        menu_repository: MenuRepository,
        tax_rate: float = DEFAULT_TAX_RATE,
        base_delivery_fee: float = DEFAULT_BASE_DELIVERY_FEE,
    ) -> None:
        self._orders = order_repository
        self._menu = menu_repository
        self._tax_rate = tax_rate
        self._base_delivery_fee = base_delivery_fee

    def get_price_breakdown(self, order_id: str, customer: User) -> PriceBreakdown:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")

        return self._compute_breakdown(order, customer)

    def quote_order(
        self,
        food_item_ids: list[str],
        customer: User,
        delivery_distance: float = 0.0,
    ) -> PriceBreakdown:
        item_prices = self._build_price_map(food_item_ids)

        from backend.app.domain.models.enums import OrderStatus
        temp_order = Order(
            order_id="__quote__",
            customer_id=customer.customer_id,
            restaurant_id="__quote__",
            items=food_item_ids,
            order_value=None,
            status=OrderStatus.PENDING,
        )

        object.__setattr__(temp_order, "delivery_distance", delivery_distance)

        return self._compute_breakdown(temp_order, customer, item_prices)

    def _compute_breakdown(
        self,
        order: Order,
        customer: User,
        item_prices: dict | None = None,
    ) -> PriceBreakdown:
        if item_prices is None:
            item_prices = self._build_price_map(order.items)

        subtotal = calculate_subtotal(order, item_prices)
        delivery_fee = calculate_delivery_fee(order, base_fee=self._base_delivery_fee)
        taxes = round(subtotal * self._tax_rate, 2)

        loyalty_discount = 0.0
        if customer.loyalty_program:
            loyalty_discount = round(subtotal * self.LOYALTY_DISCOUNT_RATE, 2)

        grand_total = round(
            subtotal + delivery_fee + taxes - loyalty_discount, 2
        )

        return PriceBreakdown(
            subtotal=round(subtotal, 2),
            delivery_fee=round(delivery_fee, 2),
            taxes=taxes,
            loyalty_discount=loyalty_discount,
            grand_total=grand_total,
        )

    def _build_price_map(self, food_item_ids: list[str]) -> dict:
        price_map: dict[str, float] = {}

        for item_id in food_item_ids:
            item = self._menu.get_by_id(item_id)

            if item and item.price is not None:
                price_map[item_id] = item.price

        return price_map
