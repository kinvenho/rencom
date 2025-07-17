from fastapi import APIRouter, HTTPException, Query, Depends, Header, Body, Request
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
import secrets
import structlog
from extensions import limiter, audit_logger

from models.review import (
    ReviewSubmission,
    ReviewResponse,
    ReviewListResponse,
    ReviewSummary,
    APIToken
)
from services.supabase import supabase

router = APIRouter()

async def require_api_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API token")
    token = authorization.split(" ", 1)[1]
    if not await supabase.validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid API token")
    return token

@router.post("/tokens", response_model=APIToken)
@limiter.limit("5/minute")
async def create_api_token(request: Request, name: str = Body(..., embed=True)):
    try:
        token = secrets.token_urlsafe(32)
        created = await supabase.create_token(token, name)
        if not created:
            audit_logger.info("create_token_failed", name=name)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Failed to create API token",
                    "status_code": 500
                }
            )
        audit_logger.info("create_token", token=token, name=name)
        return APIToken(token=created["token"], name=created.get("name"), created_at=created.get("created_at"))
    except Exception as e:
        audit_logger.error("create_token_error", name=name, error=str(e))
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to create API token: {str(e)}",
                "status_code": 500
            }
        )

@router.post("/reviews", response_model=dict, dependencies=[Depends(require_api_token)])
@limiter.limit("30/minute")
async def submit_review(request: Request, review: ReviewSubmission):
    try:
        created_review = await supabase.create_review(review.dict())
        audit_logger.info("submit_review", user_id=review.user_id, product_id=review.product_id, rating=review.rating)
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "review_id": created_review["id"],
                "message": "Review submitted successfully",
                "status_code": 201
            }
        )
    except Exception as e:
        # Check for unique constraint violation (Postgres error code 23505)
        if hasattr(e, 'args') and e.args:
            err = e.args[0]
            if isinstance(err, dict) and err.get('code') == '23505':
                audit_logger.warning("duplicate_review", user_id=review.user_id, product_id=review.product_id)
                return JSONResponse(
                    status_code=409,
                    content={
                        "success": False,
                        "error": "You have already submitted a review for this product.",
                        "status_code": 409
                    }
                )
            if isinstance(err, str) and '23505' in err:
                audit_logger.warning("duplicate_review", user_id=review.user_id, product_id=review.product_id)
                return JSONResponse(
                    status_code=409,
                    content={
                        "success": False,
                        "error": "You have already submitted a review for this product.",
                        "status_code": 409
                    }
                )
        audit_logger.error("submit_review_error", user_id=review.user_id, product_id=review.product_id, error=str(e))
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to submit review: {str(e)}",
                "status_code": 500
            }
        )

@router.get("/products/{product_external_id}/reviews", response_model=ReviewListResponse, dependencies=[Depends(require_api_token)])
async def get_product_reviews(
    product_external_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Reviews per page"),
    rating: Optional[str] = Query(None, description="Filter by rating(s), comma-separated (e.g., 4,5)"),
    status: Optional[str] = Query(None, description="Filter by review status (e.g., approved)"),
    date_from: Optional[str] = Query(None, description="Filter reviews created after this date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter reviews created before this date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field: created_at or rating"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc")
):
    try:
        result = await supabase.get_reviews(
            product_external_id,
            page,
            page_size,
            rating=rating,
            status=status,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return ReviewListResponse(**result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to get reviews: {str(e)}",
                "status_code": 500
            }
        )

@router.get("/products/{product_external_id}/summary", response_model=ReviewSummary, dependencies=[Depends(require_api_token)])
async def get_product_summary(product_external_id: str):
    try:
        summary = await supabase.get_review_summary(product_external_id)
        if not summary:
            return ReviewSummary(
                product_id=product_external_id,
                average_rating=0.0,
                total_reviews=0,
                rating_distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                last_updated=datetime.utcnow()
            )
        return ReviewSummary(**summary)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to fetch summary: {str(e)}",
                "status_code": 500
            }
        )

@router.delete("/reviews/{review_id}", response_model=dict, dependencies=[Depends(require_api_token)])
async def delete_review(review_id: str):
    try:
        deleted = await supabase.delete_review(review_id)
        if not deleted:
            audit_logger.info("delete_review_not_found", review_id=review_id)
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Review not found", "status_code": 404}
            )
        audit_logger.info("delete_review", review_id=review_id)
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Review deleted", "status_code": 200}
        )
    except Exception as e:
        audit_logger.error("delete_review_error", review_id=review_id, error=str(e))
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Failed to delete review: {str(e)}", "status_code": 500}
        ) 