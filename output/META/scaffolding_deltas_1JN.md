# Scaffolding-deltas — meta-review 1JN hoofdstukken 1-5

Gegenereerd: 2026-05-27T15:20:42Z
Aggregator: scripts/meta_diff_aggregate.py --book 1JN --chapters 1-5 --min-freq 2

Alle vijf hoofdstukken zijn volledig gemoderniseerd (10/29/24/21/21 verzen +
introducties + epiloog). De aggregator vond bij `--min-freq 2` één
cross-chapter pattern.

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| - | - | - | - | Geen bucket-C patronen gevonden. | - |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| - | - | Geen deltas afgewezen. |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---:|---|
| carryover | 0 | - |
| fossiel-lidwoord | 0 | - |
| latinaat-window | 0 | - |
| cap-asym | 1 (3 occ.) | `antichrist`: SV2026 2:18, 2:22, 4:3 |

### cap-asym `antichrist` — motivatie bucket A

SV2026 kapitaliseert de titel-naam consistent (`Antichrist`, plural
`Antichristen`) in alle drie de occurrences (2:18, 2:22, 4:3) en de
omliggende verzen (2:19, 2:20). HSV kiest consequent de kleine letter
(`antichrist`). Dit is een HSV-spellingkeuze, geen modernisatie-tekortkoming:

- SV2026 is **intern consistent** — geen enkele kleine-letter-`antichrist` in
  de hoofdtekst (de lowercase `antichristos` op 2:18 is de Griekse
  transliteratie ἀντίχριστος in de kanttekening, terecht klein).
- De kapitalisatie van een titulaire eschatologische figuur valt onder
  behoud van SV-naamkapitalen (vgl. `Koningh`/`Priesterdom`), niet onder
  toegevoegd eerbiedskapitaal — er is geen validator-overtreding.

Geen actie; cap-asym vereist per skill-regel sowieso geen auto-edit.

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen
- A (noise): 1 pattern (3 occ.)
