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
