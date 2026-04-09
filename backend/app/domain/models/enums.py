from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    OUT_FOR_DELIVERY = "out_for_delivery"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliveryMethod(str, Enum):
    WALK = "walk"
    BIKE = "bike"
    CAR = "car"
    MIXED = "mixed"


class RouteType(str, Enum):
    ROUTE_1 = "route_1"
    ROUTE_2 = "route_2"
    ROUTE_3 = "route_3"
    ROUTE_4 = "route_4"
    ROUTE_5 = "route_5"
