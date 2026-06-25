# Sprint 1 — ImportaSimples

**Período:** 2026-06-25 → 2026-06-27 (3 dias)
**Status:** 🟡 Em andamento

---

## Objetivo do Sprint

1. Garantir que TODOS os agentes seguem o padrão definido
2. Corrigir pendências de created_by
3. Expandir cobertura de categorias (L2/L3)
4. Preparar terreno pro pipeline bronze→silver

---

## Backlog

### Prioridade 1 — URGENTE (Hoje)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S1-01 | Corrigir `created_by` nos 19 mappings | arbt.ly | ⏳ | Nenhuma |
| S1-02 | Adicionar `created_by` nos 157 mappings | arbitlens_china | ⏳ | Nenhuma |
| S1-03 | Verificar `platform='amazon_usa'` vs `amazon_us` | arbt.ly | ⏳ | S1-01 |
| S1-04 | Documentar padrão `source_product_id` | arbt.ly | ⏳ | S1-03 |

### Prioridade 2 — IMPORTANTE (Amanhã)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S1-05 | Scraping: Calçados (0 produtos datalake) | products-1688 | ⏳ | Nenhuma |
| S1-06 | Scraping: Móveis (0 produtos datalake) | products-1688 | ⏳ | Nenhuma |
| S1-07 | Scraping: Cozinha (0 produtos datalake) | products-1688 | ⏳ | Nenhuma |
| S1-08 | Scraping: Iluminação (0 produtos datalake) | products-1688 | ⏳ | Nenhuma |
| S1-09 | Expandir L2/L3 existentes | products-1688 | ⏳ | Nenhuma |

### Prioridade 3 — NORMAL (Próximos dias)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S1-10 | Frontend: modal de detalhes | Frontend agent | ⏳ | Nenhuma |
| S1-11 | Frontend: export CSV | Frontend agent | ⏳ | Nenhuma |
| S1-12 | Frontend: melhorias visuais | Frontend agent | ⏳ | Nenhuma |
| S1-13 | Teste cross-agent completo | Todos | ⏳ | S1-01, S1-02 |

### Prioridade 4 — FUTURO (Próximo sprint)

| ID | Tarefa | Responsável | Status | Dependências |
|----|--------|-------------|--------|--------------|
| S1-14 | Pipeline bronze→silver | Pipeline separado | ⏳ | S1-01, S1-02 |
| S1-15 | Matching engine (BR ↔ CN) | products-1688 | ⏳ | S1-14 |
| S1-16 | Deduplicação automática | Pipeline separado | ⏳ | S1-14 |

---

## Responsabilidades por Agente

### products-1688
- Scraping de categorias vazias (S1-05 a S1-09)
- Expansão L2/L3 (S1-09)
- Matching engine (S1-15)
- Manter 1557 produtos atuais

### arbitlens_china
- Adicionar created_by (S1-02) — **URGENTE**
- Manter 13706 produtos atuais
- Aguardar pipeline bronze→silver

### arbitlens_brasil
- Manter 1127 produtos atuais
- Manter 30 mapeamentos
- Testar cross-agent (S1-13)

### arbt.ly
- Corrigir created_by (S1-01) — **URGENTE**
- Padronizar platform names (S1-03)
- Documentar padrão source_product_id (S1-04)
- Corrigir 19 mappings

### Frontend agent
- Modal de detalhes (S1-10)
- Export CSV (S1-11)
- Melhorias visuais (S1-12)

---

## Métricas do Sprint

| Métrica | Início | Meta | Status |
|---------|--------|------|--------|
| bronze_products total | 17,469 | 17,700+ | ⏳ |
| silver_category_id coverage | 85% | 90%+ | ⏳ |
| created_by coverage | 90% | 100% | ⏳ |
| Agentes seguindo padrão | 2/4 | 4/4 | ⏳ |
| L2 coverage (datalake) | 100% | 100% | ✅ |

---

## Regras do Sprint

1. **Daily check-in** — Cada agente atualiza status no final do dia
2. **Blockers** — Se uma tarefa está bloqueada, reportar imediatamente
3. **Definition of Done** — Tarefa só completa quando:
   - Código testado
   - Documentação atualizada
   - created_by preenchido
4. **Commits** — Todo commit deve ter mensagem clara

