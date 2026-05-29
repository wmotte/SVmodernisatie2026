# Scaffolding-deltas — meta-review PHM hoofdstuk 1

Gegenereerd: 2026-05-29T04:49:52Z
Aggregator: scripts/meta_diff_aggregate.py --book PHM --chapters 1 --min-freq 2

Eén hoofdstuk (PHM heeft alleen hoofdstuk 1). Bij `--min-freq 2` levert de
aggregator **0 patterns** — geen pattern komt binnen één hoofdstuk twee keer
voor. Een diagnostische run met `--min-freq 1` toont 12 freq=1-patterns
(11 latinaat-window, 1 carryover); alle vallen onder de drempel en zijn na
inspectie bucket A (HSV-keuze / vrije syntaxis). Geen bucket B, geen bucket C.

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| _(geen)_ | — | — | — | — | — |

Geen pattern haalt freq ≥ 3 (of zelfs ≥ 2). Geen scaffolding-gap. §2.7-toets
niet van toepassing.

## VOORSTEL bucket-C (niet uitgevoerd — analyse-modus)

| Pattern | Kind | Freq | Voorstel | Bewijs (3 citaten) |
|---|---|---|---|---|
| _(geen)_ | — | — | — | — |

Er zijn geen freq≥3-kandidaten, dus geen scaffolding-voorstellen.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| _(geen)_ | — | Niets bereikte de bucket-C-drempel; geen §2.7-toets nodig. |

## Noise (bucket A — HSV-keuze, geen actie)

Alle 12 sub-drempel-patronen (freq=1) zijn bucket A. Inspectie bevestigt:
HSV parafraseert/herschikt; SV2026 gebruikt al hedendaags Nederlands.

| Kind | Aantal | Voorbeelden |
|---|---|---|
| latinaat-window | 11 | PHM 1:7 "vreugde vertroosting over liefde" (HSV-herschikking "veel vreugde en troost aan uw liefde"); PHM 1:9 "bid toch liever door liefde" (HSV-parafrase "spoor ik u veel liever aan"); PHM 1:17 "houdt voor een metgezel neem hem" (HSV "aanvaard hem dan"); PHM 1:19 "betalen opdat niet zeg dat" (HSV "om niet te zeggen dat") |
| carryover | 1 | PHM 1:18 "reken dat mij toe" vs HSV "breng dat mij in rekening" — "toerekenen" is productief, courant Nederlands (theologische term: toerekening); geen archaïsme, HSV-keuze |

Detail bucket A:
- **latinaat-window (11×, alle freq=1)**: Geen Latinaat-rest in SV2026; het
  enige verschil is HSV-herschikking/parafrase van de zinsbouw. Valt onder
  SKILL §2-criterium "HSV-herschikking als enige verschil → bucket A".
- **carryover "toe" (1×, freq=1)**: SV2026 "reken dat mij toe" is modern en
  correct; HSV kiest de omschrijving "in rekening brengen". Geen
  drempel-archaïsme, geen false friend → bucket A.

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken — zie `findings_PHM.json` (leeg)
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen (geen kandidaat boven drempel)
- A (noise): 12 (11 latinaat-window + 1 carryover), allen freq=1 sub-drempel

Conclusie: voor PHM hoofdstuk 1 bij min-freq 2 zijn er geen
modernisatie-tekortkomingen en geen scaffolding-gaps. Leeg findings +
noise-only scaffolding is het verwachte en geldige resultaat voor één
hoofdstuk.
