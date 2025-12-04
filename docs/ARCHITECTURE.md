# Architecture Documentation

## System Overview

VintedScanner Web is a modern web-based alert platform for Vinted marketplace notifications. It's a complete rewrite of the CLI VintedScanner with a web interface, featuring intelligent brand/category search as the key differentiator.

**Key Architecture Principle:** Single codebase for both self-hosted and cloud deployment, controlled via environment variables.

## Technology Stack

- **Backend**: FastAPI (Python 3.11+) with SQLAlchemy ORM
- **Frontend**: React 18+ with TypeScript, Vite, TailwindCSS, Shadcn/ui
- **Database**: SQLite (self-hosted) / PostgreSQL (cloud)
- **Deployment**: Docker + docker-compose
- **Package Management**: uv (Python), npm (Node.js)

## Backend Structure

```
backend/
├── api/              # REST endpoints
│   ├── auth.py      # JWT authentication
│   ├── alerts.py    # Alert CRUD
│   ├── brands.py    # Brand search with caching
│   └── categories.py # Category tree
├── models/          # SQLAlchemy models
│   ├── user.py
│   ├── alert.py     # Stores brand_ids, brand_names, catalog_ids, catalog_names
│   ├── brand.py     # Brand cache (vinted_id, name, country_code, is_popular)
│   └── category.py  # Hierarchical categories
├── services/
│   ├── vinted_client.py    # Vinted API integration
│   ├── brand_service.py    # Brand caching service
│   ├── category_service.py # Category tree with caching
│   ├── scanner.py          # Background alert scanner
│   └── notifications.py    # Email/Slack/Telegram
├── schemas/         # Pydantic schemas for validation
├── seeds/           # Database seed scripts
│   └── popular_brands.py   # Pre-seed top 100 brands per country
├── tests/           # Test files
├── alembic/         # Database migrations
├── main.py          # FastAPI app entry point
├── config.py        # Environment configuration
└── database.py      # Database setup
```

## Critical Feature: Brand/Category Lookup

### The Problem
Original CLI requires users to manually find numeric brand IDs (Nike = "53") by inspecting network requests or URLs. This is terrible UX.

### Our Solution: Three-tier Caching System

1. **Pre-seeded popular brands** - Instant lookup for top 100 brands per country
2. **Dynamic API fetch** - On-demand fetching from Vinted API for obscure brands
3. **Local cache** - 30-day TTL in database to reduce API calls

### Flow Diagram

```
User types "Nik..." in frontend
         ↓
GET /api/brands/search?q=Nik&country=fr
         ↓
Backend BrandService checks:
  1. Local cache (brands table) → Found? Return instantly
  2. Not found? Fetch from Vinted API
  3. Cache result in database
  4. Return to frontend
         ↓
User sees: "Nike (53)" in autocomplete dropdown
         ↓
User selects → Store brand_ids="53", brand_names="Nike" in alert
```

## Database Schema

### Key Tables

**alerts**
- Stores user alert configurations
- `brand_ids`: Comma-separated Vinted IDs (e.g., "53,14")
- `brand_names`: Display names for UI (e.g., "Nike, Adidas")
- `catalog_ids`: Category IDs
- `catalog_names`: Category display names
- `check_interval_minutes`: How often to scan
- `notification_config`: JSON for notification preferences

**brands** (cache table)
- `vinted_id`: Vinted's internal ID
- `name`: Brand name
- `country_code`: Brands vary by country (e.g., "fr", "ie")
- `is_popular`: Pre-seeded flag for instant lookup
- `item_count`: Number of items (from Vinted API)
- `updated_at`: For cache invalidation (TTL: 30 days)

**categories** (hierarchical cache)
- `vinted_id`: Vinted's internal catalog ID
- `name`: Category name
- `parent_id`: Self-referencing foreign key for hierarchy
- `level`: Tree depth (0 = root)
- `path`: Full path like "/Women/Accessories/Hats"
- `country_code`: Categories vary by country

**users**
- Standard user model with JWT authentication
- Optional for self-hosted (single-user mode)

