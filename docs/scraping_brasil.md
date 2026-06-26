# Scraping Brasil — Architecture & Logic

## Overview

ArbitLens tracks products across three Brazilian marketplaces to identify arbitrage opportunities:

| Platform | Source | Products | Sales Coverage |
|----------|--------|----------|----------------|
| Mercado Livre (ML) | Best sellers pages | 328 | 90.2% |
| Amazon BR | Product pages + best sellers | 450 | 94.7% |
| Amazon US | Product pages | 301 | 99.3% |

All scraping goes through **Decodo** (scraper-api.decodo.com) — a proxy/scraping service that provides residential IPs and headless browsers.

---

## 1. Category Discovery

### How we find categories

ML organizes products in a tree of categories, each identified by an MLB ID (e.g., `MLB3835` for Audio). We discover categories via:

**A) ML Public API (free, no auth):**
```
GET https://api.mercadolibre.com/categories/MLB{id}
→ Returns: {name, path_from_root: [{id, name}], children_categories: [...]}
```

**B) ML Best Sellers Hub:**
```
https://www.mercadolivre.com.br/mais-vendidos/MLB{top_id}
```
The page contains links to subcategories. We extract subcategory IDs from the HTML.

**C) Amazon BR Best Sellers Hub:**
```
https://www.amazon.com.br/gp/bestsellers/{slug}
```
Amazon uses department slugs (electronics, kitchen, beauty, etc.).

### Our Category Mapping (28 L1 categories)

| Category L1 | ML MLB ID | Amazon BR Slug |
|-------------|-----------|----------------|
| Audio | MLB3835 | electronics |
| Moda | MLB1430 | fashion |
| Eletrônicos | MLB1000 | electronics |
| Beleza | MLB1246 | beauty |
| Infantis | MLB1384 | baby-products |
| Esportes | MLB1276 | sports |
| Casa | MLB1574 | home |
| Pets | MLB1071 | pet-products |
| Iluminação | MLB1582 | lighting |
| Ferramentas | MLB263532 | hi |
| Wearables | MLB417704 | electronics |
| Cozinha | MLB1618 | kitchen |

These map to **silver_categories** in the ImportaSimples database (383 categories total).

---

## 2. Best Sellers — The Primary Data Source

Best sellers pages are our primary source because they provide:
- **Sales data** ("Mais de X mil vendidos")
- **Top-ranked products** (pre-filtered by demand)
- **Category structure** (hierarchy of MLB IDs / Amazon slugs)

### ML Best Sellers URL Pattern
```
https://www.mercadolivre.com.br/mais-vendidos/MLB{category_id}
```

Returns top 20 products per page with:
- MLB ID (product identifier)
- Title
- Price (R$)
- Sales count ("+50 mil vendidos")
- Image URL
- Rating

### Amazon BR Best Sellers URL Pattern
```
https://www.amazon.com.br/gp/bestsellers/{department_slug}
```

Returns top 50 products per page with:
- ASIN (product identifier)
- Title
- Price (R$)
- Star rating
- Review count

**Note:** Amazon best sellers pages do NOT show sales data. Sales come from individual product pages (`/dp/{ASIN}`).

---

## 3. Scraping via Decodo

### Architecture

```
Our Scripts → Decodo Scraping API → Target Website → HTML Response
                    ↑
            Residential IP (Brazil)
```

Decodo is a proxy/scraping service. We send a URL, they fetch it from a residential IP in Brazil, and return the HTML. This bypasses bot detection because the request comes from a real Brazilian IP.

### API Endpoint

```
POST https://scraper-api.decodo.com/v2/scrape
Authorization: Basic <base64(user:pass)>
Content-Type: application/json
```

### Request Body

```json
{
  "url": "https://www.mercadolivre.com.br/mais-vendidos/MLB3835",
  "proxy_pool": "premium",
  "headless": "html",
  "geo": "Brazil"
}
```

### Parameters

| Parameter | Values | Purpose |
|-----------|--------|---------|
| `url` | Any URL | Target page to scrape |
| `proxy_pool` | `"premium"` or `"standard"` | Premium = residential IPs (required for ML) |
| `headless` | `"html"` or `"png"` | HTML = server-rendered HTML; PNG = screenshot |
| `geo` | `"Brazil"` | Route through Brazilian IP (CRITICAL for ML) |
| `locale` | `"pt-br"` | Portuguese content rendering |

