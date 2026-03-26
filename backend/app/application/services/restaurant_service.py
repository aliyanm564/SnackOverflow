
import uuid 
from typing import List, Optional

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.domain.models.restaurant import Restaurant
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.restaurant_repository import (RestaurantRepository)

class RestaurantService:

    def __init__(self, restaurant_repository: RestaurantRepository) -> None:
        self._restaurants = restaurant_repository

    def create_restaurant(self, requesting_user: User, name: str, location: Optional[str] = None, description: Optional[str] = None,) -> Restaurant:
        if requesting_user.role != UserRole.RESTAURANT_OWNER:
            raise AuthorizationError("Only restaurant owners can create restaurants.")
        
        restaurant = Restaurant(
            restaurant_id=str(uuid.uuid4()),
            owner_id=requesting_user.customer_id,
            name=name,
            location=location,
            description=description,
        )

        return self._restaurants.save(restaurant)
    
    def get_restaurant(self, restaurant_id: str) -> Restaurant:
        restaurant = self._restaurants.get_by_id(restaurant_id)
        if restaurant is None:
            raise NotFoundError(f"Restaurant '{restaurant_id}' not found.")
        return restaurant
    
    def list_restaurants(self, location: Optional[str] = None, offset: int = 0, limit: int = 20) -> List[Restaurant]:
        if location:
            return self._restaurants.get_by_location(location)
        return self._restaurants.get_paginated(offset=offset, limit=limit)
    
    def search_restaurants(self, query: str) -> List[Restaurant]:
        return self._restaurants.search_by_name(query)
    
    def get_owner_restaurants(self, owner_id: str) -> List[Restaurant]:
        return self._restaurants.get_by_owner(owner_id)
    
    def update_restaurant(self, requesting_user: User, restaurant_id: str, name: Optional[str] = None, location: Optional[str] = None, description: Optional[str] = None,) -> Restaurant:
        restaurant = self.get_restaurant(restaurant_id)
        self._check_owner(requesting_user, restaurant)

        changes = {}
        if name is not None:
            changes["name"] = name
        if location is not None:
            changes["location"] = location
        if description is not None:
            changes["description"] = description
        
        if changes:
            restaurant = restaurant.model_copy(update=changes)
        
        return self._restaurants.save(restaurant)
    
    def delete_restaurant(self, requesting_user: User, restaurant_id: str) -> None:
        restaurant = self.get_restaurant(restaurant_id)
        self._check_owner(requesting_user, restaurant)
        self._restaurants.delete(restaurant_id)

    def _check_owner(self, user: User, restaurant: Restaurant) -> None:
        if restaurant.owner_id != user.customer_id:
            raise AuthorizationError("You do not have permission to modify this restaurant.")
        