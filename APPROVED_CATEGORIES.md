# Categorias Aprovadas

**Última atualização:** 2026-07-02 | **Aprovado por:** Diogo

---

## Regras

1. **silver_categories é a única fonte de verdade** — todos os agents devem usar
2. **Cada agent só mexe nos seus products** — nunca alterar products de outros
3. **Novas categorias precisam de aprovação** de 100% dos agents via SPRINT6.md
4. **category_resolver.py** — usar para resolver e criar categorias
5. **Produtos devem ter L1 + L2** — L3 é opcional mas recomendado

---

## Plano de Trabalho — Enriquecimento L2

**Objetivo:** Todos os products devem ter L1 + L2.

### Eletrônicos — Distribuição por Source

| Source | Products sem L2 | Responsável |
|--------|-----------------|-------------|
| arbitlens_china | 1,722 | arbitlens_china |
| arbitlens_brasil | 210 | arbitlens_brasil |
| 1688 | 78 | products-1688 |

### Ordem de trabalho (por volume de products sem L2)

**Atualizado:** 2026-07-01 por products-1688

| # | L1 | Products sem L2 | Responsável | Status |
|---|-----|-----------------|-------------|--------|
| 1 | Eletrônicos | 0 | products-1688 | ✅ COMPLETO |
| 2 | Moda | 1,169 | arbt.ly | ⏳ |
| 3 | Casa | 0 | products-1688 | ✅ COMPLETO |
| 4 | Infantis | 806 | arbt.ly | ⏳ |
| 5 | Esportes | 0 | products-1688 | ✅ COMPLETO |
| 6 | Beleza | 717 | arbt.ly | ⏳ |
| 7 | Cozinha | 583 | arbitlens_brasil | ⏳ |
| 8 | Ferramentas | 0 | products-1688 | ✅ COMPLETO |
| 9 | Pets | 503 | arbitlens_brasil | ⏳ |
| 10 | Iluminação | 485 | arbitlens_china | ⏳ |
| 11 | Móveis | 291 | arbitlens_china | ⏳ |
| 12 | Papelaria | 0 | products-1688 | ✅ COMPLETO |
| 13 | Saúde | 240 | arbitlens_china | ⏳ |
| 14 | Wearables | 186 | arbitlens_china | ⏳ |
| 15 | Calçados | 150 | arbitlens_china | ⏳ |
| 16 | Jardim | 115 | arbitlens_china | ⏳ |
| 17 | Automotivo | 53 | arbitlens_china | ⏳ |
| 18 | Têxteis | 50 | arbitlens_china | ⏳ |
| 19 | Acessórios | 30 | arbitlens_china | ⏳ |
| 20 | Eletrodomésticos | 24 | arbitlens_china | ⏳ |
| 21 | Computadores | 23 | arbitlens_china | ⏳ |
| 22 | Organização | 21 | arbitlens_china | ⏳ |
| 23 | Industrial | 8 | arbitlens_china | ⏳ |
| 3 | Casa | 1,021 | products-1688 / arbitlens_brasil |
| 4 | Infantis | 806 | arbt.ly |
| 5 | Esportes | 719 | products-1688 / arbitlens_brasil |
| 6 | Beleza | 717 | arbt.ly |
| 7 | Cozinha | 583 | arbitlens_brasil |
| 8 | Ferramentas | 532 | products-1688 |
| 9 | Pets | 503 | arbitlens_brasil |
| 10 | Iluminação | 485 | arbitlens_china |
| 11 | Móveis | 291 | arbitlens_china |
| 12 | Papelaria | 278 | products-1688 |
| 13 | Saúde | 240 | arbitlens_china |
| 14 | Wearables | 186 | arbitlens_china |
| 15 | Calçados | 150 | arbitlens_china |
| 16 | Jardim | 115 | arbitlens_china |
| 17 | Automotivo | 53 | arbitlens_china |
| 18 | Têxteis | 50 | arbitlens_china |
| 19 | Acessórios | 30 | arbitlens_china |
| 20 | Eletrodomésticos | 24 | arbitlens_china |
| 21 | Computadores | 23 | arbitlens_china |
| 22 | Organização | 21 | arbitlens_china |
| 23 | Industrial | 8 | arbitlens_china |

### Como trabalhar

