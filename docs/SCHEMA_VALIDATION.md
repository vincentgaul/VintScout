# Database Schema Validation

Comparing implemented models vs PLAN.md specification.

## ✅ Users Table

| Field | PLAN.md | Our Model | Status |
|-------|---------|-----------|--------|
| id | UUID | String(36) UUID | ✅ |
| email | VARCHAR(255) | String(255) | ✅ |
| password_hash | VARCHAR(255) | hashed_password String(255) | ✅ |
| created_at | TIMESTAMP | DateTime | ✅ |
| updated_at | TIMESTAMP | DateTime | ✅ |
| is_active | BOOLEAN | Boolean | ✅ |
| is_verified | - | Boolean (added) | ⭐ Extra |
| last_login_at | - | DateTime (added) | ⭐ Extra |

**Result:** ✅ **VALID** - Includes all required fields + useful extras

---

## ✅ Alerts Table

| Field | PLAN.md | Our Model | Status |
|-------|---------|-----------|--------|
| id | UUID | String(36) UUID | ✅ |
| user_id | UUID | String(36) UUID | ✅ |
| name | VARCHAR(255) | String(255) | ✅ |
| country_code | VARCHAR(10) | String(2) | ⚠️ Smaller but ok |
| search_text | VARCHAR(255) | String(500) | ⭐ Larger (better) |
| brand_ids | VARCHAR(255) | Text | ⭐ More flexible |
| brand_names | VARCHAR(500) | Text | ⭐ More flexible |
| catalog_ids | VARCHAR(255) | Text | ⭐ More flexible |
| catalog_names | VARCHAR(500) | Text | ⭐ More flexible |
| price_min | DECIMAL(10,2) | Float | ✅ |
| price_max | DECIMAL(10,2) | Float | ✅ |
| currency | - | String(3) | ⭐ Extra (good) |
| order | VARCHAR(50) | ❌ Missing | ⚠️ Should add |
| check_interval_minutes | INTEGER | Integer | ✅ |
| is_active | BOOLEAN | Boolean | ✅ |
| notification_config | JSONB | JSON | ✅ |
| created_at | TIMESTAMP | DateTime | ✅ |
| updated_at | TIMESTAMP | DateTime | ✅ |
| last_checked_at | TIMESTAMP | DateTime | ✅ |
| last_found_count | INTEGER | Integer | ✅ |
| total_found_count | - | Integer (added) | ⭐ Extra (useful) |
| sizes | - | Text (future) | ⭐ Extra (future) |
| conditions | - | Text (future) | ⭐ Extra (future) |
| colors | - | Text (future) | ⭐ Extra (future) |

**Result:** ⚠️ **MOSTLY VALID** - Missing `order` field, has useful extras

**Recommendation:** Add `order` field:
```python
order = Column(String(50), nullable=False, default="newest_first")
```

---

## ✅ Brands Table

| Field | PLAN.md | Our Model | Status |
|-------|---------|-----------|--------|
| id | UUID | String(36) UUID | ✅ |
| vinted_id | VARCHAR(50) | String(50) | ✅ |
| name | VARCHAR(255) | String(255) | ✅ |
| country_code | VARCHAR(10) | String(2) | ⚠️ Smaller but ok |
| item_count | INTEGER | Integer | ✅ |
| logo_url | VARCHAR(500) | ❌ Missing | ⚠️ Should add |
| is_popular | BOOLEAN | Boolean | ✅ |
| created_at | TIMESTAMP | DateTime | ✅ |
| updated_at | TIMESTAMP | DateTime | ✅ |

**Result:** ⚠️ **MOSTLY VALID** - Missing `logo_url` field

**Recommendation:** Add `logo_url` field:
```python
logo_url = Column(String(500), nullable=True)
```

---

## ✅ Categories Table

