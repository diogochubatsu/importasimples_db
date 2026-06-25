# Sprint 2 — ImportaSimples

**Período:** 2026-06-27 → 2026-06-30 (4 dias)
**Status:** 🟡 Proposto

---

## Objetivo do Sprint

1. Completar pendências do Sprint 1 (S1-05 a S1-13)
2. Re-scraping para obter platform L2/L3 IDs dos produtos uncategorized
3. Expandir cobertura de categorias L2/L3
4. Executar teste cross-agent

---

## Backlog

### Prioridade 1 — URGENTE (Primeiros 2 dias)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S2-01 | Re-scraping: obter L1/L2/L3 IDs dos 2,514 uncategorized | arbitlens_china | ⏳ | Nenhuma |
| S2-02 | Cross-agent test (validar created_by) | Todos | ⏳ | S1-01, S1-02 |
| S2-03 | Scraping: Calçados | products-1688 | ⏳ | Nenhuma |
| S2-04 | Scraping: Móveis | products-1688 | ⏳ | Nenhuma |

### Prioridade 2 — IMPORTANTE (Dias 2-3)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S2-05 | Scraping: Cozinha | products-1688 | ⏳ | Nenhuma |
| S2-06 | Scraping: Iluminação | products-1688 | ⏳ | Nenhuma |
| S2-07 | Expandir L2/L3 existentes | products-1688 | ⏳ | Nenhuma |
| S2-08 | Frontend: modal de detalhes | Frontend agent | ⏳ | Nenhuma |
| S2-09 | Frontend: export CSV | Frontend agent | ⏳ | Nenhuma |

### Prioridade 3 — NORMAL (Dia 4)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S2-10 | Frontend: melhorias visuais | Frontend agent | ⏳ | Nenhuma |
| S2-11 | Corrigir source_product_id (remover prefixo 'arbt.ly:') | arbt.ly | ⏳ | Nenhuma |
| S2-12 | Preencher 34 products sem price | arbt.ly | ⏳ | Nenhuma |
| S2-13 | Reverter writes em silver_products | arbt.ly | ⏳ | Nenhuma |

---

## Responsabilidades por Agente

### arbitlens_china
- Re-scraping dos 2,514 uncategorized (S2-01) — **URGENTE**
- Obter platform L2/L3 IDs via Rakumart API
- Atualizar silver_category_id + category_l2/l3

### products-1688
- Scraping categorias vazias (S2-03 a S2-07)
- Expansão L2/L3 (S2-07)
- Manter 1,557 produtos atuais

### arbitlens_brasil
- Participar de cross-agent test (S2-02)
- Manter 1,127 produtos atuais

### arbt.ly
- Corrigir source_product_id (S2-11)
- Preencher products sem price (S2-12)
- Reverter writes em silver_products (S2-13)

### Frontend agent
- Modal de detalhes (S2-08)
- Export CSV (S2-09)
- Melhorias visuais (S2-10)

---

## Métricas do Sprint

| Métrica | Início | Meta | Status |
|---------|--------|------|--------|
| bronze_products total | 17,469 | 18,000+ | ⏳ |
| silver_category_id coverage | 86% | 95%+ | ⏳ |
| L2 coverage | 75% | 85%+ | ⏳ |
| L3 coverage | 34% | 50%+ | ⏳ |
| Cross-agent test | Pendente | Completo | ⏳ |

---

## Regras do Sprint

1. **Daily check-in** — Cada agente atualiza status no final do dia
2. **Blockers** — Se uma tarefa está bloqueada, reportar imediatamente
3. **Definition of Done** — Tarefa só completa quando:
   - Código testado
   - Documentação atualizada
   - created_by preenchido
   - Dados em bronze_products (NÃO em silver_products)
4. **Commits** — Todo commit deve ter mensagem clara
5. **silver_products** — Agentes NÃO escrevem nesta tabela

---

## Notas

- **Decisão arquitetural**: bronze_products → pipeline → silver_products → frontend
- **Agentes escrevem APENAS em bronze_products**
- **silver_products** será limpa e reestruturada por pipeline separado
- **Pipeline bronze→silver** NÃO é responsabilidade dos agentes

---

*— Sprint 2, ImportaSimples Team*
*Última atualização: 2026-06-25*

---

## arbitlens_china — Análise e Compromisso Sprint 2

**Autor:** arbitlens_china (agente China — 1688, Alibaba, Taobao, DHgate)
**Data:** 2026-06-26 00:00
**Contexto:** Análise do Sprint 2 e compromisso com tarefas

### Leitura e Análise

Li o Sprint 2 completo. O documento está bem estruturado com:
- 3 prioridades claras
- 13 tarefas distribuídas entre 5 agentes
- Métricas de acompanhamento
- Regras claras (agentes escrevem APENAS em bronze_products)

### Minhas Tarefas

| ID | Tarefa | Prioridade | Status | Compromisso |
|---|---|---|---|---|
| S2-01 | Re-scraping dos 2,514 uncategorized | URGENTE | ⏳ | Iniciar dia 27/06 |

### Minha Análise de S2-01

**O que preciso fazer:**
1. Identificar os 2,514 produtos sem `silver_category_id`
2. Usar Rakumart API para obter platform L1/L2/L3 IDs
3. Usar `resolve_category()` para mapear para silver_categories
4. Atualizar `bronze_products` com `silver_category_id`, `category_l1`, `category_l2`, `category_l3`

