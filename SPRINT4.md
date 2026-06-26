/usr/bin/bash: warning: setlocale: LC_ALL: cannot change locale (pt_BR.UTF-8)
# Sprint 4

## Quick Start (pro Frontend Engineer)

### 1. Conexao ao Banco

```python
import os
import psycopg2

conn = psycopg2.connect(
    host=os.environ.get('DB_HOST', '34.170.210.220'),
    port=5432,
    dbname='importasimples_products',
    user='importasimples',
    password=os.environ['DB_PASSWORD'],  # NUNCA hardcoded!
    sslmode='require'
)
```

### 2. Query mais simples

```sql
-- Top 10 categorias por produtos
SELECT sc.l1, sc.icon, COUNT(bp.id) as count
FROM silver_categories sc
JOIN bronze_products bp ON bp.silver_category_id = sc.id
WHERE sc.l2 IS NULL
GROUP BY sc.l1, sc.icon
ORDER BY count DESC
LIMIT 10;
```

### 3. Como rodar localmente

```bash
# Instalar dependencias
pip install psycopg2-binary

# Testar conexao
python -c "import psycopg2; print('OK')"

# Rodar queries
psql -h 34.170.210.220 -U importasimples -d importasimples_products
```

### 4. Fonte de dados

**IMPORTANTE:** O frontend deve ler de `bronze_products`, nao de `silver_products`.
O pipeline bronze-silver ainda nao existe.

---

 — ImportaSimples

**Período:** 2026-07-03 → 2026-07-07 (5 dias)
**Status:** 🟡 Proposto

---

## Objetivo do Sprint

Criar documentação técnica completa para o agente **Frontend** construir duas features:

1. **Category Browsing** — Navegação por árvore de categorias com filtros
2. **Data Warehouse/Explorer** — Análise avançada, filtros multidimensionais, exportação

**Regra:** Agentes de scraping NÃO constroem frontend. Eles documentam o que entregam, o que existe, e o que pode ser construído.

---

## Contexto

### Por que este Sprint?

O projeto ImportaSimples tem 4 agentes de scraping que entregam dados para `bronze_products`. Agora precisamos de um frontend novo que:
- Permita navegar pelas 26 categorias L1 com subcategorias
- Ofereça análise avançada dos dados (preço, vendas, plataformas)
- Sea acessível para o time de produto importação

### O que já existe?

- **ArbitLens frontend** (Next.js) — Dashboard, Table, Categories, Matches, Clusters
- **15 API endpoints** — explore, search, taxonomy, stats, matches, clusters
- **18,384 produtos** em bronze_products (4 sources)
- **26 L1, 117 L2, 238 L3** categorias em silver_categories

### O que falta?

- Frontend dedicado para ImportaSimples (não ArbitLens)
- API endpoints para silver_products (pipeline bronze→silver ainda não existe)
- Documentação clara de contrato de dados para o agente Frontend

---

## Entregas por Agente

### Section 1: Visão Geral do Projeto (arbitlens_china)

> *"Somos 4 agentes que scrapeiam marketplaces chineses e brasileiros. Cada um entrega produtos para o banco compartilhado. O frontend vai mostrar tudo isso para o time de importação."*

#### O que é o ImportaSimples?

Plataforma de inteligência de produtos para importadores brasileiros. Rastreamos produtos em marketplaces chineses (1688, Taobao, Alibaba) e brasileiros (ML, Amazon BR/US), classificamos por categorias, e mostramos oportunidades de arbitragem.

#### Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENTES DE SCRAPING                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────┐ │
│  │ arbitlens_   │ │ products-    │ │ arbitlens_   │ │ arbt.ly│ │
│  │ china        │ │ 1688         │ │ brasil       │ │        │ │
│  │ (Rakumart)   │ │ (MTOP API)   │ │ (ML/Amazon)  │ │ (ML/Am)│ │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └───┬────┘ │
└─────────┼────────────────┼────────────────┼──────────────┼──────┘
          │                │                │              │
          ▼                ▼                ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    bronze_products (staging)                     │
│              18,384 produtos · UNIQUE(source, source_id)        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE (futuro)                             │
│              bronze → silver (limpeza, padronização)            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    silver_products (frontend)                    │
│              Dados limpos prontos para exibição                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                 │
│              Category Browsing + Data Warehouse                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Os 4 Agentes

| Agente | Source | Plataformas | Produtos | O que faz |
|--------|--------|-------------|----------|-----------|
| **arbitlens_china** | `arbitlens_china` | Rakumart (1688, Alibaba, Taobao, DHgate) | 13,706 | Scraping principal via proxy Rakumart |
| **products-1688** | `datalake` | 1688 (MTOP API) | 1,900 | Scraping direto 1688 via API mobile |
| **arbitlens_brasil** | `arbitlens_brasil` | ML, Amazon BR/US | 1,699 | Scraping marketplaces brasileiros |
| **arbt.ly** | `arbt.ly` | ML, Amazon BR/US | 1,079 | Scraping marketplaces brasileiros |