### Response Format

```json
{
  "results": [
    {
      "content": "<html>...</html>",
      "url": "https://...",
      "status_code": 200
    }
  ]
}
```

The `content` field contains the full rendered HTML (typically 500KB-1.5MB for ML pages).

### Critical Rules

1. **ML requires `geo: "Brazil"`** — Without it, ML returns error 613
2. **Amazon BR does NOT use `geo: "Brazil"`** — Returns 400 error if included
3. **Premium proxy required for ML** — Standard proxy fails with 401
4. **`headless: "html"` only** — `"javascript"` is not valid, returns 400
5. **2-second delay between requests** — Prevents rate limiting

### Python Example

```python
import json, urllib.request, ssl

auth = "VTAwMDA0NDA0ODA6..."  # base64(user:pass)

def scrape_url(url, geo=None):
    payload = {"url": url, "proxy_pool": "premium", "headless": "html"}
    if geo:
        payload["geo"] = geo
    
    req = urllib.request.Request(
        "https://scraper-api.decodo.com/v2/scrape",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}"
        }
    )
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    resp = urllib.request.urlopen(req, timeout=60, context=ctx)
    result = json.loads(resp.read().decode())
    return result["results"][0]["content"]

# ML: use geo="Brazil"
html = scrape_url(
    "https://www.mercadolivre.com.br/mais-vendidos/MLB3835",
    geo="Brazil"
)

# Amazon BR: NO geo parameter
html = scrape_url(
    "https://www.amazon.com.br/dp/B0789M146B"
)
```

---

## 4. Finding Products on Best Sellers Pages

### ML — Two HTML Structures

ML uses different HTML structures depending on the category:

**Standard categories (Audio, Electronics, Home, etc.):**
- Product cards: `li[class*="ui-search-layout"]` or `div[class*="andes-card"]`
- Product links: `a[href*="/p/MLB{number}"]`
- Title: `img[alt]` inside the card
- Price: `.andes-money-amount__fraction`

**Fashion categories (Moda, Bolsas, etc.):**
- Product cards: `div[class*="poly-card"]`
- Product links: `a[href*="MLB-{number}"]` (note the dash)
- Title: `img[alt]` inside the card
- Price: Last `R$` amount in the card text

### ML — JSON-LD Extraction (Preferred)

ML embeds product data as JSON-LD in the HTML. This is the most reliable extraction method:

```python
import re, html as html_lib

def extract_ml_products(html_content):
    products = []
    
    # Find all MLB IDs
    product_ids = list(set(re.findall(r'"product_id":"(MLB\d+)"', html_content)))
    
    for pid in product_ids[:20]:  # Top 20
        pos = html_content.find(f'"product_id":"{pid}"')
        block = html_content[max(0, pos-200):pos+3000]
        
        # Title
        title = ''
        tm = re.search(r'"title":\{"text":"([^"]+)"', block)
        if tm:
            title = html_lib.unescape(tm.group(1))
        
        # Price
        price = 0.0
        pm = re.search(r'"current_price":\{"value":([\d.]+)', block)
        if pm:
            price = float(pm.group(1))
        
        # Sales
        sales = 0
        sm = re.search(r'\+(\d[\d.,]*)\s*(mil|milhão|mi|k)?\s*vendidos?', block, re.IGNORECASE)
        if sm:
            num = float(sm.group(1).replace('.', '').replace(',', ''))
            mult = sm.group(2)
            if mult:
                if mult.lower() in ('mil', 'k'): num *= 1000
                elif mult.lower() in ('milhão', 'mi'): num *= 1000000
            sales = int(num)
        
        # Image
        image_url = None
        pm2 = re.search(r'"pictures":\{"scale":"[^"]+","pictures":\[\{"id":"([^"]+)"', block)
        if pm2:
            image_url = f"https://http2.mlstatic.com/D_Q_NP_2X_{pm2.group(1)}-AB.webp"
        
        # URL
        url = f"https://www.mercadolivre.com.br/p/{pid}"
        
        if title:
            products.append({
                "platform_id": pid,
                "title": title,
                "price": price,
                "sales_30d": sales,
                "url": url,
                "image_url": image_url
            })
    
    return products
```

