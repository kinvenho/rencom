import re
from typing import Dict, Any

def sanitize_email(email: str) -> str:
    """Sanitize and normalize email address"""
    return email.lower().strip()

def format_rating_distribution(reviews: list) -> Dict[str, int]:
    """Format rating distribution from reviews"""
    distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    
    for review in reviews:
        rating = str(review.get("rating", 0))
        if rating in distribution:
            distribution[rating] += 1
    
    return distribution

def calculate_average_rating(reviews: list) -> float:
    """Calculate average rating from reviews"""
    if not reviews:
        return 0.0
    
    total_rating = sum(review.get("rating", 0) for review in reviews)
    return round(total_rating / len(reviews), 2) 