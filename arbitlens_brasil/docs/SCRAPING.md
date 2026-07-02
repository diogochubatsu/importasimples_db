# Scraping Guide — arbitlens_brasil

## Marketplaces Overview

| Marketplace | Source ID prefix | Search URL pattern | Status |
|---|---|---|---|
| Amazon BR | `amazon_br:{ASIN}` | `amazon.com.br/s?k=KEYWORD` | ✅ Working |
| Amazon US | `amazon_us:{ASIN}` | `amazon.com/s?k=KEYWORD` | ✅ Working |
| Mercado Livre | `ml:{MLB_ID}` | `lista.mercadolivre.com.br/KEYWORD` | ✅ Working |

---

## Decodo Services

### 1. Web Scraping API (RECOMMENDED for ML)

**Endpoint:** `https://scraper-api.decodo.com/v2/scrape`

**Auth:** Basic auth with token from `.env`:
```
DECODO_SCRAPING_TOKEN=VTAwMDA0MzkyODI6UFdfMWJlYWQzNDU3NWIwYTA1NTY5YzUyNmFhMTcxOThkNDdj
```

**Working call:**
```python
import requests, json, re
from bs4 import BeautifulSoup

resp = requests.post(
    'https://scraper-api.decodo.com/v2/scrape',
    headers={
        'Authorization': 'Basic VTAwMDA0MzkyODI6UFdfMWJlYWQzNDU3NWIwYTA1NTY5YzUyNmFhMTcxOThkNDdj',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    json={
        'url': 'https://lista.mercadolivre.com.br/cinto-couro',
        'proxy_pool': 'premium',
        'headless': 'html',
        'locale': 'pt-br',
        'geo': 'br'
    },
    timeout=120
)
data = resp.json()
html = data['results'][0]['content']
```

**ML product extraction from HTML:**
```python
soup = BeautifulSoup(html, 'html.parser')
product_links = soup.find_all('a', href=re.compile(r'/p/MLB'))

for link in product_links:
    mlb_match = re.search(r'(MLB\d+)', link.get('href', ''))
    if not mlb_match: continue
    mlb_id = mlb_match.group(1)

    # Walk up to poly-card parent
    card = link.find_parent('div', class_=re.compile(r'poly-card'))

    img = card.find('img', src=re.compile(r'mlstatic'))
    price = card.find(class_=re.compile(r'andes-money-amount__fraction'))
    title = card.find(class_=re.compile(r'poly-component__title'))
```

**Notes:**
- Returns 10-12 products per search page
- Each request takes ~30s
- `headless: "html"` is required (not `render_js`)
- `proxy_pool: "premium"` required for ML
- ML search URLs use hyphens: `cinto-couro-masculino` (NOT spaces)

---

### 2. Site Unblocker (via proxy)

**Proxy:** `https://unblock.decodo.com:60000`

**CRITICAL: Auth MUST use `-U` flag, NOT `-H "Proxy-Authorization"`:**
```bash
# CORRECT
curl -s -k -x https://unblock.decodo.com:60000 \
  -U "U0000441386:PW_159a92c0b34c5c320c7ed3c2f12b0291d" \
  -H "X-SU-Geo: Brazil" \
  -H "X-SU-Locale: pt-br" \
  -H "X-SU-Headless: html" \
  -H "X-SU-Markdown: 1" \
  "https://lista.mercadolivre.com.br/cinto-couro"

# WRONG — returns 0 bytes
-H "Proxy-Authorization: Basic $(echo -n 'token:pass' | base64)"
```

**Working tokens:**
- `U0000441386:PW_159a92c0b34c5c320c7ed3c2f12b0291d` ✅
- `U0000441264:PW_1f41093d66abfe4b6e56b797772d10b94` ✅
- `U0000434457:PW_17560792063f932882c0843ad92c0ed69` ❌ (rate limited)

**Returns:** Markdown format with product data (titles, images, prices)

---

### 3. Residential Proxy

