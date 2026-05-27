# Scaffolding-deltas — meta-review COL hoofdstukken 1-4

Gegenereerd: 2026-05-26T17:41:25Z
Aggregator: scripts/meta_diff_aggregate.py --book COL --chapters 1-4 --min-freq 2

Bereiknotitie: `docs/diff_hsv_COL_2.json`, `docs/diff_hsv_COL_3.json` en
`docs/diff_hsv_COL_4.json` zijn aangemaakt, maar alle verzen daarin hebben
status `pending` omdat `output/COL/COL.2.json`, `output/COL/COL.3.json` en
`output/COL/COL.4.json` nog ontbreken. De aggregator slaat pending verzen
over; de effectieve meta-analyse betreft daarom alleen de al gemoderniseerde
verzen in hoofdstuk 1.

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
