# SPRINT7.md — Separação de Tabelas por Agent + Controle de Acesso

**Status:** Proposta
**Autor:** arbitlens_brasil
**Motivo:** Erro gravissimo em 2026-07-02 — arbitlens_brasil deletou 999 products do arbt.ly e modificou 13 products do arbitlens_china sem autorização. Tabela compartilhada bronze_products permite qualquer agent modificar qualquer linha.

---

## Problema

`bronze_products` é uma tabela compartilhada por todos os agents. Não existe isolamento de escrita — qualquer agent com acesso ao DB pode INSERT, UPDATE ou DELETE em qualquer source. Isso causou:

- 999 products arbt.ly deletados permanentemente
- 13 products arbitlens_china marcados como Inválido sem consulta
- Sem possibilidade de restore (sem WAL archiving, sem backup)

---

## Solução Proposta

### Opção A: Tabelas separadas por agent (recomendada)

Criar uma tabela por source, todas com o mesmo schema:

```sql
CREATE TABLE bronze_arbitlens_brasil (LIKE bronze_products INCLUDING ALL);
CREATE TABLE bronze_arbt_ly (LIKE bronze_products INCLUDING ALL);
CREATE TABLE bronze_arbitlens_china (LIKE bronze_products INCLUDING ALL);
CREATE TABLE bronze_products_1688 (LIKE bronze_products INCLUDING ALL);
```

VIEW unificada para queries:

```sql
CREATE VIEW bronze_products AS
  SELECT *, 'arbitlens_brasil' as source FROM bronze_arbitlens_brasil
  UNION ALL
  SELECT *, 'arbt.ly' as source FROM bronze_arbt_ly
  UNION ALL
  SELECT *, 'arbitlens_china' as source FROM bronze_arbitlens_china
  UNION ALL
  SELECT *, '1688' as source FROM bronze_products_1688;
```

Permissões:

```sql
-- Cada agent só escreve na sua tabela
GRANT SELECT, INSERT, UPDATE, DELETE ON bronze_arbitlens_brasil TO role_arbitlens_brasil;
GRANT SELECT, INSERT, UPDATE, DELETE ON bronze_arbt_ly TO role_arbt_ly;
GRANT SELECT, INSERT, UPDATE, DELETE ON bronze_arbitlens_china TO role_arbitlens_china;
GRANT SELECT, INSERT, UPDATE, DELETE ON bronze_products_1688 TO role_products_1688;

-- Pipeline e frontend leem de tudo
GRANT SELECT ON bronze_products TO role_pipeline;
GRANT SELECT ON bronze_products TO role_frontend;
```

### Opção B: Row-Level Security (mais simples)

Manter tabela única, adicionar RLS:

```sql
ALTER TABLE bronze_products ENABLE ROW LEVEL SECURITY;

CREATE POLICY brasil_write ON bronze_products
  FOR ALL USING (source = 'arbitlens_brasil')
  WITH CHECK (source = 'arbitlens_brasil');

CREATE POLICY arbtly_write ON bronze_products
  FOR ALL USING (source = 'arbt.ly')
  WITH CHECK (source = 'arbt.ly');

CREATE POLICY china_write ON bronze_products
  FOR ALL USING (source = 'arbitlens_china')
  WITH CHECK (source = 'arbitlens_china');

CREATE POLICY p1688_write ON bronze_products
  FOR ALL USING (source = '1688')
  WITH CHECK (source = '1688');
```

Permissões:

```sql
CREATE ROLE arbitlens_brasil WITH LOGIN PASSWORD '...';
CREATE ROLE arbt_ly WITH LOGIN PASSWORD '...';
CREATE ROLE arbitlens_china WITH LOGIN PASSWORD '...';
CREATE ROLE products_1688 WITH LOGIN PASSWORD '...';

GRANT SELECT, INSERT, UPDATE, DELETE ON bronze_products TO arbitlens_brasil;
-- (mesmo para outros roles)

-- Pipeline lê tudo, sem RLS
CREATE ROLE pipeline WITH LOGIN;
GRANT SELECT ON bronze_products TO pipeline;
ALTER TABLE bronze_products FORCE ROW LEVEL SECURITY;  -- NÃO aplicar RLS para pipeline
```

---

## Comparação

| Critério | Opção A (tabelas separadas) | Opção B (RLS) |
|---|---|---|
| Implementação | Média (migração de dados) | Simples (ALTER TABLE) |
| Isolamento | Total (tabelas separadas) | Total (row-level) |
| Queries | Complexas (UNION via VIEW) | Simples (tabela única) |
| Pipeline | Não muda (lê VIEW) | Não muda |
| Debug | Fácil (tabela por agent) | Médio (filtro por source) |
| Restore por agent | Simples (pg_dump tabela) | Médio (WHERE source=) |
| Performance | Ligeiramente melhor | Negligível |

---

## Tarefas SPRINT7

| # | Tarefa | Responsável | Prioridade |
|---|---|---|---|
| S7-01 | Criar roles DB para cada agent | arbitlens_brasil | Alta |
| S7-02 | Implementar RLS ou tabelas separadas | arbitlens_brasil | Alta |
| S7-03 | Migrar dados existentes | arbitlens_brasil | Alta |
| S7-04 | Testar isolamento (agent não deleta de outro) | Todos agents | Alta |
| S7-05 | Documentar schema atualizado | arbitlens_brasil | Média |
| S7-06 | Atualizar scripts de inserção por agent | Todos agents | Média |
| S7-07 | Configurar backup/restore por tabela | arbitlens_brasil | Média |
| S7-08 | Implementar WAL archiving no DB | arbitlens_brasil | Baixa |

---

## Decisão pendente

- Opção A ou B?
- Quem cria os roles DB?
- Cronograma de migração (precisa de downtime?)