**Endpoints:**
```
BR: span5nxws5:N_cCzf3txm12cn5HNj@br.decodo.com:10001-10005
US: span5nxws5:N_cCzf3txm12cn5HNj@us.decodo.com:10001-10005
ISP: sp2idylm9q:J41Ytm9rgWofr=V2nr@isp.decodo.com:10001-10010
```

**Usage:**
```bash
curl -x "http://span5nxws5:N_cCzf3txm12cn5HNj@br.decodo.com:10001" "https://httpbin.org/ip"
```

**Notes:** 6GB data available. Works for HTTP but ML redirects to account-verification without JS rendering. Use Scraping API for ML instead.

---

## Firecrawl

**API key:** `fc-c3559a554f884c65bdabd20d6cd4ba6c`

**Usage:**
```python
from firecrawl import FirecrawlApp
app = FirecrawlApp(api_key='fc-c3559a554f884c65bdabd20d6cd4ba6c')
result = app.scrape_url(url, formats=['markdown'], only_main_content=True)
md = result.markdown
```

**Best for:** Amazon BR/US product pages and best sellers. NOT for ML (blocked by login wall).

**Note:** Credits may be exhausted. Check before using.

---

## Amazon Scraping

### Via Firecrawl (preferred)
- Search: `https://www.amazon.com.br/s?k=KEYWORD&i=electronics`
- Best sellers: `https://www.amazon.com.br/gp/bestsellers/{department}/{node_id}`
- Product pages: `https://www.amazon.com.br/dp/{ASIN}`

### Via requests + BeautifulSoup (fallback)
```python
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...'}
resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Product cards
asins = re.findall(r'/dp/([A-Z0-9]{10})', resp.text)
# Images
images = re.findall(r'(https://m\.media-amazon\.com/images/I/[A-Z0-9]+\._AC_[^)]+\.jpg)', resp.text)
# Prices
prices = re.findall(r'class="a-price-whole"[^>]*>([^<]+)<', resp.text)
```

**Notes:**
- Amazon blocks HEAD requests (405) but GET works with User-Agent
- Some search terms return 0 results on Amazon BR
- Firecrawl credits are limited (~60 scrapes)

---

## ML Scraping Patterns

### Search pages (WORKING)
- URL: `https://lista.mercadolivre.com.br/SEARCH_TERM`
- Returns: 10-12 products with MLB IDs, titles, images, prices
- Images: `https://http2.mlstatic.com/...` or `https://...mlstatic.com/...`

### Individual product pages (BLOCKED)
- ML blocks all scraping methods for individual product pages
- JS-rendered, requires browser rendering

### Best sellers pages (WORKING via Decodo)
- URL: `https://www.mercadolivre.com.br/mais-vendidos/MLB{id}`
- Returns: Top products with sales data

### ML Anti-Bot
- ML uses a JavaScript challenge page (not login wall)
- Scraping API with `headless: "html"` bypasses it
- Direct requests get redirected to account-verification

---

## Product Insertion

```sql
INSERT INTO bronze_products 
  (source, source_id, title, category_l1, category_l2, category_l3, image_url, product_url, currency)
VALUES 
  ('arbitlens_brasil', 'ml:MLB123456', 'Product Title', 'Eletrônicos', 'L2', 'L3', 'IMAGE_URL', 'PRODUCT_URL', 'BRL');
```

**Before insert:** Check for duplicates:
```sql
SELECT source_id FROM bronze_products WHERE source='arbitlens_brasil' AND source_id='ml:MLB123456';
```

---

## Common Issues

| Issue | Cause | Fix |
|---|---|---|
| Decodo returns 0 bytes | Wrong auth format | Use `-U user:pass` not `-H Proxy-Authorization` |
| ML shows login wall | Direct requests without Decodo | Use Decodo Scraping API |
| Amazon 503 on HEAD | Bot detection | Use GET with User-Agent |
| Firecrawl 429 | Credits exhausted | Use requests+BeautifulSoup fallback |
| Images are placeholders | Broken scrape | Delete and re-scrape |
| L3 names don't match taxonomy | Wrong L2/L3 values | Update to match silver_categories |
