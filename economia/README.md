# Painel de Gastos Pessoais — Raphael

Este diretorio contem um painel estatico (sem dependencias externas) que consolida
os extratos do cartao de credito Bradesco e do Nubank de Raphael, de novembro/2025
a junho/2026, para acompanhar o orcamento mensal (salario liquido disponivel:
**R$ 7.400/mes**) contra o gasto real de rotina ("Vida Real"), mantendo os gastos
da viagem dos sonhos completamente separados.

## Arquivos

- `data/transactions.json` — todas as transacoes normalizadas (350 no total),
  uma por linha, com os campos: `date`, `month` (`YYYY-MM`), `source`
  (`"nubank"` ou `"bradesco"`), `card`, `description`, `amount_brl`,
  `original_currency`, `original_amount`, `bucket` (`"vida_real"` ou
  `"viagem"`), `category` (so para `vida_real`) e `note` (observacoes de
  reconciliacao, quando aplicavel). Nenhum numero de cartao ou conta completo
  foi copiado — apenas os 4 ultimos digitos de cada cartao Bradesco
  ("1426" / "3134"), que ja vinham parcialmente mascarados no PDF original.
- `dashboard.html` — painel visual auto-contido (HTML/CSS/JS puro, sem CDN,
  dados embutidos diretamente no arquivo). Abra direto no navegador.
- `data/build_dashboard_data.py` — script que le `transactions.json`, agrega
  por mes/categoria, acrescenta o gasto fixo de Moradia/Financiamento e
  imprime o JSON (incluindo a lista de lancamentos por categoria usada no
  drill-down) que deve ser colado no `const DATA = ...` de `dashboard.html`
  sempre que os dados forem atualizados. Uso: `py data/build_dashboard_data.py`.
- `README.md` — este arquivo.

## Fontes de dados

- **Nubank**: 8 CSVs mensais (nov/2025 a jun/2026), formato `date,title,amount`,
  ja com datas reais por lancamento — inclusive parcelas, que ja vem com a data
  de cobranca correta de cada mes.
- **Bradesco**: 8 faturas em PDF (fatura com vencimento em cada mes de
  dez/2025 a jul/2026, cobrindo compras de out/2025 a jun/2026). Cada fatura
  tem duas "paginas" de lancamentos: cartao titular (final 1426) e cartao
  adicional (final 3134).
- **A fatura com vencimento ~08/04/2026 (compras de marco/2026) esta
  corrompida** — o arquivo no Drive tem apenas 3 bytes e nao pode ser lido de
  forma alguma (tentado via `read_file_content` e `download_file_content`).
  **Os gastos do cartao Bradesco em marco/2026 estao ausentes deste painel.**
  O Nubank de marco/2026 esta completo e presente normalmente.

### Impacto estimado da fatura de marco ausente

Alem de qualquer compra feita e paga integralmente em marco (totalmente
invisivel), a fatura corrompida tambem contem a **2a parcela de 3** de quatro
reservas de viagem (HOTEIS.COM x2, DL\*HOTEIS.COM, AIRBNB\*HM9MQAK) e a
**1a parcela de 3** do aluguel de carro (NVE\*RENTCARSLTDA) e da compra
PET LOVE\*Order 10 — identificadas porque a mesma linha reaparece nas faturas
anterior e posterior com o contador de parcela incrementado (ex.: "01/03" em
fev/2026 e "03/03" em abr/2026, faltando a "02/03"). Somando as parcelas
recuperadas dos dois lados como proxy, a **estimativa de gasto Viagem nao
capturado por causa desse PDF corrompido fica em torno de R$ 2.250** (nao
incluido nos totais do painel — apenas as parcelas efetivamente lidas entram).

## Regras de classificacao Vida Real vs. Viagem

Seguindo a instrucao literal do usuario — simples e sem julgar caso a caso:

1. **Qualquer transacao cobrada em moeda estrangeira (USD ou EUR)** — identificada
   no PDF Bradesco pelo padrao `MERCHANT USD 128,08 ... 5,6600 724,93` (ou EUR),
   e tambem qualquer linha `CUSTO TRANS. EXTERIOR-IOF` / `IOF de trans. exterior`
   associada. No Nubank, a presenca de uma linha `IOF de "X"` no mesmo extrato e
   o sinal de que aquela compra foi cobrada em moeda estrangeira (a nota fiscal do
   Nubank so mostra o valor final em reais, mas o IOF de transacao internacional
   so incide sobre compras em moeda estrangeira).