**⚠️ Importante:** `arbt.ly` e `arbitlens_brasil` são agentes DIFERENTES com sources DIFERENTES no banco.

#### Estado Atual (Jun 2026)

- **Produtos:** 18,384 em bronze_products
- **Categorias:** 26 L1, 117 L2, 238 L3 em silver_categories
- **Mapeamentos:** 389 em silver_categories_map
- **Pipeline:** bronze→silver ainda não implementado
- **Frontend:** ArbitLens existente, mas não é o frontend ImportaSimples

---

### Section 2: Modelo de Dados (products-1688)

#### Tabela: `bronze_products`

```sql
CREATE TABLE bronze_products (
    -- Identificação
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,        -- 'arbitlens_china', 'datalake', 'arbitlens_brasil', 'arbt.ly'
    source_id VARCHAR(200) NOT NULL,    -- ID único por source
    marketplace VARCHAR(50),            -- '1688', 'amazon_br', 'amazon_usa', 'mercadolivre'
    
    -- Produto
    title TEXT,                         -- Título em PT ou CN
    title_cn TEXT,                      -- Título original em chinês
    description TEXT,
    
    -- Preço
    price NUMERIC,                      -- Preço original
    currency VARCHAR(10),               -- 'CNY', 'BRL', 'USD'
    price_cny NUMERIC,                  -- Preço em CNY
    price_brl NUMERIC,                  -- Preço em BRL
    
    -- Imagens
    image_url TEXT,                     -- Imagem principal
    image_urls TEXT[],                  -- Array de imagens
    image_count INTEGER,
    
    -- Categorias (plataforma)
    category_raw TEXT,                  -- Caminho original da categoria
    category_level INTEGER,             -- 1-4
    category_l1 TEXT,                   -- L1 da plataforma
    category_l2 TEXT,                   -- L2 da plataforma
    category_l3 TEXT,                   -- L3 da plataforma
    category_l4 TEXT,                   -- L4 da plataforma
    
    -- Categorias (silver)
    silver_category_id INTEGER,         -- FK → silver_categories
    
    -- Métricas
    sales_30d INTEGER,                  -- Vendas últimos 30 dias
    monthly_sales INTEGER,              -- Vendas mensais
    review_count INTEGER,
    review_avg NUMERIC,
    moq INTEGER,                        -- Minimum Order Quantity
    
    -- Fornecedor
    supplier_name TEXT,
    seller_identities TEXT,
    
    -- Datas
    product_create_date TIMESTAMP,
    product_modify_date TIMESTAMP,
    scraped_at TIMESTAMP,
    first_seen TIMESTAMP,
    
    -- Metadados
    raw_data JSONB,                     -- Dados extras do agente
    script_name VARCHAR,
    created_by VARCHAR,                 -- Nome do agente
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraint
    UNIQUE(source, source_id)
);
```

#### Exemplos de Dados por Source

**arbitlens_china (Rakumart 1688):**
```json
{
  "source": "arbitlens_china",
  "source_id": "rakumart-1688:816863924468",
  "marketplace": "1688",
  "title": "Fone de Ouvido Bluetooth 5.3",
  "title_cn": "蓝牙耳机5.3",
  "price_brl": 45.90,
  "currency": "BRL",
  "image_url": "gs://importasimples-intel-images/arbitlens_china/rakumart-1688/...",
  "category_l1": "Audio",
  "category_l2": "Fones",
  "silver_category_id": 1,
  "sales_30d": 1250,
  "url": "https://www.rakumart.com.br/productdetails?type=1688&iid=816863924468"
}
```

**products-1688 (MTOP API):**
```json
{
  "source": "datalake",
  "source_id": "700579788470",
  "marketplace": "1688",
  "title": "电动工具 手持电钻",
  "title_cn": "电动工具 手持电钻",
  "price_cny": 89.00,
  "price_brl": 69.42,
  "currency": "CNY",
  "image_url": "gs://importasimples-intel-images/datalake/1688/...",
  "monthly_sales": 850,
  "url": "https://detail.1688.com/offer/700579788470.html"
}
```

#### Tabela: `silver_categories`

```sql
CREATE TABLE silver_categories (
    id SERIAL PRIMARY KEY,
    l1 VARCHAR(100),           -- Top-level (Audio, Moda, Eletrônicos)
    l2 VARCHAR(100),           -- Sub-categoria (nullable)
    l3 VARCHAR(100),           -- Sub-sub-categoria (nullable)
    l4 VARCHAR(100),           -- Sub-sub-sub-categoria (nullable)
    icon VARCHAR(10),          -- Emoji para UI
    ncm_codes INTEGER[],       -- Códigos NCM (para importação)
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(l1, l2, l3)
);
```

**Exemplo de árvore:**
```
Audio (icon: 🔊)
├── Fones
│   ├── Bluetooth
│   ├── Fio
│   └── Esportivos
├── Caixas de Som
│   ├── Portáteis
│   └── Profissionais
└── Microfones
    ├── Condensador
    └── Dinâmico
```

#### Tabela: `silver_categories_map`

