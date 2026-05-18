# Scaffolding-deltas — meta-review MRK hoofdstukken 1-16

Gegenereerd: 2026-05-18
Aggregator: `scripts/meta_diff_aggregate.py --book MRK --chapters 1-16 --min-freq 2`
Totaal patterns: 17 (cap-asym 12, carryover 3, fossiel-lidwoord 2, latinaat-window 0)

## Bucket-overzicht

- A (noise — HSV-keuze, geen actie): 16 patterns, 84 occurrences
- B (per-vers fixes): 3 issues over 2 hoofdstukken (13, 14) — zie `findings_MRK.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen (DREMPEL al up-to-date sinds vorige meta-review)

## Auto-toegepaste deltas (bucket C)

Geen. Het enige hard-archaïsme dat freq≥3 haalde (`ure`) staat al in
`DREMPEL_ARCHAISMEN` (`scripts/adversarial_scan.py:108`) door eerdere
meta-review MRK 1-14. Scaffolding-gap is gesloten; resterend werk is
bucket B (content-fixes, zie `findings_MRK.json`).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen.

## Noise (bucket A — HSV-keuze, geen actie)

### cap-asym (12 patterns, 67 occurrences)

| Key | Freq | Voorbeelden | Reden A |
|---|---|---|---|
| `schriftgeleerden` | 13 | MRK 7:1,5; 8:31; 9:11; 10:33; 11:27; 12:35,38; 14:1,43,53; 15:1,31 | SV-intern consistent (Schriftgeleerden); functie-titel SV1657-beleid |
| `overpriesters` | 10 | MRK 8:31; 10:33; 11:18,27; 14:1,10,43,53; 15:10,11 | idem |
| `synagoge` | 6 | MRK 1:21; 5:22,35,36,38; 6:2 | idem (instituut-naam SV1657-beleid) |
| `hogepriester` | 5 | MRK 2:26; 14:53,54,61,66 | idem |
| `profeet` | 4 | MRK 6:4,15; 11:32; 13:14 | idem |
| `profeten` | 4 | MRK 1:2; 6:15; 8:28; 13:22 | idem |
| `engelen` | 3 | MRK 8:38; 12:25; 13:32 | idem |
| `keizer` | 3 | MRK 12:14,16,17 | titel Romeinse imperator; SV1657-beleid |
| `koninkrijk` | 3 | MRK 3:24; 6:23; 13:8 | idem (Koninkrijk Gods / aardse rijken) |
| `groten` | 2 | MRK 6:21; 10:42 | zelfst. nw. machtshebbers; SV-beleid |
| `ouden` | 2 | MRK 7:3,5 | bijbeluitdrukking 'inzetting der Ouden' |
| `sabbat` | 2 | MRK 2:27,28 | feestdag-naam; consistent met 1:21, 6:2 |

### carryover (2 patterns van 3, 10 occurrences — `ure` zit in bucket B)

| Key | Freq | Voorbeelden | Reden A |
|---|---|---|---|
| `toe` | 6 | MRK 4:3; 8:15; 13:5,9,23,33 | 'Ziet/Hoort toe' is SV-renovatie van 'Siet/Hoort toe'; werkt modern in religieus register (vgl. 'toezien op'); HSV-alternatieven niet consistent (pas/luister/kijk uit/let op) → parafrase, geen modernisatie-tekortkoming. Eerder voorgesteld als regex-delta MRK 1-14, niet toegepast door user — bevestigd als A. |
| `hoe` | 4 | MRK 4:40; 8:21; 9:19,21 | 'Hoe komt het dat...' is modern NL; 'hoe lang' vs HSV 'hoelang' is enkel spelling — geen archaïsme |

### fossiel-lidwoord (2 patterns, 7 occurrences)

| Key | Freq | Voorbeelden | Reden A |
|---|---|---|---|
| `der joden` | 5 | MRK 15:2,9,12,18,26 | Bijbeluitdrukking 'Koning der Joden' (Pilatus-opschrift / kruisbord); cultureel-liturgisch fossiel |
| `des te` | 2 | MRK 14:31; 15:14 | 'des te meer' is hedendaags modern NL-idioom; geen fossiel — HSV 'krachtiger/harder' is parafrase |