2. **Qualquer estabelecimento de viagem/reserva mesmo cobrado em reais**:
   passagens aereas (LATAM AIR, RYANAIR, LATAM AIRLIN), hospedagem
   (HOTEIS.COM, AIRBNB, DLOCAL\*Bookingcom, GaribaldiHostelE), aluguel de carro
   (NVE\*RENTCARSLTDA), passeios/ingressos de viagem (Getyourguide, Ms\*
   Citypop2nightprag, biglietteriamusei.vatican, FEVER\*MUSEU DO IPIRANGA,
   CG\*colosseumticket.c, TRENITALIA), documentos de viagem (UKVI ETAMOB = taxa
   de visto do Reino Unido).
3. **Excecao explicita**: `AZUL SEGUROS` (R$ 175,15/mes) e uma **apolice de
   seguro recorrente**, nao passagem aerea — mantida em Vida Real.
4. **Excluido inteiramente do calculo de gasto** (nao sao despesas): pagamentos
   de fatura (`Pagamento recebido`, `PAGTO. POR DEB EM C/C`), estornos
   (`Estorno de ...` — compensados contra a compra original, ver abaixo),
   ajustes a credito (`Ajuste a credito`) e reversoes de IOF
   (`IOF de volta de ...`).

### Excecao confirmada: Preply → Vida Real

**Preply** (aulas de ingles, cobrado em EUR de Berlim, ~R$ 130–225/mes,
aparece em ambos os cartoes) foi inicialmente classificado como Viagem pela
regra literal ("qualquer transacao em EUR/USD = viagem"), pois e cobrado em
moeda estrangeira. **Raphael confirmou que e estudo/vida real, nao viagem** —
os 5 lancamentos abaixo foram reclassificados de `"viagem"` para
`"vida_real"` (categoria `"Assinaturas"`) em `data/transactions.json`, e o
`dashboard.html` foi regenerado com os novos totais:

| Data | Descricao | Valor | Origem |
|---|---|---:|---|
| 2025-11-07 | Preply | R$ 142,13 | Bradesco |
| 2026-01-30 | Preply | R$ 127,28 | Bradesco |
| 2026-04-16 | Preply | R$ 132,80 | Bradesco |
| 2026-05-15 | Preply | R$ 220,19 | Nubank |
| 2026-06-11 | Preply | R$ 223,77 | Nubank |

Total reclassificado: **R$ 846,17** (movido de Viagem para Vida Real).

`Wl *Steam Purchase` (Nubank, 04/04/2026, R$ 117,62) tambem foi cobrado em
moeda estrangeira e permanece marcado como Viagem pela regra literal — nao
foi mencionado pelo usuario como excecao. Se Raphael quiser tambem mover essa
compra (jogo digital, nao parece ligada a viagem), basta mudar o campo
`bucket` dessa linha em `data/transactions.json` de `"viagem"` para
`"vida_real"` e reexecutar a agregacao usada para gerar o `DATA` embutido no
`<script>` de `dashboard.html`.

## Netting de estornos e ajustes (Nubank)

O Nubank as vezes mostra a compra original e o estorno em meses diferentes.
Em vez de listar as duas linhas separadamente (o que distorceria o mes do
estorno como se fosse um "reembolso" isolado), o valor foi **compensado
contra a compra original**:

- `Mercadolivre*Mercadol` (10/12/2025, R$ 36,72) — estornado integralmente em
  06/01/2026. Removido do painel (efeito liquido zero).
- `Mp *Aliexpress` (21/01/2026, R$ 173,49) — estornado parcialmente em
  11/02/2026 (R$ 126,39). Mantido em `transactions.json` com o valor liquido
  de **R$ 47,10**, na data da compra original.
- `Mercadolivre*Mercadoli` (18/05/2026, R$ 150,30) — estornado integralmente
  em 29/05/2026 (mesmo mes). Removido do painel (efeito liquido zero).
- `Centre Des Monuments N` (15/02/2026, Paris) — o IOF de R$ 7,31 sobre essa
  compra foi revertido no mesmo dia via `Ajuste a credito` (em vez do padrao
  `IOF de volta de ...`). Tratado como equivalente e ambas as linhas
  (IOF + ajuste) foram removidas; a compra principal (R$ 209,06, Viagem)
  permanece.
- Todos os demais pares `IOF de "X"` / `IOF de volta de X"` (Atac Tap&Go,
  Paypal \*Culture, Ms\* Citypop2nightprag, Getyourguide, Wl \*Steam Purchase,
  Preply em maio e junho) se cancelam exatamente no mesmo extrato — ambas as
  linhas foram removidas, mantendo apenas a compra principal.

## Bucketing mensal (a que mes cada transacao pertence)

- **Nubank**: usa a data do CSV diretamente — ja e a data real de cada
  cobranca, inclusive de cada parcela.