1. **Começar pelo #1** (Eletrônicos) — products-1688
2. **Analisar titles** dos products sem L2
3. **Criar L2** com `ensure_category(conn, l1, l2)`
4. **Mover products** com `UPDATE bronze_products SET silver_category_id = <novo_id>`
5. **Repetir** para o próximo L1

### Status

| # | L1 | Status |
|---|-----|--------|
| 1 | Eletrônicos | ⏳ Pendente |
| 2 | Moda | ⏳ Pendente |
| 3 | Casa | ⏳ Pendente |
| 4 | Infantis | ⏳ Pendente |
| 5 | Esportes | ⏳ Pendente |
| 6 | Beleza | ⏳ Pendente |
| 7 | Cozinha | ⏳ Pendente |
| 8 | Ferramentas | ⏳ Pendente |
| 9 | Pets | ⏳ Pendente |
| 10 | Iluminação | ⏳ Pendente |
| 11 | Móveis | ⏳ Pendente |
| 12 | Papelaria | ⏳ Pendente |
| 13 | Saúde | ⏳ Pendente |
| 14 | Wearables | ⏳ Pendente |
| 15 | Calçados | ⏳ Pendente |
| 16 | Jardim | ⏳ Pendente |
| 17 | Automotivo | ⏳ Pendente |
| 18 | Têxteis | ⏳ Pendente |
| 19 | Acessórios | ⏳ Pendente |
| 20 | Eletrodomésticos | ⏳ Pendente |
| 21 | Computadores | ⏳ Pendente |
| 22 | Organização | ⏳ Pendente |
| 23 | Industrial | ⏳ Pendente |

---

## Estado Atual

| Métrica | Valor |
|---------|-------|
| Total categorias | 291 |
| L1 | 26 |
| L2/L3 | 265 |
| Total products | 16,564 |

---

## Categorias por L1

### Audio (1,344 products)

| L2 | L3 | ID | China | Brasil | arbt.ly | Total |
|----|----|-----|-------|--------|---------|-------|
| Fones | Fone Bluetooth | 75 | 299 | 136 | 41 | **476** |
| Microfones | Lapela Sem Fio | 34 | 354 | 20 | 59 | **433** |
| Caixas de Som | Portátil | 72 | 211 | 69 | 76 | **356** |
| Fones | Headset | 77 | — | — | 39 | **39** |
| Players | DVD/Blu-ray | 81 | 3 | 2 | 29 | **34** |
| Fones | Fone Gamer | 76 | — | — | 2 | **2** |
| Caixas de Som | Smart Speaker | 73 | — | — | 1 | **1** |
| Som Automotivo | Boombox | 83 | — | — | 1 | **1** |
| Som Automotivo | Caixa Amplificada | 84 | — | — | 1 | **1** |
| Som Automotivo | Processador | 85 | — | — | 1 | **1** |

### Iluminação (1,269 products)

| L2 | L3 | ID | China | Brasil | arbt.ly | Total |
|----|----|-----|-------|--------|---------|-------|
| *(sem L2)* | | 4 | 460 | 25 | — | **485** |
| Lâmpadas | | 424 | 304 | 5 | — | **309** |
| Flashlights | | 427 | 126 | 1 | — | **127** |
| Fita LED | | 425 | 96 | 1 | — | **97** |
| Luminárias | | 426 | 62 | 1 | — | **63** |
| Ring Light | Médio | 241 | — | — | 26 | **26** |
| Ring Light | *(sem L3)* | 240 | 2 | 29 | — | **31** |
| Painel LED | Estúdio | 239 | — | — | 44 | **44** |
| Painel LED | *(sem L3)* | 238 | — | 20 | — | **20** |
| Painel LED | Softbox | 402 | — | 5 | — | **5** |
| Bastão LED | RGB | 237 | — | — | 8 | **8** |
| Bastão LED | *(sem L3)* | 236 | 3 | 12 | — | **15** |
| Faróis LED | | 429 | 22 | — | — | **22** |
| Luzes Noturnas | | 430 | 11 | — | — | **11** |
| Projetores | | 431 | 6 | — | — | **6** |

### Automotivo (294 products)

