# Products-1688

Agente de scraping do 1688.com para o ImportaSimples.

## Quem sou

**Products-1688** é o agente responsável por buscar produtos no 1688.com (marketplace chinês) e sincronizar com o banco de dados compartilhado do ImportaSimples.

**Escopo:**
- ✅ Scraping de produtos no 1688 via MTOP API
- ✅ Upload de imagens pro GCS bucket
- ✅ Sincronização com ImportaSimples DB
- ❌ NÃO scrape de Mercado Livre / Amazon BR (outros agentes fazem)

## Estado Atual (V1 Production)

```
Produtos:      1557
Categorias:    9 L1, 24 L2, 38 L3, 82 N4
Imagens:       1557/1557 (100% GCS)
DB:            1557 em ImportaSimples (source='datalake')
Server:        http://136.111.212.52:3003/
Cron:          Sync diário 06:00 UTC
Repo:          github.com/diogochubatsu/products-1688
```

## Como funciona

### Pipeline

```
MTOP API → scrape_1688_mtop.py → bronze/ → migrate_to_importa.py → ImportaSimples DB
                                          → upload_images.py → GCS bucket
```

### Scripts

| Script | Função | Uso |
|--------|--------|-----|
| `scrape_1688_mtop.py` | Busca produtos no 1688 | `python3 scrape_1688_mtop.py --query "电钻" --pages 2` |
| `save_bronze.py` | Salva dados brutos | Chamado por outros scripts |
| `upload_images.py` | Envia imagens pro GCS | `python3 upload_images.py --limit 10` |
| `migrate_to_importa.py` | Sincroniza pro DB | `python3 migrate_to_importa.py --dry-run` |
| `api_server.py` | Frontend web | `python3 api_server.py` (port 3003) |

### MTOP API

O 1688 usa MTOP gateway (h5api.m.1688.com) — mesmo API que o app mobile.

**Vantagens:**
- Gratuito (sem proxy, sem cookies)
- Retorna: offerId, title, price, shop, image, bookedCount
- Funciona sem BaXia anti-bot

**Limitações:**
- ~20 produtos por página
- Rate limit não documentado (funciona bem com 1-2 req/s)

### Como buscar um produto

```python
from scrape_1688_mtop import scrape

# Buscar por keyword chinesa
results = scrape('电钻', pages=2)  # 40 produtos

# Cada resultado tem:
# - offer_id (int)
# - title (str, chinês)
# - price_cny (str)
# - shop (str)
# - image_url (str, alicdn.com)
# - booked_count (str, vendas mensais)
```

## Lições Aprendidas

### 1. MTOP é a melhor via
- Tentamos Firecrawl, Decodo SU, browser automation
- MTOP API é mais rápida, gratuita, e confiável

### 2. Imagens precisam de proxy
- URLs do alicdn.com são bloqueadas por hotlinking
- Solução: proxy via FastAPI ou GCS bucket

### 3. Schema simplificado funciona melhor
- Reduzimos de 32 para 14 campos
- Menos dados = menos problemas
- Campos mortos só confundem

### 4. Paths quebram quando se move scripts
- `Path(__file__).parent.parent` muda quando script move
- Sempre testar path relativo após mudanças

### 5.银 categories são compartilhadas
- `silver_categories` é a única fonte de verdade
- Cada agente contribui com seus mapeamentos
- Nunca modificar categorias de outros agentes

## Categorias 1688

### Estrutura (4 níveis)

```
L1: 服装鞋帽 (Vestuário)
  L2: 内衣 (Roupa Íntima)
    L3: 塑身衣 (Modeladores)
      L4: 提臀塑身 (Levanta-bumbum)
      L4: 连体塑身 (Corpo inteiro)
    L3: 内裤 (Cuecas)
      L4: 无痕内裤 (Sem costura)
    L3: 塑身裤 (Calças modeladoras)
      L4: 提臀塑裤 (Levanta-bumbum)
  L2: 袜子 (Meias)
    L3: 通用袜子 (Meias gerais)
```

### Categorias completas

| L1 | L2 | L3 | Produtos |
|----|----|----|----------|
| 服装鞋帽 | 内衣 | 塑身衣/内裤/塑身裤 | 150 |
| 美妆护肤 | 化妆工具 | 化妆刷/美妆蛋 | 118 |
| 电子数码 | 照明/安防 | 手电筒/摄像头 | 177 |
| 户外运动 | 健身/户外 | 哑铃/帐篷 | 180 |
| 五金工具 | 电动/手动 | 电钻/扳手 | 172 |
| 家居日用 | 浴室/卧室 | 毛巾架/枕头 | 180 |
| 母婴用品 | 童装/玩具 | 婴儿袜/魔尺 | 57 |
| 宠物用品 | 猫粮/狗用品 | 猫条/牵引绳 | 60 |
| 文具办公 | 笔记本/笔类 | A5本/中性笔 | 60 |

## Deploy

### Requisitos
- Python 3.11+
- psycopg2 (em /mnt/ssd/arbitlens/.venv/)
- google-cloud-storage (para GCS)

### Servidor
- FastAPI em port 3003
- HTML + JSON no mesmo servidor
- Acesso: http://136.111.212.52:3003/

### Cron
```bash
# Sync diário às 06:00 UTC
cd /mnt/ssd/1688-only
/mnt/ssd/arbitlens/.venv/bin/python3 scripts/production/migrate_to_importa.py
```

## Contato

- **Repo:** github.com/diogochubatsu/products-1688
- **DB:** importasimples_products (GCP Cloud SQL)
- **Bucket:** importasimples-intel-images (GCS)
