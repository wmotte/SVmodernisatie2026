# Scaffolding-deltas - meta-review HEB hoofdstukken 1-13

Gegenereerd: 2026-05-28T18:02:08Z
Aggregator: `scripts/meta_diff_aggregate.py --book HEB --chapters 1-13 --min-freq 2`

Opmerking: HSV-diffs ontbraken voor HEB 5, 6, 8, 10 en 12. De meta-review is daarom gebaseerd op de beschikbare HSV-diffs voor HEB 1, 2, 3, 4, 7, 9, 11 en 13.

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---:|---|---|---|
| - | - | 0 | - | geen regel-deltas toegepast | geen bucket-C patroon dat de §2.7-toets haalde |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `fol` | carryover | false positive door folio-markers `[fol....]`; HSV-alternatieven zijn inconsistent en dit is geen modernisatie-tekortkoming |

## Noise (bucket A - HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---:|---|
| cap-asym | 8 | `Engelen`, `Heiligdom`, `Hogepriester`, `Koning`, `Priesterschap`, `Ark`, `Heilige`, `Priester` - SV-hoofdletterdiscipline behouden |
| carryover | 1 | `fol` in HEB 3:4, 7:9, 11:18 - folio-marker, geen tekstuele modernisatie |

## Bucket-overzicht

- B (per-vers fixes): 4 issues over 2 hoofdstukken - zie `findings_HEB.json`
- C (scaffolding-deltas): 0 toegepast, 1 afgewezen
- A (noise): 9 patronen
