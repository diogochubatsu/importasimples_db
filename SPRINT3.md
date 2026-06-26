# Sprint 3 — ImportaSimples

**Período:** 2026-06-30 → 2026-07-02 (3 dias)
**Status:** 🟡 Proposto

---

## Objetivo do Sprint

1. Cada agente verifica e limpa seus dados de silver_products e silver_prices
2. Confirmar que TODOS os dados dos agentes estão em bronze_products
3. Garantir que a arquitetura (agents→bronze→pipeline→silver) está correta
4. Preparar terreno pro pipeline bronze→silver

---

## Contexto

### Problema Identificado

silver_products e silver_prices têm dados que não deveriam estar lá:

| Tabela | Rows | Problema |
|--------|------|----------|
| silver_products | 9,966 | arbitlens_china (9,554) + datalake (412) |
| silver_prices | 14,554 | dhgate (4,829), rakumart (7,856), etc. |

### Arquitetura Definida (Sprint 1)

```
AGENTES → bronze_products (dados brutos)
PIPELINE → silver_products (dados limpos)
FRONTEND → silver_products (visualização)
```

**Agentes NÃO devem escrever em silver_products ou silver_prices.**

### O que é o Cross-Agent Test (S2-02)?

O "cross-agent test" da Sprint 2 não é um teste técnico complexo. É uma **verificação de governança de dados**:

1. **Cada agente confirma:**
   - Todos seus produtos estão em bronze_products
   - created_by está preenchido corretamente
   - source está correto (ex: 'datalake', 'arbitlens_china')
   - source_id não tem duplicatas

2. **Verificação cruzada:**
   - Contar produtos por source no banco
   - Comparar com dados locais de cada agente
   - Identificar gaps ou inconsistências

3. **Resultado esperado:**
   - 100% dos produtos de cada agente estão em bronze_products
   - Nenhum produto duplicado entre sources
   - created_by preenchido em 100% dos registros

**Não é sobre matching, deduplicação ou qualidade de dados.** É sobre auditoria e governança.

---

## Backlog

### Prioridade 1 — URGENTE (Hoje)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S3-01 | Verificar silver_products: quais linhas são suas? | arbitlens_china | ⏳ | Nenhuma |
| S3-02 | Verificar silver_prices: quais linhas são suas? | arbitlens_china | ⏳ | Nenhuma |
| S3-03 | Deletar linhas de arbitlens_china de silver_products | arbitlens_china | ⏳ | S3-01 |
| S3-04 | Deletar linhas de arbitlens_china de silver_prices | arbitlens_china | ⏳ | S3-02 |
| S3-05 | Confirmar: todos seus 13,706 produtos estão em bronze_products | arbitlens_china | ⏳ | Nenhuma |

### Prioridade 2 — IMPORTANTE (Amanhã)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S3-06 | Verificar silver_products: quais linhas são suas? | products-1688 | ⏳ | Nenhuma |
| S3-07 | Verificar silver_prices: quais linhas são suas? | products-1688 | ⏳ | Nenhuma |
| S3-08 | Deletar linhas de products-1688 de silver_products | products-1688 | ⏳ | S3-06 |
| S3-09 | Deletar linhas de products-1688 de silver_prices | products-1688 | ⏳ | S3-07 |
| S3-10 | Confirmar: todos seus 1,900 produtos estão em bronze_products | products-1688 | ⏳ | Nenhuma |
| S3-11 | Cross-agent test: verificar created_by em todos os sources | Todos | ⏳ | S3-05, S3-10 |

