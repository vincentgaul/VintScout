# VintedScanner Web Platform - Technical Plan
**Open Source Vinted Alert System with Web Interface**

---

## Executive Summary

**Project**: VintedScanner Web - Modern web-based alert platform for Vinted marketplace notifications

**Repository Strategy**: New repository (not a fork) with attribution to original VintedScanner

**Target Users**: 
- Self-hosted: Individual users, developers, privacy-conscious users
- Cloud: Non-technical users wanting zero maintenance

**Core Value Proposition**: Web-based interface for managing Vinted alerts across 20+ countries with real-time notifications and intelligent brand/category search

**Key Differentiator**: Unlike the CLI version that requires manual numeric ID lookup, our web interface provides autocomplete brand search and visual category trees

---

## Project Objectives

### Primary Objectives

1. **Build a web-based alternative** to the CLI VintedScanner:
   - React frontend for alert management
   - REST API backend
   - Real-time dashboard
   - Multi-user support
   - **Intelligent brand/category lookup** (major UX improvement)

2. **Maintain single codebase** for all deployment scenarios:
   - Self-hosted via Docker
   - Cloud deployment ready
   - Environment-driven configuration

3. **Launch MVP within 3 months**:
   - Month 1: Core backend + Vinted integration + brand/category API
   - Month 2: Frontend + autocomplete components + Docker packaging
   - Month 3: Documentation + beta testing

### Secondary Objectives

1. Improve upon original with better error handling
2. Add comprehensive logging and monitoring
3. Create extensible architecture for future features
4. Build active open-source community
5. **Solve the brand/category ID problem** that plagues the original

---

## Core Principles

### Development Principles

**P1: Single Codebase**
- One repository serves both self-hosted and cloud
- Environment variables control deployment mode
- No code duplication between targets

**P2: Simplicity First**
- Monolithic architecture initially
- SQLite for self-hosted, PostgreSQL for cloud
- Minimal dependencies
- Avoid premature optimization

**P3: API-First Design**
- Backend exposes REST API
- Frontend consumes API exclusively
- Clear separation of concerns
- Enables future mobile app

**P4: User-Centric Search**
- **Brand search by name, not numeric IDs**
- **Visual category tree navigation**
- Autocomplete for better UX
- Cache common brands/categories

**P5: Privacy-Respecting**
- Minimal data collection
- GDPR compliant by design
- Clear data policies
- No tracking in self-hosted

**P6: Docker-Native**
- Docker as primary deployment
- docker-compose for orchestration
- Multi-stage builds for efficiency
- Health checks included

### Architectural Principles

**AP1: Stateless API**
- JWT-based authentication
- No server-side sessions
- Horizontal scaling possible
- Simplified deployment

**AP2: Database Abstraction**
- SQLAlchemy ORM exclusively
- Support SQLite + PostgreSQL
- Migrations with Alembic
- No raw SQL

**AP3: Background Processing**
- Separate scanner service from API
- APScheduler for job management
- Graceful shutdown handling
- Job persistence across restarts

**AP4: Configuration via Environment**
- No hardcoded values
- 12-factor app methodology
- .env files for local development
- Cloud-ready configuration

**AP5: Smart Caching**
- Cache brand/category lookups locally
- Reduce Vinted API calls
- Hybrid approach: seed + dynamic fetch
- Invalidate cache appropriately

---

## Technical Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                       │
│                   (React SPA)                           │
│  - Autocomplete brand search                            │
│  - Category tree navigation                             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS / REST API
                     ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend Container                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │             API Server (FastAPI)                 │  │
│  │  - Authentication (JWT)                          │  │
│  │  - Alert CRUD endpoints                          │  │
│  │  - Brand/Category search endpoints              │  │
│  │  - User management                               │  │
│  │  - Static file serving (self-hosted)             │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │        Scanner Service (APScheduler)             │  │
│  │  - Alert polling loop                            │  │
│  │  - Vinted API integration                        │  │
│  │  - Item deduplication                            │  │
│  │  - Notification dispatch                         │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │     Brand/Category Cache Service                 │  │
│  │  - Fetch brands from Vinted                      │  │
│  │  - Fetch category tree                           │  │
│  │  - Local caching with TTL                        │  │
│  │  - Pre-seed common brands                        │  │
│  └──────────────────┬───────────────────────────────┘  │
└────────────────────┬┴────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ↓           ↓           ↓
    ┌────────┐  ┌────────┐  ┌──────────┐
    │Database│  │ Vinted │  │Notifica- │
    │SQLite/ │  │  APIs  │  │tion APIs │
    │Postgres│  │(20+    │  │(Email/   │
    │+ Brand │  │domains)│  │Slack/TG) │
    │ Cache  │  │        │  │          │
    └────────┘  └────────┘  └──────────┘
```

### Technology Stack

**Frontend**
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS v3
- **Component Library**: Shadcn/ui (headless components)
- **Routing**: React Router v6
- **State Management**: 
  - React Query (server state)
  - Zustand (client state)
- **Form Handling**: React Hook Form + Zod validation
- **HTTP Client**: Axios
- **Autocomplete**: Radix UI Combobox or Downshift

**Backend**
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Scheduler**: APScheduler
- **HTTP Client**: httpx (async)
- **Caching**: TTLCache or Redis (future)
- **Testing**: pytest + pytest-asyncio

**Database**
- **Self-Hosted**: SQLite 3 (embedded)
- **Cloud**: PostgreSQL 15+
- **Schema**: Single unified schema
- **Migrations**: Alembic (supports both)

**Infrastructure**
- **Container**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx (optional)
- **Process Manager**: Uvicorn (ASGI server)

### Database Schema

```sql
-- Users table (for cloud multi-user, optional for self-hosted)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    country_code VARCHAR(10) NOT NULL,  -- 'fr', 'ie', 'de', etc.
    
    -- Search parameters
    search_text VARCHAR(255),           -- Free text search
    brand_ids VARCHAR(255),             -- Comma-separated: "53,14"
    brand_names VARCHAR(500),           -- Display names: "Nike, Adidas"
    catalog_ids VARCHAR(255),           -- Comma-separated category IDs
    catalog_names VARCHAR(500),         -- Display names: "Hats, Shoes"
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    order VARCHAR(50) DEFAULT 'newest_first',
    
    -- Alert configuration
    check_interval_minutes INTEGER DEFAULT 15,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Notification settings (JSON)
    notification_config JSONB,  -- {email: true, slack: false, etc.}
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked_at TIMESTAMP,
    last_found_count INTEGER DEFAULT 0,
    
    CONSTRAINT valid_interval CHECK (check_interval_minutes >= 5)
);

CREATE INDEX idx_alerts_user ON alerts(user_id);
CREATE INDEX idx_alerts_active ON alerts(is_active);

-- Brand cache table (for autocomplete)
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vinted_id VARCHAR(50) NOT NULL,     -- Vinted's internal brand ID
    name VARCHAR(255) NOT NULL,
    country_code VARCHAR(10) NOT NULL,  -- Brands may vary by country
    item_count INTEGER DEFAULT 0,       -- Number of items for this brand
    logo_url VARCHAR(500),
    is_popular BOOLEAN DEFAULT FALSE,   -- Flag for pre-seeded brands
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(vinted_id, country_code)
);

CREATE INDEX idx_brands_name ON brands(name);
CREATE INDEX idx_brands_country ON brands(country_code);
CREATE INDEX idx_brands_popular ON brands(is_popular);
CREATE INDEX idx_brands_search ON brands USING gin(to_tsvector('english', name));

