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
