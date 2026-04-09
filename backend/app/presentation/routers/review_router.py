from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.application.services.review_service import ReviewService
from backend.app.domain.models.review import Review
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import (
    get_current_user,
    get_review_service,
    handle_app_errors,
)
from backend.app.presentation.schemas import (
    ReviewCreateRequest,
    ReviewResponse,
    ReviewUpdateRequest,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def _to_response(review: Review) -> ReviewResponse:
    return ReviewResponse(
        review_id=review.review_id,
        order_id=review.order_id,
        customer_id=review.customer_id,
        restaurant_id=review.restaurant_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review for a completed order (customers only)",
)
@handle_app_errors
def create_review(
    body: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    review_svc: ReviewService = Depends(get_review_service),
):
    review = review_svc.create_review(
        requesting_user=current_user,
        order_id=body.order_id,
        rating=body.rating,
        comment=body.comment,
    )
    return _to_response(review)


@router.get(
    "/my",
    response_model=List[ReviewResponse],
    summary="Get all reviews submitted by the current user",
)
@handle_app_errors
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    review_svc: ReviewService = Depends(get_review_service),
):
    return [_to_response(r) for r in review_svc.get_my_reviews(current_user)]


@router.get(
    "/order/{order_id}",
    response_model=ReviewResponse,
    summary="Get the review for a specific order",
)
@handle_app_errors
def get_review_for_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    review_svc: ReviewService = Depends(get_review_service),
):
    review = review_svc.get_review_for_order(current_user, order_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No review found for this order.",
        )
    return _to_response(review)


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=List[ReviewResponse],
    summary="Get all reviews for a restaurant",
)
@handle_app_errors
def get_restaurant_reviews(
    restaurant_id: str,
    review_svc: ReviewService = Depends(get_review_service),
):
    return [_to_response(r) for r in review_svc.get_restaurant_reviews(restaurant_id)]


@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Update an existing review",
)
@handle_app_errors
def update_review(
    review_id: str,
    body: ReviewUpdateRequest,
    current_user: User = Depends(get_current_user),
    review_svc: ReviewService = Depends(get_review_service),
):
    review = review_svc.update_review(
        requesting_user=current_user,
        review_id=review_id,
        rating=body.rating,
        comment=body.comment,
    )
    return _to_response(review)