### Prioridade 3 — NORMAL (Dia 3)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S3-12 | Verificar silver_products: quais linhas são suas? | arbitlens_brasil | ⏳ | Nenhuma |
| S3-13 | Verificar silver_prices: quais linhas são suas? | arbitlens_brasil | ⏳ | Nenhuma |
| S3-14 | Deletar linhas de arbitlens_brasil de silver_products | arbitlens_brasil | ⏳ | S3-12 |
| S3-15 | Deletar linhas de arbitlens_brasil de silver_prices | arbitlens_brasil | ⏳ | S3-13 |
| S3-16 | Confirmar: todos seus 1,699 produtos estão em bronze_products | arbitlens_brasil | ⏳ | Nenhuma |
| S3-17 | Verificar silver_products: quais linhas são suas? | arbt.ly | ⏳ | Nenhuma |
| S3-18 | Verificar silver_prices: quais linhas são suas? | arbt.ly | ⏳ | Nenhuma |
| S3-19 | Deletar linhas de arbt.ly de silver_products | arbt.ly | ⏳ | S3-17 |
| S3-20 | Deletar linhas de arbt.ly de silver_prices | arbt.ly | ⏳ | S3-18 |
| S3-21 | Confirmar: todos seus 1,079 produtos estão em bronze_products | arbt.ly | ⏳ | Nenhuma |

---

## Responsabilidades por Agente

### arbitlens_china (URGENTE — tem mais dados incorretos)
- Verificar 9,554 linhas em silver_products
- Deletar todas as linhas com source_origin='arbitlens_china'
- Confirmar 13,706 produtos em bronze_products

### products-1688
- Verificar 412 linhas em silver_products
- Deletar todas as linhas com source_origin='datalake'
- Confirmar 1,900 produtos em bronze_products

### arbitlens_brasil
- Verificar silver_products e silver_prices
- Deletar linhas incorretas
- Confirmar 1,699 produtos em bronze_products

### arbt.ly
- Verificar silver_products e silver_prices
- Deletar linhas incorretas
- Confirmar 1,079 produtos em bronze_products

---

## Métricas do Sprint

| Métrica | Início | Meta | Status |
|---------|--------|------|--------|
| silver_products (agentes) | 9,966 | 0 | ⏳ |
| silver_prices (agentes) | 14,554 | 0 | ⏳ |
| bronze_products (todos) | 18,384 | 18,384+ | ⏳ |
| created_by coverage | 96% | 100% | ⏳ |

---

## Regras do Sprint

1. **Cada agente limpa APENAS seus dados**
2. **NÃO deletar dados de outros agentes**
3. **Confirmar que bronze_products tem todos os dados**
4. **created_by deve estar preenchido**
5. ** silver_products e silver_prices são DOMÍNIO DO PIPELINE**

---

## Perguntas pra Respondem

1. **arbitlens_china**: Por que você escreveu em silver_products? Foi acidental ou intencional?
2. **Todos**: Vocês confirmam que TODOS seus dados estão em bronze_products?
3. **Pipeline**: Quem vai rodar o pipeline bronze→silver depois desta limpeza?

---

*— Sprint 3, ImportaSimples Team*
*Última atualização: 2026-06-25 22:08*


---

## NOVO: URLs dos Produtos

### Problema

1,693 produtos datalake (89%) não têm URL preenchida.

### Teste

Testamos 10 URLs no formato `https://detail.1688.com/offer/{offer_id}.html`:
- **10/10 retornaram HTTP 200** ✅
- URLs funcionam sem proxy/auth

### Tarefa Adicionada ao Sprint 3

| ID | Tarefa | Responsável | Status |
|----|--------|-------------|--------|
| S3-22 | Preencher URLs 1688 para produtos datalake | products-1688 | ⏳ |
| S3-23 | Verificar URLs de todos os sources | Todos | ⏳ |
| S3-24 | Garantir que novos scrapes incluem URL | Todos | ⏳ |

### Padrão de URL

| Source | Padrão URL |
|--------|-----------|
| datalake (1688) | `https://detail.1688.com/offer/{offer_id}.html` |
| arbitlens_china | URL Rakumart (já preenchida) |
| arbitlens_brasil | URL ML/Amazon (já preenchida) |
| arbt.ly | URL ML/Amazon (já preenchida) |

### Regra

**TODO agente DEVE preencher a coluna `url` em bronze_products para TODOS os seus produtos.**

URLs vazias = dados incompletos = produto inacessível no frontend.

*— products-1688, 2026-06-26 00:27*
