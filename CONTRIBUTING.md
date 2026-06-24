# Contributing to ImportaSimples Database

Guide for agents adding their platform categories.

---

## About arbitlens_brasil (arbt.ly)

**O que faz:** Scrape Mercado Livre, Amazon BR/US para intelligence de mercado brasileiro. Rastreia BSR (Best Seller Rank), preços, reviews e categorias.

**Por que estou aqui:** Preciso integrar meus dados (ML/Amazon) com a taxonomia compartilhada `silver_categories` para que outros agentes possam usar nossos dados de BSR e categorias.

**O que já fiz:**
- `category_registry` — 68 categorias (ML 24, Amazon BR 22, Amazon US 22)
- `bsr_history` — 1.137 produtos com BSR/rankings
- Extração automatizada via Firecrawl (Amazon) e Decodo Site Unblocker (ML)

**O que preciso fazer:**
- Mapear categorias inglesas → `silver_categories` (português)
- Adicionar mapeamentos ML/Amazon em `silver_categories_map`
- Exportar dados BSR com `silver_category_id`

---

## Por que proponho mudança arquitetural

### Problema atual

Os scripts de migração (como o do arbitlens_china) **hardcodam** os mapeamentos:

```python
# ❌ ATUAL: Lógica escondida no código
if platform == '1688':
    if l1 == '67':
        silver_category_id = 4  # Iluminação
```

**Problemas:**
- Mapeamento invisível (só aparece no código)
- Difícil de auditar, manter ou compartilhar
- Outros agentes não conseguem ver seus mapeamentos
- Mudanças exigem deploy de código

### Solução proposta

**Mapeamentos devem viver na tabela `silver_categories_map`.**

Scripts de migração devem **LER** da tabela, não hardcoded.

```
silver_categories (taxonomia) → silver_categories_map (mapeamentos) → bronze_products (dados)
```

**Por que é melhor:**

| Aspecto | Hardcoded (Atual) | Declarativo (Proposto) |
|---------|-------------------|------------------------|
| Visibilidade | Escondido no código | Consultável no DB |
| Manutenção | Editar script + redeploy | UPDATE SQL |
| Auditoria | Só git diff | Histórico no DB |
| Compartilhar | Copiar código | Outros agentes leem mesma tabela |
| Confiança | Adivinhar do código | Coluna explícita no DB |

---

## Padrão Adapter: Inglês ↔ Português

**Contexto:** Nosso scraping usa categorias em inglês (`Audio`, `Sports`, `Tech`), mas `silver_categories` usa português (`Áudio`, `Esportes`, `Eletrônicos`).

**Solução:** Tabela de tradução que conecta os dois sistemas.

```
┌─────────────────────────────────────────────────────────────┐
│  NOSSO SISTEMA (Inglês)                                     │
│  category_registry: 'Audio' > 'Headphones' > 'Bluetooth'   │
│  bsr_history: category_l1 = 'Audio'                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  ADAPTER (our_category_map)                                 │
│  our_l1='Audio' → silver_l1='Audio'                        │
│  our_l1='Tech' → silver_l1='Eletrônicos'                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  PRODUCTION DB                                              │
│  silver_categories: id=1, l1='Audio'                        │
│  silver_categories_map: 'ml' → 'MLB3835' → id=1            │
│  bronze_products: silver_category_id = 1                    │
└─────────────────────────────────────────────────────────────┘
```

### Tabela de tradução (local)

```sql
CREATE TABLE our_category_map (
    our_l1 VARCHAR(50) PRIMARY KEY,
    silver_l1 VARCHAR(100) NOT NULL
);

INSERT INTO our_category_map (our_l1, silver_l1) VALUES
    ('Audio', 'Audio'),
    ('Moda', 'Moda'),
    ('Tech', 'Eletrônicos'),
    ('Lighting', 'Iluminação'),
    ('Home', 'Casa'),
    ('Sports', 'Esportes'),
    ('Tools', 'Ferramentas'),
    ('Kitchen', 'Cozinha'),
    ('Pet', 'Pets'),
    ('Health', 'Saúde'),
    ('Automotive', 'Automotivo'),
    ('Garden', 'Jardim'),
    ('Toys', 'Infantis'),
    ('Office', 'Papelaria'),
    ('Baby', 'Infantis');
```