### Amazon BR — HTML Extraction

Amazon BR best sellers pages use this structure:

```python
import re

def extract_amazon_products(html_content):
    products = []
    
    # Find ASINs
    asins = list(set(re.findall(r'data-asin="(B0[A-Z0-9]{8})"', html_content)))
    
    for asin in asins[:50]:  # Top 50
        # Title
        title_match = re.search(
            rf'data-asin="{asin}".*?<span[^>]*>([^<]+)</span>',
            html_content, re.DOTALL
        )
        title = title_match.group(1).strip() if title_match else ""
        
        # Price
        price_match = re.search(
            rf'data-asin="{asin}".*?R\$\s*([\d.,]+)',
            html_content, re.DOTALL
        )
        price = float(price_match.group(1).replace('.', '').replace(',', '.')) if price_match else 0
        
        # Rating
        rating_match = re.search(
            rf'data-asin="{asin}".*?([\d.]+)\s*out of',
            html_content, re.DOTALL
        )
        rating = float(rating_match.group(1)) if rating_match else 0
        
        url = f"https://www.amazon.com.br/dp/{asin}"
        
        products.append({
            "platform_id": asin,
            "title": title,
            "price": price,
            "url": url
        })
    
    return products
```

---

## 5. Extracting Sales Data

Sales data is the most valuable piece of information. The format differs by platform:

### ML Sales Extraction

ML shows sales on both best sellers pages and product pages:

**On best sellers pages:**
```
"+50 mil vendidos"
"+100 vendidos"
"+500 mil vendidos"
```

**On product pages (with `geo: "Brazil"`):**
```json
"subtitle": "Novo | +50 mil vendidos"
```

**Regex:**
```python
match = re.search(r'\+(\d[\d.,]*)\s*(mil|milhão|mi|k)?\s*vendidos?', html, re.IGNORECASE)
if match:
    num = float(match.group(1).replace('.', '').replace(',', ''))
    mult = match.group(2)
    if mult:
        if mult.lower() in ('mil', 'k'): num *= 1000
        elif mult.lower() in ('milhão', 'mi'): num *= 1000000
    sales = int(num)
```

**Formats seen:**
| Text | Parsed Value |
|------|--------------|
| +100 vendidos | 100 |
| +500 vendidos | 500 |
| +5 mil vendidos | 5,000 |
| +50 mil vendidos | 50,000 |
| +500 mil vendidos | 500,000 |
| +1M vendidos | 1,000,000 |

**Important:** ML sales = TOTAL lifetime sales (not monthly).

### Amazon BR Sales Extraction

Amazon BR shows sales on individual product pages (`/dp/{ASIN}`):

**HTML element:**
```html
<p id="pqv-bought-in-last-month">Mais de 300 compras no mês passado</p>
```

**Regex:**
```python
# First, fix &nbsp; encoding
html = html.replace('&nbsp;', ' ')

# Then extract
match = re.search(r'pqv-bought-in-last-month[^>]*>([^<]+)', html, re.IGNORECASE)
if match:
    text = match.group(1)
    
    # "no mês passado" = monthly
    m = re.search(r'Mais de ([\d.,]+)\s*(mil)?\s*compras?\s*no mês', text, re.IGNORECASE)
    if m:
        num = float(m.group(1).replace('.', '').replace(',', ''))
        if m.group(2) and m.group(2).lower() in ('mil', 'k'): num *= 1000
        sales = int(num)
    
    # "na semana passada" = weekly (multiply by 4.3)
    m = re.search(r'Mais de ([\d.,]+)\s*(mil)?\s*compras?\s*na semana', text, re.IGNORECASE)
    if m:
        num = float(m.group(1).replace('.', '').replace(',', ''))
        if m.group(2) and m.group(2).lower() in ('mil', 'k'): num *= 1000
        sales = int(num * 4.3)
```

**Formats seen:**
| Text | Parsed Value |
|------|--------------|
| Mais de 100 compras no mês passado | 100 |
| Mais de 2 mil compras no mês passado | 2,000 |
| Mais de 500 compras na semana passada | 2,150 (500 × 4.3) |
| Mais de 5 mil compras no mês passado | 5,000 |

**Important:** Amazon sales = LAST MONTH sales (not total).

### Amazon US Sales Extraction