| L2 | ID | China | Brasil | Total |
|----|----|-------|--------|-------|
| Acessórios | 436 | 202 | 4 | **206** |
| *(sem L2)* | 18 | 48 | 5 | **53** |
| Limpeza | 438 | 9 | 6 | **15** |
| Peças | 439 | 9 | 4 | **13** |
| Eletrônicos | 440 | 6 | — | **6** |
| Iluminação | 437 | 1 | — | **1** |

### Jardim (311 products)

| L2 | ID | China | Brasil | Total |
|----|----|-------|--------|-------|
| *(sem L2)* | 14 | 99 | 16 | **115** |
| Vasos | 433 | 96 | — | **96** |
| Irrigação e Aspersão | 401 | 47 | — | **47** |
| Ferramentas | 432 | 28 | 2 | **30** |
| Ferramentas *(jardim)* | 35 | 30 | — | **30** |
| Plantas | 434 | 22 | 1 | **23** |

### Eletrônicos (2,633 products)

| L2 | L3 | ID | China | 1688 | Brasil | Total |
|----|----|-----|-------|------|--------|-------|
| *(sem L2)* | | 3 | 1,722 | 78 | 210 | **2,010** |
| PC | | 336 | 81 | 60 | — | **141** |
| Acessórios | | 390 | 11 | 60 | 27 | **98** |
| Eletrodomésticos | | 389 | — | 80 | — | **80** |
| Tripés | Profissional | 234 | — | — | 40 | **40** |
| Tripés | Universais | 235 | — | — | 24 | **24** |
| Iluminação | | 332 | 52 | 10 | — | **62** |
| Celular | | 340 | — | 60 | — | **60** |
| Smart Home | | 344 | — | 57 | — | **57** |
| Acessorios Mobile | | 67 | 19 | — | — | **19** |
| Acessorios Mobile | Acessorios Mobile | 68 | — | — | 9 | **9** |
| Suportes | Mesa/Carro | 70 | — | — | 20 | **20** |
| Segurança | | 334 | — | 10 | — | **10** |
| Tripés | Monopé | 233 | — | — | 3 | **3** |

### Moda (1,791 products)

| L2 | L3 | ID | China | 1688 | Brasil | arbt.ly | Total |
|----|----|-----|-------|------|--------|---------|-------|
| *(sem L2)* | | 2 | 872 | 93 | 204 | — | **1,169** |
| Bolsas | | 58 | 266 | — | — | — | **266** |
| Meias | | 310 | — | 76 | — | — | **76** |
| Roupa Íntima | | 306 | — | 74 | — | — | **74** |
| Banho | *(sem L3)* | 257 | 40 | — | — | — | **40** |
| Banho | Toalha | 258 | 6 | — | — | 1 | **7** |
| Cintas | Modeladora | 279 | — | — | — | 20 | **20** |
| Puma | Kit | 246 | — | — | — | 18 | **18** |
| Calcinhas | Fio Dental | 277 | — | — | — | 18 | **18** |
| Viagem | Mala Bordo | 154 | — | — | — | 15 | **15** |
| Viagem | Necessaire | 155 | — | — | — | 2 | **2** |
| Cueca | Boxer | 281 | — | — | — | 15 | **15** |
| Cueca | Cueca | 282 | — | — | — | 2 | **2** |
| Mochilas | Mochila | 248 | — | — | — | 10 | **10** |
| Acessórios | | *(8 IDs)* | — | — | — | 13 | **13** |
| Feminina | | *(5 IDs)* | — | — | — | 15 | **15** |
| Roupas | | *(5 IDs)* | — | — | — | 9 | **9** |
| Outros | | *(5 IDs)* | — | — | — | 7 | **7** |
| Carteira | Carteira | 263 | — | — | — | 6 | **6** |
| Calçados | Chinelo | 260 | — | — | — | 2 | **2** |
| Calçados | Tênis | 261 | — | — | — | 1 | **1** |
| Meia Calça | | *(2 IDs)* | — | — | — | 4 | **4** |
| Artesanato | Artesanato | 256 | — | — | — | 1 | **1** |
| Auto | Acessório Auto | 146 | — | — | — | 1 | **1** |

### Casa (1,660 products)