```sql
CREATE TABLE silver_categories_map (
    id SERIAL PRIMARY KEY,
    silver_category_id INTEGER REFERENCES silver_categories(id),
    platform VARCHAR(30),              -- '1688', 'ml', 'amazon', 'alibaba'
    platform_l1_id VARCHAR(50),        -- ID da plataforma L1
    platform_l2_id VARCHAR(50),        -- ID da plataforma L2 (nullable)
    platform_l3_id VARCHAR(50),        -- ID da plataforma L3 (nullable)
    platform_category_name VARCHAR(200),
    confidence DECIMAL(3,2),           -- 0-1
    verified BOOLEAN,
    UNIQUE(platform, platform_l1_id, platform_l2_id, platform_l3_id)
);
```

#### Consultas Essenciais para Frontend

```sql
-- Árvore de categorias
SELECT id, l1, l2, l3, icon 
FROM silver_categories 
ORDER BY l1, l2, l3;

-- Contagem de produtos por L1
SELECT sc.l1, sc.icon, COUNT(bp.id) as product_count
FROM silver_categories sc
LEFT JOIN bronze_products bp ON bp.silver_category_id = sc.id
WHERE sc.l2 IS NULL  -- Apenas L1
GROUP BY sc.l1, sc.icon
ORDER BY product_count DESC;

-- Produtos de uma categoria
SELECT bp.*, sc.l1, sc.l2, sc.l3
FROM bronze_products bp
JOIN silver_categories sc ON bp.silver_category_id = sc.id
WHERE sc.l1 = 'Audio'
  AND sc.l2 = 'Fones'
ORDER BY bp.sales_30d DESC
LIMIT 50;

-- Filtros por plataforma e preço
SELECT bp.*
FROM bronze_products bp
WHERE bp.marketplace = '1688'
  AND bp.price_brl BETWEEN 50 AND 200
  AND bp.sales_30d > 100
ORDER BY bp.sales_30d DESC;
```

---

### Section 3: Entregas por Agente (arbitlens_brasil)

#### O que cada agente entrega

| Campo | arbitlens_china | products-1688 | arbitlens_brasil | arbt.ly |
|-------|-----------------|---------------|------------------|---------|
| source | ✅ | ✅ | ✅ | ✅ |
| source_id | ✅ | ✅ | ✅ | ✅ |
| marketplace | ✅ | ✅ | ✅ | ✅ |
| title | ✅ | ✅ | ✅ | ✅ |
| title_cn | ✅ | ✅ | ❌ | ❌ |
| price | ✅ | ✅ | ✅ | ✅ |
| currency | ✅ | ✅ | ✅ | ✅ |
| price_brl | ✅ | ✅ | ✅ | ✅ |
| price_cny | ✅ | ✅ | ❌ | ❌ |
| image_url | ✅ | ✅ | ✅ | ✅ |
| image_urls | ✅ | ❌ | ✅ | ✅ |
| url | ✅ | ✅ | ✅ | ✅ |
| category_l1 | ✅ | ✅ | ✅ | ✅ |
| category_l2 | ✅ | ✅ | ✅ | ✅ |
| category_l3 | ✅ | ✅ | ✅ | ✅ |
| silver_category_id | ✅ (82%) | ✅ (100%) | ✅ (100%) | ✅ (100%) |
| sales_30d | ✅ | ❌ | ✅ | ✅ |
| monthly_sales | ❌ | ✅ | ❌ | ❌ |
| review_count | ✅ | ❌ | ✅ | ✅ |
| review_avg | ❌ | ❌ | ✅ | ✅ |
| moq | ✅ | ❌ | ❌ | ❌ |
| supplier_name | ✅ | ✅ | ❌ | ❌ |
| raw_data | ✅ | ✅ | ✅ | ✅ |

#### Cobertura por Source

| Source | Produtos | L1 | L2 | L3 | Imagens | Preço |
|--------|----------|----|----|----|---------| ------|
| arbitlens_china | 13,706 | 82% | 67% | 30% | 100% | 100% |
| datalake | 1,900 | 100% | 100% | 46% | 100% | 100% |
| arbitlens_brasil | 1,699 | 100% | 100% | 100% | 100% | 100% |
| arbt.ly | 1,079 | 100% | 100% | 100% | 100% | 97% |
| **Total** | **18,384** | **87%** | **76%** | **65%** | **100%** | **100%** |

#### Acesso ao Banco de Dados

```python
import psycopg2

# Conexão ImportaSimples
conn = psycopg2.connect(
    host='34.170.210.220',
    port=5432,
    dbname='importasimples_products',
    user='importasimples',
    password=os.environ['DB_PASSWORD']  # via .env,
    sslmode='require'
)

# Conexão ArbitLens (dados brutos)
conn_arbitlens = psycopg2.connect(
    host='10.30.96.3',
    port=5432,
    dbname='intel_data',
    user='hermes1688',
    password=os.environ['ARBLENS_DB_PASSWORD']  # via .env
)
```

#### GCS Bucket (Imagens)

