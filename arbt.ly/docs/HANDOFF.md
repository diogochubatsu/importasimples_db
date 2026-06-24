# ArbitLens (arbt.ly) — Handoff Document

## Overview

ArbitLens is a cross-marketplace arbitrage intelligence platform tracking products across:
- **Amazon BR** (amazon_br)
- **Amazon US** (amazon_us)  
- **Mercado Livre** (ml)

**Source value:** `arbt.ly` (NOT `arbitlens_brasil` — that's another agent)

## Database

### Source DB (Local)
- Host: localhost:5432
- Database: arbtbr
- User: hermes1688
- 1,079 products, 154 matches, 19 L1 categories

### Destination DB (ImportaSimples)
- Host: 34.170.210.220:5432
- Database: importasimples_products
- User: importasimples
- **1,079 products migrated, 100% silver_category_id coverage**

## Category Mapping (arbt.ly → silver_categories)

| arbt.ly L1 | Silver L1 | Silver ID | Confidence | Notes |
|------------|-----------|-----------|------------|-------|
| Audio | Audio | 1 | 0.95 | Microfones, Fones, Caixas de Som |
| Moda Intima | Moda | 2 | 0.90 | Calcinhas, Cintas, Cuecas |
| Moda | Moda | 2 | 0.90 | Roupas em geral |
| Acessórios Mobile | Eletrônicos | 3 | 0.90 | Suportes, Capas |
| Bebê | Infantis | 6 | 0.90 | Fraldas, Roupas Bebê |
| Beleza | Beleza | 7 | 0.90 | Skincare, Maquiagem |
| Bolsas | Moda | 2 | 0.85 | Mochilas, Malas |
| Brinquedos | Infantis | 6 | 0.90 | Brinquedos em geral |
| Casa | Casa | 5 | 0.90 | Organização, Decoração |
| Cozinha | Cozinha | 9 | 0.90 | Panelas, Utensílios |
| Esportes | Esportes | 8 | 0.90 | Roupas, Equipamentos |
| Ferramentas | Ferramentas | 10 | 0.95 | Ferramentas manuais/elétricas |
| Fotografia | Eletrônicos | 3 | 0.85 | Câmeras, Tripés |
| Iluminação | Iluminação | 4 | 0.95 | LEDs, Luminárias |
| Meias | Moda | 2 | 0.85 | Meias em geral |
| Mochilas | Moda | 2 | 0.85 | Mochilas de viagem |
| Pet Shop | Pets | 11 | 0.95 | Ração, Acessórios |
| Praia | Esportes | 8 | 0.85 | Produtos de praia |
| Wearables | Wearables | 19 | 0.95 | Smartwatches, Fitness |

## Platform Category IDs

### Mercado Livre (ML)
| arbt.ly L1 | MLB ID |
|------------|--------|
| Audio | MLB3835 |
| Acessórios Mobile | MLB3813 |
| Bebê | MLB1384 |
| Beleza | MLB1246 |
| Bolsas | MLB1457 |
| Brinquedos | MLB1132 |
| Casa | MLB1574 |
| Cozinha | MLB1618 |
| Esportes | MLB1276 |
| Ferramentas | MLB263532 |
| Fotografia | MLB1039 |
| Iluminação | MLB430378 |
| Meias | MLB437816 |
| Mochilas | MLB3127 |
| Moda | MLB1430 |
| Moda Intima | MLB108786 |
| Pet Shop | MLB1071 |
| Praia | MLB430391 |
| Wearables | MLB417704 |

### Amazon BR/US
| Category | Amazon Browse Node |
|----------|-------------------|
| Audio | 14513987011 |
| Electronics | 14513987011 |
| All others | 14513987011 |

## Data Quality

| Metric | arbt.ly | ImportaSimples |
|--------|---------|----------------|
| Products | 1,079 | 1,079 |
| Silver Category | 100% | 100% |
| Sales Data | 90.7% | 90.7% |
| Images | 100% | 100% |
| Matches | 154 (106 BR↔ML + 48 BR↔US) | N/A |

## Scripts

- `scripts/migrate_to_importasimples.py` — UPSERT products to bronze_products
- `scripts/upload_images_to_gcp.py` — Upload images to GCP bucket
- `scripts/scrape_ml_sales.py` — Scrape ML product pages for sales data

## Key Learnings

1. **Decodo `geo: "Brazil"`** is CRITICAL for ML scraping — without it, ML returns 613
2. **ML sales data** is in JSON subtitle: `"+50 mil vendidos"`
3. **Amazon US** needs realistic headers (Mac Safari Chrome 120) to bypass CAPTCHA
4. **Source value must be `arbt.ly`** — never `arbitlens_brasil` (that's another agent)

## Contact

- GitHub: https://github.com/diogochubatsu/arbt.ly
- Dashboard: http://136.111.212.52:5000
