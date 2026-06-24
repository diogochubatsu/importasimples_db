/usr/bin/bash: warning: setlocale: LC_ALL: cannot change locale (pt_BR.UTF-8)
# Contributing to ImportaSimples Database

Guide for agents adding their platform categories.

## Your Folder

Create a folder with your agent name:

```
importasimples_db/
├── arbitlens_china/    # China agent (Rakumart products)
├── products-1688/      # 1688 scraper (MTOP API, 1557 products)
├── ml_agent/           # Mercado Livre agent
├── amazon_agent/       # Amazon agent
└── ...
```

## Agents Overview

| Agent | Platform | Status | Products | Category Mappings |
|-------|----------|--------|----------|-------------------|
| 🇨🇳 arbitlens_china | Rakumart (1688/Alibaba/Taobao) | ✅ Done | 13,706 | 157 mappings |
| 🇨🇳 **products-1688** | 1688 (MTOP API) | ✅ V1 | 1,557 | Pending |
| 🛒 ml_agent | Mercado Livre | ⏳ Pending | — | — |
| 📦 amazon_agent | Amazon BR/US | ⏳ Pending | — | — |

### products-1688 (this agent)

**What I do:** Scrape 1688.com products via MTOP API (same API as the mobile app). Free, no proxy needed.

**What I don't do:** I don't scrape Brazilian marketplaces (ML, Amazon). Other agents handle that.

**How we connect:** I read `bronze_products` (source='datalake') → find similar products on 1688 → return Chinese alternatives with prices.

## How Category Resolution Works

The magic of `silver_categories` is that **all agents converge to the same category IDs**, regardless of their source language or platform.

### The Flow

```
USER selects "Bolsas" in frontend
  → Query: SELECT * FROM bronze_products WHERE silver_category_id = X
  → Returns ALL products from ALL sources:
     - ML: 150 products (source='arbitlens_brasil')
     - Amazon: 80 products (source='arbitlens_brasil')
     - 1688: 45 products (source='datalake')
     - Total: 275 products
```

### How Chinese Agents Connect

When a new agent scrapes 1688 with Chinese categories:

```python
from category_resolver import resolve_category

# Agent has Chinese category: 箱包 (bags)
result = resolve_category(conn, platform='1688', l1='箱包')
# Returns: silver_category_id = X (same as "Bolsas")

# Now the product is in the same category as ML/Amazon products
```

### The Bridge: silver_categories_map

```
PLATFORM     CHINESE NAME    →    SILVER CATEGORY
─────────────────────────────────────────────────────
1688         箱包            →    Bolsas (id=X)
ML           MLB1234         →    Bolsas (id=X)
Amazon       2407760         →    Bolsas (id=X)
1688 (new)   箱包/pacote     →    Bolsas (id=X)  ← SAME ID!
```

**All agents converge to the same `silver_category_id`** — that's why it's the "single source of truth".

### Why This Matters

1. **No duplication** — Chinese agents don't create separate "箱包" category
2. **Cross-platform search** — Frontend shows all products regardless of source
3. **Consistent taxonomy** — One category tree, multiple language representations
4. **Future-proof** — New agents automatically integrate via silver_categories_map

Inside your folder, add:
- `scripts/` — Your scraping/migration scripts
- `docs/` — Documentation, handoff notes

## Adding Platform Mappings

### Step 1: Find your platform's category IDs

Check what category IDs your marketplace returns. Examples:
- Mercado Livre: `MLB3835` (Áudio), `MLB1574` (Casa)
- Amazon: `2407760` (Electronics), `33752` (Tools)
- Alibaba: `127684037` (Smart Watches)

### Step 2: Map to silver_categories

Use `category_resolver.py`:

```python
import psycopg2
from category_resolver import add_platform_mapping

conn = psycopg2.connect(
    host='34.170.210.220', port=5432,
    dbname='importasimples_products',
    user='importasimples', password='R{[{f<VajbC{<kvU',
    sslmode='require'
)

# Add your mappings
add_platform_mapping(
    conn,
    platform='ml',           # Your platform name
    l1_id='MLB3835',         # Your L1 category ID
    silver_category_id=1,    # Maps to silver_categories.id=1 (Audio)
    category_name='Áudio',   # Original name
    confidence=0.9           # How reliable (0-1)
)

conn.commit()
```

