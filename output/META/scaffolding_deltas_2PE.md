# Scaffolding-deltas — meta-review 2PE hoofdstukken 1-3

Gegenereerd: 2026-05-26T10:52:00Z
Aggregator: scripts/meta_diff_aggregate.py --book 2PE --chapters 1-3 --min-freq 2

Bereiknotitie: `docs/diff_hsv_2PE_2.json` en `docs/diff_hsv_2PE_3.json`
zijn aangemaakt, maar alle verzen daarin hebben status `pending` omdat
`output/2PE/2PE.2.json` en `output/2PE/2PE.3.json` nog ontbreken. De
aggregator slaat pending verzen over; de effectieve meta-analyse betreft
daarom alleen de al gemoderniseerde verzen in hoofdstuk 1.

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| - | - | - | - | Geen bucket-C patronen gevonden. | - |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| - | - | Geen deltas afgewezen; er waren geen kandidaten uit gemoderniseerde verzen. |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---:|---|
| carryover | 0 | - |
| fossiel-lidwoord | 0 | - |
| latinaat-window | 0 | - |
| cap-asym | 0 | - |

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen
- A (noise): 0