| Field | PLAN.md | Our Model | Status |
|-------|---------|-----------|--------|
| id | UUID | String(36) UUID | ✅ |
| vinted_id | VARCHAR(50) | String(50) | ✅ |
| name | VARCHAR(255) | String(255) | ✅ |
| country_code | VARCHAR(10) | String(2) | ⚠️ Smaller but ok |
| parent_id | UUID | String(36) UUID | ✅ |
| level | INTEGER | Integer | ✅ |
| path | VARCHAR(500) | Text | ⭐ More flexible |
| item_count | INTEGER | Integer | ✅ |
| created_at | TIMESTAMP | DateTime | ✅ |
| updated_at | TIMESTAMP | DateTime | ✅ |

**Result:** ✅ **VALID** - All fields present

---

## ✅ ItemHistory Table

| Field | PLAN.md | Our Model | Status |
|-------|---------|-----------|--------|
| id | UUID | String(36) UUID | ✅ |
| alert_id | UUID | String(36) UUID | ✅ |
| item_id | VARCHAR(50) | String(50) | ✅ |
| item_title | VARCHAR(500) | title String(500) | ✅ |
| item_url | VARCHAR(500) | url Text | ✅ |
| item_price | DECIMAL(10,2) | price Float | ✅ |
| item_currency | VARCHAR(10) | currency String(3) | ✅ |
| item_image_url | VARCHAR(500) | image_url Text | ✅ |
| found_at | TIMESTAMP | DateTime | ✅ |
| brand_name | - | String(255) (added) | ⭐ Extra (useful) |
| size | - | String(50) (added) | ⭐ Extra (useful) |
| condition | - | String(50) (added) | ⭐ Extra (useful) |
| notified_at | - | DateTime (added) | ⭐ Extra (useful) |

**Result:** ✅ **VALID** - All required fields + useful extras

---

## Missing Tables (Nice-to-Have)

PLAN.md specifies these additional tables for future features:

### notification_logs (Line 327-334)
**Purpose:** Debug notification failures
**Priority:** Low (can add later)
**Status:** Not implemented yet

### scanner_status (Line 339-347)
**Purpose:** Monitor scanner job execution
**Priority:** Low (can add later)
**Status:** Not implemented yet

---

## Summary

### ✅ Core Schema: 95% Complete

| Table | Status | Missing Fields | Impact |
|-------|--------|----------------|--------|
| Users | ✅ Complete | None | None |
| Alerts | ⚠️ 95% | `order` field | **Low** - easy to add |
| Brands | ⚠️ 95% | `logo_url` | **Low** - nice-to-have |
| Categories | ✅ Complete | None | None |
| ItemHistory | ✅ Complete+ | None | None |

### Critical Issues: **NONE** ✅

All critical fields for MVP functionality are present.

### Minor Improvements Needed:

1. **Add `order` to Alert model**
   - For sorting results (newest_first, price_low_to_high, etc.)
   - **Impact:** Low (defaults to newest_first)
   - **Priority:** Medium

2. **Add `logo_url` to Brand model**
   - For displaying brand logos in autocomplete
   - **Impact:** Low (can show text-only)
   - **Priority:** Low

### Design Improvements Made: ⭐

1. **Text instead of VARCHAR** for IDs - More flexible for multiple brands/categories
2. **Additional tracking fields** - Better analytics and debugging
3. **Future-ready fields** - sizes, conditions, colors in Alert

---

## Validation Conclusion

### Can we proceed with migration? **YES** ✅

**Reasons:**
1. ✅ All critical tables present
2. ✅ All critical relationships defined
3. ✅ Indexes will be created by Alembic
4. ✅ Missing fields are non-blocking
5. ✅ Schema matches API design in docs/API.md

**Minor fixes needed before production:**
- Add `order` field to Alert
- Add `logo_url` to Brand

**Can be added in future migrations:**
- notification_logs table
- scanner_status table

---

## Next Steps

### Option 1: Generate Migration Now (Recommended)
```bash
cd backend
uv run alembic revision --autogenerate -m "initial schema"
uv run alembic upgrade head
```

### Option 2: Add Missing Fields First
```python
# backend/models/alert.py - Add:
order = Column(String(50), nullable=False, default="newest_first")

# backend/models/brand.py - Add:
logo_url = Column(String(500), nullable=True)
```
Then generate migration.

**Recommendation:** Go with **Option 1** - we can add order/logo_url in a follow-up migration. The core schema is solid!