-- Category cache table (hierarchical)
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vinted_id VARCHAR(50) NOT NULL,     -- Vinted's internal catalog ID
    name VARCHAR(255) NOT NULL,
    country_code VARCHAR(10) NOT NULL,
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    level INTEGER DEFAULT 0,            -- Tree depth (0 = root)
    path VARCHAR(500),                  -- "/Women/Accessories/Hats"
    item_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(vinted_id, country_code)
);

CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_country ON categories(country_code);
CREATE INDEX idx_categories_path ON categories(path);

-- Item history (deduplication)
CREATE TABLE item_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    item_id VARCHAR(50) NOT NULL,      -- Vinted item ID
    item_title VARCHAR(500),
    item_url VARCHAR(500),
    item_price DECIMAL(10,2),
    item_currency VARCHAR(10),
    item_image_url VARCHAR(500),
    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(alert_id, item_id)
);

CREATE INDEX idx_item_history_alert ON item_history(alert_id);
CREATE INDEX idx_item_history_item ON item_history(item_id);
CREATE INDEX idx_item_history_found ON item_history(found_at DESC);

-- Notification logs (for debugging)
CREATE TABLE notification_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    notification_type VARCHAR(50),      -- 'email', 'slack', 'telegram'
    status VARCHAR(50),                 -- 'sent', 'failed'
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notification_logs_alert ON notification_logs(alert_id);

-- Scanner job status (for monitoring)
CREATE TABLE scanner_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    items_found INTEGER,
    status VARCHAR(50),                 -- 'running', 'completed', 'failed'
    error_message TEXT
);

CREATE INDEX idx_scanner_status_alert ON scanner_status(alert_id);
```

---

## Brand & Category ID Lookup Strategy

### The Problem

The original VintedScanner requires users to manually find numeric IDs:
- Nike = `53`
- Louis Vuitton = `417`
- Hats category = `1193`

Users must:
1. Search Vinted website manually
2. Inspect URLs to find `brand_id[]=53`
3. Trial and error
4. Edit Python config files

**This is terrible UX and our biggest opportunity to improve.**

### Discovery: Brand Search API is Dead

**What We Found (Dec 2025):**
- ❌ `/api/v2/catalog/brands` endpoint returns 404 (DEAD)
- ✅ `brand_ids` parameter in item search still works
- ✅ `/api/v2/catalogs` (category tree) works perfectly

**Implications:**
- Cannot dynamically search/browse brands via API
- Can still filter items by brand_ids if you know them
- Categories work great with full hierarchical tree

### Our Solution: Pragmatic MVP Approach

**Phase 1 (MVP - Now): Text Search Only**
- Users type brand name in `search_text` field
- Example: "Nike sneakers" instead of finding brand ID
- Pros: Zero complexity, works immediately
- Cons: Less precise (might match brand in description)
- **This is good enough for 90% of use cases**

**Phase 2 (Optional - Later): Hardcoded Popular Brands**
- Create static mapping: {"Nike": "53", "Adidas": "14", ...}
- Top 100-200 brands manually curated
- Enable autocomplete for known brands only
- Fallback to text search for unknown brands

**Phase 3 (Future - Nice to Have): Crowdsourced Discovery**
- Extract brand IDs from search results
- Build database organically over time
- Users contribute discovered brand IDs
- Community-maintained brand list

### Implementation Architecture

```
User types "Nik..." in brand search
         ↓
Frontend sends: GET /api/brands/search?q=Nik&country=fr
         ↓
Backend checks:
  1. Local cache (brands table) → Found? Return instantly
  2. Not found? Fetch from Vinted API
  3. Cache result in database
  4. Return to frontend
         ↓
User sees: "Nike (53)" in autocomplete
         ↓