**item_history**
- Deduplication table
- Prevents re-notifying about same items
- Links to alert_id and Vinted item_id

See `PLAN.md` for complete schema with all columns.

## Vinted API Integration

### VintedClient Service

**Key Methods:**
- `initialize_session()`: Acquire country-specific session cookies
- `search(search_text, brand_ids, catalog_ids, price_from, price_to)`: Search for items
- `search_brands(query)`: Search brands by name (NEW for this project)
- `get_category_tree()`: Fetch complete category hierarchy (NEW)

**Important Notes:**
- Vinted API is unofficial and may change without notice
- All integration goes through `VintedClient` service layer for easy updates
- Respect rate limits: 30s minimum between API calls per country
- Each country has different base URL and cookies

## Design Patterns

### API-First Design
- Frontend exclusively consumes REST API
- Backend serves static frontend files in self-hosted mode
- All business logic in backend services
- Clear separation of concerns

### Stateless API
- JWT authentication, no server sessions
- Enables horizontal scaling
- Each request is independent

### Background Processing
- Scanner service runs via APScheduler
- Separate from API server
- Polls alerts based on `check_interval_minutes`
- Graceful shutdown handling

### Database Abstraction
- SQLAlchemy ORM exclusively (no raw SQL)
- Supports both SQLite and PostgreSQL with same codebase
- Alembic for migrations

### Smart Caching
- Brand/category lookups are aggressively cached
- Cache is expendable (can always re-fetch from Vinted)
- Reduces API calls and improves UX (< 100ms response times)

## Multi-Country Support

Vinted operates in 20+ countries: FR, IE, DE, UK, ES, IT, PL, CZ, LT, LV, NL, BE, AT, LU, PT, SE, DK, FI, NO, HU, RO

Each country has:
- Different base URL (e.g., vinted.fr, vinted.ie)
- Separate session cookies
- Potentially different brand/category IDs
- Different currencies

Handle via `country_code` parameter throughout the stack.

## Architecture Decisions

### Why monolithic initially?
Simplicity for MVP. Microservices add complexity without benefit at small scale. Can split later if needed.

### Why SQLite for self-hosted?
Zero configuration. Single file database. Perfect for single-user deployments. Easy backups.

### Why separate brand/category cache tables?
- Reduces Vinted API calls significantly
- Brands rarely change
- Improves autocomplete performance (< 100ms cached, < 500ms API fetch)
- Enables offline mode for common brands

### Why store both IDs and names in alerts?
- Display purposes (show "Nike" not "53" in UI)
- IDs for API calls to Vinted
- Names for user clarity and history

## Performance Targets

- API response time p95: < 200ms
- Brand search (cached): < 100ms
- Brand search (API fetch): < 500ms
- Category tree load: < 300ms
- Alert scan: < 30s per alert
- Brand cache hit rate: > 80%
- Category cache hit rate: > 95%

## Security Considerations

- JWT secrets stored in environment variables
- Never commit `.env` files
- Input validation via Pydantic schemas
- SQL injection protected by SQLAlchemy ORM
- Rate limiting on API endpoints (future)
- HTTPS required for production

## Deployment Architecture

### Self-Hosted (Docker Compose)
```
[User Browser] → [Docker Container]
                  ├── FastAPI backend (port 3000)
                  ├── React frontend (static files)
                  └── SQLite database (volume mount)
```

### Cloud (Docker Compose with PostgreSQL)
```
[User Browser] → [Load Balancer] → [App Containers]
                                    ├── FastAPI + React
                                    └── Background Scanner
                                         ↓
                                    [PostgreSQL Database]
```

## Future Considerations

### Scalability
- Redis for caching (replace in-memory)
- Separate scanner service
- Message queue for notifications (RabbitMQ/Celery)
- Read replicas for database

### Monitoring
- Prometheus metrics
- Grafana dashboards
- Sentry error tracking
- APM integration

### Features
- Microservices if load increases
- GraphQL API option
- WebSocket for real-time updates
- Mobile app (React Native)
