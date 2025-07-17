from supabase import create_client, Client
from config.settings import settings
from typing import Dict, Any, Optional
from datetime import datetime
import math
import uuid

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )

    async def find_or_create_product(self, product_id: str) -> Dict[str, Any]:
        result = self.client.table("products").select("*").eq("product_id", product_id).execute().data
        if result:
            return result[0]
        created = self.client.table("products").insert({"product_id": product_id, "name": product_id}).execute().data
        return created[0]

    async def find_or_create_user(self, user_id: str, api_token_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        result = self.client.table("users").select("*").eq("id", user_id).execute().data
        if result:
            return result[0]
        data = {"id": user_id}
        if api_token_id:
            data["api_token_id"] = str(api_token_id)
        created = self.client.table("users").insert(data).execute().data
        return created[0]

    async def create_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        # Find or create product
        product = await self.find_or_create_product(review_data["product_id"])
        # Find or create user
        user = await self.find_or_create_user(review_data["user_id"])
        # Insert review
        data = {
            "product_id": product["product_id"],
            "user_id": user["id"],
            "rating": review_data["rating"],
            "comment": review_data.get("comment"),
            "status": "approved"
        }
        result = self.client.table("reviews").insert(data).execute()
        return result.data[0] if result.data else None

    async def get_reviews(
        self,
        product_id: str,
        page: int = 1,
        page_size: int = 50,
        rating: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc"
    ) -> Dict[str, Any]:
        product = self.client.table("products").select("*").eq("product_id", product_id).execute().data
        if not product:
            return {"reviews": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 1, "has_next": False, "has_prev": False}
        query = self.client.table("reviews").select("*").eq("product_id", product_id)
        # Filtering
        if rating:
            ratings = [int(r.strip()) for r in rating.split(",") if r.strip().isdigit()]
            if ratings:
                query = query.in_("rating", ratings)
        if status:
            query = query.eq("status", status)
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                query = query.gte("created_at", date_from_dt.isoformat())
            except Exception:
                pass
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                query = query.lte("created_at", date_to_dt.isoformat())
            except Exception:
                pass
        # Sorting
        if sort_by not in ("created_at", "rating"):
            sort_by = "created_at"
        desc = sort_order != "asc"
        query = query.order(sort_by, desc=desc)
        all_reviews = query.execute().data or []
        total = len(all_reviews)
        start = (page - 1) * page_size
        paginated_reviews = all_reviews[start:start+page_size]
        reviews_with_info = []
        for review in paginated_reviews:
            reviews_with_info.append({
                **review,
                "product_id": product_id
            })
        total_pages = math.ceil(total / page_size) if page_size else 1
        has_next = page < total_pages
        has_prev = page > 1
        return {
            "reviews": reviews_with_info,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }

    async def get_review_summary(self, product_id: str) -> Optional[Dict[str, Any]]:
        product = self.client.table("products").select("*").eq("product_id", product_id).execute().data
        if not product:
            return None
        reviews = self.client.table("reviews").select("*").eq("product_id", product_id).execute().data or []
        total_reviews = len(reviews)
        if total_reviews == 0:
            return None
        rating_sum = 0
        rating_distribution = {str(i): 0 for i in range(1, 6)}
        for review in reviews:
            rating = int(review.get("rating", 0))
            rating_sum += rating
            if str(rating) in rating_distribution:
                rating_distribution[str(rating)] += 1
        average_rating = round(rating_sum / total_reviews, 2) if total_reviews else 0.0
        return {
            "product_id": product_id,
            "average_rating": average_rating,
            "total_reviews": total_reviews,
            "rating_distribution": rating_distribution,
            "last_updated": datetime.utcnow()
        }

    async def update_review_status(self, review_id: uuid.UUID, status: str, moderation_note: str = None) -> Dict[str, Any]:
        """Update review status"""
        data = {"status": status}
        if moderation_note:
            data["moderation_note"] = moderation_note
        result = self.client.table("reviews").update(data).eq("id", str(review_id)).execute()
        return result.data[0] if result.data else None

    async def create_token(self, token: str, name: Optional[str] = None) -> Dict[str, Any]:
        data = {"token": token, "name": name, "created_at": datetime.utcnow().isoformat()}
        result = self.client.table("api_tokens").insert(data).execute()
        return result.data[0] if result.data else None

    async def get_token(self, token: str) -> Optional[Dict[str, Any]]:
        result = self.client.table("api_tokens").select("*").eq("token", token).execute()
        return result.data[0] if result.data else None

    async def validate_token(self, token: str) -> bool:
        result = await self.get_token(token)
        return result is not None

    async def delete_review(self, review_id: str) -> bool:
        result = self.client.table("reviews").delete().eq("id", review_id).execute()
        # result.data is a list of deleted rows; if empty, nothing was deleted
        return bool(result.data)

supabase = SupabaseService() 