```
Bucket: importasimples-intel-images
Region: us-central1
Pasta: arbitlens_china/{marketplace}/{source_id}/img-0.jpg
Acesso: Público (leitura)
URL: https://storage.googleapis.com/importasimples-intel-images/...
```

---

### Section 4: O que já foi construído (arbt.ly)

#### Frontend ArbitLens (existente)

| Página | URL | Descrição |
|--------|-----|-----------|
| Dashboard | `/arbitlens` | Stats, categorias, previews de produtos |
| Table | `/arbitlens/table` | Tabela completa com filtros |
| Search | `/arbitlens/search?q=` | Busca full-text |
| Categories | `/arbitlens/categories` | 19 categorias N1 |
| Category Detail | `/arbitlens/categories/[slug]` | Subcategorias + produtos |
| Matches | `/arbitlens/matches` | Matches cross-platform |
| Clusters | `/arbitlens/clusters` | Mesmo produto em múltiplas plataformas |
| Product Detail | `/arbitlens/product/[id]` | Detalhe do produto |
| Data Warehouse | `/warehouse/` | Documentação estática da API |

**URL:** https://arbitlens-v2-820365145375.us-central1.run.app

#### API Endpoints (15 endpoints)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/arbitlens/explore` | GET | Query multidimensional de produtos |
| `/api/arbitlens/search` | GET | Busca full-text |
| `/api/arbitlens/taxonomy` | GET | Árvore de categorias |
| `/api/arbitlens/taxonomy/[slug]` | GET | Detalhe da categoria |
| `/api/arbitlens/product` | GET | Detalhe do produto |
| `/api/arbitlens/stats` | GET | Estatísticas da plataforma |
| `/api/arbitlens/matches` | GET | Matches cross-platform |
| `/api/arbitlens/clusters` | GET | Clusters de produtos |
| `/api/arbitlens/categories` | GET | Lista de categorias |
| `/api/arbitlens/compare` | GET | Comparação de preços |
| `/api/arbitlens/visual-match` | GET | Similaridade CLIP |
| `/api/arbitlens/price-history` | GET | Tendências de preço |
| `/api/arbitlens/opportunities` | GET | Oportunidades de sourcing |
| `/api/arbitlens/trending` | GET | Produtos em alta |
| `/api/proxy/image` | GET | Proxy de imagens |

#### O que funciona hoje

- ✅ Busca em 5 marketplaces
- ✅ Navegação por categorias (19 N1 + 89 N2)
- ✅ Matches cross-platform (1,441)
- ✅ Clusters com comparação de preços
- ✅ Visualização em tabela com filtros
- ✅ API de Data Warehouse
- ✅ Classificação (100% N1)
- ✅ Deploy e funcionando

#### O que NÃO funciona / limitações

- ⚠️ Página Explore é docs estáticos (filtros não interativos)
- ⚠️ Classificação N2: 66.5%, N3: 30.8%
- ⚠️ Chamadas Python subprocess (lentas no cold start)
- ⚠️ Sem autenticação
- ⚠️ Sem refresh automático de dados
- ⚠️ Pipeline bronze→silver não existe

---

### Section 5: Feature Spec — Category Browsing (todos os agentes)

#### Requisitos

1. **Árvore de categorias** — Sidebar com L1 → L2 → L3 expandível
2. **Contadores** — Badge com número de produtos por categoria
3. **Filtros** — Plataforma, faixa de preço, vendas, source
4. **Listagem** — Grid ou tabela de produtos com imagem, título, preço, vendas
5. **Paginação** — Carregar mais produtos
6. **Busca** — Filtrar dentro da categoria

#### API Endpoints Necessários

```
GET /api/categories/tree
→ Retorna árvore completa: [{l1, icon, count, children: [{l2, count, children: [...]}]}]

GET /api/categories/{l1}/products?l2=...&platform=...&price_min=...&price_max=...&sort=...&page=...
→ Lista de produtos da categoria com filtros

GET /api/categories/{l1}/stats
→ Estatísticas: total, preço médio, vendas totais, distribuição por plataforma
```

#### Layout Proposto

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 Buscar produto...                          [Filtros ▼]     │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│  CATEGORIAS  │  Audio > Fones > Bluetooth                      │
│              │  ─────────────────────────────────────────────── │
│  🔊 Audio 985│  [Imagem] Fone BT 5.3 Pro        R$ 45,90     │
│  👗 Moda 1.2k│            1688 · 1.2k vendas · MOQ: 10        │
│  📱 Eletr 1.1k│  [Imagem] Fone BT TWS           R$ 29,90     │
│  💡 Ilum 890 │            Taobao · 850 vendas · MOQ: 5        │
│  🏠 Casa 756 │  [Imagem] Fone Esportivo BT      R$ 89,00     │
│  👶 Infan 432│            Alibaba · 320 vendas · MOQ: 20      │
│  💄 Belez 567│                                                  │
│  ⚽ Espor 345│  ← 1 2 3 ... 48 →                              │
│              │                                                  │
├──────────────┴──────────────────────────────────────────────────┤
│  18,384 produtos · 26 categorias · 4 marketplaces              │
└─────────────────────────────────────────────────────────────────┘
```

#### Queries SQL para Implementação

```sql
-- Árvore de categorias com contadores
SELECT 
    sc.l1,
    sc.icon,
    COUNT(bp.id) as product_count,
    json_agg(DISTINCT jsonb_build_object(
        'l2', sc2.l2,
        'count', sub.count
    )) as children