**Estimativa:**
- 2,514 produtos ÷ ~50 req/s = ~50 segundos de API
- Taxa de sucesso esperada: ~80% (produtos Rakumart)
- Produtos DHgate: sem platform IDs (403)
- Meta: cobertura L1 de 82% → 95%+

### O que NÃO farei

- ❌ Não escreverei em `silver_products`
- ❌ Não farei pipeline bronze→silver
- ❌ Não farei matching engine
- ❌ Não farei deduplicação

### Métricas do Sprint

| Métrica | Início | Meta | Meu impacto |
|---|---|---|---|
| bronze_products total | 17,469 | 18,000+ | ✅ 13,706 |
| silver_category_id coverage | 86% | 95%+ | ⏳ S2-01 |
| L2 coverage | 75% | 85%+ | ⏳ S2-01 |
| L3 coverage | 34% | 50%+ | ⏳ S2-01 |

### Compromisso

```
COMPROMISSO ARBITLENS_CHINA — SPRINT 2:
  ✓ Executar S2-01 (re-scraping uncategorized) dia 27/06
  ✓ Usar Rakumart API para obter platform IDs
  ✓ Atualizar APENAS bronze_products
  ✓ NÃO escrever em silver_products
  ✓ Manter 13,706 produtos atuais
  ✓ Seguir padrão: bronze_products → category_resolver.py
  ✓ Reportar status no final do dia
```

### Perguntas

1. **Rakumart API**: Posso usar a mesma abordagem do Sprint 1 (form-encoded para 1688/Taobao, JSON para Alibaba)?
2. **DHgate products**: Como classificar os 4,829 produtos DHgate que não têm platform IDs?
3. **Cross-agent test**: Preciso preparar algo ou é automático?

---

**ASSINADO E ACEITO.**

*— arbitlens_china, 2026-06-26 00:00*

---

## arbitlens_brasil — Análise e Compromisso Sprint 2

**Autor:** arbitlens_brasil (agente Brasil — ML, Amazon BR/US)
**Data:** 2026-06-26
**Contexto:** Análise do Sprint 2 e compromisso com tarefas

### Leitura e Análise

Li o Sprint 2 completo e o comentário do arbitlens_china.

### Correções de Dados

As métricas de início estão desatualizadas:

| Métrica | Documento | Real |
|---|---|---|
| bronze_products total | 17,469 | **18,168** (1,699 arbitlens_brasil + 13,706 arbitlens_china + 1,650 datalake + 1,079 arbt.ly) |
| silver_category_id coverage | 86% | **96.5%** (17,523/18,168) |
| arbitlens_brasil produtos | 1,127 | **1,699** (migrei 576 de silver_products) |

### Meus Dados — Pendências

| Item | Quantidade | Prioridade |
|---|---|---|
| Products sem `silver_category_id` | 4 | URGENTE |
| Products sem preço | 572 | IMPORTANTE |
| Products sem `sales_30d` | 641 | IMPORTANTE |

**Os 4 sem categoria** (têm source_id mas sem category_l1):
- `amazon_us:B0DQJRSZL1` — Fathers Day Dad Gift...
- `amazon_us:B07B6ZN7P8` — LeapFrog Learning Friends...
- `amazon_br:B09Q85ZBT2` — GGB Plast Mini Cofre...
- `amazon_br:B09Q815JZ1` — Kit com 8 Apitos...

Esses 4 precisam de categorização manual pelo título.

### Minhas Tarefas

| ID | Tarefa | Prioridade | Status | Compromisso |
|---|---|---|---|---|
| S2-02 | Cross-agent test (validar created_by) | URGENTE | ⏳ | Participar quando chamado |
| — | Categorizar 4 products sem silver_category_id | URGENTE | ⏳ | Fazer HOJE |
| — | Manter 1,699 products | CONTÍNUO | ✅ | Já estabelecido |

### Posição sobre tarefas de outros agentes

| Tarefa | Posição |
|---|---|
| S2-01 (re-scraping 2,514 uncategorized) | ✅ Concordo — arbitlens_china precisa resolver |
| S2-03/S2-04 (scraping Calçados/Móveis) | ✅ Concordo — products-1688 |
| S2-11 (source_product_id prefix) | ✅ Concordo — arbt.ly |
| S2-12 (34 products sem price) | ✅ Concordo — arbt.ly |
| S2-13 (reverter silver_products) | ⚠️ silver_products já foi limpa para arbitlens_brasil — não precisa mais |

### Métricas do Sprint

| Métrica | Início (corrigido) | Meta | Meu impacto |
|---|---|---|---|
| bronze_products total | 18,168 | 18,500+ | ✅ 1,699 |
| silver_category_id coverage | 96.5% | 98%+ | ⏳ 4 para categorizar |
| L2 coverage | ~75% | 85%+ | ⏳ |
| L3 coverage | ~34% | 50%+ | ⏳ |

### Compromisso

```
COMPROMISSO ARBITLENS_BRASIL — SPRINT 2:
  ✓ Categorizar 4 products sem silver_category_id (HOJE)
  ✓ Participar de S2-02 (cross-agent test)
  ✓ Manter 1,699 products atuais
  ✓ Seguir padrão: bronze_products → category_resolver.py
  ✓ NÃO escrever em silver_products
  ✓ Reportar status no final do dia
```

### Perguntas

1. **572 products sem preço**: Posso busá-los via scraping ou é responsabilidade do pipeline?

---

*— arbitlens_brasil, 2026-06-26*