Amazon US uses English format:

```python
match = re.search(r'([\d.,]+)\s*[kK]?\+?\s*bought in past (month|week)', html, re.IGNORECASE)
if match:
    num = float(match.group(1).replace('.', '').replace(',', ''))
    if 'k' in match.group(1).lower(): num *= 1000
    if match.group(2).lower() == 'week': num *= 4.3
    sales = int(num)
```

| Text | Parsed Value |
|------|--------------|
| 300+ bought in past month | 300 |
| 5K+ bought in past week | 21,500 (5,000 × 4.3) |
| 10K+ bought in past month | 10,000 |

---

## 6. URL Registration

Every product gets a direct URL to its listing page. This is stored in the `url` column.

### URL Patterns

| Platform | URL Pattern | Example |
|----------|-------------|---------|
| ML | `https://www.mercadolivre.com.br/p/MLB{id}` | `/p/MLB21361292` |
| Amazon BR | `https://www.amazon.com.br/dp/{ASIN}` | `/dp/B0789M146B` |
| Amazon US | `https://www.amazon.com/dp/{ASIN}` | `/dp/B075XN1KNG` |

### URL Generation

For products from best sellers pages, the URL is constructed from the product ID:

```python
# ML
url = f"https://www.mercadolivre.com.br/p/{mlb_id}"

# Amazon
url = f"https://www.amazon.com.br/dp/{asin}"
```

### URL Validation

All 1,079 products have valid URLs (100% coverage):
- Amazon BR: 450/450 (100%)
- Amazon US: 301/301 (100%)
- ML: 328/328 (100%)

---

## 7. Complete Scraping Pipeline

### Step-by-Step Flow

```
1. DISCOVER CATEGORY
   └→ ML API: GET /categories/MLB{id} → name, hierarchy
   └→ Amazon: /gp/bestsellers/{slug} → department

2. SCRAPE BEST SELLERS
   └→ Decodo API: POST /v2/scrape with URL
   └→ Returns: HTML (500KB-1.5MB)

3. EXTRACT PRODUCTS
   └→ Parse HTML (JSON-LD for ML, DOM for Amazon)
   └→ Get: platform_id, title, price, image, url

4. EXTRACT SALES
   └→ Regex on HTML text
   └→ ML: "+50 mil vendidos" → 50000
   └→ Amazon: "Mais de 2 mil compras no mês passado" → 2000

5. STORE IN DATABASE
   └→ products table (local DB)
   └→ bronze_products table (ImportaSimples DB)
   └→ Map to silver_categories for cross-platform matching

6. ENRICH (optional)
   └→ Scrape individual product pages for additional data
   └→ Amazon: /dp/{ASIN} for sales data
   └→ ML: /p/MLB{id} for detailed sales
```

### Python Script Example

```python
import json, urllib.request, ssl, re, time

auth = "VTAwMDA0NDA0ODA6..."  # Decodo auth

def scrape_ml_bestsellers(category_id):
    """Scrape ML best sellers for a category."""
    url = f"https://www.mercadolivre.com.br/mais-vendidos/MLB{category_id}"
    
    payload = json.dumps({
        "url": url,
        "proxy_pool": "premium",
        "headless": "html",
        "geo": "Brazil"
    }).encode()
    
    req = urllib.request.Request(
        "https://scraper-api.decodo.com/v2/scrape",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}"
        }
    )
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    resp = urllib.request.urlopen(req, timeout=60, context=ctx)
    result = json.loads(resp.read().decode())
    html = result["results"][0]["content"]
    
    # Extract products
    products = []
    product_ids = list(set(re.findall(r'"product_id":"(MLB\d+)"', html)))
    
    for pid in product_ids[:20]:
        pos = html.find(f'"product_id":"{pid}"')
        block = html[max(0, pos-200):pos+3000]
        
        title = ""
        tm = re.search(r'"title":\{"text":"([^"]+)"', block)
        if tm:
            import html as html_lib
            title = html_lib.unescape(tm.group(1))
        
        price = 0.0
        pm = re.search(r'"current_price":\{"value":([\d.]+)', block)
        if pm:
            price = float(pm.group(1))
        
        sales = 0
        sm = re.search(r'\+(\d[\d.,]*)\s*(mil|milhão|mi|k)?\s*vendidos?', block, re.IGNORECASE)
        if sm:
            num = float(sm.group(1).replace('.', '').replace(',', ''))
            mult = sm.group(2)
            if mult:
                if mult.lower() in ('mil', 'k'): num *= 1000
                elif mult.lower() in ('milhão', 'mi'): num *= 1000000
            sales = int(num)
        
        products.append({
            "platform_id": pid,
            "title": title,
            "price": price,
            "sales_30d": sales,
            "url": f"https://www.mercadolivre.com.br/p/{pid}"
        })
    
    return products

# Example usage
products = scrape_ml_bestsellers(3835)  # Audio category
for p in products[:3]:
    print(f"{p['title'][:50]}")
    print(f"  R$ {p['price']:.2f} | {p['sales_30d']} vendas")
    print(f"  {p['url']}")
    print()
```

