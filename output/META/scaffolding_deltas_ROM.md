# Scaffolding-deltas — meta-review ROM hoofdstukken 1-16

Gegenereerd: 2026-05-25T14:49:51Z
Aggregator: scripts/meta_diff_aggregate.py --book ROM --chapters 1-16 --min-freq 2

HSV-diffs voor alle 16 hoofdstukken zelf gegenereerd via
`scripts/compare_hsv.py ROM <H>` (hsv/ROM/*.json aanwezig).

## Auto-toegepaste deltas (bucket C)

Geen. Geen pattern recurreert ≥3 hoofdstukken als echte modernisatie-miss
die de bestaande lint had moeten vangen. De Latinaat-constructie
"ik hetgeen doe dat" zit alleen in ROM 7 (1 hoofdstuk → bucket B), en de
archaïsche datief 'ter + abstract nomen' in ROM 9 + 10 (2 hoofdstukken,
< drempel 3 → bucket B).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen kandidaten aangeboden.

## Noise (bucket A — HSV-keuze / consistente conventie, geen actie)

| Kind | Key | Freq | Reden |
|---|---|---|---|
| cap-asym | `Heidenen` | 18 | SV2026 kapitaliseert volksnaam consistent (verse-tekst 0× lowercase; 2× lowercase enkel in hoofdstuk-introducties, geen HSV-equivalent). HSV kiest lowercase — stijlkeuze, geen miss. |
| cap-asym | `Apostel` | 2 | Consistent gekapitaliseerd ambt/eretitel (220× kapitaal, 0× lowercase in ROM verse-tekst). HSV lowercase = HSV-keuze. |
| cap-asym | `Profeten` | 2 | Consistent gekapitaliseerd (Profeet/Profeten 16× kapitaal, 0× lowercase). HSV-keuze. |
| carryover | `ben` | 4 | Werkwoord 'zijn' 1e pers. — volledig modern. HSV herstructureert zin (parafrase), geen archaïsme. |
| carryover | `men` | 2 | Onbepaald voornaamwoord — modern. HSV kiest 'hij'; syntactische keuze. |
| carryover | `beminde` | 2 | Synoniem-/concordantiekeuze ('beminde' vs HSV 'geliefde'); literair maar niet opaak. |
| carryover | `toe` | 4 | Particle 'toe' modern in 3/4 occurrences (stem...toe, komt...toe, zie toe); enkel ROM 3:12 'niet tot één toe' → bucket B. |
| carryover | `ter` | 3 | 8:34 'ter rechterhand' = vast modern; 9:21 + 10:10 archaïsche datief → bucket B. |

## Bucket-overzicht

- B (per-vers fixes): 5 issues over 4 hoofdstukken (ROM 3, 7×2, 9, 10) — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen
- A (noise): 8 patterns
