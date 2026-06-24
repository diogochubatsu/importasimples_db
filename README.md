# ImportaSimples Database

Shared database schema and category architecture for all ImportaSimples agents.

---

## About Me

I'm the **China Agent** (ArbitLens / arbitlens_china). I scrape Chinese marketplaces via Rakumart proxy:

- **1688** (rakumart-1688) — 2,714 products
- **Alibaba** (rakumart-alibaba) — 2,714 products
- **Taobao** (rakumart-taobao) — 2,428 products
- **DHgate** — 4,829 products

**What I've done:**
1. Scraped 13,706 products from Chinese marketplaces
2. Classified products into 20 L1 categories using keywords + CLIP fallback
3. Migrated all products to ImportaSimples bronze_products
4. Uploaded 13,653 images to GCS (100% coverage)
5. Built the category resolver utility for all agents
6. Mapped 1688 platform category IDs to silver_categories (157 mappings)
7. Added `silver_category_id` FK to bronze_products

**My suggestion for silver_categories:**
- `silver_categories` should be the **single source of truth** — one canonical tree shared by all agents
- `silver_categories_map` maps each marketplace's native IDs to silver_categories
- Each agent adds their own rows to `silver_categories_map` — no conflicts
- L2/L3 categories are added on-demand when agents process products
- Confidence scores indicate mapping reliability (0.5 = low, 0.9 = high)

**Coverage so far:**
- L1: 81.7% (11,192 / 13,706 products)
- L2: 67.1% (9,190 products)
- L3: 30.4% (4,163 products)

**What other agents need to do:**
1. Add their platform L1 mappings to `silver_categories_map`
2. Use `resolve_category()` to map platform IDs → silver IDs
3. Store `silver_category_id` in bronze_products
4. Add L2/L3 to `silver_categories` as needed

— *China Agent (ArbitLens), June 2026*

---

## Overview

ImportaSimples uses a **Medallion architecture**: Bronze → Silver → Gold → UI. All agents write to the same database and share the same category system.

## Database Connection

```
Host: 34.170.210.220
Port: 5432
Database: importasimples_products
User: importasimples
Password: R{[{f<VajbC{<kvU
SSL: required (rejectUnauthorized: false)
```

## Category Architecture

### Tables

| Table | Purpose |
|---|---|
| `silver_categories` | **Single source of truth** — canonical category tree (L1→L2→L3→L4) |
| `silver_categories_map` | Maps marketplace native category IDs → `silver_categories.id` |
| `bronze_products` | Products table with `silver_category_id` FK |

### silver_categories

The canonical category tree shared by ALL agents. Each agent adds their L2/L3 as needed.

```sql
-- Structure
id          SERIAL PRIMARY KEY
l1          VARCHAR  -- Top-level (Audio, Moda, Eletrônicos, etc.)
l2          VARCHAR  -- Sub-category (nullable)
l3          VARCHAR  -- Sub-sub-category (nullable)
l4          VARCHAR  -- Sub-sub-sub-category (nullable)
icon        VARCHAR  -- Emoji for UI
created_at  TIMESTAMP
updated_at  TIMESTAMP
```

**Current L1 categories (19):**

| ID | L1 | Icon |
|---|---|---|
| 1 | Audio | 🔊 |
| 2 | Moda | 👗 |
| 3 | Eletrônicos | 📱 |
| 4 | Iluminação | 💡 |
| 5 | Casa | 🏠 |
| 6 | Infantis | 🧸 |
| 7 | Beleza | 💄 |
| 8 | Esportes | ⚽ |
| 9 | Cozinha | 🍳 |
| 10 | Ferramentas | 🔧 |
| 11 | Pets | 🐾 |
| 12 | Móveis | 🪑 |
| 13 | Papelaria | 📎 |
| 14 | Jardim | 🌱 |
| 15 | Segurança | 🔒 |
| 16 | Saúde | ❤️ |
| 17 | Calçados | 👟 |
| 18 | Automotivo | 🚗 |
| 19 | Wearables | ⌚ |

### silver_categories_map

Maps each marketplace's native category IDs to `silver_categories.id`.

```sql
-- Structure
id                  SERIAL PRIMARY KEY
silver_category_id  INTEGER REFERENCES silver_categories(id)
platform            VARCHAR(30)   -- '1688', 'ml', 'amazon', 'alibaba', 'dhgate'
platform_l1_id      VARCHAR(50)   -- Marketplace's L1 category ID
platform_l2_id      VARCHAR(50)   -- Marketplace's L2 category ID (nullable)
platform_l3_id      VARCHAR(50)   -- Marketplace's L3 category ID (nullable)
platform_category_name VARCHAR(200) -- Original name (e.g., Chinese/English)
confidence          DECIMAL(3,2)  -- How reliable this mapping is (0-1)
verified            BOOLEAN       -- Manually verified?
created_at          TIMESTAMP
updated_at          TIMESTAMP
UNIQUE(platform, platform_l1_id, platform_l2_id, platform_l3_id)
```

**Current mappings (1688):**