---

## 8. Decodo Service Reference

### Available Services

| Service | Endpoint | Use Case |
|---------|----------|----------|
| Scraping API | `scraper-api.decodo.com/v2/scrape` | ML + Amazon BR pages |
| Site Unblocker | `unblock.decodo.com:60000` | Amazon (forward proxy) |
| Residential BR | `br.decodo.com:10001` | Brazilian IPs |
| Residential US | `us.decodo.com:10001` | US IPs (Amazon US) |
| ISP Static | `isp.decodo.com:10001` | Static IPs |

### What We Use

**Primary: Scraping API** — For ML and Amazon BR best sellers + product pages.

**Fallback: Site Unblocker** — Forward proxy for Amazon when Scraping API is blocked.

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 613 (ML) | Missing `geo: "Brazil"` | Add `geo` parameter |
| 400 (Amazon) | `geo: "Brazil"` on Amazon | Remove `geo` parameter |
| 401 | Wrong auth format | Check Basic vs Bearer auth |
| <10KB HTML | JS shell (ML) | Retry up to 10x |
| 429 | Quota exhausted | Wait for reset or use new account |

### Cost Optimization

- 2-second delay between requests (prevents rate limiting)
- Premium proxy only when needed (ML requires it)
- Retry logic (10 attempts before fallback)
- Batch processing (scrape 20 products per page load)

---

## 9. Data Quality Rules

Every product MUST have:
1. ✅ `platform_id` (MLB ID or ASIN)
2. ✅ `title` (product name)
3. ✅ `price` (R$ value, > 0)
4. ✅ `image_url` (full HTTPS URL, not local path)
5. ✅ `url` (direct link to listing)
6. ✅ `sales_30d` (monthly sales, 0 if unavailable)
7. ✅ `category_l1` (mapped to silver_categories)

### Quality Audit Query

```sql
SELECT platform,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE sales_30d > 0) as has_sales,
    COUNT(*) FILTER (WHERE price > 0) as has_price,
    COUNT(*) FILTER (WHERE url IS NOT NULL) as has_url
FROM products WHERE is_active = true
GROUP BY platform;
```

---

## 10. Key Learnings

1. **ML requires `geo: "Brazil"`** — Without it, all product pages return 613
2. **Amazon BR does NOT use `geo`** — Returns 400 if included
3. **ML sales = lifetime, Amazon sales = monthly** — Different semantics
4. **JSON-LD extraction is most reliable for ML** — DOM selectors vary by category
5. **Amazon has `&nbsp;` encoding** — Always replace before regex matching
6. **Best sellers pages have sales data, search pages don't** — Always use best sellers URLs
7. **Fashion categories use different HTML** — `poly-card` + `MLB-{id}` format
8. **Decodo retry logic is essential** — Same URL can return different states
9. **Store full HTTPS URLs for images** — Never local paths
10. **2-second delay between requests** — Prevents rate limiting

---

## Appendix: Category MLB IDs

