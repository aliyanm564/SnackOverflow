import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
)
from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.review import Review
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.order_repository import OrderRepository
from backend.app.infrastructure.repositories.restaurant_repository import RestaurantRepository
from backend.app.infrastructure.repositories.review_repository import ReviewRepository


class ReviewService:

    def __init__(
        self,
        review_repository: ReviewRepository,
        order_repository: OrderRepository,
        restaurant_repository: RestaurantRepository,
    ) -> None:
        self._reviews = review_repository
        self._orders = order_repository
        self._restaurants = restaurant_repository

    def create_review(
        self,
        requesting_user: User,
        order_id: str,
        rating: int,
        comment: Optional[str],
    ) -> Review:
        if requesting_user.role != UserRole.CUSTOMER:
            raise AuthorizationError("Only customers may submit reviews.")

        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")

        if order.customer_id != requesting_user.customer_id:
            raise AuthorizationError("You may only review your own orders.")

        if order.status != OrderStatus.COMPLETED:
            raise BusinessRuleError("Reviews can only be submitted for completed orders.")

        existing = self._reviews.get_by_order(order_id)
        if existing is not None:
            raise ConflictError("A review for this order already exists.")

        review = Review(
            review_id=str(uuid.uuid4()),
            order_id=order_id,
            customer_id=requesting_user.customer_id,
            restaurant_id=order.restaurant_id,
            rating=rating,
            comment=comment,
            created_at=datetime.now(timezone.utc),
        )
        saved = self._reviews.save(review)
        self._refresh_restaurant_rating(order.restaurant_id)
        return saved

    def update_review(
        self,
        requesting_user: User,
        review_id: str,
        rating: Optional[int],
        comment: Optional[str],
    ) -> Review:
        review = self._reviews.get_by_id(review_id)
        if review is None:
            raise NotFoundError(f"Review '{review_id}' not found.")

        if review.customer_id != requesting_user.customer_id:
            raise AuthorizationError("You may only edit your own reviews.")

        changes: dict = {"updated_at": datetime.now(timezone.utc)}
        if rating is not None:
            changes["rating"] = rating
        if comment is not None:
            changes["comment"] = comment

        updated = review.model_copy(update=changes)
        saved = self._reviews.save(updated)
        self._refresh_restaurant_rating(review.restaurant_id)
        return saved

    def get_review_for_order(self, requesting_user: User, order_id: str) -> Optional[Review]:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")

        if order.customer_id != requesting_user.customer_id:
            raise AuthorizationError("You may not access this order.")

        return self._reviews.get_by_order(order_id)

    def get_restaurant_reviews(self, restaurant_id: str) -> List[Review]:
        restaurant = self._restaurants.get_by_id(restaurant_id)
        if restaurant is None:
            raise NotFoundError(f"Restaurant '{restaurant_id}' not found.")
        return self._reviews.get_by_restaurant(restaurant_id)

    def get_my_reviews(self, requesting_user: User) -> List[Review]:
        return self._reviews.get_by_customer(requesting_user.customer_id)

    def _refresh_restaurant_rating(self, restaurant_id: str) -> None:
        avg, count = self._reviews.get_aggregate(restaurant_id)
        restaurant = self._restaurants.get_by_id(restaurant_id)
        if restaurant is None:
            return
        updated = restaurant.model_copy(update={
            "avg_rating": round(avg, 2) if count > 0 else None,
            "review_count": count,
        })
        self._restaurants.save(updated)
