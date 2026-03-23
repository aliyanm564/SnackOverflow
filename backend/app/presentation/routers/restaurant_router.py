from typing import List, Optional 

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.application.services.restaurant_service import RestaurantService
from backend.app.domain.models.user import User 
from backend.app.presentation.dependencies import get_current_user, get_restaurant_service
from backend.app.presentation.schemas import(
    CreateRestaurantRequest,
    UpdateRestaurantRequest,
    RestaurantResponse,
)
router = APIRouter(prefix ="/restaurants", tags=["Restaurants"])

def _to_response(restaurant) -> RestaurantResponse:
    return RestaurantResponse(
        restaurant_id=restaurant.restaurant_id,
        owner_id=restaurant.owner_id,
        name=restaurant.name,
        location=restaurant.location,
        description=restaurant.description,

    )

@router.post("", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    body: CreateRestaurantRequest,
    current_user: User = Depends(get_current_user),
    svc: RestaurantService = Depends(get_restaurant_service)

):
    try:
        restaurant = svc.create_restaurant(
            requesting_user = current_user, 
            name = body.name,
            location = body.location, 
            description = body.description,
        )

    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail =str(exc))
    return _to_response(restaurant)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(
    restaurant_id: str, 
    svc: RestaurantService = Depends(get_restaurant_service)

):
    try: 
        restaurant = svc.get_restaurant(restaurant_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = str(exc))
    return _to_response(restaurant)

@router.get("", response_model=List[RestaurantResponse])
def list_restaurants(
    location: Optional[str] = Query(default=None),
    query: Optional[str] = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: RestaurantService = Depends(get_restaurant_service),
):
    if query:
        restaurants = svc.search_restaurants(query)
    else:
        restaurants = svc.list_restaurants(location=location, offset=offset, limit=limit)
    return [_to_response(r) for r in restaurants]

@router.get("/owner/{owner_id}", response_model=List[RestaurantResponse])
def get_owner_restaurants(
    owner_id: str,
    svc: RestaurantService = Depends(get_restaurant_service),
):
    return [_to_response(r) for r in svc.get_owner_restaurants(owner_id)]

@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: str,
    body: UpdateRestaurantRequest,
    current_user: User = Depends(get_current_user),
    svc: RestaurantService = Depends(get_restaurant_service),
):
    try:
        updated = svc.update_restaurant(
            requesting_user=current_user,
            restaurant_id=restaurant_id,
            name=body.name,
            location=body.location,
            description=body.description,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return _to_response(updated)

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: str,
    current_user: User = Depends(get_current_user),
    svc: RestaurantService = Depends(get_restaurant_service),
):
    try:
        svc.delete_restaurant(requesting_user=current_user, restaurant_id=restaurant_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))