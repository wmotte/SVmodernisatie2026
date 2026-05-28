# Scaffolding-deltas - meta-review EPH hoofdstukken 1-6

Gegenereerd: 2026-05-28T18:01:48Z
Aggregator: scripts/meta_diff_aggregate.py --book EPH --chapters 1-6 --min-freq 2

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---:|---|---|---|
| `prijs` | carryover | 3 | `ARCHAISMEN.md` + `scripts/rules_data.py` `DREMPEL_ARCHAISMEN` | toegevoegd als drempelarchaïsme; alternatief `lof` bij Gr. `ἔπαινος` | EPH 1:6, 1:12, 1:14 |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| - | - | - |

## Noise (bucket A - HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---:|---|
| cap-asym | 3 | `Heidenen` (EPH 2:11; 3:1,6,8), `Apostelen` (EPH 2:20; 3:5), `Profeten` (EPH 2:20; 3:5). SV1657 heeft `Heydenen`, `Apostelen`, `Propheten`; hoofdletterdiscipline bewaart dit. |

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken - zie `findings_EPH.json`
- C (scaffolding-deltas): 1 toegepast, 0 afgewezen
- A (noise): 3
