# Scaffolding-deltas — meta-review 1TI hoofdstukken 1-6

Gegenereerd: 2026-05-29T04:49:47Z
Aggregator: scripts/meta_diff_aggregate.py --book 1TI --chapters 1-6 --min-freq 2

Modus: ANALYSE (Stap 1-3). Geen apply, geen commits, geen regel-edits.

## Auto-toegepaste deltas (bucket C)

Geen. Geen enkel pattern haalt de bucket-C-drempel (freq ≥ 3 met consistent
HSV-modern alternatief, of niet-bijbelse fossiel-lidwoord ≥ 3). De enige
carryover ('fabelen') komt 2× voor → bucket B (per-vers fix), niet C.

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| — | — | — | — | (geen) | — |

## Voorstel-tabel bucket C (NIET uitgevoerd — toekomstige promotie)

Borderline kandidaat: 'fabelen' staat nu op freq 2 (bucket B). Bij een 3e
voorkomen in de rest van het Timoteüs-/Titus-corpus zou promotie naar
bucket-C gerechtvaardigd zijn (uitbreiding `DREMPEL_ARCHAISMEN` in
`scripts/rules_data.py` + rij in `ARCHAISMEN.md`: fabelen → verzinsels).
§2.7-toets: productiviteit faalt ('fabel' = dierenverhaal, dominant andere
betekenis = verwarringtest gezakt voor de bedoelde zin 'verzonnen verhalen').

| Voorstel | Kind | Target | Bewijs (3 citaten) |
|---|---|---|---|
| `fabelen → verzinsels` (DREMPEL_ARCHAISMEN + ARCHAISMEN.md) | carryover | `scripts/rules_data.py`, `ARCHAISMEN.md` | (1) 1TI 1:4 "in te laten met fabelen en eindeloze geslachtsregisters" / HSV "verzinsels"; (2) 1TI 4:7 "ongoddelijke en oudewijvenachtige fabelen" / HSV "verzinsels"; (3) SV1657 1:4 "fabelen, ende oneyndelicke geslacht-reeckeningen" = Grieks μῦθος (mythos) = verzonnen verhalen |

NB: alleen 2 voorkomens binnen 1TI 1-6 → blijft voorlopig bucket B.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen bucket-C-delta voorgesteld voor onmiddellijke toepassing, dus niets
afgewezen op §2.7-grond. De 4 cap-asym-patterns zijn bucket A (zie noise).

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| — | — | — |

## Noise (bucket A — HSV-keuze, geen actie)

Alle cap-asym-patterns: SV2026 behoudt de SV1657-hoofdletter op het
zelfstandig naamwoord; HSV kiest consistent kleine letter. Dit is een
HSV-keuze, geen modernisatie-tekortkoming. SV-intern is elk woord
consistent gekapitaliseerd binnen 1TI 1-6 (geen lowercase-variant gevonden),
dus geen interne inconsistentie → geen bucket-C-note nodig. Behoud is conform
projectregel (toegevoegde caps verboden; SV-noun-caps bewaren ≠
eerbiedskapitaal). Eigennamen niet geflagd (Paulus, Jezus Christus).

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 4 | Apostel (1:1, 2:7), Engelen (3:16, 5:21), Heidenen (2:7, 3:16), Opziener (3:1, 3:2) |

## Bucket-overzicht

- B (per-vers fixes): 2 issues over 2 hoofdstukken (1:4, 4:7) — zie `findings_1TI.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen (1 voorstel-kandidaat geparkeerd op freq 2)
- A (noise): 4 cap-asym-patterns
