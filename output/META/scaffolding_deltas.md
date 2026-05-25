# Scaffolding-deltas — meta-review ROM hoofdstukken 1-16

Gegenereerd: 2026-05-25T00:00:00Z
Aggregator: scripts/meta_diff_aggregate.py --book ROM --chapters 1-16 --min-freq 2
Beschikbare diffs: ch 1-16 (compleet)
Modus: apply

## Auto-toegepaste deltas (bucket C)

Geen. Geen carryover-patroon levert een schoon lexicaal archaïsme met
consistent HSV-alternatief bij freq≥3; de carryover-keys (`ben`/`toe`/`ter`/`men`)
zijn functiewoord-ruis. cap-asym wordt nooit auto-geëdit. → 4a overgeslagen.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `zo`-apodosis ("zo stem/zo doe/zo is/zo zal") | latinaat-window | Pervasief in ROM (6× "zo is", 4× "zo zal", + "zo doe/zo stem"). Consistente SV-register-keuze, geen geïsoleerd archaïsme. Cherry-pick zou inconsistent zijn → register, geen delta. |
| `indien` (kaal) | carryover | Aanvaardbaar formeel Nederlands; geen drempel-archaïsme. Alleen de combinatie `indien anders` (8:9) is opaak → bucket B. |

## Noise (bucket A — HSV-keuze / al gemoderniseerd, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 22 occ | "Heidenen" (18×, SV-intern consistent hoofdletter), "Apostel" (1:1, 11:13), "Profeten" (1:2, 11:3) |
| carryover al gemoderniseerd | 4 | 3:12 ("niet één toe"→"niet één"), 9:21 ("ter ere"→"tot eer"), 10:10 ("ter"→"tot"), 14:2 ("men ... mag eten" ok) |
| carryover HSV-parafrase | 1 | 12:3 "wijs is boven wat men behoort" — SV-literair vs HSV-parafrase, verdedigbaar |

## Bucket-overzicht

- B (per-vers fixes): 7 issues over 6 hoofdstukken (7, 8, 9, 11, 15, 16) — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast, 2 afgewezen (§2.7)
- A (noise): ~27