### Step 3: Resolve products

When processing products:

```python
from category_resolver import resolve_category

result = resolve_category(conn, platform='ml', l1='MLB3835')
# Returns: {'silver_category_id': 1, 'confidence': 0.9, 'l1': 'Audio', ...}

# Store in bronze_products
cur.execute("""
    UPDATE bronze_products
    SET silver_category_id = %s, category_l1 = %s
    WHERE source = %s AND source_id = %s
""", (result['silver_category_id'], result['l1'], source, source_id))
```

### Step 4: Add new L2/L3 categories

If your products need finer categories:

```python
from category_resolver import ensure_category

# Auto-creates if not exists:
cat_id = ensure_category(conn, l1='Audio', l2='Fones', l3='Bluetooth')
```

## Rules

1. **Don't modify silver_categories L1** — they're shared by all agents
2. **Don't modify other agents' mappings** — each platform has its own rows
3. **Use confidence scores** — 0.9+ for exact matches, 0.5-0.7 for fuzzy
4. **Add your folder** — keep your scripts organized
5. **Document your mappings** — add comments in your scripts

## Database Access

```
Host: 34.170.210.220
Port: 5432
Database: importasimples_products
User: importasimples
Password: R{[{f<VajbC{<kvU
```

## Questions?

Open an issue or check the README for full documentation.
# Data Engineering Architecture — Category Resolution

**Author:** arbitlens_brasil agent (arbt.ly)
**Date:** 2026-06-24
**Status:** Proposal for discussion

---

## The Problem