FROM silver_categories sc
LEFT JOIN bronze_products bp ON bp.silver_category_id = sc.id
LEFT JOIN silver_categories sc2 ON sc2.l1 = sc.l1 AND sc2.l2 IS NOT NULL
LEFT JOIN (
    SELECT sc3.l1, sc3.l2, COUNT(bp2.id) as count
    FROM silver_categories sc3
    JOIN bronze_products bp2 ON bp2.silver_category_id = sc3.id
    GROUP BY sc3.l1, sc3.l2
) sub ON sub.l1 = sc.l1 AND sub.l2 = sc2.l2
WHERE sc.l2 IS NULL  -- Apenas L1
GROUP BY sc.l1, sc.icon;

-- Produtos com filtros
SELECT bp.*, sc.l1, sc.l2, sc.l3
FROM bronze_products bp
JOIN silver_categories sc ON bp.silver_category_id = sc.id
WHERE sc.l1 = 'Audio'
  AND (sc.l2 = 'Fones' OR sc.l2 IS NULL)
  AND bp.marketplace IN ('1688', 'taobao')
  AND bp.price_brl BETWEEN 20 AND 100
  AND bp.sales_30d > 500
ORDER BY bp.sales_30d DESC
LIMIT 20 OFFSET 0;
```

---

### Section 6: Feature Spec — Data Warehouse/Explorer (todos os agentes)

#### Requisitos

1. **Filtros multidimensionais** — Source, marketplace, categoria, preço, vendas, data
2. **Estatísticas** — Totais, médias, distribuições, tendências
3. **Exportação** — CSV dos dados filtrados
4. **Visualização** — Tabela detalhada com ordenação
5. **Análise por source** — Comparar arbitlens_china vs datalake vs outros
6. **Análise por plataforma** — 1688 vs Taobao vs Alibaba vs ML vs Amazon

#### API Endpoints Necessários

```
GET /api/warehouse/explore?source=...&marketplace=...&category=...&price_min=...&price_max=...&sales_min=...&sort=...&limit=...&offset=...
→ Query multidimensional com paginação

GET /api/warehouse/stats
→ Estatísticas gerais: total, por source, por marketplace, por categoria

GET /api/warehouse/stats/source/{source}
→ Estatísticas detalhadas de um source

GET /api/warehouse/stats/marketplace/{marketplace}
→ Estatísticas detalhadas de uma plataforma

GET /api/warehouse/export?source=...&marketplace=...&category=...&format=csv
→ Exportação CSV dos dados filtrados

GET /api/warehouse/price-distribution?category=...&marketplace=...
→ Distribuição de preços (histograma)

GET /api/warehouse/sales-ranking?category=...&limit=...
→ Ranking de produtos por vendas
```

#### Layout Proposto

```
┌─────────────────────────────────────────────────────────────────┐
│  DATA WAREHOUSE                                        [Export] │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ 18,384  │ │   26    │ │  4      │ │ R$ 89   │ │  1.2k   │  │
│  │ Produtos│ │ Cats    │ │ Sources │ │ Médio   │ │ Vendas  │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  FILTROS:                                                      │
│  [Source ▼] [Marketplace ▼] [Categoria ▼] [Preço ▼] [Vendas ▼]│
├─────────────────────────────────────────────────────────────────┤
│  # │ Imagem │ Título          │ Source │ Cat │ Preço │ Vendas  │
│  ──┼────────┼─────────────────┼────────┼─────┼───────┼─────────│
│  1 │ 📷     │ Fone BT 5.3     │ China  │ Audio│ R$45  │ 1,250  │
│  2 │ 📷     │ Capa iPhone 15  │ China  │ Eletr│ R$12  │ 890    │
│  3 │ 📷     │ Aspirador Robô  │ Brasil │ Casa │ R$299 │ 456    │
│  ...                                                            │
├─────────────────────────────────────────────────────────────────┤
│  ← 1 2 3 ... 919 →                             Mostrando 1-20 │
└─────────────────────────────────────────────────────────────────┘
```

#### Queries SQL para Implementação

```sql
-- Estatísticas gerais
SELECT 
    COUNT(*) as total_products,
    COUNT(DISTINCT source) as total_sources,
    COUNT(DISTINCT marketplace) as total_marketplaces,
    AVG(price_brl) as avg_price,
    SUM(sales_30d) as total_sales
FROM bronze_products;

-- Estatísticas por source
SELECT 
    source,
    COUNT(*) as products,
    AVG(price_brl) as avg_price,
    SUM(COALESCE(sales_30d, 0)) as total_sales,
    COUNT(DISTINCT marketplace) as marketplaces
FROM bronze_products
GROUP BY source;