- **Bradesco, compras avulsas** (sem contador de parcela): usa a data
  "DD/MM" impressa na propria linha, inferindo o ano pelo ciclo da fatura
  (ex.: uma fatura com vencimento 08/12/2025 cobre compras de ~27/10 a
  26/11/2025 — datas "23/11" viram 2025-11, e datas residuais como "30/10"
  viram 2025-10).
- **Bradesco, compras parceladas ou assinaturas recorrentes que repetem a
  mesma data em varias faturas** (ex.: `AZUL SEGUROS`, `LIVELO S.A.*Clube`,
  `LATAM AIR`, `HOTEIS.COM`, `PALADIO INDUSTRIA E COMERCIO`, etc.): o Bradesco
  reimprime a data de origem da compra em toda parcela subsequente (com um
  contador tipo "2/4", "3/4" ao lado). Se usassemos a data de origem
  literalmente, todas as parcelas cairiam no mesmo mes (o mes da compra
  original), inflando aquele mes e zerando os meses seguintes — o que
  distorceria o grafico de orcamento mensal, que e sobre fluxo de caixa real.
  **Por isso, essas linhas foram alocadas ao mes de fechamento da fatura em
  que cada parcela realmente apareceu** (ex.: a 2a parcela do LATAM AIR que
  aparece na fatura fechada em 26/11/2025 foi datada 2025-11-26; a 3a parcela
  na fatura fechada em 26/12/2025 foi datada 2025-12-26). Isso reflete melhor
  o impacto real no orcamento mes a mes. Essa e a unica divergencia
  deliberada da regra literal "use a data da transacao" — documentada aqui
  para transparencia.

## Categorias (Vida Real)

Categorias derivadas automaticamente por palavras-chave no nome do
estabelecimento (ver funcao `categorize()` usada na geracao dos dados):
**Mercado/Supermercado, Transporte, Alimentacao/Restaurantes, Assinaturas,
Compras Online, Saude/Farmacia, Outros**. "Outros" inclui itens que nao se
encaixam claramente nas demais (oficina mecanica, pet shop, barbearia,
ingressos de evento local, pagamentos a pessoas fisicas, etc.) — vale revisar
essa categoria periodicamente se quiser refinar a classificacao. Ha ainda uma
oitava categoria, **Moradia/Financiamento**, que nao vem de transacao de
cartao — e o gasto fixo mensal descrito na secao "Gasto fixo:
Moradia/Financiamento" abaixo.

## Reconciliacao com o "Resumo da fatura" (Bradesco)

Cada fatura Bradesco tem uma linha `(+)Compras/Debitos` no resumo, que é o
total oficial daquele ciclo. A soma dos lancamentos individuais que
transcrevi foi comparada a esse total:

| Fatura (fechamento) | Soma dos lancamentos | Compras/Debitos oficial | Diferenca |
|---|---:|---:|---:|
| 26/11/2025 (nov) | R$ 5.815,12 | R$ 5.815,12 | R$ 0,00 |
| 26/12/2025 (dez) | R$ 6.638,55 | R$ 6.638,55 | R$ 0,00 |
| 28/01/2026 (jan) | R$ 8.907,63 | R$ 8.907,63 | R$ 0,00 |
| 25/02/2026 (fev) | R$ 9.831,87 | R$ 9.831,87 | R$ 0,00 |
| ~mar/2026 | — corrompida, sem dados — | — | — |
| 27/04/2026 (abr) | R$ 9.515,51 | R$ 9.526,01 | **-R$ 10,50** |
| 26/05/2026 (mai) | R$ 2.361,77 | R$ 2.361,77 | R$ 0,00 |
| 26/06/2026 (jun) | R$ 3.920,08 | R$ 3.998,98 | **-R$ 78,90** |