| L2 | L3 | ID | China | 1688 | Brasil | arbt.ly | Total |
|----|----|-----|-------|------|--------|---------|-------|
| *(sem L2)* | | 5 | 720 | 171 | 130 | — | **1,021** |
| Organização | *(sem L3)* | 203 | 294 | — | — | — | **294** |
| Cozinha | *(sem L3)* | 196 | 2 | 59 | — | — | **61** |
| Banheiro | | 349 | — | 60 | — | — | **60** |
| Quarto | | 353 | — | 60 | — | — | **60** |
| Sala | | 357 | — | 60 | — | — | **60** |
| Banho | Tapete de Banho | 194 | — | — | — | 29 | **29** |
| Cozinha | Garrafa Térmica | 199 | — | — | — | 9 | **9** |
| Cozinha | Pote Hermético | 200 | — | — | — | 7 | **7** |
| Cozinha | Copo | 198 | — | — | — | 5 | **5** |
| Organização | Organizador | 207 | 9 | — | — | 6 | **15** |
| Jardim | | 45 | 22 | — | — | — | **22** |
| Decoracao | | 29 | 5 | — | — | — | **5** |
| Banho | *(sem L3)* | 193 | 3 | — | — | — | **3** |
| Cozinha | Bolsa Térmica | 197 | — | — | — | 1 | **1** |
| Banho | Tapete de Entrada | 195 | — | — | — | 1 | **1** |
| Organização | Cesto | 205 | — | — | — | 2 | **2** |
| Organização | Cabide | 204 | — | — | — | 1 | **1** |
| Organização | Lixeira | 206 | — | — | — | 1 | **1** |
| Lavanderia | Varal | 202 | — | — | — | 1 | **1** |
| Outros | Outros | 209 | — | — | — | 1 | **1** |
| Pote | Pote | 211 | — | — | — | 1 | **1** |

### Esportes (1,130 products)

| L2 | L3 | ID | China | 1688 | Brasil | arbt.ly | Total |
|----|----|-----|-------|------|--------|---------|-------|
| *(sem L2)* | | 8 | 596 | — | 123 | — | **719** |
| Academia | | 25 | 4 | 120 | — | — | **124** |
| Localizadores | Smart Tag | 224 | — | — | — | 69 | **69** |
| Praia | | 312 | 4 | 59 | — | — | **63** |
| Bolas | | 320 | — | 60 | — | — | **60** |
| Outdoor | | 316 | — | 60 | — | — | **60** |
| Automotivo | | 423 | 12 | — | — | — | **12** |
| Acessórios | Clips | 295 | — | — | — | 7 | **7** |
| Pesca | | 398 | 5 | — | — | — | **5** |
| Acessórios Smart Tag | Capas | 405 | — | — | — | 3 | **3** |
| Acessórios Smart Tag | Garrafas | 417 | 1 | — | — | — | **1** |
| Mobiliário | Cadeira de Praia | 297 | — | — | — | 3 | **3** |
| Têxtil | Toalha de Praia | 299 | — | — | — | 3 | **3** |
| Têxtil | *(sem L3)* | 298 | 1 | — | — | — | **1** |

### Beleza (938 products)

| L2 | L3 | ID | China | 1688 | Brasil | arbt.ly | Total |
|----|----|-----|-------|------|--------|---------|-------|
| *(sem L2)* | | 7 | 671 | — | 46 | — | **717** |
| Skincare | Limpeza | 365 | — | 59 | — | — | **59** |
| Maquiagem | Base | 56 | — | 59 | — | 1 | **60** |
| Skincare | Limpeza Facial | 138 | — | — | — | 10 | **10** |
| Skincare | Hidratante Facial | 137 | — | — | — | 9 | **9** |
| Corpo & Banho | Reparador | 122 | — | — | — | 9 | **9** |
| Skincare | Hidratante Corporal | 136 | — | — | — | 7 | **7** |
| Skincare | Protetor Solar | 140 | — | — | — | 6 | **6** |
| Higiene | Sabonete | 125 | — | — | — | 5 | **5** |
| Maquiagem | Máscara de Cílios | 133 | — | — | — | 5 | **5** |
| Cabelo | Escova | 114 | 14 | — | — | 1 | **15** |
| Skincare | Sérum | 141 | — | — | — | 3 | **3** |
| Skincare | *(sem L3)* | 135 | 4 | — | — | — | **4** |
| Cabelo | Secador | 24 | — | — | — | 4 | **4** |
| Maquiagem | *(sem L3)* | 20 | 4 | — | — | — | **4** |
| Cabelo | Óleo Capilar | 120 | — | — | — | 3 | **3** |
| Barbear | Aparador | 111 | — | — | — | 3 | **3** |
| Higiene | Desodorante | 124 | — | — | — | 2 | **2** |
| Cabelo | Shampoo | 119 | — | — | — | 2 | **2** |
| Barbear | Barbeador | 112 | — | — | — | 2 | **2** |
| Industrial | Higiene | 127 | — | — | — | 1 | **1** |
| Industrial | Limpeza | 128 | — | — | — | 1 | **1** |
| Cabelo | Finalizador | 115 | — | — | — | 1 | **1** |
| Cabelo | Máscara Capilar | 116 | — | — | — | 1 | **1** |
| Cabelo | Prancha | 117 | — | — | — | 1 | **1** |
| Maquiagem | Batom | 131 | — | — | — | 1 | **1** |
| Maquiagem | Corretivo | 132 | — | — | — | 1 | **1** |
| Maquiagem | Sobrancelha | 134 | — | — | — | 1 | **1** |
| Skincare | Outros | 139 | — | — | — | 1 | **1** |

