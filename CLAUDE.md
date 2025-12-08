# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VintScout is a modern web-based alert platform for Vinted marketplace notifications. It features intelligent brand/category search (users type "Nike" instead of finding ID "53").

**Tech Stack:** FastAPI (Python 3.11+), React 18 + TypeScript, SQLite/PostgreSQL, Docker

**Key Principle:** 
- Single codebase for self-hosted and cloud deployment (controlled via environment variables)
- Modular architecture with clear separation of concerns
- DRY. Keep things simple and maintainable



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
- `DEPLOYMENT_MODE` - "self-hosted" or "cloud" # TODO: implement cloud mode


**Notifications (optional):**

- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` - Telegram bot