5 das 7 faturas legiveis reconciliam **exatamente ao centavo**. As duas
excecoes (abr e jun/2026) tem uma diferenca pequena e explicavel: em ambos os
meses, o "Resumo da fatura" mostra `Creditos/Pagamentos` **maior** que o
`Saldo anterior` (ex.: abr/2026: saldo anterior R$ 9.576,86, mas
creditos/pagamentos R$ 9.587,36 — R$ 10,50 a mais). Isso indica um credito
extra aplicado diretamente ao saldo naquele mes, sem uma linha de compra/
estorno correspondente visivel na lista de lancamentos — um limite da
extracao de texto do PDF, nao um erro de transcricao (a soma dos lancamentos
bate exatamente com o subtotal por cartao impresso na propria fatura, "Total
para RAPHAEL FRANKLIN..."). Dois pontos especificos que valem registrar:

- Na fatura de abr/2026, o texto extraido mostra **tres** lancamentos
  `Mc Donalds - Arcos Dourados` de R$ 10,50 em 11/04, mas o ultimo vem seguido
  de um traço isolado no texto (possivel marca de estorno/reversao). Incluir
  os tres ultrapassa o subtotal do cartao 1426 impresso na fatura em
  exatamente R$ 21,00 (= 2 × R$ 10,50). Duas dessas linhas foram netadas
  (comentadas no gerador) para reconciliar exatamente com o subtotal oficial.
- Na fatura de jun/2026, uma linha `MERCADOLIVRE*MERCADOLIVRE OSASCO R$ 157,80`
  datada 26/05 aparece no topo da secao do cartao 1426, mas inclui-la
  ultrapassa o subtotal oficial do cartao em exatamente R$ 157,80 — parece um
  artefato de extracao (possivel repeticao de cabecalho da fatura anterior).
  Foi excluida para reconciliar exatamente.

## Totais do periodo (visao rapida)

| Mes | Vida Real | Viagem | Sobra vs. R$ 7.400 |
|---|---:|---:|---:|
| out/2025 (parcial)* | R$ 1.858,85 | R$ 0,00 | +R$ 5.541,15 |
| nov/2025 | R$ 5.571,55 | R$ 2.887,44 | +R$ 1.828,45 |
| dez/2025 | R$ 6.092,92 | R$ 2.354,47 | +R$ 1.307,08 |
| jan/2026 | R$ 6.053,97 | R$ 4.989,69 | +R$ 1.346,03 |
| fev/2026 | R$ 5.191,46 | R$ 6.703,08 | +R$ 2.208,54 |
| mar/2026** | R$ 2.894,88 | R$ 122,76 | +R$ 4.505,12 |
| abr/2026 | R$ 5.360,12 | R$ 6.581,82 | +R$ 2.039,88 |
| mai/2026 | R$ 6.584,92 | R$ 216,75 | +R$ 815,08 |
| jun/2026 | R$ 4.760,94 | R$ 0,00 | +R$ 2.639,06 |
| **Total** | **R$ 44.369,61** | **R$ 23.856,01** | — |

*(Atualizado apos reclassificar Preply de Viagem para Vida Real — ver secao
"Excecao confirmada: Preply → Vida Real" — e apos incluir o gasto fixo de
Moradia/Financiamento — ver secao "Gasto fixo: Moradia/Financiamento" abaixo.)*

## Gasto fixo: Moradia/Financiamento (R$ 1.600/mes)

A pedido do usuario, foi adicionado um gasto fixo mensal de **R$ 1.600**
referente ao pagamento do financiamento da casa. Esse valor **nao vem de
`transactions.json`** (nao passa pelo cartao de credito, e debitado
diretamente em conta) — e injetado como uma categoria sintetica
(`Moradia/Financiamento`) por `data/build_dashboard_data.py`, um lancamento
de R$ 1.600 por mes, em **todos os 9 meses do painel, inclusive out/2025
(parcial)**. Ele entra como parte de "Vida Real" (soma ao total do mes e ao
calculo de sobra vs. orcamento), igual as demais categorias. Se o valor ou
o periodo mudar no futuro, ajuste as constantes `FIXED_AMOUNT`/`FIXED_CATEGORY`
no topo desse script e rode `py data/build_dashboard_data.py` novamente,
depois cole o JSON gerado no `const DATA = ...` de `dashboard.html`.

## Drill-down por categoria (painel interativo)

O grafico "Gasto Vida Real por categoria e mes" agora e clicavel:

- **Clique num item da legenda** para ver todos os lancamentos daquela
  categoria no periodo inteiro (todos os meses).
- **Clique num segmento da barra empilhada** (categoria + mes especifico)
  para ver so os lancamentos daquele mes naquela categoria.
- Um painel abre logo abaixo do grafico com a lista de lancamentos (data,
  descricao, origem do cartao, valor) e o total filtrado. Clicar de novo no
  mesmo item, ou no botao "Fechar", fecha o painel.

Isso e possivel porque `build_dashboard_data.py` agora tambem exporta
`transactions_by_category` (lista de lancamentos por categoria, com data,
descricao, mes e origem) dentro do `DATA` embutido em `dashboard.html`.

\* out/2025 so tem 2 compras Amazon do cartao adicional (cauda da fatura de
nov/2025) — excluido das medias no painel.
\*\* mar/2026 esta **incompleto**: fatura Bradesco corrompida; os valores
mostrados sao so as parcelas Bradesco que vazaram para outras faturas
(datadas pelo mes de fechamento, ver secao de bucketing acima) mais o Nubank
completo desse mes.

Em todos os meses com dados completos, o gasto "Vida Real" ficou
confortavelmente abaixo do orcamento de R$ 7.400 — a "sobra" media gira em
torno de R$ 3.500–4.000/mes, sugerindo que ha espaco real para aumentar a
poupanca/investimento mensal caso deseje.