### Ferramentas (820 products)

| L2 | L3 | ID | China | 1688 | Brasil | arbt.ly | Total |
|----|----|-----|-------|------|--------|---------|-------|
| *(sem L2)* | | 10 | 462 | — | 68 | 2 | **532** |
| Elétricas | *(sem L3)* | 225 | 27 | 102 | — | — | **129** |
| Manuais | *(sem L3)* | 63 | — | 60 | — | — | **60** |
| Medição | | 328 | — | 59 | — | — | **59** |
| Manuais | Jogo de Ferramentas | 230 | — | — | — | 29 | **29** |
| Elétricas | Furadeira | 226 | — | — | — | 7 | **7** |
| Elétricas | Lixadeira | 228 | — | — | — | 2 | **2** |
| Elétricas | Lavadora | 227 | — | — | — | 1 | **1** |
| Manuais | Soquete | 231 | — | — | — | 1 | **1** |

### Cozinha (632 products)

| L2 | L3 | ID | China | Brasil | arbt.ly | Total |
|----|----|-----|-------|--------|---------|-------|
| *(sem L2)* | | 9 | 539 | 44 | — | **583** |
| Utensílios | *(sem L3)* | 216 | 38 | — | — | **38** |
| Utensílios | Garrafa | 219 | — | — | 1 | **1** |
| Utensílios | Pote Hermético | 220 | — | — | 1 | **1** |
| Utensílios | Copo | 218 | — | — | 1 | **1** |
| Utensílios | Talher | 221 | — | — | 2 | **2** |
| Utensílios | Bowl | 217 | — | — | 1 | **1** |
| Utensílios | Cápsula | 218 | — | — | 1 | **1** |
| Utensílios | Pipoqueira | 220 | — | — | 1 | **1** |
| Utensílios | Utensílios | 222 | — | — | 1 | **1** |
| Eletrodomésticos | Chaleira | 214 | — | — | 2 | **2** |
| Eletrodomésticos | Cafeteira | 213 | — | — | 1 | **1** |
| Eletrodomésticos | Liquidificador | 215 | — | — | 1 | **1** |

### Pets (590 products)

| L2 | L3 | ID | China | 1688 | Brasil | arbt.ly | Total |
|----|----|-----|-------|------|--------|---------|-------|
| *(sem L2)* | | 11 | 430 | — | 73 | — | **503** |
| Dia a Dia | Acessórios | 373 | — | 24 | — | — | **24** |
| Ração | Gatos | 375 | — | 21 | — | — | **21** |
| Acessórios | Coleira | 376 | — | 15 | — | — | **15** |
| Saúde | *(sem L3)* | 292 | 13 | — | — | — | **13** |
| Cães | Ração | 288 | — | — | — | 4 | **4** |
| Saúde | Antipulgas | 293 | — | — | — | 4 | **4** |
| Acessórios | Acessório Pet | 284 | — | — | — | 2 | **2** |
| Cães | Tapete Higiênico | 289 | — | — | — | 2 | **2** |
| Brinquedos | Brinquedo Pet | 286 | — | — | — | 1 | **1** |
| Gatos | Areia Sanitária | 291 | — | — | — | 1 | **1** |

