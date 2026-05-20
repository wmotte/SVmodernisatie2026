# Scaffolding-deltas — meta-review ROM hoofdstukken 1-4

Gegenereerd: 2026-05-20
Aggregator: `scripts/meta_diff_aggregate.py --book ROM --chapters 1-4 --min-freq 2`
Totaal patterns: 2 (cap-asym 1, carryover 1)

Opmerking: alleen ROM 1-4 zijn gemoderniseerd (`output/ROM/ROM.{1..4}.json`).
Diff-bestanden bestaan voor 1-16, maar verzen 5-16 zijn nog `pending` en
worden door de aggregator overgeslagen.

## Auto-toegepaste deltas (bucket C)

Geen. Beide patterns classificeren als bucket A (noise).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen kandidaten voor C/B.

## Noise (bucket A — HSV-keuze / detector-false-positive, geen actie)

| Kind | Key | Freq | Reden | Voorbeelden |
|---|---|---|---|---|
| cap-asym | `heidenen` | 5 | SV2026 schrijft consistent "Heidenen" (hoofdletter, SV1657-interne case), HSV lowercase. Intern consistent over ROM 1-4 → geen auto-edit (cap-asym default = HSV-keuze). | ROM 1:5, 1:13, 2:14, 2:24, 3:29 |
| carryover | `ben` | 2 | Vervoeging van `zijn` (to be) — volledig modern, geen archaïsme. Detector-false-positive; HSV-"alternatieven" (dikwijls/echter/sta) zijn diff-window-ruis, geen consistent alternatief. | ROM 1:13, 1:14 |

## Bucket-overzicht

- B (per-vers fixes): 0 issues — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen
- A (noise): 2

## Apply-modus

Niets toe te passen. Geen 4a-PR (regel-deltas), geen 4b-PRs (content-fixes).