User selects → Store brand_ids="53", brand_names="Nike"
```

### Brand Search API

**Endpoint**: `GET /api/brands/search`

**Parameters:**
- `q` (string): Search query (e.g., "Nike")
- `country` (string): Country code (e.g., "fr")
- `limit` (int, optional): Max results (default: 10)

**Response:**
```json
{
  "brands": [
    {
      "id": "53",
      "name": "Nike",
      "item_count": 12459,
      "logo_url": "https://vinted.com/assets/brands/nike.jpg",
      "is_popular": true
    },
    {
      "id": "12345",
      "name": "Nike SB",
      "item_count": 234,
      "logo_url": null,
      "is_popular": false
    }
  ],
  "from_cache": true
}
```

### Category Tree API

**Endpoint**: `GET /api/categories`

**Parameters:**
- `country` (string): Country code (e.g., "fr")
- `parent_id` (UUID, optional): Parent category (for lazy loading)

**Response:**
```json
{
  "categories": [
    {
      "id": "uuid-1",
      "vinted_id": "1",
      "name": "Women",
      "level": 0,
      "has_children": true,
      "item_count": 50000,
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

### Pre-seeded Brands

**Seed script** (run on first install):
```python
# backend/seeds/popular_brands.py

POPULAR_BRANDS = {
    # Format: "name": "vinted_id"
    "Nike": "53",
    "Adidas": "14",
    "Zara": "12",
    "H&M": "21",
    "Louis Vuitton": "417",
    "Gucci": "89",
    "Prada": "156",
    "Chanel": "67",
    "Hermès": "104",
    "Burberry": "45",
    # ... top 100 brands
}

def seed_brands(db: Session, country_code: str):
    """Seed popular brands for a country"""
    for name, vinted_id in POPULAR_BRANDS.items():
        brand = Brand(
            vinted_id=vinted_id,
            name=name,
            country_code=country_code,
            is_popular=True
        )
        db.merge(brand)  # Insert or update
    db.commit()
```

### Vinted API Integration

**New methods in VintedClient:**

```python
# backend/services/vinted_client.py

class VintedClient:
    def search_brands(self, query: str) -> List[Dict]:
        """Search for brands by name"""
        if not self.session:
            self.initialize_session()
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v2/brands",
                params={"search_text": query} if query else {},
                cookies=self.session.cookies.get_dict(),
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('brands', [])
        except requests.RequestException as e:
            logger.error(f"Brand search failed: {e}")
            return []
    
    def get_category_tree(self) -> List[Dict]:
        """Fetch complete category hierarchy"""
        if not self.session:
            self.initialize_session()
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v2/catalogs",
                cookies=self.session.cookies.get_dict(),
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('catalogs', [])
        except requests.RequestException as e:
            logger.error(f"Category fetch failed: {e}")
            return []
```

### Backend Service Layer

```python
# backend/services/brand_service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Brand
from .vinted_client import VintedClient
import logging

logger = logging.getLogger(__name__)

class BrandService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_brands(
        self,
        query: str,
        country_code: str,
        limit: int = 10
    ) -> tuple[List[Brand], bool]:
        """
        Search for brands by name with caching
        Returns: (brands, from_cache)
        """
        # 1. Try local cache first (fast path)
        cached_brands = self.db.query(Brand).filter(
            Brand.name.ilike(f"%{query}%"),
            Brand.country_code == country_code
        ).limit(limit).all()
        
        if cached_brands:
            logger.info(f"Returning {len(cached_brands)} brands from cache")
            return cached_brands, True
        
        # 2. Fetch from Vinted API (slow path)
        logger.info(f"Fetching brands from Vinted API: {query}")
        try:
            client = VintedClient(country_code)
            client.initialize_session()
            api_brands = client.search_brands(query)
            
            # 3. Cache results
            db_brands = []
            for brand_data in api_brands:
                brand = Brand(
                    vinted_id=str(brand_data['id']),
                    name=brand_data['title'],
                    country_code=country_code,
                    item_count=brand_data.get('item_count', 0),
                    logo_url=brand_data.get('logo_url'),
                    is_popular=False
                )
                self.db.merge(brand)
                db_brands.append(brand)
            
            self.db.commit()
            logger.info(f"Cached {len(db_brands)} brands from API")
            return db_brands, False
            
        except Exception as e:
            logger.error(f"Failed to fetch brands: {e}")
            return [], False
    
    def get_brand_by_id(
        self,
        vinted_id: str,
        country_code: str
    ) -> Optional[Brand]:
        """Get brand by Vinted ID"""
        return self.db.query(Brand).filter(
            Brand.vinted_id == vinted_id,
            Brand.country_code == country_code
        ).first()
```

```python
# backend/services/category_service.py

from typing import List, Dict
from sqlalchemy.orm import Session
from ..models import Category
from .vinted_client import VintedClient
import logging

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_category_tree(
        self,
        country_code: str,
        force_refresh: bool = False
    ) -> List[Dict]:
        """
        Get category tree with caching
        Returns hierarchical structure
        """
        # 1. Check cache (unless force refresh)
        if not force_refresh:
            cached_categories = self.db.query(Category).filter(
                Category.country_code == country_code,
                Category.level == 0  # Root categories
            ).all()
            
            if cached_categories:
                logger.info(f"Returning category tree from cache")
                return self._build_tree(cached_categories)
        
        # 2. Fetch from Vinted API
        logger.info(f"Fetching categories from Vinted API")
        try:
            client = VintedClient(country_code)
            client.initialize_session()
            api_categories = client.get_category_tree()
            
            # 3. Cache in database (recursive)
            self._cache_categories(api_categories, country_code, parent_id=None, level=0)
            self.db.commit()
            
            # 4. Return fresh data
            root_categories = self.db.query(Category).filter(
                Category.country_code == country_code,
                Category.level == 0
            ).all()
            
            return self._build_tree(root_categories)
            
        except Exception as e:
            logger.error(f"Failed to fetch categories: {e}")
            return []
    
    def _cache_categories(
        self,
        categories: List[Dict],
        country_code: str,
        parent_id: Optional[str],
        level: int,
        path_prefix: str = ""
    ):
        """Recursively cache category tree"""
        for cat_data in categories:
            path = f"{path_prefix}/{cat_data['title']}"
            
            category = Category(
                vinted_id=str(cat_data['id']),
                name=cat_data['title'],
                country_code=country_code,
                parent_id=parent_id,
                level=level,
                path=path,
                item_count=cat_data.get('item_count', 0)
            )
            self.db.merge(category)
            self.db.flush()  # Get the ID for children
            
            # Recursively cache children
            if 'catalogs' in cat_data:
                self._cache_categories(
                    cat_data['catalogs'],
                    country_code,
                    category.id,
                    level + 1,
                    path
                )
    
    def _build_tree(self, categories: List[Category]) -> List[Dict]:
        """Convert flat list to hierarchical structure"""
        result = []
        for category in categories:
            node = {
                "id": str(category.id),
                "vinted_id": category.vinted_id,
                "name": category.name,
                "level": category.level,
                "item_count": category.item_count,
                "has_children": bool(category.children),
                "children": self._build_tree(category.children) if category.children else []
            }
            result.append(node)
        return result
```

### API Endpoints

```python
# backend/api/brands.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..services.brand_service import BrandService
from ..schemas import BrandResponse

router = APIRouter(prefix="/api/brands", tags=["brands"])

@router.get("/search", response_model=List[BrandResponse])
def search_brands(
    q: str = Query(..., min_length=1, description="Search query"),
    country: str = Query(..., description="Country code (e.g., 'fr')"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Search for brands by name
    
    - Searches local cache first
    - Falls back to Vinted API if not cached
    - Automatically caches results
    """
    service = BrandService(db)
    brands, from_cache = service.search_brands(q, country, limit)
    
    return [
        BrandResponse(
            id=brand.vinted_id,
            name=brand.name,
            item_count=brand.item_count,
            logo_url=brand.logo_url,
            is_popular=brand.is_popular
        )
        for brand in brands
    ]

@router.get("/popular", response_model=List[BrandResponse])
def get_popular_brands(
    country: str = Query(..., description="Country code"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get pre-seeded popular brands (instant response)"""
    brands = db.query(Brand).filter(
        Brand.country_code == country,
        Brand.is_popular == True
    ).limit(limit).all()
    
    return [
        BrandResponse(
            id=brand.vinted_id,
            name=brand.name,
            item_count=brand.item_count,
            logo_url=brand.logo_url,
            is_popular=brand.is_popular
        )
        for brand in brands
    ]
```

```python
# backend/api/categories.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from ..database import get_db
from ..services.category_service import CategoryService

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("/tree")
def get_category_tree(
    country: str = Query(..., description="Country code"),
    force_refresh: bool = Query(False, description="Force API fetch"),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get complete category hierarchy
    
    - Cached after first fetch
    - Use force_refresh=true to update
    """
    service = CategoryService(db)
    tree = service.get_category_tree(country, force_refresh)
    
    return {
        "country": country,
        "categories": tree
    }

@router.get("/search")
def search_categories(
    q: str = Query(..., min_length=1),
    country: str = Query(...),
    db: Session = Depends(get_db)
):
    """Search categories by name (flat results)"""
    categories = db.query(Category).filter(
        Category.name.ilike(f"%{q}%"),
        Category.country_code == country
    ).limit(20).all()
    
    return {
        "categories": [
            {
                "id": cat.vinted_id,
                "name": cat.name,
                "path": cat.path,
                "item_count": cat.item_count
            }
            for cat in categories
        ]
    }
```

### Frontend Components

**Brand Autocomplete Component:**

```typescript
// frontend/src/components/BrandAutocomplete.tsx

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Command, CommandInput, CommandList, CommandItem } from '@/components/ui/command';
import { api } from '@/lib/api';

interface Brand {
  id: string;
  name: string;
  item_count: number;
  is_popular: boolean;
}

interface Props {
  countryCode: string;
  selectedBrands: Brand[];
  onSelect: (brand: Brand) => void;
  onRemove: (brandId: string) => void;
}

export function BrandAutocomplete({ 
  countryCode, 
  selectedBrands, 
  onSelect, 
  onRemove 
}: Props) {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Fetch brands based on search query
  const { data: brands, isLoading } = useQuery({
    queryKey: ['brands', searchQuery, countryCode],
    queryFn: async () => {
      if (!searchQuery || searchQuery.length < 2) {
        // Show popular brands by default
        const response = await api.get('/api/brands/popular', {
          params: { country: countryCode, limit: 10 }
        });
        return response.data;
      }
      
      const response = await api.get('/api/brands/search', {
        params: { q: searchQuery, country: countryCode }
      });
      return response.data;
    },
    enabled: !!countryCode
  });
  
  return (
    <div className="space-y-2">
      {/* Selected brands */}
      <div className="flex flex-wrap gap-2">
        {selectedBrands.map(brand => (
          <div 
            key={brand.id}
            className="flex items-center gap-2 px-3 py-1 bg-blue-100 rounded-full"
          >
            <span className="text-sm">{brand.name}</span>
            <button
              onClick={() => onRemove(brand.id)}
              className="text-blue-600 hover:text-blue-800"
            >
              ×
            </button>
          </div>
        ))}
      </div>
      
      {/* Search input */}
      <Command className="border rounded-lg">
        <CommandInput
          placeholder="Search brands (e.g., Nike, Adidas)..."
          value={searchQuery}
          onValueChange={setSearchQuery}
        />
        <CommandList>
          {isLoading && (
            <div className="p-4 text-sm text-gray-500">Searching...</div>
          )}
          
          {brands && brands.length === 0 && (
            <div className="p-4 text-sm text-gray-500">No brands found</div>
          )}
          
          {brands?.map((brand: Brand) => (
            <CommandItem
              key={brand.id}
              onSelect={() => onSelect(brand)}
              className="flex items-center justify-between"
            >
              <div>
                <span className="font-medium">{brand.name}</span>
                {brand.is_popular && (
                  <span className="ml-2 text-xs text-gray-500">Popular</span>
                )}
              </div>
              <span className="text-xs text-gray-400">
                {brand.item_count} items
              </span>
            </CommandItem>
          ))}
        </CommandList>
      </Command>
    </div>
  );
}
```

**Category Tree Component:**

```typescript
// frontend/src/components/CategoryTree.tsx

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { api } from '@/lib/api';

interface Category {
  id: string;
  vinted_id: string;
  name: string;
  level: number;
  item_count: number;
  has_children: boolean;
  children?: Category[];
}

interface Props {
  countryCode: string;
  selectedCategory: Category | null;
  onSelect: (category: Category) => void;
}

function CategoryNode({ 
  category, 
  isSelected, 
  onSelect 
}: { 
  category: Category;
  isSelected: boolean;
  onSelect: (cat: Category) => void;
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div>
      <div
        className={`
          flex items-center gap-2 px-3 py-2 rounded cursor-pointer
          hover:bg-gray-100
          ${isSelected ? 'bg-blue-100 font-medium' : ''}
        `}
        onClick={() => onSelect(category)}
      >
        {category.has_children && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="p-1"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
        )}
        
        {!category.has_children && <div className="w-6" />}
        
        <span>{category.name}</span>
        <span className="text-xs text-gray-400 ml-auto">
          ({category.item_count})
        </span>
      </div>
      
      {/* Render children recursively */}
      {isExpanded && category.children && (
        <div className="ml-6 border-l pl-2">
          {category.children.map(child => (
            <CategoryNode
              key={child.id}
              category={child}
              isSelected={isSelected}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function CategoryTree({ countryCode, selectedCategory, onSelect }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ['categories', countryCode],
    queryFn: async () => {
      const response = await api.get('/api/categories/tree', {
        params: { country: countryCode }
      });
      return response.data;
    },
    enabled: !!countryCode
  });
  
  if (isLoading) {
    return <div className="p-4 text-sm text-gray-500">Loading categories...</div>;
  }
  
  return (
    <div className="border rounded-lg p-2 max-h-96 overflow-y-auto">
      {data?.categories.map((category: Category) => (
        <CategoryNode
          key={category.id}
          category={category}
          isSelected={selectedCategory?.id === category.id}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
```

**Alert Form with Brand/Category:**

```typescript
// frontend/src/components/AlertForm.tsx

import { useState } from 'react';
import { BrandAutocomplete } from './BrandAutocomplete';
import { CategoryTree } from './CategoryTree';

export function AlertForm() {
  const [countryCode, setCountryCode] = useState('fr');
  const [selectedBrands, setSelectedBrands] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Prepare alert data
    const alertData = {
      country_code: countryCode,
      search_text: formData.searchText,
      brand_ids: selectedBrands.map(b => b.id).join(','),
      brand_names: selectedBrands.map(b => b.name).join(', '),
      catalog_ids: selectedCategory?.vinted_id || '',
      catalog_names: selectedCategory?.name || '',
      // ... other fields
    };
    
    // Submit to API
    createAlert(alertData);
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Country Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Country
        </label>
        <select
          value={countryCode}
          onChange={(e) => setCountryCode(e.target.value)}
          className="w-full border rounded px-3 py-2"
        >
          <option value="fr">🇫🇷 France</option>
          <option value="ie">🇮🇪 Ireland</option>
          <option value="de">🇩🇪 Germany</option>
          {/* ... other countries */}
        </select>
      </div>
      
      {/* Keyword Search */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Keywords (Optional)
        </label>
        <input
          type="text"
          placeholder="e.g., vintage, XL, red..."
          className="w-full border rounded px-3 py-2"
        />
        <p className="text-xs text-gray-500 mt-1">
          Search within titles and descriptions
        </p>
      </div>
      
      {/* Brand Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Brands (Optional)
        </label>
        <BrandAutocomplete
          countryCode={countryCode}
          selectedBrands={selectedBrands}
          onSelect={(brand) => setSelectedBrands([...selectedBrands, brand])}
          onRemove={(id) => setSelectedBrands(selectedBrands.filter(b => b.id !== id))}
        />
        <p className="text-xs text-gray-500 mt-1">
          Filter by specific brands
        </p>
      </div>
      
      {/* Category Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Category (Optional)
        </label>
        {selectedCategory ? (
          <div className="flex items-center gap-2 mb-2">
            <span className="px-3 py-1 bg-blue-100 rounded">
              {selectedCategory.path}
            </span>
            <button
              onClick={() => setSelectedCategory(null)}
              className="text-blue-600 hover:text-blue-800"
            >
              Clear
            </button>
          </div>
        ) : (
          <CategoryTree
            countryCode={countryCode}
            selectedCategory={selectedCategory}
            onSelect={setSelectedCategory}
          />
        )}
        <p className="text-xs text-gray-500 mt-1">
          Narrow down to specific category
        </p>
      </div>
      
      {/* Price Range */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Min Price (EUR)
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">
            Max Price (EUR)
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            placeholder="100.00"
            className="w-full border rounded px-3 py-2"
          />
        </div>
      </div>
      
      <button
        type="submit"
        className="w-full bg-blue-600 text-white rounded py-2 hover:bg-blue-700"
      >
        Create Alert
      </button>
    </form>
  );
}
```

---

## Feature Specifications

### MVP Features (Phase 1)

**User Management**
- Email/password registration
- JWT authentication
- Password reset (email-based)
- Profile management
- Single-user mode for self-hosted (optional)

**Alert Management**
- Create alert with:
  - Alert name
  - Country selection (dropdown)
  - **Brand search with autocomplete** (NEW)
  - **Category tree navigation** (NEW)
  - Keyword search (optional)
  - Price range (optional)
  - Check interval (5-60 minutes)
- List all user alerts
- Edit existing alerts
- Delete alerts
- Enable/disable alerts (toggle)

**Brand/Category Search** (NEW)
- Autocomplete brand search by name
- Visual category tree navigation
- Popular brands pre-loaded (instant)
- Dynamic brand lookup with caching
- Multi-brand selection
- Display brand/category names (not just IDs)

**Vinted Integration**
- Support for 20+ countries
- Session cookie management per country
- Search API integration
- Item data extraction (title, price, URL, image)
- Brand/category API integration
- Automatic retry on API failures

**Notification System**
- Email notifications (SMTP)
- Slack notifications (webhook URL)
- Telegram notifications (bot token + chat ID)
- Per-alert notification channel selection
- Notification template customization

**Dashboard**
- Alert list with status indicators
- Last check timestamp
- Items found today counter
- Quick enable/disable toggle
- Recent items preview
- **Display brand/category names in alerts** (NEW)

**Item History**
- View previously found items per alert
- Item details (title, price, image, link to Vinted)
- Deduplication system (no repeat notifications)
- Search within history

### Future Features (Post-MVP)

**Phase 2 (Months 4-6)**
- Price drop tracking
- Advanced search filters (size, condition, location)
- Saved search templates
- Bulk alert operations
- Alert scheduling (pause during hours)
- Mobile-responsive improvements
- **Brand/category favorites**
- **Smart brand suggestions based on searches**

**Phase 3 (Months 7-12)**
- Team workspaces (multi-user collaboration)
- Alert sharing (share alert configs)
- Advanced analytics dashboard
- Export alerts/history to CSV
- API access for integrations
- Webhook notifications
- Mobile app (React Native)
- **AI-powered brand recommendations**

---

## Development Roadmap

### Pre-Development (Week 0)

**Repository Setup**
```bash
# Create new repository
mkdir vintedscanner-web
cd vintedscanner-web
git init

# Project structure
mkdir -p backend/{api,models,services,seeds,tests}
mkdir -p frontend/{src,public}
mkdir -p docs
```

**Initial Files**
- README.md (with attribution to original)
- LICENSE (MIT)
- .gitignore (Python + Node)
- docker-compose.yml
- .env.example

**Development Environment**
- Python 3.11+ with virtual environment
- Node.js 18+ with npm
- Docker Desktop
- PostgreSQL (for testing)
- VS Code / PyCharm
- Postman / Insomnia (API testing)

### Phase 1: Backend Foundation (Weeks 1-4)

#### Week 1: Project Setup & Database

**Tasks:**
- [ ] Initialize FastAPI project structure
- [ ] Set up SQLAlchemy models (User, Alert, **Brand, Category**, ItemHistory)
- [ ] Create Alembic migrations
- [ ] Test SQLite connection
- [ ] Test PostgreSQL connection
- [ ] **Create brand seed script with top 100 brands**
- [ ] Write database seeder scripts
- [ ] Set up pytest framework

**Deliverables:**
- Working database with all tables (including Brand and Category)
- Migration scripts
- Brand seed data
- Basic test suite

**Code Example - Brand Model:**
```python
# backend/models/brand.py
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from ..database import Base

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vinted_id = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    country_code = Column(String(10), nullable=False)
    item_count = Column(Integer, default=0)
    logo_url = Column(String(500))
    is_popular = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Week 2: Vinted API Integration + Brand/Category Lookup

**Tasks:**
- [ ] Study original VintedScanner Vinted integration
- [ ] Create VintedClient service class
- [ ] Implement session cookie acquisition per country
- [ ] Implement search API calls
- [ ] **Implement brand search API method**
- [ ] **Implement category tree API method**
- [ ] Add error handling and retries
- [ ] Create unit tests for Vinted client
- [ ] Test with 3-5 different countries

**Deliverables:**
- `VintedClient` service with brand/category methods
- Country configuration module
- Integration tests

**Code Example - Brand Search:**
```python
# backend/services/vinted_client.py

def search_brands(self, query: str = None) -> List[Dict]:
    """Search for brands by name or get all brands"""
    if not self.session:
        self.initialize_session()
    
    params = {}
    if query:
        params['search_text'] = query
    
    try:
        response = self.session.get(
            f"{self.base_url}/api/v2/brands",
            params=params,
            cookies=self.session.cookies.get_dict(),
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        brands = data.get('brands', [])
        logger.info(f"Found {len(brands)} brands for query: {query}")
        return brands
        
    except requests.RequestException as e:
        logger.error(f"Brand search failed: {e}")
        return []

def get_category_tree(self) -> List[Dict]:
    """Fetch complete category hierarchy"""
    if not self.session:
        self.initialize_session()
    
    try:
        response = self.session.get(
            f"{self.base_url}/api/v2/catalogs",
            cookies=self.session.cookies.get_dict(),
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        catalogs = data.get('catalogs', [])
        logger.info(f"Fetched {len(catalogs)} root categories")
        return catalogs
        
    except requests.RequestException as e:
        logger.error(f"Category fetch failed: {e}")
        return []
```

#### Week 3: REST API Endpoints + Brand/Category APIs

**Tasks:**
- [ ] Create authentication endpoints (register, login, refresh)
- [ ] Implement JWT token generation and validation
- [ ] Create alert CRUD endpoints
- [ ] **Create brand search endpoint**
- [ ] **Create category tree endpoint**
- [ ] **Create popular brands endpoint**
- [ ] Add input validation with Pydantic
- [ ] Implement pagination for list endpoints
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Write integration tests

**Deliverables:**
- Complete REST API including brand/category endpoints
- API documentation
- Postman collection

**Code Example - Brand API:**
```python
# backend/api/brands.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..services.brand_service import BrandService
from ..schemas import BrandResponse

router = APIRouter(prefix="/api/brands", tags=["brands"])

@router.get("/search", response_model=List[BrandResponse])
async def search_brands(
    q: str = Query(..., min_length=1, max_length=100),
    country: str = Query(..., regex="^[a-z]{2}(\\.[a-z]{2})?$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Search for brands by name
    
    Uses local cache first, falls back to Vinted API
    """
    try:
        service = BrandService(db)
        brands, from_cache = service.search_brands(q, country, limit)
        
        return [
            BrandResponse(
                id=brand.vinted_id,
                name=brand.name,
                item_count=brand.item_count or 0,
                logo_url=brand.logo_url,
                is_popular=brand.is_popular
            )
            for brand in brands
        ]
    except Exception as e:
        logger.error(f"Brand search failed: {e}")
        raise HTTPException(status_code=500, detail="Brand search failed")

@router.get("/popular", response_model=List[BrandResponse])
async def get_popular_brands(
    country: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get pre-seeded popular brands (instant response)"""
    brands = db.query(Brand).filter(
        Brand.country_code == country,
        Brand.is_popular == True
    ).order_by(Brand.name).limit(limit).all()
    
    return [
        BrandResponse(
            id=brand.vinted_id,
            name=brand.name,
            item_count=brand.item_count or 0,
            logo_url=brand.logo_url,
            is_popular=True
        )
        for brand in brands
    ]

@router.post("/seed")
async def seed_popular_brands(
    country: str = Query(...),
    db: Session = Depends(get_db)
):
    """Seed popular brands for a country (admin endpoint)"""
    from ..seeds.popular_brands import seed_brands
    
    try:
        count = seed_brands(db, country)
        return {"message": f"Seeded {count} popular brands for {country}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Week 4: Scanner Service & Notifications

**Tasks:**
- [ ] Create AlertScanner service
- [ ] Implement APScheduler integration
- [ ] Add item deduplication logic
- [ ] Create notification service (Email, Slack, Telegram)
- [ ] **Update scanner to use brand_ids/catalog_ids from database**
- [ ] Test scanner with real alerts (including brand/category filters)
- [ ] Add comprehensive logging
- [ ] Write unit tests for scanner

**Deliverables:**
- Working scanner service
- Notification service
- Background job system

**Code Example - Scanner with Brand IDs:**
```python
# backend/services/scanner.py

def scan_alert(self, db: Session, alert: Alert):
    """Scan a single alert for new items"""
    logger.info(f"Scanning: {alert.name} (country: {alert.country_code})")
    
    # Initialize Vinted client
    client = VintedClient(alert.country_code)
    
    # Build search parameters from alert
    search_params = {
        'search_text': alert.search_text,
        'brand_ids': alert.brand_ids,      # e.g., "53,14" for Nike, Adidas
        'catalog_ids': alert.catalog_ids,  # e.g., "1193" for Hats
        'price_from': alert.price_min,
        'price_to': alert.price_max,
        'order': alert.order or 'newest_first'
    }
    
    # Log search parameters for debugging
    logger.debug(f"Search params: {search_params}")
    if alert.brand_names:
        logger.debug(f"Searching brands: {alert.brand_names}")
    if alert.catalog_names:
        logger.debug(f"In category: {alert.catalog_names}")
    
    # Search for items
    items = client.search(**search_params)
    
    # ... rest of deduplication and notification logic
```

### Phase 2: Frontend Development (Weeks 5-8)

#### Week 5: Frontend Setup & Authentication

**Tasks:**
- [ ] Initialize React + Vite + TypeScript project
- [ ] Set up TailwindCSS and Shadcn/ui
- [ ] Configure React Router
- [ ] Create layout components
- [ ] Build login page
- [ ] Build registration page
- [ ] Implement JWT token management
- [ ] Create API client with Axios
- [ ] **Install and configure Radix UI Combobox for autocomplete**

**Deliverables:**
- Working authentication flow
- Base layout and routing
- API integration layer

#### Week 6: Alert Management UI + Brand/Category Components

**Tasks:**
- [ ] Create alert list/dashboard page
- [ ] Build alert creation form (basic structure)
- [ ] **Build BrandAutocomplete component**
- [ ] **Build CategoryTree component**
- [ ] **Integrate brand/category components into alert form**
- [ ] Add country selector dropdown
- [ ] Implement alert edit modal
- [ ] Add delete confirmation
- [ ] Create alert detail view
- [ ] Add enable/disable toggle

**Deliverables:**
- Complete alert management interface with brand/category search
- Responsive design
- Working autocomplete

**Code Example - Integration Test:**
```typescript
// frontend/src/components/__tests__/BrandAutocomplete.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrandAutocomplete } from '../BrandAutocomplete';

const queryClient = new QueryClient();

describe('BrandAutocomplete', () => {
  it('shows popular brands on focus', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrandAutocomplete
          countryCode="fr"
          selectedBrands={[]}
          onSelect={jest.fn()}
          onRemove={jest.fn()}
        />
      </QueryClientProvider>
    );
    
    const input = screen.getByPlaceholderText(/search brands/i);
    fireEvent.focus(input);
    
    await waitFor(() => {
      expect(screen.getByText('Nike')).toBeInTheDocument();
      expect(screen.getByText('Adidas')).toBeInTheDocument();
    });
  });
  
  it('searches brands dynamically', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrandAutocomplete
          countryCode="fr"
          selectedBrands={[]}
          onSelect={jest.fn()}
          onRemove={jest.fn()}
        />
      </QueryClientProvider>
    );
    
    const input = screen.getByPlaceholderText(/search brands/i);
    fireEvent.change(input, { target: { value: 'Guc' } });
    
    await waitFor(() => {
      expect(screen.getByText('Gucci')).toBeInTheDocument();
    });
  });
});
```

#### Week 7: Dashboard & Item History

**Tasks:**
- [ ] Build dashboard overview
- [ ] Add statistics cards
- [ ] Create item history table
- [ ] Add search/filter functionality
- [ ] Implement pagination
- [ ] Add item preview modals
- [ ] Create empty states
- [ ] **Display brand/category names in alert cards**

**Deliverables:**
- Dashboard page
- Item history viewer
- Brand/category display in UI

#### Week 8: Settings & Polish

**Tasks:**
- [ ] Build settings page
- [ ] Add notification configuration UI
- [ ] Implement dark mode toggle
- [ ] Add loading states
- [ ] Implement error handling
- [ ] Mobile responsive testing
- [ ] Cross-browser testing
- [ ] Performance optimization
- [ ] **Test brand/category autocomplete across browsers**
- [ ] **Optimize brand search debouncing**

**Deliverables:**
- Polished, production-ready frontend
- Smooth autocomplete experience

### Phase 3: Docker & Documentation (Weeks 9-10)

#### Week 9: Docker Packaging

**Tasks:**
- [ ] Create multi-stage Dockerfile
- [ ] Write docker-compose.yml (self-hosted)
- [ ] Write docker-compose.cloud.yml
- [ ] Add health check endpoints
- [ ] Test SQLite configuration
- [ ] Test PostgreSQL configuration
- [ ] **Ensure brand seeds run on container startup**
- [ ] Create .env.example with all variables
- [ ] Add Docker build automation

**Deliverables:**
- Production-ready Docker setup
- Both self-hosted and cloud configs
- Auto-seeding of popular brands

**Startup Script:**
```bash
#!/bin/bash
# backend/startup.sh

# Run migrations
alembic upgrade head

# Seed popular brands (idempotent)
python -m backend.seeds.seed_popular_brands

# Start application
uvicorn backend.main:app --host 0.0.0.0 --port 3000
```

#### Week 10: Documentation

**Tasks:**
- [ ] Write comprehensive README
- [ ] Create self-hosting guide
- [ ] Document all environment variables
- [ ] Write API documentation
- [ ] Create troubleshooting guide
- [ ] **Document brand/category search feature**
- [ ] **Add screenshots of autocomplete UI**
- [ ] Add architecture diagrams
- [ ] Write contributing guidelines
- [ ] Create example configurations

**Deliverables:**
- Complete documentation
- User guides
- Developer documentation
- Feature showcase

**README Section:**
```markdown
## Key Features

### 🎯 Intelligent Brand & Category Search

Unlike the original CLI tool that requires finding numeric IDs manually, VintedScanner Web provides:

- **Autocomplete Brand Search**: Just type "Nike" - no need to find ID "53"
- **Visual Category Tree**: Browse categories like a file explorer
- **Smart Caching**: Popular brands load instantly
- **Multi-brand Selection**: Search for multiple brands at once

[Screenshot of brand autocomplete]
[Screenshot of category tree]
```

### Phase 4: Testing & Launch (Weeks 11-13)

#### Week 11: Private Beta

**Tasks:**
- [ ] Deploy to test environment
- [ ] Invite 5-10 beta testers
- [ ] Set up error monitoring (Sentry)
- [ ] Monitor logs and performance
- [ ] **Gather feedback on brand/category UX**
- [ ] Gather structured feedback
- [ ] Fix critical bugs
- [ ] Optimize database queries
- [ ] **Test brand cache performance under load**

**Deliverables:**
- Stable beta version
- Bug fixes
- Performance improvements
- Brand/category UX validation

#### Week 12: Public Beta

**Tasks:**
- [ ] Make GitHub repository public
- [ ] Post to /r/selfhosted
- [ ] Post to Hacker News (Show HN)
- [ ] **Highlight brand/category feature in launch post**
- [ ] Create demo video/screenshots
- [ ] Set up GitHub issues templates
- [ ] Monitor community feedback
- [ ] Respond to issues quickly
- [ ] Iterate on UX improvements

**Deliverables:**
- Public release
- Community engagement
- Issue tracking

**Launch Post (Example):**
```markdown
Show HN: VintedScanner Web - Find deals on Vinted with intelligent search

Unlike existing tools that require you to manually find brand/category IDs,
VintedScanner Web lets you just type "Nike" or browse categories visually.

Features:
- Autocomplete brand search (no more hunting for IDs!)
- Visual category tree navigation
- 20+ country support
- Self-hosted or use our cloud version

Try it: [link]
GitHub: [link]
```

#### Week 13: v1.0 Launch

**Tasks:**
- [ ] Final bug fixes
- [ ] Performance tuning
- [ ] Security audit
- [ ] Create v1.0 release notes
- [ ] Tag v1.0 release on GitHub
- [ ] Announce on social media
- [ ] Update documentation
- [ ] Plan v1.1 features
- [ ] **Collect analytics on brand/category usage**

**Deliverables:**
- Stable v1.0 release
- Public announcement
- Usage metrics

---

## Project Structure

```
vintedscanner-web/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── alerts.py        # Alert CRUD endpoints
│   │   ├── brands.py        # Brand search endpoints (NEW)
│   │   ├── categories.py    # Category endpoints (NEW)
│   │   ├── items.py         # Item history endpoints
│   │   └── users.py         # User management endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── alert.py         # Alert model (with brand/category fields)
│   │   ├── brand.py         # Brand cache model (NEW)
│   │   ├── category.py      # Category cache model (NEW)
│   │   └── item_history.py  # ItemHistory model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vinted_client.py # Vinted API integration (with brand/category)
│   │   ├── brand_service.py # Brand caching service (NEW)
│   │   ├── category_service.py # Category service (NEW)
│   │   ├── scanner.py       # Alert scanner service
│   │   └── notifications.py # Notification service
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── alert.py         # Pydantic schemas
│   │   ├── brand.py         # Brand schemas (NEW)
│   │   ├── category.py      # Category schemas (NEW)
│   │   └── user.py
│   ├── seeds/
│   │   ├── __init__.py
│   │   ├── popular_brands.py # Brand seed data (NEW)
│   │   └── seed_runner.py    # Seed orchestrator (NEW)
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_vinted.py
│   │   ├── test_brands.py    # Brand tests (NEW)
│   │   ├── test_categories.py # Category tests (NEW)
│   │   └── test_scanner.py
│   ├── alembic/             # Database migrations
│   ├── database.py          # Database setup
│   ├── config.py            # Configuration
│   ├── main.py              # FastAPI app entry
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          # Shadcn/ui components
│   │   │   ├── AlertCard.tsx
│   │   │   ├── AlertForm.tsx
│   │   │   ├── BrandAutocomplete.tsx # (NEW)
│   │   │   ├── CategoryTree.tsx      # (NEW)
│   │   │   └── Layout.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Alerts.tsx
│   │   │   └── Settings.tsx
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   └── auth.ts      # Auth utilities
│   │   ├── hooks/
│   │   │   ├── useAlerts.ts    # React Query hooks
│   │   │   ├── useBrands.ts    # Brand hooks (NEW)
│   │   │   └── useCategories.ts # Category hooks (NEW)
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── BRAND_CATEGORY_GUIDE.md # How brand/category works (NEW)
│   └── CONTRIBUTING.md
│
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Self-hosted setup
├── docker-compose.cloud.yml # Cloud deployment
├── startup.sh               # Container startup script (NEW)
├── .env.example
├── .gitignore
├── README.md
└── LICENSE                  # MIT License
```

---

## Environment Variables Reference

### Required Variables

```bash
# Application
NODE_ENV=production
DEPLOYMENT_MODE=self-hosted  # or 'cloud'

# Database
DATABASE_URL=sqlite:///data/vinted.db  # or postgresql://...

# Authentication
JWT_SECRET=your-secret-key-here  # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Notifications (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=VintedScanner <noreply@vintedscanner.com>

# Slack Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Telegram Notifications (Optional)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Brand/Category Cache (NEW)
BRAND_CACHE_TTL_DAYS=30  # How long to cache brand lookups
SEED_POPULAR_BRANDS_ON_STARTUP=true  # Auto-seed on first run
```

### Optional Variables (Cloud)

```bash
# Feature Flags
ENABLE_REGISTRATION=true  # Set false for single-user mode
ENABLE_TEAMS=false  # Future feature

# Monitoring
SENTRY_DSN=https://...  # Error tracking

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Brand/Category Settings
VINTED_API_TIMEOUT=30  # Seconds
MAX_BRAND_SEARCH_RESULTS=50
CATEGORY_CACHE_REFRESH_DAYS=7  # Refresh category tree weekly
```

---

## Success Metrics

### Technical Metrics

**Performance**
- API response time p95: <200ms
- Brand search response: <100ms (cached), <500ms (API)
- Category tree load: <300ms
- Alert scan time: <30s per alert
- Database query time: <100ms
- Frontend initial load: <2s

**Caching Effectiveness**
- Brand cache hit rate: >80%
- Category cache hit rate: >95%
- Average brands per user: 2-3
- Popular brand usage: >60% of searches

**Reliability**
- Uptime: >99% (self-hosted depends on user)
- Error rate: <1%
- Failed notifications: <2%
- Scanner success rate: >95%
- Brand API failure graceful handling: 100%

**Scalability**
- Support 1,000 active alerts
- Support 100 concurrent users (cloud)
- 10,000 items checked per hour
- Database size: <1GB per 10k alerts
- Brand cache: <100MB per country

### Project Metrics

**Community**
- GitHub stars: 100 (Month 3), 500 (Year 1)
- Contributors: 5 (Year 1)
- Issues resolved: >80% within 7 days
- Documentation completeness: 100%

**Adoption**
- Self-hosted installations: 100 (Month 3)
- Active users: 50 (Month 3)
- Average alerts per user: 3-5
- Retention: Users check dashboard weekly
- Brand search usage: >70% of alerts use brands
- Category usage: >50% of alerts use categories

**User Satisfaction**
- Positive feedback on brand/category UX: >90%
- Time to create alert: <2 minutes (vs 10+ with original)
- Feature requests for brand/category: Should be minimal (already solved)

---

## Risk Management

### Technical Risks

**R1: Vinted API Changes**
- **Impact**: High - Could break all functionality
- **Probability**: Medium
- **Mitigation**:
  - Abstract Vinted API behind service layer
  - Automated tests detect API changes
  - Community can help with workarounds
  - Fallback to web scraping if needed
  - **Brand/category IDs may change** - handle gracefully

**R2: Brand/Category API Limitations**
- **Impact**: Medium - Could affect search quality
- **Probability**: Low
- **Mitigation**:
  - Cache aggressively (reduce API calls)
  - Pre-seed popular brands
  - Graceful fallback to text search only
  - Regular updates to seed data

**R3: Rate Limiting by Vinted**
- **Impact**: High - Could block scanning
- **Probability**: Medium
- **Mitigation**:
  - Respectful rate limiting (30s between requests)
  - Rotate user agents
  - Support for proxy configuration
  - Clear terms of service about acceptable use
  - **Separate rate limits for search vs brand/category APIs**

**R4: Database Migration Issues**
- **Impact**: Medium - Could cause data loss
- **Probability**: Low
- **Mitigation**:
  - Test migrations on both SQLite and PostgreSQL
  - Automated backups before migrations
  - Rollback procedures documented
  - Use Alembic for version control
  - **Brand/category cache is expendable** - can re-fetch

**R5: Brand Cache Stale Data**
- **Impact**: Low - Slightly outdated brand info
- **Probability**: Medium
- **Mitigation**:
  - TTL-based cache invalidation
  - Manual refresh endpoint for admins
  - Users can still search for new brands
  - Item counts may be approximate (acceptable)

### Project Risks

**R6: Low Community Adoption**
- **Impact**: Medium - Less feedback, slower improvement
- **Probability**: Low (brand search is compelling feature)
- **Mitigation**:
  - Clear value proposition (no more ID hunting!)
  - Good documentation
  - Active in relevant communities
  - Responsive to issues
  - **Demo video showcasing autocomplete**

**R7: Maintenance Burden**
- **Impact**: Medium - Time sink
- **Probability**: Medium
- **Mitigation**:
  - Comprehensive automated tests
  - Clear contributing guidelines
  - Encourage community contributions
  - Prioritize bug fixes over features
  - **Brand seeds need quarterly updates**

**R8: Legal Issues (Scraping/ToS)**
- **Impact**: High - Could require shutdown
- **Probability**: Low
- **Mitigation**:
  - Only access public data
  - Respect robots.txt
  - Review Vinted ToS
  - Clear disclaimers for users
  - Consult lawyer if needed
  - **Brand/category data is public** - lower risk

---

## Next Steps

### This Week

1. **Create GitHub Repository**
   ```bash
   mkdir vintedscanner-web
   cd vintedscanner-web
   git init
   
   # Create structure
   mkdir -p backend/{api,models,services,seeds,tests}
   mkdir -p frontend/src
   mkdir docs
   
   # Initial files
   touch README.md LICENSE .gitignore
   touch backend/main.py
   touch frontend/package.json
   touch backend/seeds/popular_brands.py
   ```

2. **Write README with Attribution**
   ```markdown
   ## Acknowledgments
   
   This project was inspired by [VintedScanner](https://github.com/drego85/VintedScanner) 
   by Andrea Draghetti. While this is a complete rewrite with a web-based architecture, 
   we studied the original for Vinted API integration patterns.
   
   ## Key Improvements Over Original
   
   - **Web-based interface** (no command line)
   - **Intelligent brand search** - Just type "Nike" instead of finding ID "53"
   - **Visual category tree** - Browse like a file explorer
   - Multi-user support
   - Real-time dashboard
   ```

3. **Set Up Development Environment**
   - Python 3.11 virtual environment
   - Node.js 18+ installed
   - Docker Desktop running
   - PostgreSQL for testing

4. **Start Backend Development**
   - Initialize FastAPI project
   - Set up SQLAlchemy models (including Brand/Category)
   - Create first database migration
   - **Create popular brands seed data file**

5. **Research Brand IDs**
   - Browse Vinted websites in different countries
   - Compile list of top 50-100 brands with IDs
   - Document the ID discovery process
   - Test brand search API manually

### Month 1 Milestones

- [ ] Working backend API with authentication
- [ ] Vinted API integration for 3+ countries
- [ ] **Brand search API working with cache**
- [ ] **Category tree API working**
- [ ] **Popular brands seeded for 3 countries**
- [ ] Alert CRUD operations
- [ ] Scanner service running
- [ ] Email notifications working
- [ ] 50+ passing tests

### Month 2 Milestones

- [ ] Complete frontend with polish
- [ ] **BrandAutocomplete component working**
- [ ] **CategoryTree component working**
- [ ] **Alert form integrated with brand/category**
- [ ] Docker packaging complete
- [ ] Documentation written
- [ ] Private beta with 10 users
- [ ] Landing page for cloud service

### Month 3 Milestones

- [ ] Public beta launch
- [ ] Cloud service deployed to Railway
- [ ] Stripe integration complete
- [ ] Product Hunt launch
- [ ] First 5 paying customers
- [ ] **Analytics showing 70%+ brand search usage**
- [ ] **User testimonials about improved UX**

---

## Appendix

### Popular Brands Seed Data (Sample)

```python
# backend/seeds/popular_brands.py

# Top 100 brands across fashion categories
# Format: {brand_name: vinted_id}
# IDs discovered by inspecting Vinted search URLs

POPULAR_BRANDS = {
    # Sportswear
    "Nike": "53",
    "Adidas": "14",
    "Puma": "167",
    "Under Armour": "289",
    "Reebok": "178",
    "New Balance": "145",
    
    # Fast Fashion
    "Zara": "12",
    "H&M": "21",
    "Mango": "98",
    "Forever 21": "87",
    "Primark": "234",
    "Uniqlo": "276",
    
    # Luxury
    "Louis Vuitton": "417",
    "Gucci": "89",
    "Prada": "156",
    "Chanel": "67",
    "Hermès": "104",
    "Burberry": "45",
    "Dior": "78",
    "Fendi": "82",
    "Givenchy": "91",
    "Saint Laurent": "201",
    
    # Mid-range
    "Michael Kors": "132",
    "Coach": "69",
    "Kate Spade": "114",
    "Tommy Hilfiger": "254",
    "Calvin Klein": "58",
    "Ralph Lauren": "176",
    
    # Streetwear
    "Supreme": "234",
    "Off-White": "189",
    "Palace": "198",
    "Stüssy": "243",
    
    # ... add 60+ more brands
}

def seed_brands(db: Session, country_code: str) -> int:
    """
    Seed popular brands for a country
    Returns: number of brands seeded
    """
    count = 0
    for name, vinted_id in POPULAR_BRANDS.items():
        try:
            brand = Brand(
                vinted_id=vinted_id,
                name=name,
                country_code=country_code,
                is_popular=True,
                updated_at=datetime.utcnow()
            )
            db.merge(brand)  # Insert or update if exists
            count += 1
        except Exception as e:
            logger.error(f"Failed to seed brand {name}: {e}")
            continue
    
    db.commit()
    logger.info(f"Seeded {count} popular brands for {country_code}")
    return count
```

### Category IDs (Common Examples)

```python
# Common category IDs (discovered by inspection)
# These vary slightly by country but generally consistent

COMMON_CATEGORIES = {
    "Women": {
        "id": "1",
        "children": {
            "Accessories": "1920",
            "Bags": "18",
            "Shoes": "16",
            "Clothing": "1193",
            "Hats": "1193",
            "Jewelry": "22",
        }
    },
    "Men": {
        "id": "5",
        "children": {
            "Accessories": "1924",
            "Bags": "23",
            "Shoes": "20",
            "Clothing": "1197",
        }
    },
    "Kids": {
        "id": "3",
        "children": {
            "Girls": "1210",
            "Boys": "1214",
            "Baby": "1218",
        }
    }
}
```

### Useful Resources

**Technical Documentation**
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- React Query: https://tanstack.com/query/
- Shadcn/ui: https://ui.shadcn.com/
- Radix UI Combobox: https://www.radix-ui.com/primitives/docs/components/combobox

**Vinted Integration**
- Original VintedScanner: https://github.com/drego85/VintedScanner
- Vinted API wrappers: Search GitHub for "vinted-api"

**Deployment**
- Railway Docs: https://docs.railway.app/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/

### Contact & Feedback

**Project Maintainer**: Vincent (Bright Reaction, Ireland)

**Feedback Channels**:
- GitHub Issues: Technical bugs and feature requests
- Email: support@vintedscanner.com (when launched)
- Community: Reddit /r/vintedscanner

---

**Document Version**: 2.0 (Technical + Brand/Category Feature)  
**Last Updated**: December 2, 2025  
**Author**: Vincent  
**Project**: VintedScanner Web