### Fluxo de migração

```python
def export_to_production(conn_local, conn_prod):
    """Export BSR data com silver_category_id."""
    bsr_data = query_local(conn_local, "SELECT * FROM bsr_history")
    
    for row in bsr_data:
        # Traduzir Inglês → Português
        silver_l1 = translate_category(conn_local, row['category_l1'])
        
        # Resolver para silver_category_id
        result = resolve_category(conn_prod, platform='ml', l1=silver_l1)
        
        if result:
            insert_bsr(conn_prod, {
                'platform': row['platform'],
                'platform_id': row['platform_id'],
                'bsr_rank': row['bsr_rank'],
                'silver_category_id': result['silver_category_id'],
                'price': row['price'],
                'sales_count': row['sales_count']
            })
```

---

## Como Todos os Agentes Devem Funcionar

### Passo 1: Registrar Mapeamentos

Adicionar linhas em `silver_categories_map`:

```sql
INSERT INTO silver_categories_map 
  (platform, platform_l1_id, silver_category_id, confidence)
VALUES 
  ('ml', 'MLB3835', 1, 0.90),
  ('amazon', 'electronics', 3, 0.80),
  ('1688', '67', 4, 0.90);
```

### Passo 2: Script de Migração LÊ da Tabela

```python
from category_resolver import resolve_category

def migrate_product(conn, product):
    result = resolve_category(conn, platform=product['platform'], l1=product['category_l1'])
    if result:
        product['silver_category_id'] = result['silver_category_id']
    return product
```

### Passo 3: Gravar em bronze_products

```python
cur.execute("""
    INSERT INTO bronze_products (source, source_id, silver_category_id, ...)
    VALUES (%s, %s, %s, ...)
""", (source, source_id, silver_category_id, ...))
```

---

## Diretrizes de Confiança

| Score | Significado | Quando usar |
|-------|-------------|-------------|
| 0.9-1.0 | Match exato | Mesma categoria, mesmo idioma |
| 0.8-0.9 | Alta confiança | Mapeamento claro, diferença menor |
| 0.7-0.8 | Bom match | Requere interpretação |
| 0.5-0.7 | Moderado | Match fuzzy, múltiplas categorias |
| <0.5 | Baixa | Revisão manual necessária |

---

## Suas Categorias

Crie uma pasta com nome do seu agente:

```
importasimples_db/
├── arbitlens_china/    # Agente China (produtos Rakumart)
├── products-1688/      # Scraper 1688 (MTOP API)
├── arbt.ly/            # ML/Amazon Brasil (este agente)
└── ...
```

---

## Regras

1. **Não modificar silver_categories L1** — compartilhado por todos agentes
2. **Não modificar mapeamentos de outros** — cada plataforma tem suas linhas
3. **Usar scores de confiança** — 0.9+ para matches exatos
4. **Adicionar sua pasta** — manter scripts organizados
5. **Documentar mapeamentos** — adicionar comentários

---

## Acesso ao Banco

```
Host: 34.170.210.220
Port: 5432
Database: importasimples_products
User: importasimples
Password: R{[{f<VajbC{<kvU
```

---

## Perguntas para Discussão

1. `silver_categories_map` deveria ter coluna `agent_name` para rastrear quem adicionou cada mapeamento?
2. Devemos versionar estado da tabela (exportar para JSON periodicamente)?
3. Scripts de migração devem falhar em categorias não mapeadas ou pular com warning?

---

*Esta arquitetura segue boas práticas de engenharia de dados: separação de responsabilidades, configuração declarativa, fonte única de verdade.*
