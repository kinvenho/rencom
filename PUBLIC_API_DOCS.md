# Rencom Public API Documentation

Welcome to the Rencom E-commerce Reviews API! This document provides all the essential information for developers and users to integrate with and use the API.

---

## Authentication
- All endpoints (except health checks) require an API token.
- Pass your token in the `Authorization` header:
  ```
  Authorization: Bearer <your-api-token>
  ```

---

## Endpoints

### General
- `GET /` — Health check (returns API status, version, etc.)
  - Example response:
    ```json
    {"message": "Rencom API is running", "version": "1.0.0", "status": "healthy"}
    ```
- `GET /health` — Detailed health check (returns status of services)
  - Example response:
    ```json
    {"status": "healthy", "services": {"supabase": "connected"}}
    ```

### Token Management
- `POST /api/v1/tokens` — Create a new API token
  - Body: `{ "name": "my-token-name" }`
  - Rate limit: 5 requests/minute per IP
  - Example response:
    ```json
    {"token": "...", "name": "my-token-name", "created_at": "..."}
    ```

### Reviews
- `POST /api/v1/reviews` — Submit a new review
  - Body: `{ "product_id": "prod-123", "user_id": "user-abc-123", "rating": 5, "comment": "Great!" }`
  - Rate limit: 30 requests/minute per IP
  - Duplicate reviews (same product_id + user_id) are not allowed.
  - Example success response:
    ```json
    {"success": true, "review_id": "...", "message": "Review submitted successfully", "status_code": 201}
    ```
  - Example duplicate error:
    ```json
    {"success": false, "error": "You have already submitted a review for this product.", "status_code": 409}
    ```
- `DELETE /api/v1/reviews/{review_id}` — Permanently delete a review
  - Requires: valid API token
  - Example success response:
    ```json
    {"success": true, "message": "Review deleted", "status_code": 200}
    ```
  - Example not found error:
    ```json
    {"success": false, "error": "Review not found", "status_code": 404}
    ```
- `GET /api/v1/products/{product_id}/reviews` — Get paginated reviews for a product
  - Query params: `page`, `page_size`
  - Example response:
    ```json
    {
      "reviews": [
        {"id": "...", "product_id": "prod-123", "user_id": "user-abc-123", "rating": 5, "comment": "Great!", "status": "approved", "created_at": "..."}
      ],
      "total": 100,
      "page": 1,
      "page_size": 10,
      "total_pages": 10,
      "has_next": true,
      "has_prev": false
    }
    ```
- `GET /api/v1/products/{product_id}/summary` — Get review summary for a product
  - Example response:
    ```json
    {
      "product_id": "prod-123",
      "average_rating": 4.5,
      "total_reviews": 10,
      "rating_distribution": {"1": 0, "2": 0, "3": 1, "4": 2, "5": 7},
      "last_updated": "..."
    }
    ```

---

## Status Codes & Error Handling
- **201**: Successful creation (review, token)
- **200**: Successful GET or DELETE
- **401**: Missing or invalid API token
- **404**: Review not found (on delete)
- **409**: Duplicate review
- **429**: Rate limit exceeded
- **500**: Internal server error

All errors are returned in:
```json
{
  "success": false,
  "error": "Error message",
  "status_code": <code>
}
```

---

## Pagination Metadata
- `total`: Total number of reviews
- `page`: Current page number
- `page_size`: Number of reviews per page
- `total_pages`: Total number of pages
- `has_next`: Is there a next page?
- `has_prev`: Is there a previous page?

---

## Rate Limiting
- Token creation: 5 requests/minute per IP
- Review submission: 30 requests/minute per IP
- Default: 10 requests/minute per IP
- Exceeding the limit returns:
  ```json
  {
    "success": false,
    "error": "Rate limit exceeded. Try again later.",
    "status_code": 429
  }
  ```

---

## Audit Logging
- All sensitive actions (token creation, review submission, review deletion, duplicate review attempts, errors) are logged to `audit.log`.
- Each log entry is a JSON object with timestamp, action, and relevant details.
- Example:
  ```json
  {"event": "delete_review", "review_id": "...", "timestamp": "..."}
  ```

---

## Support & Contact
- For help, issues, or feature requests, contact: [support@rencom.com](mailto:support@rencom.com)
- Or create an issue on our GitHub repository.

---

## Terms & Privacy
- By using this API, you agree to our Terms of Service and Privacy Policy (coming soon).

---

## Changelog
- See the repository for the latest updates and release notes. 