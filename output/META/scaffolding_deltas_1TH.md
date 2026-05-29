# Scaffolding-deltas — meta-review 1TH hoofdstukken 1-5

Gegenereerd: 2026-05-29T04:49:21Z
Aggregator: scripts/meta_diff_aggregate.py --book 1TH --chapters 1-5 --min-freq 2

## Samenvatting

Bij `--min-freq 2` levert de aggregator **0 patterns** op
(`total_patterns: 0`, lege `patterns_by_kind`). Geen enkel
carryover-, fossiel-lidwoord-, latinaat-window- of cap-asym-patroon
herhaalt zich ≥2× over de vijf hoofdstukken. Een controle-run met
`--min-freq 1` toont 29 kandidaten, allemaal met **frequency = 1**;
er is dus geen cross-chapter recurrentie om te classificeren.

Gevolg: **geen bucket B**, **geen bucket C**. De singletons hieronder
zijn ter informatie gedocumenteerd (niet flagbaar onder de
min-freq=2-drempel die de skill voor 1TH voorschrijft).

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| _(geen)_ | — | — | — | Geen patroon haalt freq ≥3; niets auto-toe te passen | — |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| _(geen)_ | — | Geen bucket-C-kandidaat bereikte de §2.7-toets; bij min-freq=2 zijn er geen kandidaten |

## Noise (bucket A — HSV-keuze, geen actie)

Alle cap-asym-vondsten zijn SV-interne hoofdletter-/eerbiedskeuzes
(zelfstandignaamwoord- of reverence-caps) die HSV lowercaset. Conform
projectregel "SV-nouncaps bewaren ≠ eerbiedskapitaal" blijven deze
staan; zuiver HSV-keuze, geen modernisatie-tekortkoming.

| Kind | Aantal | Voorbeelden (alle freq=1) |
|---|---|---|
| cap-asym | 6 | Aartsengel (4:16), Apostelen (2:6), Genade (1:1), Heidenen (4:5), Profeten (2:15), Satan (2:18) |
| latinaat-window | 17 | HSV-herschikkingen rond 4:11, 4:13/15, 5:12, 2:4/5/8/18, 3:7 — telkens enige verschil is HSV-zinsbouw, geen Latinaat-rest in SV2026 |

## Singletons buiten drempel (informatief — freq=1, niet geclassificeerd)

Carryover-kandidaten die bij min-freq=1 opdoken. Geen van alle staat in
`DREMPEL_ARCHAISMEN` (`severity_hint: soft`). Bij de
skill-voorgeschreven min-freq=2 vallen ze buiten scope; opgenomen zodat
een latere reviewer ze desgewenst per-vers kan wegen.

| Pattern | Kind | Vers | SV2026 | HSV-alternatief |
|---|---|---|---|---|
| `belet` | carryover | 2:18 | "de Satan heeft ons belet" | verhinderd |
| `genegen` | carryover | 2:8 | "omdat wij zeer tot u genegen waren" | vol verlangen naar |
| `ontslapen` | carryover | 4:15 | "die ontslapen zijn" | ontslapenen (HSV behoudt stam) |
| `sticht` | carryover | 5:11 | "sticht de een de ander" | bouw … op |
| `vat` | carryover | 4:4 | "zijn vat te bezitten" | lichaam |
| `worde` | carryover | 5:23 | "worde onberispelijk bewaard" | moge |

Opmerking: `ontslapen` is geen archaïsme — HSV gebruikt zelf "ontslapenen"
(zelfde stam); HSV-bewijs ontbreekt voor modernisatie. `vat` (σκεῦος)
en `genegen` zijn semantisch beladen keuzes die per-vers oordeel vragen,
geen scaffolding-gap.

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken — zie `findings_1TH.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen (geen kandidaten bij min-freq=2)
- A (noise): 23 (6 cap-asym + 17 latinaat-window, allemaal freq=1 HSV-keuze)
- Singletons buiten drempel (informatief): 6 carryover (freq=1)