| Category | MLB ID | Notes |
|----------|--------|-------|
| Audio | MLB3835 | ✅ Decodo HTML |
| Microfones | MLB270243 | ✅ Decodo HTML |
| Headphones | MLB196208 | ✅ Decodo HTML |
| Acessórios Celular | MLB3813 | ✅ Decodo HTML |
| Smartwatches | MLB417704 | ✅ Decodo HTML |
| Malas e Bolsas | MLB1457 | ✅ Decodo HTML |
| Mochilas | MLB3127 | ✅ Decodo HTML |
| Pet Shop | MLB1071 | ✅ Decodo HTML |
| Esportes | MLB1276 | ✅ Decodo HTML |
| Beleza | MLB1246 | ✅ Decodo HTML |
| Brinquedos | MLB1132 | ✅ Decodo HTML |
| Bebê | MLB1384 | ✅ Decodo HTML |
| Casa | MLB1574 | ✅ Decodo HTML |
| Ferramentas | MLB263532 | ✅ Decodo HTML |
| Cozinha | MLB1618 | ✅ Decodo HTML |
| Iluminação | MLB1582 | ✅ Decodo HTML |
| Fotografia | MLB1039 | ✅ Decodo HTML |
| Moda | MLB1430 | ✅ Browser (JS-rendered) |
| Calçados | MLB4954 | ✅ Browser (brand filter) |

---

*Last updated: 2026-06-25*
*ArbitLens — See the arbitrage. Before everyone else.*

---

## Appendix: ML Product Page URLs for Testing

These are verified ML product pages with high sales volume. Use to test scraping approaches.

| MLB ID | Title | Price | Sales | URL |
|--------|-------|-------|-------|-----|
| MLB5646077008 | Omo Lavanderia Profissional 7L | R$92 | 750k | https://www.mercadolivre.com.br/p/MLB5646077008 |
| MLB21361292 | CeraVe Loção Hidratante 473ml | R$90 | 500k | https://www.mercadolivre.com.br/loco-hidratante-corporal-sem-perfume-com-ceramidas-essenciais-e-acido-hialurnico-textura-fluida-cerave-473ml/p/MLB21361292 |
| MLB53979422 | Microfone Lapela Kaidi Tipo-C | R$53 | 410k | https://www.mercadolivre.com.br/p/MLB53979422 |
| MLB3463647427 | Marinex Assadeiras Oval 3 Peças | R$62 | 250k | https://www.mercadolivre.com.br/p/MLB3463647427 |
| MLB37271347 | Lenços Umedecidos Huggies 192un | R$30 | 250k | https://www.mercadolivre.com.br/lencos-umedecidos-huggies-higiene-superior-192-unidades/p/MLB37271347 |
| MLB19309318 | CeraVe Creme Hidratante 454g | R$101 | 250k | https://www.mercadolivre.com.br/creme-hidratante-corporal-e-facial-para-pole-seca-a-extra-seca-sem-perfume-454g-cerave/p/MLB19309318 |
| MLB3239976866 | Kit 6 Meias Puma Cano Médio | R$69 | 250k | https://www.mercadolivre.com.br/p/MLB3239976866 |
| MLB2070063236 | Calça Jeans Masculina Elastano | R$44 | 250k | https://www.mercadolivre.com.br/p/MLB2070063236 |
| MLB35848144 | Máquina Cabelo Drago 4 Pentes | R$18 | 250k | https://www.mercadolivre.com.br/maquina-de-cortar-cabelo-sem-fio-barbeador-eletrico-aparador-de-pelos-acabamento-drago-motor-profissional-4-pentes-recarregavel-usb-tipo-c-dourada/p/MLB35848144 |
| MLB39962085 | Xiaomi Redmi Buds 6 Play | R$87 | 100k | https://www.mercadolivre.com.br/p/MLB39962085 |

### Scraping Notes

**ML Product Pages via Decodo:**
- Returns 404 page (144KB HTML) — ML blocks product pages
- Only generic image in link rel="preload" — not the product image
- geo: "Brazil" does NOT bypass this block
- wait_until: "network_idle" does NOT help

**ML Best Sellers Pages via Decodo:**
- Returns rendered HTML (400-500KB) with product cards
- Images in img class="poly-component__picture" src="..."
- Each product has unique image URL
- geo: "Brazil" is REQUIRED

**ML Residential Proxy:**
- Returns "suspicious-traffic" challenge page
- Blocked from datacenter IPs

**ML Site Unblocker:**
- Returns 62 bytes (auth error)
- Cannot authenticate for ML product pages

### Image Extraction Pattern (Best Sellers Only)

From best sellers HTML:
- pictures: find all img.poly-component__picture with src
- wids: find all wid=MLB{id}
- Match by position: picture N -> wid N
