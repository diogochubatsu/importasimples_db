# Products-1688

Agente de scraping do 1688.com para o ImportaSimples.

## Quem sou

**Products-1688** é o agente responsável por buscar produtos no 1688.com (marketplace chinês) e sincronizar com o banco de dados compartilhado do ImportaSimples.

**Escopo:**
- ✅ Scraping de produtos no 1688 via MTOP API
- ✅ Upload de imagens pro GCS bucket
- ✅ Sincronização com ImportaSimples DB
- ❌ NÃO scrape de Mercado Livre / Amazon BR (outros agentes fazem)

## Estado Atual (2026-07-02)

```
Produtos:      4.005
Fonte:         1688 (source='1688')
Categorias:    9 L1, 31 L2, 176 L3
L3 com >=10:   176/176 (100%) ✅
Imagens:       4.005/4.005 (100%) ✅
URLs:          4.005/4.005 (100%) ✅
Tradução:      99.7% (1.894/1.899)
DB:            4.005 em ImportaSimples (source='1688')
Repo:          github.com/diogochubatsu/products-1688
```

## Comportamento do Marketplace 1688

### O que funciona

1. **MTOP API** — Busca de produtos
   - Gratuito, sem proxy, sem cookies
   - Retorna: offerId, title, price, shop, image, bookedCount, detail_url
   - Funciona sem BaXia anti-bot
   - ~20 produtos por página

2. **Decodo Scraping API** — Verificação de URLs
   - Endpoint: scraper-api.decodo.com/v2/scrape
   - Auth: Basic (username:password em base64)
   - Retorna HTML renderizado com headless Chrome
   - ~30 segundos por request
   - Rate limit: ~100 requests/mês (plano free)

3. **Decodo Site Unblocker** — Verificação de URLs
   - Endpoint: unblock.decodo.com:60000
   - Auth: Basic (username:password)
   - Headers obrigatórios:
     - X-SU-Geo: China
     - X-SU-Locale: zh-cn
     - X-SU-Headless: html
     - X-SU-Markdown: 1
   - Retorna Markdown pronto
   - ~30-45 segundos por request

### O que NÃO funciona

1. **Acesso direto a detail.1688.com**
   - HTTP 200 mas conteúdo é captcha (BaXia)
   - 2.5KB de JS anti-bot, não produto
   - Precisa de proxy ou headless Chrome

2. **Residential/ISP proxies sem headless**
   - Conexão funciona (IP retorna)
   - MAS: 1688 redireciona pra login
   - Detecta IP não-chinês → login wall
   - Detecta bot → BaXia captcha

3. **China proxy (cn.decodo.com)**
   - IP chinês confirmado
   - MAS: 1688 detecta como bot
   - Retorna "action":"captcha"
   - Precisa de browser real (headless Chrome)

### Anti-bot BaXia (1688)

4 camadas de detecção:

1. **IP Reputation** — Datacenter IPs bloqueados
2. **User-Agent** — Spider detection
3. **AWSC Captcha** — JS-based challenge
4. **Session/Cookie** — Login wall

**Solução:** Scraping API ou Site Unblocker (usam headless Chrome)

### URLs do 1688

Padrão: `https://detail.1688.com/offer/{offer_id}.html`

- Funcionam com headless Chrome
- Não funcionam com requests diretos
- Precisam de proxy chinês OU headless
- Mobile: `https://detail.m.1688.com/offer/{offer_id}.html`

## Pipeline

```
MTOP API → scrape_1688_mtop.py → bronze/ → migrate_to_importa.py → ImportaSimples DB
                                          → upload_images.py → GCS bucket
```

## Scripts

| Script | Função | Uso |
|--------|--------|-----|
| `scrape_1688_mtop.py` | Busca produtos no 1688 | `python3 scrape_1688_mtop.py --query "电钻" --pages 2` |
| `save_bronze.py` | Salva dados brutos | Chamado por outros scripts |
| `upload_images.py` | Envia imagens pro GCS | `python3 upload_images.py --limit 10` |
| `migrate_to_importa.py` | Sincroniza pro DB | `python3 migrate_to_importa.py --dry-run` |
| `verify_urls.py` | Verifica URLs via Decodo | `python3 verify_urls.py` |

## MTOP API

O 1688 usa MTOP gateway (h5api.m.1688.com) — mesmo API que o app mobile.

**Campos retornados:**
- `offer_id` (int) — ID do produto
- `title` (str) — Título em chinês
- `price_cny` (float) — Preço em RMB
- `shop` (str) — Nome da loja
- `province` (str) — Província
- `city` (str) — Cidade
- `image_url` (str) — URL da imagem (alicdn.com)
- `detail_url` (str) — URL da página do produto
- `booked_count` (int) — Vendas mensais
- `repurchase_rate` (str) — Taxa de recompra

## Credenciais Decodo

### Scraping API
```
Endpoint: https://scraper-api.decodo.com/v2/scrape
Auth: Basic VTAwMDA0NDEzOTM6UFdfMWNkNzRlNTdjZmY3MjdmOTdiZTczNDM4NDNhN2Y4NjYw
```

### Site Unblocker
```
Endpoint: https://unblock.decodo.com:60000
User: U0000446415
Pass: PW_175269699c8c2859bc8499cc9161922fb
Headers:
  X-SU-Geo: China
  X-SU-Locale: zh-cn
  X-SU-Headless: html
  X-SU-Markdown: 1
```

### Residential Proxy
```
Gateway: gate.decodo.com:10001-10005
User: user-span5nxws5-continent-na
Pass: N_cCzf3txm12cn5HNj
NOTA: Funciona mas 1688 bloqueia IP não-chinês
```

## Categorias

### L1 (9 categorias)

| L1 | Produtos |
|----|----------|
| 家居日用 (Casa) | 931 |
| 电子数码 (Eletrônicos) | 615 |
| 户外运动 (Esportes) | 496 |
| 服装鞋帽 (Vestuário) | 445 |
| 五金工具 (Ferramentas) | 341 |
| 美妆护肤 (Beleza) | 223 |
| 宠物用品 (Pets) | 153 |
| 文具办公 (Escritório) | 132 |
| 母婴用品 (Infantil) | 112 |

### Cobertura L3
- Total L3: 176
- L3 com >= 10 products: 176 (100%) ✅

## Lições Aprendidas

### 1. MTOP é a melhor via de scraping
- Gratuito, rápido, confiável
- Retorna dados completos incluindo detail_url

### 2. URLs precisam de verificação
- HTTP 200 não garante conteúdo real
- Precisa de headless Chrome pra verificar
- Scraping API ou Site Unblocker

### 3. Proxies sem headless não funcionam pra 1688
- BaXia detecta bots mesmo com IP chinês
- Precisa de browser fingerprint

### 4. Source naming importa
- 'datalake' → '1688' (padronizado)
- Mappings precisam bater com source

### 5. L3 com >= 10 products é viável
- Scraping de 2.106 products adicionais
- 176 L3 categories todas >= 10 products

## Contato

- **Repo:** github.com/diogochubatsu/products-1688
- **DB:** importasimples_products (GCP Cloud SQL)
- **Bucket:** importasimples-intel-images (GCS)
