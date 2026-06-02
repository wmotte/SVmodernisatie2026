# Scaffolding-deltas - meta-review JHN hoofdstukken 1-18

Gegenereerd: 2026-06-02T09:14:31Z
Aggregator: `scripts/meta_diff_aggregate.py --book JHN --chapters 1-18 --min-freq 2`
Beschikbare diffs: ch 1-18 (compleet)
Modus: apply

## Auto-toegepaste deltas (bucket C)

Geen. De enige recurrente drempel-formule (`ten uitersten dage`) wordt al
door `DREMPEL_FOSSIELEN` in `scripts/rules_data.py` gedekt. Daarom was er
geen 4a regel-PR nodig.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen bucket-C kandidaat is op de §2.7-toets afgewezen.

## Noise (bucket A - HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---:|---|
| cap-asym | 8 patterns | `Hogepriester`, `Sabbat`, `Synagoge`, `Profeet`, `Engel`, `Goden`, `Leraar`, `Overpriesters`. HSV gebruikt onderkast, maar SV1657 heeft hier hoofdletter; AGENTS.md hoofdletterdiscipline vereist behoud. |
| carryover | 3 patterns | `toe` (`tot boven toe`, `tot nu toe`), `wandelt`, `warmde`. Dit zijn productieve moderne vormen of HSV-syntaxiskeuzes. |
| fossiel-lidwoord | 2 patterns | `der joden`, `der wereld`. Beide vallen onder bestaande `FOSSIL_GENITIVE_PAIRS`/vast bijbels register; geen nieuwe regel-delta. |

## Bucket-overzicht

- B (per-vers fixes): 11 issues over 4 hoofdstukken (2, 3, 6, 10) - toegepast; zie `findings_JHN.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen
- A (noise): 13 patterns

## Apply-modus

Toegepaste content-fixes:

| Hoofdstuk | Verzen | Wijziging |
|---|---|---|
| JHN 2 | 8-10 | `hofmeester` -> `ceremoniemeester`; `Iedere man` -> `Iedereen` |
| JHN 3 | 15-16 | `verderve`/`hebbe` -> `omkomt`/`heeft` |
| JHN 6 | 39,40,44,54 | `ten uitersten dage` -> `op de laatste dag` |
| JHN 10 | 1,16 | `stal` -> `schaapskooi` |

Validatie: `validate.py check --terse` groen op alle aangepaste verzen.
Restlint: `lint_false_friends.py` meldt nog een bestaande introductieflag in JHN 3 (`Leert`), buiten de aangepaste verzen.