| Platform L1 ID | 1688 Name | Silver L1 | Confidence |
|---|---|---|---|
| 2 | 服装/服饰 | Moda | 0.90 |
| 4 | 鞋靴 | Calçados | 0.90 |
| 5 | 箱包 | Moda | 0.80 |
| 6 | 数码/消费电子 | Eletrônicos | 0.50 |
| 7 | 手机/手机配件 | Eletrônicos | 0.70 |
| 8 | 电脑/办公 | Papelaria | 0.60 |
| 13 | 家居/日用 | Casa | 0.70 |
| 15 | 玩具/礼品 | Infantis | 0.90 |
| 18 | 运动/户外 | Esportes | 0.80 |
| 53 | 美容/个护 | Beleza | 0.90 |
| 54 | 汽车用品 | Automotivo | 0.90 |
| 55 | 珠宝/饰品 | Moda | 0.70 |
| 59 | 家装/建材 | Casa | 0.60 |
| 65 | 仪器/仪表 | Eletrônicos | 0.50 |
| 66 | 工具/五金 | Ferramentas | 0.90 |
| 67 | 照明/LED | Iluminação | 0.90 |
| 68 | 办公/文具 | Papelaria | 0.90 |
| 70 | 宠物用品 | Pets | 0.90 |
| 97 | 家居/家饰 | Casa | 0.70 |
| 1813 | 母婴用品 | Infantis | 0.90 |
| 10208 | 食品/饮料 | Cozinha | 0.60 |
| 122916001 | 园艺/户外 | Jardim | 0.80 |
| 122916002 | 数码配件 | Eletrônicos | 0.70 |
| 130822002 | 通讯/电信 | Eletrônicos | 0.50 |
| 201547901 | 美容/化妆 | Beleza | 0.90 |

### bronze_products

Products table with category columns:

```sql
-- Category columns
silver_category_id  INTEGER REFERENCES silver_categories(id)  -- FK to silver_categories
category_l1         VARCHAR  -- Denormalized L1 name (for fast queries)
category_l2         VARCHAR  -- Denormalized L2 name
category_l3         VARCHAR  -- Denormalized L3 name
category_l4         VARCHAR  -- Denormalized L4 name
category_l5         VARCHAR  -- Denormalized L5 name
category_level      INTEGER  -- Depth level (1-5)
category_raw        VARCHAR  -- Raw category path (e.g., "audio.fones.bluetooth")
```

## How to Use (for all agents)

### 1. Resolve a product's category

```python
from category_resolver import resolve_category

result = resolve_category(
    conn,
    platform='1688',
    l1='67',     # Platform's L1 ID
    l2='2127',   # Platform's L2 ID (optional)
    l3='1033103' # Platform's L3 ID (optional)
)

# Returns:
# {
#     'silver_category_id': 4,
#     'confidence': 0.9,
#     'l1': 'Iluminação',
#     'l2': None,
#     'l3': None,
#     'match_level': 'L1'
# }
```

### 2. Store in bronze_products

```python
cur.execute("""
    UPDATE bronze_products
    SET silver_category_id = %s,
        category_l1 = %s,
        category_l2 = %s,
        category_l3 = %s
    WHERE source = %s AND source_id = %s
""", (
    result['silver_category_id'],
    result['l1'],
    result.get('l2'),
    result.get('l3'),
    source,
    source_id
))
```

### 3. Add new platform mappings

```python
from category_resolver import add_platform_mapping

# ML agent adds their mappings:
add_platform_mapping(
    conn,
    platform='ml',
    l1_id='MLB3835',
    silver_category_id=1,  # Audio
    category_name='Áudio',
    confidence=0.9
)

# Amazon agent adds their mappings:
add_platform_mapping(
    conn,
    platform='amazon',
    l1_id='2407760',
    silver_category_id=3,  # Eletrônicos
    category_name='Electronics',
    confidence=0.9
)
```

### 4. Add new L2/L3 categories

```python
from category_resolver import ensure_category

# Auto-creates if not exists:
cat_id = ensure_category(conn, l1='Audio', l2='Fones', l3='Bluetooth')
```

## Category Resolution Flow

```
┌─────────────────┐
│  Agent scrapes   │
│  product         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gets platform   │
│  category IDs    │
│  (e.g., 1688     │
│   L1=67, L2=2127)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  resolve_category│
│  looks up        │
│  silver_categories│
│  _map            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Returns         │
│  silver_category │
│  _id = 4         │
│  (Iluminação)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stores in       │
│  bronze_products │
│  - silver_category_id = 4
│  - category_l1 = 'Iluminação'
└─────────────────┘
```

## Agent Responsibilities

### China Agent (ArbitLens) — `arbitlens_china/`
- Scrapes: 1688, Alibaba, Taobao, DHgate via Rakumart proxy
- Platform IDs: `top_category_id`, `second_category_id`, `third_category_id`
- Adds mappings to `silver_categories_map` for 1688/Alibaba/Taobao
- **Status:** 13,706 products migrated, 13,653 images uploaded, 157 category mappings

### ML Agent — `ml_agent/`
- Scrapes: Mercado Livre (MLB categories)
- Platform IDs: MLB category IDs (e.g., MLB3835)
- Adds mappings to `silver_categories_map` for ML
- **Status:** Pending

### Amazon Agent — `amazon_agent/`
- Scrapes: Amazon BR, Amazon US
- Platform IDs: Amazon browse node IDs
- Adds mappings to `silver_categories_map` for Amazon
- **Status:** Pending

## Files

```
importasimples_db/
├── README.md                    # This file
├── category_resolver.py         # Shared utility for all agents
├── schema.sql                   # Database schema
└── arbitlens_china/             # China agent scripts & docs
    ├── scripts/
    │   ├── migrate_to_importasimples.py
    │   ├── migrate_images_to_gcs.py
    │   └── category_resolver.py
    └── docs/
        └── HANDOFF.md
```
