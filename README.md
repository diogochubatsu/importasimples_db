/usr/bin/bash: warning: setlocale: LC_ALL: cannot change locale (pt_BR.UTF-8)
# ImportaSimples Database

Banco de dados compartilhado para todos os agentes ImportaSimples.

> **⚠️ IMPORTANTE:** `silver_categories` é a **única fonte de verdade** para categorização de produtos. TODOS os agentes devem usá-la e contribuir com seus mapeamentos.

## Quick Start

```python
import psycopg2
from category_resolver import resolve_category

conn = psycopg2.connect(
    host='34.170.210.220', port=5432,
    dbname='importasimples_products',
    user='importasimples', password='R{[{f<VajbC{<kvU',
    sslmode='require'
)

# Resolver categoria de um produto
result = resolve_category(conn, platform='1688', l1='67', l2='2127')
# → {'silver_category_id': 4, 'l1': 'Iluminação', 'confidence': 0.9}
```

## Agentes

Cada agente é **responsável** por adicionar seus mapeamentos de categoria em `silver_categories_map`.

| Agente | Platform | Status | O que deve fazer |
|---|---|---|---|
| 🇨🇳 **China (ArbitLens)** | 1688, Alibaba, Taobao, DHgate | ✅ 157 mappings adicionados | Completar mapeamentos L2/L3 |
| 🛒 **ArbitLens (arbt.ly)** | ML, Amazon BR/US | ✅ 38 mappings adicionados (19 ML + 19 Amazon) | Completar mapeamentos L2/L3 |
| 🛒 **Mercado Livre** | MLB categories | ✅ 38 mappings (via arbt.ly) | — |
| 📦 **Amazon** | Amazon BR/US | ✅ 38 mappings (via arbt.ly) | — |

**Regra:** Cada agente usa `add_platform_mapping()` para registrar seus IDs de plataforma → `silver_categories`. Ninguém modifica os mappings de outros.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│  silver_categories                                          │
│  ← ÚNICA FONTE DE VERDADE para categorias                  │
│  ← Compartilhada por TODOS os agentes                      │
│  ← 19 L1, 27 L2, 20 L3 (atualmente)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  silver_categories_map                                      │
│  ← Cada agente adiciona seus mapeamentos                   │
│  ← 1688: 157 mappings (feito)                               │
│  ← ML: 38 mappings (feito via arbt.ly)                       │
│  ← Amazon: 38 mappings (feito via arbt.ly)                   │


└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  bronze_products                                            │
│  ← Produtos com silver_category_id (FK)                     │
│  ← Cada agente resolve e salva sua categoria               │
└─────────────────────────────────────────────────────────────┘
```

## Como Usar

### 1. Resolver categoria

```python
from category_resolver import resolve_category

result = resolve_category(conn, platform='1688', l1='67', l2='2127', l3='1033103')
# Tenta L3 → L2 → L1 (mais específico primeiro)
```

### 2. Salvar no banco

```python
cur.execute("""
    UPDATE bronze_products
    SET silver_category_id = %s, category_l1 = %s
    WHERE source = %s AND source_id = %s
""", (result['silver_category_id'], result['l1'], source, source_id))
```

### 3. Adicionar mapeamentos da sua plataforma

```python
from category_resolver import add_platform_mapping

# Exemplo ML:
add_platform_mapping(conn, 'ml', 'MLB3835', silver_category_id=1, category_name='Áudio')

# Exemplo Amazon:
add_platform_mapping(conn, 'amazon', '2407760', silver_category_id=3, category_name='Electronics')
```

### 4. Criar novas categorias L2/L3

```python
from category_resolver import ensure_category

cat_id = ensure_category(conn, l1='Audio', l2='Fones', l3='Bluetooth')
```

## Categorias L1 (19)

| ID | Nome | Ícone |
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

## Mapeamentos 1688 → Silver

| ID 1688 | Nome Chinês | Silver L1 | Confiança |
|---|---|---|---|
| 2 | 服装/服饰 | Moda | 0.90 |
| 4 | 鞋靴 | Calçados | 0.90 |
| 6 | 数码/消费电子 | Eletrônicos | 0.50 |
| 7 | 手机/手机配件 | Eletrônicos | 0.70 |
| 18 | 运动/户外 | Esportes | 0.80 |
| 53 | 美容/个护 | Beleza | 0.90 |
| 66 | 工具/五金 | Ferramentas | 0.90 |
| 67 | 照明/LED | Iluminação | 0.90 |
| 70 | 宠物用品 | Pets | 0.90 |

*Ver `silver_categories_map` para lista completa (157 mappings)*

## Cobertura (arbitlens_china)

| Nível | Produtos | % |
|---|---|---|
| L1 | 11,192 | 81.7% |
| L2 | 9,190 | 67.1% |
| L3 | 4,163 | 30.4% |

## Arquivos

```
importasimples_db/
├── README.md                    # Este arquivo
├── CONTRIBUTING.md              # Guia para novos agentes
├── category_resolver.py         # Utilitário compartilhado
├── schema.sql                   # Schema do banco
├── test_resolver.py             # Script de teste
├── requirements.txt             # Dependências
├── platform_categories/         # Dados exportados (JSON)
│   ├── silver_categories.json
│   └── silver_categories_map.json
└── arbitlens_china/             # Scripts do agente China
    ├── scripts/
    └── docs/
```

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para guia completo.

**Regras:**
1. Não modificar categorias L1 em `silver_categories`
2. Não modificar mapeamentos de outros agentes
3. Adicionar sua pasta com scripts e docs
4. Documentar seus mapeamentos