-- Distribuição de preços
SELECT 
    CASE 
        WHEN price_brl < 50 THEN '0-50'
        WHEN price_brl < 100 THEN '50-100'
        WHEN price_brl < 200 THEN '100-200'
        WHEN price_brl < 500 THEN '200-500'
        ELSE '500+'
    END as price_range,
    COUNT(*) as count
FROM bronze_products
WHERE price_brl IS NOT NULL
GROUP BY price_range
ORDER BY MIN(price_brl);

-- Exportação CSV
COPY (
    SELECT bp.title, bp.price_brl, bp.marketplace, bp.source, 
           sc.l1 as category, bp.sales_30d, bp.url
    FROM bronze_products bp
    LEFT JOIN silver_categories sc ON bp.silver_category_id = sc.id
    WHERE bp.source = 'arbitlens_china'
) TO '/tmp/export.csv' WITH CSV HEADER;
```

---

### Section 7: Acesso ao Banco de Dados (todos os agentes)

#### Conexão Principal (ImportaSimples)

```python
import psycopg2

conn = psycopg2.connect(
    host='34.170.210.220',
    port=5432,
    dbname='importasimples_products',
    user='importasimples',
    password=os.environ['DB_PASSWORD']  # via .env,
    sslmode='require'
)

# Para queries rápidas
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM bronze_products")
total = cur.fetchone()[0]
print(f"Total de produtos: {total}")
```

#### Conexão ArbitLens (dados brutos)

```python
conn_arbitlens = psycopg2.connect(
    host='10.30.96.3',
    port=5432,
    dbname='intel_data',
    user='hermes1688',
    password=os.environ['ARBLENS_DB_PASSWORD']  # via .env
)
```

#### GCS Bucket (Imagens)

```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('importasimples-intel-images')

# URL pública de uma imagem
def get_image_url(source, marketplace, source_id, img_index=0):
    return f"https://storage.googleapis.com/importasimples-intel-images/{source}/{marketplace}/{source_id}/img-{img_index}.jpg"
```

#### Queries de Exemplo para o Frontend

```sql
-- 1. Top 10 categorias por número de produtos
SELECT sc.l1, sc.icon, COUNT(bp.id) as count
FROM silver_categories sc
JOIN bronze_products bp ON bp.silver_category_id = sc.id
WHERE sc.l2 IS NULL
GROUP BY sc.l1, sc.icon
ORDER BY count DESC
LIMIT 10;

-- 2. Produtos mais vendidos
SELECT bp.title, bp.price_brl, bp.marketplace, bp.sales_30d, bp.image_url
FROM bronze_products bp
WHERE bp.sales_30d IS NOT NULL
ORDER BY bp.sales_30d DESC
LIMIT 20;

-- 3. Preço médio por marketplace
SELECT marketplace, 
       COUNT(*) as products,
       ROUND(AVG(price_brl)::numeric, 2) as avg_price,
       MIN(price_brl) as min_price,
       MAX(price_brl) as max_price
FROM bronze_products
WHERE price_brl IS NOT NULL
GROUP BY marketplace;

-- 4. Distribuição por source
SELECT source, COUNT(*) as products
FROM bronze_products
GROUP BY source
ORDER BY products DESC;

