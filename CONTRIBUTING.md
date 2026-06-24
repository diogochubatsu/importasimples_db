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
