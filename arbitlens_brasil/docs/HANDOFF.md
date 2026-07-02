# arbitlens_brasil — Handoff Document

## Identity
- **Agent name:** arbitlens_brasil
- **Source field:** `source = 'arbitlens_brasil'` in bronze_products
- **Scope:** Products from Amazon BR, Amazon US, and Mercado Livre for the Brazilian market
- **Responsibility:** Scrape, categorize (L1/L2/L3), and maintain product data quality

## Current State (2026-07-02)
- **Total products:** ~2,200+
- **L1 categories with products:** Eletrônicos, Audio, Moda, Casa, Wearables, Iluminação, Esportes, Infantis, Pets, Saúde, Ferramentas, Beleza, Cozinha, Automotivo, Jardim, Papelaria, Segurança, Escritório
- **L3 coverage:** All L3s in silver_categories have ≥10 products
- **Taxonomy alignment:** 100% — all category_l2/l3 match silver_categories names

## Key Rules
1. **NEVER modify silver_categories** — only bronze_products (category_l2, category_l3)
2. **Product-by-product verification** — no automated scripts for final quality checks
3. **All L3s need ≥10 products** — scrape more if below threshold
4. **Verify images and URLs** — every scraped product must have working image
5. **Match silver_categories taxonomy** — product L2/L3 must exist in silver_categories table
6. **3 marketplaces:** Amazon BR (amazon_br:), Amazon US (amazon_us:), Mercado Livre (ml:MLB*)

## Scraping Tools
See `docs/SCRAPING.md` for complete documentation on Decodo, Firecrawl, and marketplace-specific scraping.

## DB Access
- **Production DB:** 34.170.210.220:5432/importasimples_products
- **User:** importasimples
- **Table:** bronze_products (source, source_id, title, category_l1, category_l2, category_l3, image_url, product_url, price, currency)
