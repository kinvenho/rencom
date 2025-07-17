from fastapi import APIRouter, HTTPException, Query, Depends, Header, Body
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
import secrets
import asyncpg

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
async def create_api_token(name: str = Body(..., embed=True)):
    token = secrets.token_urlsafe(32)
    created = await supabase.create_token(token, name)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create API token")
    return APIToken(token=created["token"], name=created.get("name"), created_at=created.get("created_at"))

@router.post("/reviews", response_model=dict, dependencies=[Depends(require_api_token)])
async def submit_review(review: ReviewSubmission):
    try:
        created_review = await supabase.create_review(review.dict())
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
                return JSONResponse(
                    status_code=409,
                    content={
                        "success": False,
                        "error": "You have already submitted a review for this product.",
                        "status_code": 409
                    }
                )
            if isinstance(err, str) and '23505' in err:
                return JSONResponse(
                    status_code=409,
                    content={
                        "success": False,
                        "error": "You have already submitted a review for this product.",
                        "status_code": 409
                    }
                )
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
    page_size: int = Query(50, ge=1, le=100, description="Reviews per page")
):
    try:
        result = await supabase.get_reviews(product_external_id, page, page_size)
        return ReviewListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reviews: {str(e)}")

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}") 