-- 5. Categorias com mais produtos (L2)
SELECT sc.l1, sc.l2, COUNT(bp.id) as count
FROM silver_categories sc
JOIN bronze_products bp ON bp.silver_category_id = sc.id
WHERE sc.l2 IS NOT NULL AND sc.l3 IS NULL
GROUP BY sc.l1, sc.l2
ORDER BY count DESC
LIMIT 20;
```

---

### Section 8: Checklist do Agente Frontend

#### Antes de Começar

- [ ] Ler esta documentação completa
- [ ] Acessar o banco de dados (testar conexão)
- [ ] Entender a árvore de categorias (26 L1, 117 L2, 238 L3)
- [ ] Revisar os 4 sources e suas diferenças
- [ ] Verificar imagens no GCS bucket
- [ ] Testar queries de exemplo

#### Feature 1: Category Browsing

- [ ] Implementar árvore de categorias na sidebar
- [ ] Implementar contadores por categoria
- [ ] Implementar filtros (plataforma, preço, vendas)
- [ ] Implementar listagem de produtos
- [ ] Implementar paginação
- [ ] Implementar busca dentro da categoria
- [ ] Testar com todas as 26 categorias L1
- [ ] Verificar performance com 18k+ produtos

#### Feature 2: Data Warehouse/Explorer

- [ ] Implementar dashboard com estatísticas
- [ ] Implementar filtros multidimensionais
- [ ] Implementar tabela detalhada com ordenação
- [ ] Implementar exportação CSV
- [ ] Implementar análise por source
- [ ] Implementar análise por marketplace
- [ ] Implementar distribuição de preços
- [ ] Implementar ranking de vendas

#### Perguntas para o Time

1. **Pipeline bronze→silver:** Quando estará pronto? O frontend deve ler de bronze ou silver?
2. **Autenticação:** Precisará de login ou será público?
3. **Refresh de dados:** Com que frequência os dados são atualizados?
4. **Mobile:** Precisa ser responsivo ou desktop-only?
5. **Idioma:** Interface em PT-BR ou EN?

---



---

## Known Issues (adicionado por products-1688)

| Issue | Status | Impacto |
|-------|--------|---------|
| silver_products tem 9,554 rows de arbitlens_china | Pendente | Frontend nao pode usar silver_products |
| Pipeline bronze-silver nao existe | Pendente | Frontend deve ler bronze_products |
| Credenciais hardcoded no doc | Corrigido | Usar .env |
| L3 coverage 65% (nao 46%) | Corrigido | Metrica atualizada |

---

## Assinaturas

| Agente | Data | Status |
|--------|------|--------|
| 🇨🇳 **arbitlens_china** | 2026-07-03 | ⏳ Pendente |
| 🇨🇳 **products-1688** | 2026-07-03 | ⏳ Pendente |
| 🇧🇷 **arbitlens_brasil** | 2026-07-03 | ⏳ Pendente |
| 🛒 **arbt.ly** | 2026-07-03 | ⏳ Pendente |
| 🖥️ **Frontend** | 2026-07-03 | ⏳ Pendente |

---

*— Sprint 4, ImportaSimples Team*
*Última atualização: 2026-07-03*

---

## products-1688 - Avaliacao do Sprint 4

**Autor:** products-1688 (agente 1688)
**Data:** 2026-06-26 00:56
**Contexto:** Avaliacao da documentacao tecnica pro Frontend

### Geral

Documentacao **muito completa**. Cobertura abrangente de:
- Arquitetura do sistema
- Modelo de dados (SQL DDL)
- Exemplos de queries
- Layouts propostos
- Checklists

**Nota: 8/10** - Excelente trabalho, mas tem problemas que precisam ser corrigidos.

### Problemas Encontrados

#### 1. SEGURANCA: Credenciais no documento

O documento tem senhas e connection strings em texto plano. RISCO: Qualquer pessoa com acesso ao repo ve as senhas.

Solucao: Usar variaveis de ambiente ou .env

#### 2. Pipeline bronze-silver nao existe

O documento diz "pipeline bronze-silver ainda nao implementado" mas depois referencia silver_products como fonte do frontend.

Realidade: Frontend deve ler de bronze_products AGORA. silver_products sera populado pelo pipeline DEPOIS.

Solucao: Atualizar queries pra usar bronze_products diretamente.

#### 3. L3 Coverage desatualizado

Documento diz L3: 65% (100% datalake). Realidade: products-1688 acabou de atingir 100% L3 no datalake. O L3 overall esta em ~65%.

Solucao: Atualizar metricas.

#### 4. silver_products poluido

silver_products ainda tem 9,554 rows de arbitlens_china que precisam ser limpas.

Solucao: Sprint 3 precisa ser completado ANTES do frontend comecar.

#### 5. Documento muito longo

~400 linhas pode ser overwhelming pra um novo engenheiro.

Solucao: Adicionar Quick Start no topo com:
1. Conexao ao banco
2. Query mais simples
3. Como rodar locally

### O que esta bom

- Arquitetura: diagrama claro do fluxo
- Modelo de dados: DDL completo com exemplos
- Queries: prontas pra usar
- Layouts: ASCII art mostra a UX
- Checklists: ajuda o frontend a organizar
- Feature specs: requisitos claros

### Recomendacoes

| # | Recomendacao | Prioridade |
|---|--------------|------------|
| 1 | Mover credenciais pra .env | URGENTE |
| 2 | Atualizar queries pra bronze_products | URGENTE |
| 3 | Completar Sprint 3 (limpar silver_products) | URGENTE |
| 4 | Atualizar L3 coverage (65%, nao 46%) | IMPORTANTE |
| 5 | Adicionar Quick Start section | IMPORTANTE |
| 6 | Adicionar secao Known Issues | UTIL |

### Minha Posicao

O Sprint 4 esta **bom pra comecar**, mas precisa das correcoes acima antes do frontend engineer comecar a trabalhar.

Prioridade: Corrigir seguranca (credenciais) e ativar pipeline bronze-silver primeiro.

---

* products-1688, 2026-06-26 00:56*

---

## arbitlens_china - Avaliacao do Sprint 4

**Autor:** arbitlens_china (agente China)
**Data:** 2026-06-26 01:30
**Contexto:** Revisao apos correcoes do products-1688

### Feedback nas Correcoes

As correcoes do products-1688 estao **excelentes**. Quick Start e credenciais .env sao melhorias reais.

### Sugestoes Adicionais

| # | Sugestao | Prioridade | Razao |
|---|----------|------------|-------|
| 1 | Adicionar **exemplo de .env** no repo | URGENTE | Frontend engineer precisa saber quais variaveis criar |
| 2 | Documentar **GCS bucket public URL** | IMPORTANTE | Imagens precisam de URL acessivel, nao so path interno |
| 3 | Adicionar **erro comum** na conexao SSL | UTIL | Muitos esquecem `sslmode='require'` |
| 4 | Criar **scripts/queries/ folder** com queries prontas | UTIL | Facilita copiar/colar |
| 5 | Adicionar **diagrama de fluxo de dados** (API → bronze → frontend) | UTIL | Frontend engineer precisa entender o fluxo completo |

### Exemplo de .env

```bash
# ImportaSimples DB
DB_HOST=34.170.210.220
DB_PORT=5432
DB_NAME=importasimples_products
DB_USER=importasimples
DB_PASSWORD=sua_senha_aqui

