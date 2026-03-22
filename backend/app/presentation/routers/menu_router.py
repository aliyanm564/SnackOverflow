from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.application.services.menu_service import MenuService
from backend.app.domain.models.menu_item import MenuItem
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import get_current_user, get_menu_service
from backend.app.presentation.schemas.schemas import (
    CreateMenuItemRequest,
    MenuItemResponse,
    UpdateMenuItemRequest,
)

router = APIRouter(tags=["Menu"])


def _to_response(item: MenuItem) -> MenuItemResponse:
    return MenuItemResponse(
        food_item_id=item.food_item_id,
        restaurant_id=item.restaurant_id,
        name=item.name,
        category=item.category,
        price=item.price,
    )


@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an item to a restaurant's menu (owner only)",
)
def add_menu_item(
    restaurant_id: str,
    body: CreateMenuItemRequest,
    current_user: User = Depends(get_current_user),
    menu_svc: MenuService = Depends(get_menu_service),
):
    try:
        item = menu_svc.add_item(
            requesting_user=current_user,
            restaurant_id=restaurant_id,
            name=body.name,
            category=body.category,
            price=body.price,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_response(item)


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=List[MenuItemResponse],
    summary="Get all menu items for a restaurant",
)
def get_restaurant_menu(
    restaurant_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    menu_svc: MenuService = Depends(get_menu_service),
):
    try:
        items = menu_svc.list_items_paginated(
            restaurant_id=restaurant_id, offset=offset, limit=limit
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return [_to_response(i) for i in items]


@router.get(
    "/menu/search",
    response_model=List[MenuItemResponse],
    summary="Search menu items by name across all restaurants",
)
def search_menu_items(
    q: str = Query(min_length=1, description="Search query"),
    current_user: User = Depends(get_current_user),
    menu_svc: MenuService = Depends(get_menu_service),
):
    return [_to_response(i) for i in menu_svc.search_items(q)]


@router.get(
    "/menu/filter",
    response_model=List[MenuItemResponse],
    summary="Filter menu items by category or price range",
)
def filter_menu_items(
    category: Optional[str] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    current_user: User = Depends(get_current_user),
    menu_svc: MenuService = Depends(get_menu_service),
):
    if category:
        items = menu_svc.filter_by_category(category)
    elif min_price is not None and max_price is not None:
        try:
            items = menu_svc.filter_by_price_range(min_price, max_price)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    else:
        items = menu_svc.list_items_paginated()
    return [_to_response(i) for i in items]


@router.get(
    "/menu/{food_item_id}",
    response_model=MenuItemResponse,
    summary="Get a single menu item by ID",
)
def get_menu_item(
    food_item_id: str,
    current_user: User = Depends(get_current_user),
    menu_svc: MenuService = Depends(get_menu_service),
):
    try:
        item = menu_svc.get_item(food_item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return _to_response(item)


@router.patch(
    "/menu/{food_item_id}",
    response_model=MenuItemResponse,
    summary="Update a menu item (owner only)",
)
def update_menu_item(
    food_item_id: str,
    body: UpdateMenuItemRequest,
    current_user: User = Depends(get_current_user),
    menu_svc: MenuService = Depends(get_menu_service),
):
    try:
        updated = menu_svc.update_item(
            requesting_user=current_user,
            food_item_id=food_item_id,
            name=body.name,
            category=body.category,
            price=body.price,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_response(updated)


@router.delete(
    "/menu/{food_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a menu item (owner only)",
)
def delete_menu_item(
    food_item_id: str,
    current_user: User = Depends(get_current_user),
    menu_svc: MenuService = Depends(get_menu_service),
):
    try:
        menu_svc.delete_item(current_user, food_item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))