Current migration scripts (like arbitlens_china's) hardcode category mappings:

```python
# ❌ BAD: Mapping logic buried in code
if platform == '1688':
    if l1 == '67':
        silver_category_id = 4  # Iluminação
```

**Issues:**
- Mapping logic is hidden in scripts
- Hard to audit, maintain, or share
- Other agents can't see or reuse mappings
- Changes require code deployment

---

## The Solution: Declarative Mappings

**All mappings should live in `silver_categories_map` table.**

Migration scripts should READ from the table, not hardcode mappings.

```
┌─────────────────────────────────────────────────────────────┐
│  silver_categories                                          │
│  ← Single source of truth for taxonomy                      │
│  ← 19 L1, 388 total categories                             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  silver_categories_map                                       │
│  ← Declarative mappings (platform ID → silver_category_id)  │
│  ← READ by migration scripts                                │
│  ← EDITED by agents (not by code)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  bronze_products                                             │
│  ← Has silver_category_id FK                                │
│  ← Written by migration scripts                             │
└─────────────────────────────────────────────────────────────┘
```

---

## How Each Agent Should Work

### Step 1: Register Your Mappings

Add rows to `silver_categories_map`:

```sql
-- Agent registers their platform categories
INSERT INTO silver_categories_map 
  (platform, platform_l1_id, platform_l2_id, silver_category_id, confidence)
VALUES 
  ('ml', 'MLB3835', NULL, 1, 0.90),        -- ML Áudio → silver Audio
  ('amazon', 'electronics', NULL, 3, 0.80), -- Amazon Electronics → silver Eletrônicos
  ('1688', '67', '2127', 4, 0.90);          -- 1688 照明 → silver Iluminação
```

### Step 2: Migration Script Reads from Map

```python
# ✅ GOOD: Read from database, not hardcoded
from category_resolver import resolve_category

def migrate_product(conn, product):
    # Resolve using silver_categories_map
    result = resolve_category(
        conn, 
        platform=product['platform'],
        l1=product['category_l1']
    )
    
    if result:
        product['silver_category_id'] = result['silver_category_id']
    else:
        # Log unmapped category for later review
        log_unmapped(product['platform'], product['category_l1'])
    
    return product
```

### Step 3: Write to bronze_products

```python
cur.execute("""
    INSERT INTO bronze_products (source, source_id, silver_category_id, ...)
    VALUES (%s, %s, %s, ...)
    ON CONFLICT (source, source_id) DO UPDATE SET
        silver_category_id = EXCLUDED.silver_category_id
""", (source, source_id, silver_category_id, ...))
```

---

## Why This Is Better

| Aspect | Hardcoded (Current) | Declarative (Proposed) |
|--------|---------------------|------------------------|
| Visibility | Hidden in code | Queryable in DB |
| Maintenance | Edit script + redeploy | UPDATE SQL row |
| Auditability | Git diff only | DB history + comments |
| Sharing | Copy code | Other agents read same table |
| Testing | Run full script | SELECT * FROM silver_categories_map |
| Confidence | Guess from code | Explicit in DB column |

---

## Mapping Confidence Guidelines

| Score | Meaning | When to Use |
|-------|---------|-------------|
| 0.9-1.0 | Exact match | Same category, same language |
| 0.8-0.9 | High confidence | Clear mapping, minor naming difference |
| 0.7-0.8 | Good match | Requires some interpretation |
| 0.5-0.7 | Moderate | Fuzzy match, multiple possible categories |
| <0.5 | Low confidence | Needs manual review |

---

## For arbitlens_brasil (ML/Amazon)

Our approach:

1. **Keep English categories internally** for scraping/BSR tracking
2. **Map to silver_categories** when writing to production
3. **Add to silver_categories_map** so other agents can find our categories

```sql
-- Our ML mappings
INSERT INTO silver_categories_map 
  (platform, platform_l1_id, platform_category_name, silver_category_id, confidence)
VALUES 
  ('ml', 'MLB3835', 'Áudio', 1, 0.90),
  ('ml', 'MLB1000', 'Eletrônicos', 3, 0.90),
  ('ml', 'MLB1051', 'Celulares', 3, 0.85),
  ...;

-- Our Amazon mappings
INSERT INTO silver_categories_map 
  (platform, platform_l1_id, platform_category_name, silver_category_id, confidence)
VALUES 
  ('amazon', 'electronics', 'Electronics', 3, 0.90),
  ('amazon', 'kitchen', 'Kitchen', 9, 0.85),
  ...;
```

---

## Questions for Discussion

1. Should `silver_categories_map` have an `agent_name` column to track who added each mapping?
2. Should we version-control the table state (export to JSON periodically)?
3. Should migration scripts fail on unmapped categories or skip with warning?

---

*This proposal follows data engineering best practices: separate concerns, declarative configuration, single source of truth.*

---

## English↔Portuguese Adapter Pattern

Our scraping/BRS tracking uses English categories internally, but `silver_categories` is Portuguese. The adapter pattern bridges this gap.

### Our Internal System (English)

```sql
-- category_registry (our local DB)
CREATE TABLE category_registry (
    id SERIAL PRIMARY KEY,
    our_l1 VARCHAR(50),      -- 'Audio', 'Sports', 'Tech'
    our_l2 VARCHAR(50),      -- 'Headphones', 'Wearables'
    our_l3 VARCHAR(50),      -- 'Bluetooth', 'Smartwatch'
    platform VARCHAR(20),    -- 'ml', 'amazon_br', 'amazon_us'
    platform_category_id VARCHAR(100),
    bestsellers_url TEXT,
    is_blacklisted BOOLEAN
);

-- bsr_history (our local DB)
CREATE TABLE bsr_history (
    id SERIAL PRIMARY,
    platform VARCHAR(20),
    platform_id VARCHAR(100),
    bsr_rank INTEGER,
    category_l1 VARCHAR(50),  -- 'Audio', 'Sports' (English)
    price NUMERIC,
    sales_count INTEGER,
    recorded_at TIMESTAMP
);
```

### Shared Taxonomy (Portuguese)

```sql
-- silver_categories (production DB)
CREATE TABLE silver_categories (
    id SERIAL PRIMARY KEY,
    l1 VARCHAR(100),  -- 'Audio', 'Esportes', 'Eletrônicos'
    l2 VARCHAR(100),
    l3 VARCHAR(100)
);
```

### The Adapter: Mapping Table

```sql
-- silver_categories_map (production DB)
-- Maps BOTH directions:
-- 1. Platform IDs → silver_categories (for resolution)
-- 2. Our English names → silver_categories (for translation)
```

### Translation Layer (New Table)

```sql
-- our_category_map (our local DB)
CREATE TABLE our_category_map (
    id SERIAL PRIMARY KEY,
    our_l1 VARCHAR(50) NOT NULL,
    silver_l1 VARCHAR(100) NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.9,
    UNIQUE(our_l1)
);

-- Seed data
INSERT INTO our_category_map (our_l1, silver_l1) VALUES
    ('Audio', 'Audio'),
    ('Moda', 'Moda'),
    ('Tech', 'Eletrônicos'),
    ('Lighting', 'Iluminação'),
    ('Home', 'Casa'),
    ('Sports', 'Esportes'),
    ('Tools', 'Ferramentas'),
    ('Kitchen', 'Cozinha'),
    ('Pet', 'Pets'),
    ('Photography', 'Eletrônicos'),  -- Maps to parent
    ('Health', 'Saúde'),
    ('Fashion', 'Moda'),  -- Duplicate of Moda
    ('Automotive', 'Automotivo'),
    ('Garden', 'Jardim'),
    ('Musical', 'Audio'),  -- Maps to parent
    ('Toys', 'Infantis'),
    ('Office', 'Papelaria'),
    ('Baby', 'Infantis');
```

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  OUR SYSTEM (English)                                       │
│  category_registry: 'Audio' > 'Headphones' > 'Bluetooth'   │
│  bsr_history: category_l1 = 'Audio'                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  ADAPTER (our_category_map)                                 │
│  our_l1='Audio' → silver_l1='Audio'                        │
│  our_l1='Tech' → silver_l1='Eletrônicos'                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  PRODUCTION DB                                              │
│  silver_categories: id=1, l1='Audio'                        │
│  silver_categories_map: 'ml' → 'MLB3835' → id=1            │
│  bronze_products: silver_category_id = 1                    │
└─────────────────────────────────────────────────────────────┘
```

### Migration Script Flow

```python
def export_to_production(conn_local, conn_prod):
    """Export bsr_history to production with silver_category_id."""
    
    # Get our BSR data
    bsr_data = query_local(conn_local, "SELECT * FROM bsr_history")
    
    for row in bsr_data:
        # Translate English → Portuguese
        silver_l1 = translate_category(conn_local, row['category_l1'])
        
        # Resolve to silver_category_id
        result = resolve_category(conn_prod, platform='ml', l1=silver_l1)
        
        if result:
            # Write to production with proper FK
            insert_bsr(conn_prod, {
                'platform': row['platform'],
                'platform_id': row['platform_id'],
                'bsr_rank': row['bsr_rank'],
                'silver_category_id': result['silver_category_id'],
                'price': row['price'],
                'sales_count': row['sales_count']
            })
        else:
            log_unmapped(row['category_l1'], silver_l1)


def translate_category(conn, our_l1):
    """Translate our English category to silver Portuguese."""
    result = query(conn, 
        "SELECT silver_l1 FROM our_category_map WHERE our_l1 = %s",
        (our_l1,)
    )
    return result[0]['silver_l1'] if result else our_l1
```

### Benefits of This Pattern

1. **Dual system support**: English for local, Portuguese for production
2. **Single translation point**: `our_category_map` is the only place to maintain
3. **Flexible**: Can add new L2/L3 mappings without changing code
4. **Auditable**: All translations visible in database
5. **Reversible**: Can translate back if needed

### Example: Our BSR Data → Production

| Our BSR Data | Translation | Production |
|---|---|---|
| category_l1='Audio' | → 'Audio' | silver_category_id=1 |
| category_l1='Tech' | → 'Eletrônicos' | silver_category_id=3 |
| category_l1='Lighting' | → 'Iluminação' | silver_category_id=4 |
| category_l1='Sports' | → 'Esportes' | silver_category_id=8 |

---

*This architecture keeps our internal system clean while integrating with the shared taxonomy.*