### Infantis (990 products)

| L2 | L3 | ID | China | 1688 | Brasil | arbt.ly | Total |
|----|----|-----|-------|------|--------|---------|-------|
| *(sem L2)* | | 6 | 716 | — | 88 | 2 | **806** |
| Roupas | Acessórios | 368 | — | 45 | — | — | **45** |
| Fraldas & Lenços | Fralda Descartável | 95 | — | — | — | 27 | **27** |
| Jogos | Cartas | 172 | — | — | — | 13 | **13** |
| Alimentação | Refeição | 93 | — | 12 | — | 1 | **13** |
| Educativo | Blocos de Montar | 166 | — | — | — | 10 | **10** |
| Massinha | Massinha | 177 | — | — | — | 8 | **8** |
| Splash/Água | Piscina/Água | 189 | — | — | — | 3 | **3** |
| Pelúcia | Personagem | 181 | — | — | — | 5 | **5** |
| Bonecos | Carrinho | 160 | — | — | — | 6 | **6** |
| Bonecos | Action Figure | 159 | 3 | — | — | 2 | **5** |
| Brinquedos | | 369 | 4 | — | — | — | **4** |
| Eletrônicos | Robô | 168 | — | — | — | 4 | **4** |
| Higiene | Sabonete | 97 | — | — | — | 3 | **3** |
| Higiene | Shampoo | 98 | — | — | — | 3 | **3** |
| Livros | Livro | 175 | — | — | — | 3 | **3** |
| Bebê | Bebê | 157 | — | — | — | 3 | **3** |
| Coleção | Figurinhas | 162 | — | — | — | 3 | **3** |
| Mobilidade | Carrinho | 104 | — | — | — | 2 | **2** |
| Alimentação | Copo com Bico | 90 | — | — | — | 2 | **2** |
| Splash/Água | Bolhas | 187 | — | — | — | 1 | **1** |
| Splash/Água | Educativo | 188 | — | — | — | 1 | **1** |
| Splash/Água | Pistola Água | 190 | — | — | — | 1 | **1** |
| Industrial | Luvas | 100 | — | — | — | 1 | **1** |
| Industrial | Outros | 101 | — | — | — | 1 | **1** |
| Industrial | Sabão | 102 | — | — | — | 1 | **1** |
| Cubo Mágico | Cubo Mágico | 164 | — | — | — | 1 | **1** |
| Festa | Balão | 170 | — | — | — | 1 | **1** |
| Jogos | Tabuleiro | 173 | — | — | — | 1 | **1** |
| Presentes | Presente | 183 | — | — | — | 1 | **1** |
| Quarto | Swaddle | 106 | — | — | — | 1 | **1** |
| Quarto | Toalha | 107 | — | — | — | 1 | **1** |
| Roupas | Conjunto | 109 | — | — | — | 1 | **1** |
| Sensory | Sensory | 185 | — | — | — | 1 | **1** |
| Utensílios | Utensílios | 192 | — | — | — | 1 | **1** |
| Alimentação | Bebida | 87 | — | — | — | 1 | **1** |
| Alimentação | Cadeira | 88 | — | — | — | 1 | **1** |
| Alimentação | Canguru | 89 | — | — | — | 1 | **1** |
| Alimentação | Forma | 91 | — | — | — | 1 | **1** |
| Alimentação | Mamadeira | 92 | — | — | — | 3 | **3** |

### Wearables (276 products)

| L2 | L3 | ID | China | Brasil | arbt.ly | Total |
|----|----|-----|-------|--------|---------|-------|
| *(sem L2)* | | 19 | 150 | 36 | — | **186** |
| Smartwatch | Outros | 303 | 13 | — | 32 | **45** |
| Pulseiras | Smartwatch | 410 | — | — | 21 | **21** |
| Smartwatch | Samsung | 304 | — | — | 8 | **8** |
| Smartwatch | Amazfit | 301 | — | — | 7 | **7** |
| Smartwatch | Xiaomi | 305 | — | — | 6 | **6** |
| Smartwatch | *(sem L3)* | 300 | 2 | — | — | **2** |
| Smartwatch | Apple Watch | 302 | — | — | 1 | **1** |