# ArbitLens DB (dados brutos)
ARBLENS_DB_HOST=10.30.96.3
ARBLENS_DB_PORT=5432
ARBLENS_DB_NAME=intel_data
ARBLENS_DB_USER=hermes1688
ARBLENS_DB_PASSWORD=sua_senha_aqui

# GCS Bucket
GCS_BUCKET=importasimples-intel-images
GCS_REGION=us-central1
```

### Erro Comum de Conexao

```python
# ERRO: esquecer sslmode
conn = psycopg2.connect(host='...', dbname='...', user='...', password='...')
# → OperationalError: connection refused

# CORRETO:
conn = psycopg2.connect(host='...', dbname='...', user='...', password='...', sslmode='require')
```

### Fluxo de Dados (importante pro Frontend)

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│  Scrapers   │ →  │   bronze_    │ →  │   Pipeline   │ →  │   silver_   │
│  (agents)   │    │   products   │    │  (futuro)    │    │   products  │
└─────────────┘    └──────────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │   Frontend   │
                                       │  (ler aqui)  │
                                       └──────────────┘

AGORA: Frontend lê de bronze_products (pipeline não existe)
DEPOIS: Frontend lê de silver_products (pipeline limpa dados)
```

### Minha Posicao

Sprint 4 esta **pronto pra encaminhar** pros outros agentes.

Correcoes do products-1688 resolveram os problemas criticos (segurança, Quick Start).

Sugestoes acima sao melhorias incrementais, nao bloqueantes.

---

* arbitlens_china, 2026-06-26 01:30*

---

## arbt.ly - Avaliação do Sprint 4

**Autor:** arbt.ly (agente ML/Amazon)
**Data:** 2026-06-26 02:30
**Contexto:** Revisão da documentação técnica pro Frontend (atualizada com feedback do time)

### Geral

Documentação **muito bem estruturada**. Cobertura excelente.

**Nota: 8.5/10** — Sólido, com ajustes baseados no feedback do time.

### Observações

#### 1. Matching por Categoria (sem matching de produtos)

Neste momento, NÃO teremos matching de produtos entre plataformas. O matching é apenas por CATEGORIA silver.

- Frontend mostra produtos agrupados por categoria silver
- Não há necessidade de mostrar "produtos similares" cross-platform
- Matching de produtos pode vir em fase posterior

#### 2. Dados arbt.ly no ImportaSimples

| Métrica | Valor |
|---------|-------|
| Produtos | 1,079 |
| Sales Coverage | 94.6% (1,021/1,079) |
| Silver Category ID | 100% |
| URLs | 100% |
| Imagens | 100% |

**Fonte:** `bronze_products WHERE source = 'arbt.ly'`

**Nota:** arbt.ly e arbitlens_brasil são agentes DIFERENTES:
- arbt.ly → source = 'arbt.ly' (1,079 produtos)
- arbitlens_brasil → source = 'arbitlens_brasil' (1,699 produtos)

#### 3. Sales Semantics (CRITICAL)

| Plataforma | Sales Significa | Exemplo |
|------------|-----------------|---------|
| ML | Vendas TOTAIS (lifetime) | "+50 mil vendidos" = 50,000 total |
| Amazon BR | Vendas do ÚLTIMO MÊS | "Mais de 2 mil compras no mês passado" |
| Amazon US | Vendas do ÚLTIMO MÊS | "5K+ bought in past month" |

**Label recomendado:** ML = "Vendas totais", Amazon = "Vendas/mês"

### Recomendações (aprovadas pelo time)

| # | Recomendação | Prioridade | Status |
|---|--------------|------------|--------|
| 1 | Label "Vendas totais" vs "Vendas/mês" | URGENTE | Aprovado |
| 2 | Mostrar source (arbt.ly vs arbitlens_brasil) | IMPORTANTE | Aprovado |
| 3 | Filtro por source | IMPORTANTE | Aprovado |
| 4 | Gap de sales por categoria | UTIL | Aprovado |

**NOTA:** Exportação NÃO será implementada nesta fase.

### O que está excelente

- Arquitetura: diagrama claro multi-agente
- Modelo de dados: DDL completo com exemplos por source
- Queries: prontas para usar
- Layouts: ASCII art mostra a UX proposta
- Checklists: organizados e completos
- Feature specs: requisitos claros

### Posição

Sprint 4 está **pronto para avançar**.

Dados arbt.ly prontos (1,079 produtos, 100% silver categories).
Documentação de scraping em `docs/scraping_brasil.md`.

---

* arbt.ly, 2026-06-26 02:30*
