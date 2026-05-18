# Scaffolding-deltas — meta-review MRK hoofdstukken 1-14

Gegenereerd: 2026-05-18
Aggregator: `scripts/meta_diff_aggregate.py --book MRK --chapters 1-14 --min-freq 2`
Totaal patterns: 14 (cap-asym 11, carryover 3, fossiel-lidwoord 0, latinaat-window 0)

## Bucket-overzicht

- A (noise — HSV-keuze, geen actie): 11 patterns, 44 occurrences (alle cap-asym)
- B (per-vers fixes): 6 issues over 5 hoofdstukken (3, 4, 8, 11, 14) — zie `findings_MRK.json`
- C (scaffolding-deltas): 2 voorgesteld, 0 afgewezen — **nog niet toegepast** (vereist `apply rules`)

## Voorgestelde auto-deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| `ure` | carryover | 3 | `DREMPEL_ARCHAISMEN` (scripts/adversarial_scan.py r.86) + `ARCHAISMEN.md` tabel | toevoegen 'ure' → 'uur' / 'moment' | MRK 13:11, 13:32, 14:35 |
| `(zie\|ziet\|hoort)\s+toe` imperatief | carryover | 6 | `DREMPEL_FOSSIELEN` (scripts/adversarial_scan.py r.111) — nieuwe regex `\b(?:hoort\|ziet\|zie)\s+toe\b` | toevoegen multi-word drempel-fossiel; modern alternatief context-afhankelijk (luister/let op/pas op/kijk uit) | MRK 4:3, 8:15, 13:5, 13:9, 13:23, 13:33 |

**§2.7-toets per delta:**

- `ure`: productiviteit ✓ ('uur' is hedendaagse vorm); constructie ✓ ('die ure' → 'dat uur'); verwarring ✓ (geen homoniem).
- `(zie|ziet|hoort)\s+toe` imperatief: productiviteit ✓ (modern 'luister'/'let op'/'pas op' is hedendaags); constructie ✓ (imperatief vervangbaar); verwarring ✓ ('toe' als losse particle bestaat modern, maar niet in deze imperatief-constructie).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen.

## Noise (bucket A — HSV-keuze, geen actie)

Alle cap-asym patterns zijn SV1657-conventie (categorie- of titel-substantieven met hoofdletter); HSV consistent lowercase. Geen interne SV-inconsistentie in de samples van MRK 1-14.

| Key | Freq | Voorbeelden |
|---|---|---|
| `schriftgeleerden` (Schriftgeleerden) | 9 | MRK 7:1, 7:5, 8:31, 9:11, 10:33, 11:27, 12:35, 12:38, 14:1 |
| `overpriesters` (Overpriesters) | 6 | MRK 8:31, 10:33, 11:18, 11:27, 14:1, 14:10 |
| `synagoge` (Synagoge) | 6 | MRK 1:21, 5:22, 5:35, 5:36, 5:38, 6:2 |
| `profeet` (Profeet) | 4 | MRK 6:4, 6:15, 11:32, 13:14 |
| `profeten` (Profeten) | 4 | MRK 1:2, 6:15, 8:28, 13:22 |
| `engelen` (Engelen) | 3 | MRK 8:38, 12:25, 13:32 |
| `keizer` (Keizer) | 3 | MRK 12:14, 12:16, 12:17 |
| `koninkrijk` (Koninkrijk) | 3 | MRK 3:24, 6:23, 13:8 |
| `groten` (Groten) | 2 | MRK 6:21, 10:42 |
| `ouden` (Ouden) | 2 | MRK 7:3, 7:5 |
| `sabbat` (Sabbat) | 2 | MRK 2:27, 2:28 |

## Notitie — bucket-B `hoe`-cluster

Het carryover-patroon `hoe` (freq=8) splitst op in twee semantische sub-clusters die niet als één regel te scaffolden zijn (te smal/fragiel of te breed/false-positief):

1. **'Hoe + ontkenning'** (4:40, 8:21) — drempel-archaïsche SV-syntaxis; modern NL gebruikt 'Hebt u dan geen ...?' / 'Waarom ... niet?'. Twee occurrences, regex-detectie te smal → per-vers fix (bucket B).
2. **'zoeken hoe X zou(den) ...'** (11:18, 14:1, 14:11) — fossielconstructie (ζητέω πῶς + opt./conj.). Drie occurrences; regex `\bzocht(en)?\s+hoe\s+\w+\s+\w+\s+zou(den)?\b` is breekbaar → per-vers fix (bucket B).

Restant: `hoe lang` (9:19, 9:21) is modern OK (geen fix); `hoe grote dingen` (3:8) → bucket B.

## Filename-conventie

Bestaand `output/META/findings.json` + `scaffolding_deltas.md` zijn LUK-output (meta-review LUK 1-24, mei 2026). Om die te bewaren zijn de MRK-resultaten onder boek-suffix opgeslagen: `findings_MRK.json` + `scaffolding_deltas_MRK.md`. Apply-modus moet dezelfde suffix lezen.
