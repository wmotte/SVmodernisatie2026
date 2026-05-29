# Scaffolding-deltas — meta-review 2TI hoofdstukken 1-4

Gegenereerd: 2026-05-29T04:50:20Z
Aggregator: scripts/meta_diff_aggregate.py --book 2TI --chapters 1-4 --min-freq 2

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| _(geen)_ | — | — | — | Geen pattern haalt de bucket-C-drempel (freq ≥ 3 + recurrent over ≥3 hoofdstukken). | — |

## Voorgestelde deltas (bucket C — VOORSTEL, niet uitgevoerd)

| Pattern | Kind | Freq | Voorgesteld target | Voorstel | Bewijs (3 citaten) |
|---|---|---|---|---|---|
| _(geen)_ | — | — | — | Alle 3 patterns blijven onder freq==2; geen recurrent scaffolding-gap. Niets ter voorstel. | — |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `geve` | carryover | §2.7 productiviteits-/constructie-test: de vrijstaande optatief-subjunctief ('De Heere geve ...') is in plechtig/liturgisch register nog productief modern NL (vgl. 'God zegene u', 'Leve de koning'). Bron SV1657 + Grieks δῴη (optatief) ondersteunen de conjunctief. Niet als scaffolding-delta (DREMPEL_ARCHAISMEN) opnemen — false positives op alle legitieme zegen-optatieven. Behandeld als per-vers bucket-B-afweging i.p.v. regel-delta. |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 2 | `Apostel` (2TI 1:1, 1:11) — SV1657-interne hoofdletter, consistent in 2TI (32× 'Apostel', 0× kleine letter); HSV kiest kleine letter (HSV-keuze). `Heidenen` (2TI 1:11, 4:17) — consistent gekapitaliseerd in 2TI (5× 'Heidenen'/'Heidense', geen kleine-letter-variant van het zelfstandig naamwoord); HSV kiest kleine letter. Geen TOEGEVOEGDE eerbiedskapitaal; bewaarde SV-nouncaps. |

## Bucket-overzicht

- B (per-vers fixes): 2 issues over 1 hoofdstuk (2TI 1, verzen 16 + 18) — zie `findings_2TI.json`
- C (scaffolding-deltas): 0 toegepast, 0 voorgesteld, 1 afgewezen (§2.7: `geve`)
- A (noise): 2 cap-asym patterns (`Apostel`, `Heidenen`)
