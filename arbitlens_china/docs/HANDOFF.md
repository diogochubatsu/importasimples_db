# Handoff Document — ArbitLens Assessment & Integration

## Quick Access

### Live App
- **Dashboard:** https://arbitlens-v2-820365145375.us-central1.run.app/arbitlens
- **Table View:** https://arbitlens-v2-820365145375.us-central1.run.app/arbitlens/table
- **Data Warehouse:** https://arbitlens-v2-820365145375.us-central1.run.app/warehouse/
- **Search:** https://arbitlens-v2-820365145375.us-central1.run.app/arbitlens/search?q=microfone
- **Categories:** https://arbitlens-v2-820365145375.us-central1.run.app/arbitlens/categories
- **Matches:** https://arbitlens-v2-820365145375.us-central1.run.app/arbitlens/matches
- **Clusters:** https://arbitlens-v2-820365145375.us-central1.run.app/arbitlens/clusters

### API Endpoints (Direct Data Access)
```
GET /api/arbitlens/explore?category=audio&platform=rakumart-1688&sort=price_asc&limit=50
GET /api/arbitlens/search?q=microfone&k=24
GET /api/arbitlens/taxonomy?level=1
GET /api/arbitlens/product?id=rakumart-1688_12345
GET /api/arbitlens/stats
GET /api/arbitlens/matches
GET /api/arbitlens/clusters
```

### Database Access
```
Host: 10.30.96.3 (Cloud SQL private IP)
Database: intel_data
User: hermes1688
Password: (see .env)
Connection: postgresql://hermes1688:***@10.30.96.3:5432/intel_data
```

### GitHub Repo
- **URL:** https://github.com/diogochubatsu/sourcing-lens
- **Local:** /mnt/ssd/arbitlens
- **Branch:** master

---

## What Was Built

### Frontend Pages (9 pages)
| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/arbitlens` | Stats, categories, product previews |
| Table | `/arbitlens/table` | Full product table with filters |
| Search | `/arbitlens/search?q=` | Full-text search |
| Categories | `/arbitlens/categories` | 19 N1 categories |
| Category Detail | `/arbitlens/categories/[slug]` | Subcategories + products |
| Matches | `/arbitlens/matches` | Cross-platform matches |
| Clusters | `/arbitlens/clusters` | Same product across platforms |
| Product Detail | `/arbitlens/product/[id]` | Full product info |
| Data Warehouse | `/warehouse/` | Static API documentation |

### API Endpoints (15 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/arbitlens/explore` | GET | Multi-dimensional product query |
| `/api/arbitlens/search` | GET | Full-text search |
| `/api/arbitlens/taxonomy` | GET | Category tree |
| `/api/arbitlens/taxonomy/[slug]` | GET | Category detail |
| `/api/arbitlens/product` | GET | Product detail |
| `/api/arbitlens/stats` | GET | Platform statistics |
| `/api/arbitlens/matches` | GET | Cross-platform matches |
| `/api/arbitlens/clusters` | GET | Product clusters |
| `/api/arbitlens/categories` | GET | Category list |
| `/api/arbitlens/compare` | GET | Price comparison |
| `/api/arbitlens/visual-match` | GET | CLIP similarity |
| `/api/arbitlens/price-history` | GET | Price trends |
| `/api/arbitlens/opportunities` | GET | Sourcing opportunities |
| `/api/arbitlens/trending` | GET | Trending products |
| `/api/proxy/image` | GET | Image proxy |

### Data Available
- **13,508 products** across 5 platforms
- **1,441 cross-platform matches**
- **435 taxonomy categories** (19 N1 → 89 N2 → 162 N3 → 32 N4)
- **12,608 CLIP embeddings** (93% coverage)
- **100% N1 classification** (19 categories + Uncategorized)

---

## Integration Points

### Option 1: Embed via iframe
```html
<iframe src="https://arbitlens-v2-820365145375.us-central1.run.app/arbitlens/table" width="100%" height="800"></iframe>
```

### Option 2: Use API endpoints
```javascript
// Fetch products
const res = await fetch('https://arbitlens-v2-820365145375.us-central1.run.app/api/arbitlens/explore?category=audio&limit=10');
const data = await res.json();
// data.products = [{ platform, title, price, image_url, url, ... }]
```

### Option 3: Direct database access
```sql
-- Connect to Cloud SQL
SELECT * FROM arbitlens_products WHERE category = 'audio' LIMIT 10;

-- Get matches
SELECT * FROM arbitlens_matches WHERE confidence > 0.8 LIMIT 20;

-- Get taxonomy
SELECT * FROM taxonomy WHERE level = 1;
```

---

## Architecture Notes

- **Frontend:** Next.js 15 + Tailwind CSS
- **Backend:** Node.js API routes + Python scrapers
- **Database:** PostgreSQL + pgvector (Cloud SQL)
- **ML:** CLIP (openai/clip-vit-base-patch32)
- **Deployment:** Cloud Run (standalone mode)
- **Limitation:** Server components with DB queries fail at build time in standalone mode. Use API routes or Python subprocesses.

---

## What's Working
- ✅ Search across 5 marketplaces
- ✅ Category browsing (19 N1 + 89 N2)
- ✅ Cross-platform matches (1,441)
- ✅ Product clusters with price comparison
- ✅ Table view with filters and sorting
- ✅ Data Warehouse API
- ✅ Classification (100% N1)
- ✅ Deployed and live

## What's Not Ideal
- ⚠️ Explore page is static docs (filters don't work interactively)
- ⚠️ Classification N2: 66.5%, N3: 30.8%
- ⚠️ Python subprocess calls (slow on cold start)
- ⚠️ No authentication
- ⚠️ No automated data refresh