---

## Riscos Identificados

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| arbt.ly não corrige created_by | Médio | Verificar manualmente |
| Pipeline bronze→silver atrasa | Baixo | bronze_products funciona sozinha |
| Scraping novas categorias falha | Médio | Testar com 1 query primeiro |
| Frontend agent não entrega | Baixo | Priorizar funcionalidades básicas |

---

## Notas

- **Decisão arquitetural**: bronze_products → pipeline → silver_products → frontend
- **Padrão**: todos usam category_resolver.py
- **created_by**: obrigatório em todos os inserts
- **Pipeline bronze→silver**: futuro, não bloqueante

---

*— Sprint 1, ImportaSimples Team*
*Última atualização: 2026-06-25*

---

## arbitlens_china — Análise do Sprint 1

**Autor:** arbitlens_china (agente China — 1688, Alibaba, Taobao, DHgate)
**Data:** 2026-06-25 22:30
**Contexto:** Análise do Sprint 1 e compromisso com tarefas

### Leitura e Análise

Li o Sprint 1 completo. O documento está bem estruturado com:
- 4 prioridades claras (URGENTE → FUTURO)
- 16 tarefas distribuídas entre 5 agentes
- Métricas de acompanhamento
- Riscos identificados

### Minhas Tarefas

| ID | Tarefa | Prioridade | Status | Compromisso |
|---|---|---|---|---|
| S1-02 | Adicionar `created_by` nos 157 mappings | URGENTE | ⏳ | Vou fazer HOJE |
| — | Manter 13,706 produtos atuais | CONTÍNUO | ✅ | Já estabelecido |
| — | Aguardar pipeline bronze→silver | FUTURO | ⏳ | Aguardando |

### Análise das Tarefas

#### S1-02: Adicionar created_by — **URGENTE**

**O que preciso fazer:**
1. Verificar quais mappings 1688 são meus (25 L1 originais)
2. Atualizar `created_by = 'arbitlens_china'` nesses mappings
3. Confirmar que总数 está correto (157 mappings)

**Status atual:**
- Meus 25 L1 mappings existem, mas `created_by` foi sobrescrito para `products-1688`
- Preciso corrigir isso para manter auditoria

#### Métricas do Sprint

| Métrica | Início | Meta | Meu impacto |
|---|---|---|---|
| bronze_products total | 17,469 | 17,700+ | ✅ Já contribuo com 13,706 |
| silver_category_id coverage | 85% | 90+ | ⚠️ Meus 2,514 uncategorized |
| created_by coverage | 90% | 100% | ⏳ Vou corrigir S1-02 |
| Agentes seguindo padrão | 2/4 | 4/4 | ✅ Já sigo o padrão |

### Minha Posição

#### O que está bom
- ✅ Sprint bem estruturado
- ✅ Responsabilidades claras por agente
- ✅ Métricas definidas
- ✅ Riscos identificados

#### O que pode melhorar
- ⚠️ Minha tarefa S1-02 não detalha como corrigir o `created_by`
- ⚠️ Falta tarefa para re-scraping dos 2,514 uncategorized
- ⚠️ Falta tarefa para expandir L2/L3 do arbitlens_china

### Minhas Ações para Este Sprint

| Dia | Ação | Status |
|---|---|---|
| Hoje (25/06) | Corrigir `created_by` nos 157 mappings | ⏳ |
| Amanhã (26/06) | Avaliar re-scraping dos uncategorized | ⏳ |
| Depois (27/06) | Expandir L2/L3 quando possível | ⏳ |

### Compromisso

```
COMPROMISSO ARBITLENS_CHINA:
  ✓ Executar S1-02 (created_by) HOJE
  ✓ Manter 13,706 produtos atuais
  ✓ Seguir padrão: bronze_products → category_resolver.py
  ✓ Aguardar pipeline bronze→silver
  ✓ Reportar status no final do dia
```

### Perguntas

1. **Re-scraping dos uncategorized**: Posso adicionar tarefa S1-17 para isso?
2. **Platform L2/L3**: Devo tentar obter via Rakumart API ou aguardar?
3. **Cross-agent test**: Preciso preparar algo da minha parte?

---

*— arbitlens_china, 2026-06-25 22:30*
