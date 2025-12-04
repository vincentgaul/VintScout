# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VintedScanner Web is a modern web-based alert platform for Vinted marketplace notifications. It features intelligent brand/category search (users type "Nike" instead of finding ID "53").

**Tech Stack:** FastAPI (Python 3.11+), React 18 + TypeScript, SQLite/PostgreSQL, Docker

**Key Principle:** 
- Single codebase for self-hosted and cloud deployment (controlled via environment variables)
- Modular architecture with clear separation of concerns
- DRY. Keep things simple and maintainable

## Documentation Structure

- **`docs/ARCHITECTURE.md`** - Detailed architecture, design patterns, database schema, performance targets
- **`docs/API.md`** - Complete API endpoint documentation
- **`docs/DEPLOYMENT.md`** - Deployment guides (Docker, cloud platforms)
- **`PLAN.md`** - Full technical specification and implementation plan

## Critical File Locations

### Backend (`backend/`)
- `main.py` - FastAPI app entry point
- `config.py` - Environment variable configuration
- `database.py` - SQLAlchemy setup (works with both SQLite and PostgreSQL)
- `api/` - REST endpoints (auth, alerts, brands, categories)
- `models/` - SQLAlchemy models (User, Alert, Brand, Category, ItemHistory)
- `services/` - Business logic (VintedClient, brand/category caching, scanner, notifications)
- `schemas/` - Pydantic validation schemas
- `seeds/` - Database seed scripts (popular_brands.py with top 100 brands per country)
- `alembic/` - Database migrations

### Frontend (`frontend/src/`)
- `components/ui/` - Shadcn/ui components
- `lib/api.ts` - Axios client with JWT interceptors
- `lib/utils.ts` - Utility functions (cn for Tailwind classes)

## Development Commands

### Backend (using uv - recommended)

Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

```bash
cd backend
uv pip install -r requirements.txt

# Database
uv run alembic upgrade head                    # Apply migrations
uv run alembic revision --autogenerate -m "msg" # Create migration
uv run alembic downgrade -1                    # Rollback

# Seed data
uv run python -m backend.seeds.popular_brands

# Run dev server
uv run uvicorn backend.main:app --reload --port 3000

# Tests
uv run pytest                                  # All tests
uv run pytest backend/tests/test_brands.py    # Specific test
```

**Without uv:** Use `python -m venv venv`, activate, then run commands without `uv run` prefix.

### Frontend

```bash
cd frontend
npm install
npm run dev          # Dev server (port 5173)
npm run build        # Production build
```

### Docker

```bash
docker-compose up --build                       # Self-hosted (SQLite)
docker-compose -f docker-compose.cloud.yml up   # Cloud (PostgreSQL)
```

## Key Architecture Concepts

_(See `docs/ARCHITECTURE.md` for full details)_

### Brand/Category Caching
Three-tier system to avoid manual ID lookup:
1. **Pre-seeded popular brands** (top 100 per country) - instant lookup
2. **Dynamic API fetch** from Vinted - on-demand for obscure brands
3. **Local database cache** - 30-day TTL

**Flow:** User types → Check cache → Not found? Fetch from Vinted → Cache → Return

### Database Schema Highlights
- `alerts.brand_ids` - Comma-separated IDs ("53,14")
- `alerts.brand_names` - Display names ("Nike, Adidas")
- `brands` table - Cache with `vinted_id`, `name`, `country_code`, `is_popular`
- `categories` table - Hierarchical with `parent_id` and `path`

### Vinted API Integration
All calls go through `VintedClient` service:
- `initialize_session()` - Get country-specific cookies
- `search()` - Find items
- `search_brands()` - NEW: Search brands by name
- `get_category_tree()` - NEW: Fetch category hierarchy

**Important:** Vinted API is unofficial - expect changes. Always use `VintedClient` abstraction.

## Configuration

See `.env.example` for all options. Key variables:

**Required:**
- `DATABASE_URL` - SQLite or PostgreSQL connection
- `JWT_SECRET` - Generate with `openssl rand -hex 32`
- `DEPLOYMENT_MODE` - "self-hosted" or "cloud"

**Brand/Category:**
- `BRAND_CACHE_TTL_DAYS` (default: 30)
- `SEED_POPULAR_BRANDS_ON_STARTUP` (default: true)

**Notifications (optional):**
- `SMTP_*` - Email configuration
- `SLACK_WEBHOOK_URL` - Slack webhooks
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` - Telegram bot

## Common Workflows

### Adding a New Alert Parameter

1. Add column to `alerts` table: `uv run alembic revision --autogenerate -m "add param"`
2. Update `Alert` model in `models/alert.py`
3. Update Pydantic schemas in `schemas/alert.py`
4. Modify `VintedClient.search()` to use parameter
5. Update API endpoint in `api/alerts.py`
6. Add UI field in `AlertForm.tsx`

### Adding Brand/Category Support for New Country

1. Add country-specific brands to `seeds/popular_brands.py`
2. Run: `uv run python -m backend.seeds.seed_popular_brands --country XX`
3. Verify: `GET /api/brands/search?q=Nike&country=XX`
4. Verify: `GET /api/categories/tree?country=XX`

### Debugging Vinted API Issues

1. Check logs for specific country
2. Test cookie acquisition: `VintedClient.initialize_session()`
3. Verify endpoint URLs (may change)
4. Check rate limiting (30s minimum between calls per country)
5. Brand/category APIs are separate from item search - test independently

## Important Notes

- **Vinted API is unofficial** - Abstract all calls through `VintedClient` for easy updates
- **Rate limits** - 30s minimum between Vinted API calls per country
- **Brand IDs vary by country** - Always include `country_code` in queries
- **Cache is expendable** - Can always re-fetch from Vinted if corrupted
- **Security** - Never commit `.env` files
- **Multi-country** - Supports 20+ countries (FR, IE, DE, UK, ES, IT, PL, CZ, LT, LV, NL, BE, AT, LU, PT, SE, DK, FI, NO, HU, RO)

## Testing Guidelines

**Backend:**
- Mock Vinted API responses (unofficial API)
- Test both SQLite and PostgreSQL
- Mock external APIs (email, Slack, Telegram)

**Frontend:**
- Test BrandAutocomplete with React Query
- Test CategoryTree recursive rendering
- Test AlertForm integration

## Attribution

Original VintedScanner by Andrea Draghetti. This is a complete rewrite but inspired by the original's Vinted API integration patterns.
