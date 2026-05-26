# Scaffolding-deltas — meta-review 1PE hoofdstukken 1-5

Gegenereerd: 2026-05-26
Aggregator: scripts/meta_diff_aggregate.py --book 1PE --chapters 1-5 --min-freq 2
(supersedeert de eerdere ch1-4-run; alle 5 diffs vers geregenereerd)

## Auto-toegepaste deltas (bucket C)

Geen nieuwe. Het enige carryover-patroon met freq≥3 (`wandel`, freq 5)
staat al in `DREMPEL_ARCHAISMEN` (scripts/rules_data.py:327) én
`ARCHAISMEN.md` — toegevoegd door de eerdere ch1-4-meta-review. De
scaffolding is dus compleet; alleen de content laggt (zie bucket B).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen.

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Key | Freq | Reden |
|---|---|---|---|
| carryover | `broederschap` | 2 | `broederschap` (Gr. ἀδελφότης) is modern NL, geen archaïsme; HSV `broeders` is exegetische explicitering. Reeds 4c afgehandeld in semantic-review 1PE 5:9. |
| cap-asym | `engelen` | 2 | SV2026 `Engelen` (1:12, 3:22) behoudt SV1657-kapitaal; HSV-kleinletter is HSV-keuze. Regel verbiedt enkel TOEGEVOEGDE caps. |
| cap-asym | `koning` | 2 | `Koning` (2:13, 2:17, AARDSE vorst = Romeinse keizer) behoudt SV1657 `Koningh`-kapitaal. Géén eerbiedskapitaal-fout — zie feedback_sv_cap_preservation_vs_eerbied: lowercasing zou validator 0F→F breken. **Correctie t.o.v. ch1-4-meta-review**, die `Koning` ten onrechte als bucket B markeerde; die fix is terecht nooit toegepast. |
| fossiel-lidwoord | `der heerlijkheid` | 2 | `Geest der heerlijkheid` (4:14, πνεῦμα τῆς δόξης) en `kroon der heerlijkheid` (5:4, τῆς δόξης στέφανον) zijn gefossiliseerde bijbelgenitieven (FOSSIL_GENITIVE_PAIRS; validator 0F). Reeds rebutted-verified in adversarial review 1PE 5. |

## Status eerdere bucket-B (ch1-4-meta-review)

- `priesterdom`→`Priesterschap` (2:5, 2:9): **voltooid** (commit 792e051), geverifieerd in huidige output.
- `Koning`→`koning` (2:13, 2:17): **vervalt** — herclassificeerd naar bucket A (zie boven).

## Bucket B — per-vers fixes (findings.json)

`wandel` (zelfst. = levenswijze) → `levenswandel`, HSV-consequent. Regel
bestaat al; content-fix uit de ch1-4-meta-review is nooit voltooid.
5 occurrences: 1:15, 2:12, 3:1, 3:2, 3:16.

Buiten scope (werkwoord-imperatief `wandel`, geen zelfst.naamwoord-archaïsme):
1:14 (kanttekening `wandel niet`), 1:17 (hoofdtekst `wandel dan in vrees`).

## Bucket-overzicht

- B (per-vers fixes): 5 issues over 3 hoofdstukken (1:15, 2:12, 3:1, 3:2, 3:16) — zie `findings.json`
- C (scaffolding-deltas): 0 nieuw (regel `wandel` bestond al)
- A (noise): 4 patterns
