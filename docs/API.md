# API Documentation

REST API endpoints for VintedScanner Web. All endpoints return JSON.

**Base URL:** `http://localhost:3000/api` (development)

**Authentication:** JWT Bearer tokens in `Authorization` header (where required)

## Interactive Documentation

When the server is running, visit:
- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

## Authentication Endpoints

### Register User
```
POST /api/auth/register
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "access_token": "jwt...",
  "refresh_token": "jwt..."
}
```

### Login
```
POST /api/auth/login
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response:** `200 OK`
```json
{
  "access_token": "jwt...",
  "refresh_token": "jwt...",
  "token_type": "bearer"
}
```

### Refresh Token
```
POST /api/auth/refresh
```
**Body:**
```json
{
  "refresh_token": "jwt..."
}
```
**Response:** `200 OK`
```json
{
  "access_token": "new_jwt..."
}
```

## Alert Endpoints

All alert endpoints require authentication.

### List Alerts
```
GET /api/alerts
```
**Query Params:**
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Max results (default: 100)

**Response:** `200 OK`
```json
{
  "alerts": [
    {
      "id": "uuid",
      "name": "Nike Sneakers",
      "country_code": "fr",
      "search_text": "sneakers",
      "brand_ids": "53",
      "brand_names": "Nike",
      "catalog_ids": "1193",
      "catalog_names": "Shoes",
      "price_min": 20.00,
      "price_max": 100.00,
      "check_interval_minutes": 15,
      "is_active": true,
      "created_at": "2024-12-02T20:00:00Z",
      "last_checked_at": "2024-12-02T20:30:00Z",
      "last_found_count": 5
    }
  ],
  "total": 1
}
```

### Create Alert
```
POST /api/alerts
```
**Body:**
```json
{
  "name": "Nike Sneakers",
  "country_code": "fr",
  "search_text": "sneakers",
  "brand_ids": "53",
  "brand_names": "Nike",
  "catalog_ids": "1193",
  "catalog_names": "Shoes",
  "price_min": 20.00,
  "price_max": 100.00,
  "check_interval_minutes": 15,
  "notification_config": {
    "email": true,
    "slack": false,
    "telegram": false
  }
}
```
**Response:** `201 Created` (same structure as list item)

### Get Alert by ID
```
GET /api/alerts/{alert_id}
```
**Response:** `200 OK` (single alert object)

### Update Alert
```
PUT /api/alerts/{alert_id}
```
**Body:** Same as create (partial updates supported)
**Response:** `200 OK` (updated alert object)

### Delete Alert
```
DELETE /api/alerts/{alert_id}
```
**Response:** `204 No Content`

### Toggle Alert Status
```
PATCH /api/alerts/{alert_id}/toggle
```
**Response:** `200 OK`
```json
{
  "id": "uuid",
  "is_active": true
}
```

## Brand Search Endpoints

### Search Brands
```
GET /api/brands/search
```
**Query Params:**
- `q` (string, required): Search query (min 1 char)
- `country` (string, required): Country code (e.g., "fr", "ie")
- `limit` (int, optional): Max results (default: 10, max: 50)

**Response:** `200 OK`
```json
{
  "brands": [
    {
      "id": "53",
      "name": "Nike",
      "item_count": 12459,
      "logo_url": "https://vinted.com/assets/brands/nike.jpg",
      "is_popular": true
    }
  ],
  "from_cache": true
}
```

**Notes:**
- Checks local cache first (instant < 100ms)
- Falls back to Vinted API if not cached (< 500ms)
- Automatically caches results for 30 days

### Get Popular Brands
```
GET /api/brands/popular
```
**Query Params:**
- `country` (string, required): Country code
- `limit` (int, optional): Max results (default: 20, max: 100)

**Response:** `200 OK` (same structure as search, all `is_popular: true`)

**Use case:** Display popular brands on page load before user types

## Category Endpoints

### Get Category Tree
```
GET /api/categories/tree
```
**Query Params:**
- `country` (string, required): Country code
- `force_refresh` (bool, optional): Force fetch from Vinted API (default: false)

**Response:** `200 OK`
```json
{
  "country": "fr",
  "categories": [
    {
      "id": "uuid-1",
      "vinted_id": "1",
      "name": "Women",
      "level": 0,
      "item_count": 50000,
      "has_children": true,
      "children": [
        {
          "id": "uuid-2",
          "vinted_id": "1920",
          "name": "Accessories",
          "level": 1,
          "has_children": true,
          "children": [
            {
              "id": "uuid-3",
              "vinted_id": "1193",
              "name": "Hats",
              "level": 2,
              "has_children": false,
              "item_count": 1234
            }
          ]
        }
      ]
    }
  ]
}
```

**Notes:**
- Returns full hierarchical tree
- Cached after first fetch
- Use `force_refresh=true` to update (e.g., weekly cron job)

### Search Categories (Flat)
```
GET /api/categories/search
```
**Query Params:**
- `q` (string, required): Search query
- `country` (string, required): Country code

**Response:** `200 OK`
```json
{
  "categories": [
    {
      "id": "1193",
      "name": "Hats",
      "path": "/Women/Accessories/Hats",
      "item_count": 1234
    }
  ]
}
```

**Use case:** Search by name if user doesn't want to navigate tree

## Item History Endpoints

### Get Items for Alert
```
GET /api/alerts/{alert_id}/items
```
**Query Params:**
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Max results (default: 50)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "item_id": "vinted_item_id",
      "title": "Nike Air Max 90",
      "price": 85.00,
      "currency": "EUR",
      "url": "https://www.vinted.fr/items/...",
      "image_url": "https://images.vinted.net/...",
      "found_at": "2024-12-02T20:30:00Z"
    }
  ],
  "total": 42
}
```

## Health & Status

### Health Check
```
GET /health
```
**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

### API Info
```
GET /
```
**Response:** `200 OK`
```json
{
  "message": "VintedScanner Web API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (Pydantic validation error)
- `500` - Internal Server Error

## Rate Limiting

(To be implemented)

- Authenticated: 1000 requests/hour
- Unauthenticated: 100 requests/hour
- Brand/Category search: 60 requests/minute

## Pagination

List endpoints support pagination via `skip` and `limit` query params.

**Example:**
```
GET /api/alerts?skip=0&limit=20  # First page
GET /api/alerts?skip=20&limit=20  # Second page
```

## Webhooks

(Future feature)

Users will be able to register webhook URLs to receive notifications instead of/in addition to email/Slack/Telegram.
