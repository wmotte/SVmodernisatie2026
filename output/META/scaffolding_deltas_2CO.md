# Scaffolding-deltas — meta-review 2CO hoofdstukken 1-13

Gegenereerd: 2026-05-29T07:25:36Z
Aggregator: `scripts/meta_diff_aggregate.py --book 2CO --chapters 1-13 --min-freq 2`

## Auto-toegepaste deltas (bucket C)

Geen. De aggregator vond 6 patterns; geen enkele haalde de bucket-C-drempel
(recurrente, niet-bijbelse, op DREMPEL te zetten archaïsme-rest). 2CO is per
hoofdstuk al door adversarial-review gegaan; meta-review levert enkel ruis op.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `regel` (2CO 10:15, 10:16) | carryover | Grieks κανών; SV1657 kiest bewust "regel" als technische term voor het apostolische werkgebied en **glosseert het woord zelf in de kanttekening** ("zodat het woord regel hier genomen wordt voor het gebied"). Een content-fix `regel`→`gebied/werkterrein` (zoals HSV hervertaalt) zou de zelf-verwijzende kanttekening onzinnig maken. Renovatie ≠ hervertaling: SV-vorm + glosserende kanttekening blijft. |

## Noise (bucket A — HSV-keuze / parafrase / modern, geen actie)

| Kind | Key | Freq | Reden |
|---|---|---|---|
| carryover | `ben` | 7 | Vorm van "zijn" ("ik ben") — volstrekt modern; hsv_alternatives ('namelijk','sta','deed'…) zijn alignment-ruis uit HSV's vrije herschikking. |
| carryover | `toe` | 3 | Constructie "tot … toe" ("tot de huidige dag toe", "tot u toe gekomen") werkt in modern NL; HSV herschikt vrij ("tot op heden", "bereiken"). |
| carryover | `ten` | 2 | "ten dele" / "ten aanzien van" — productieve, moderne vaste uitdrukkingen. |
| carryover | `vertroosten` | 2 | Verheven maar begrepen register (Van Dale); renovatie behoudt SV-vorm waar die modern werkt. HSV kiest "troosten"/"bemoedigen" als stijlkeuze, geen drempel-archaïsme. |
| cap-asym | `apostelen` | 3 | "Apostel/Apostelen" is in heel 2CO 2026 consistent gekapitaliseerd (178× hoofdletter, 0× klein) — bewaarde SV1657-naamwoordkapitaal, geen toegevoegd eerbiedskapitaal. HSV kiest klein; HSV-keuze. |

## Bucket-overzicht

- B (per-vers fixes): 0 issues — zie `findings_2CO.json` (leeg)
- C (scaffolding-deltas): 0 toegepast, 1 afgewezen (§2.7: `regel`)
- A (noise): 5 patterns
