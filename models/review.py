from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class Product(BaseModel):
    product_id: str = Field(..., description="External product ID")
    name: str = Field(..., description="Product name")

class ReviewSubmission(BaseModel):
    product_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, min_length=0, max_length=2000)

class ReviewResponse(BaseModel):
    id: uuid.UUID
    product_id: str
    user_id: str
    rating: int
    comment: Optional[str]
    status: str  # e.g., 'approved', 'pending', 'rejected', 'spam' (for moderation/workflow)
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

class ReviewSummary(BaseModel):
    product_id: str
    average_rating: float
    total_reviews: int
    rating_distribution: dict
    last_updated: datetime

    class Config:
        from_attributes = True

class APIToken(BaseModel):
    token: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None 