### Móveis (510 products)

| L2 | ID | China | Brasil | Total |
|----|----|-------|--------|-------|
| *(sem L2)* | 12 | 290 | 1 | **291** |
| Escritório | 395 | 199 | — | **199** |
| Gamer | 396 | 20 | — | **20** |

### Papelaria (354 products)

| L2 | L3 | ID | China | 1688 | Brasil | Total |
|----|----|-----|-------|------|--------|-------|
| *(sem L2)* | | 13 | 265 | — | 13 | **278** |
| Escrita | Canetas | 379 | — | 40 | — | **40** |
| Organização | Pastas | 381 | — | 35 | — | **35** |
| Escrita | *(sem L3)* | 377 | 1 | — | — | **1** |

### Industrial (50 products)

| L2 | ID | China | 1688 | Total |
|----|----|-------|------|-------|
| Equipamentos | 399 | 33 | 1 | **34** |
| Máquinário | 400 | 8 | — | **8** |
| *(sem L2)* | 387 | 8 | — | **8** |

### L1 com poucos products

| L1 | ID | China | Total |
|----|-----|-------|-------|
| Calçados | 17 | 150 | **150** |
| Saúde | 16 | 172 | **241** |
| Saúde | Monitores | 397 | 1 | **1** |
| Têxteis | 386 | 50 | **50** |
| jardim | 35 | 30 | **30** |
| Eletrodomésticos | 384 | 24 | **24** |
| Computadores | 385 | 23 | **23** |
| Organização | 388 | 21 | **21** |
| Bolsas | Bolsas de Mão | 392 | 2 | **2** |

---

## Rejeitadas (não criar)

| L1 | L2 | Motivo |
|----|----|--------|
| Pets | Equinos | 2 products — muito pouco |
| Papelaria | Organização | 1 product — muito pouco |
| Iluminação | Smart Home | 0 products — category_resolver.py já resolve para Eletrônicos > Smart Home |
| Jardim | Decoração | 0 products — usar Casa > Decoracao (ID 29) |

---

## Instruções por Agent

### Para arbitlens_china

1. Usar `category_resolver.py` para resolver categorias
2. Products devem ter L1 + L2 no mínimo
3. Para criar nova categoria: `ensure_category(conn, l1, l2, l3)`
4. Para mapear: `add_platform_mapping(conn, platform, l1_id, l2_id, silver_category_id)`
5. Verificar categories existentes antes de criar novas

### Para products-1688

1. Rodar `resolve_category()` em todos os products
2. Source agora é '1688' (era 'datalake')
3. Mappings em `silver_categories_map` com `created_by='products-1688'`
4. Não criar categorias sem aprovação

### Para arbitlens_brasil

1. Usar `category_resolver.py` para resolver categorias
2. Mappings em `silver_categories_map` com `created_by='arbitlens_brasil'`
3. Verificar categories existentes antes de criar novas

### Para arbt.ly

1. L2/L3 já estão 100% preenchidos ✅
2. Manter consistência ao adicionar novos products
3. Usar categorias existentes sempre que possível

---

## Contacts

| Agent | Source | DB |
|-------|--------|-----|
| arbitlens_china | arbitlens_china | importasimples_products |
| products-1688 | 1688 | importasimples_products |
| arbitlens_brasil | arbitlens_brasil | importasimples_products |
| arbt.ly | arbt.ly | importasimples_products |

---

*Referência: [SPRINT6.md](SPRINT6.md) | [ASSESSMENT_CATEGORIES.md](ASSESSMENT_CATEGORIES.md)*


---

## products-1688 — Status Atualizado (2026-07-01)

### Cobertura

| Métrica | Valor |
|---------|-------|
| Total products | 1,899 |
| Com L1 | 1,899 (100%) |
| Com L2 | 1,899 (100%) |
| Com L3 | 1,899 (100%) |
| Com silver_category_id | 1,899 (100%) |

### Mappings

| Platform | Count |
|----------|-------|
| 1688 | 264 |
| datalake | 0 (renomeado para 1688) |

### Conclusão

**products-1688 NÃO tem products sem L2.** Todos os 1,899 products já têm L1 + L2 + L3.

O documento original estava desatualizado — os 2,010 products sem L2 eram de arbitlens_china, não de products-1688.
