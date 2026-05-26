# Scaffolding-deltas — meta-review 1PE hoofdstukken 1-4

Gegenereerd: 2026-05-26T05:37:51Z
Aggregator: scripts/meta_diff_aggregate.py --book 1PE --chapters 1-4 --min-freq 2

Let op: 1PE 1 heeft (nog) geen `docs/diff_hsv_1PE_1.json`; de aggregator sloeg
dat hoofdstuk over. De bucket-C-delta `wandel` is desondanks systemisch:
naast de 4 gevlagde occurrences in ch2/ch3 staan er nog 4 in ch1
(1:14, 1:15, 1:17, 1:18), waarvan twee imperatief-werkwoord ('wandel niet',
'wandel dan') — die worden door de exacte-woord-match ook soft-geflagd; dat is
aanvaardbare ruis (soft severity, reviewer arbitreert: ww. of zn.).

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| `wandel` (zelfst. = levenswijze) | carryover | 4 (+4 in ch1) | `ARCHAISMEN.md` tabel + `DREMPEL_ARCHAISMEN` (scripts/rules_data.py) | toegevoegd als soft drempel-archaisme; modern alt. 'levenswandel/leven/gedrag' | 1PE 2:12, 3:1, 3:2, 3:16 |

§2.7-toets `wandel`:
1. Productiviteit: standalone 'wandel' (= gedrag) komt niet voor in modern zakelijk NL; 'levenswandel' wel.
2. Constructie: 'houd uw levenswandel eerbaar' werkt modern.
3. Verwarring: 'wandel' leest modern primair als 'wandeling/stroll' -> verwarrend. HSV consequent 'levenswandel'. Slaagt -> toepassen.

Match-veiligheid: `\bwandel\b` op lowercased tekst raakt NIET 'levenswandel'
(geen \b vóór 'w'), 'wandelen'/'wandeling'/'wandelende' (geen \b na 'l').
Geverifieerd tegen output/1PE/*.json: geen negatieve treffers.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| (geen) | | |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| (geen pure noise; cap-asym 'koning' geherclassificeerd naar bucket B, zie hieronder) | | |

## Bucket B — per-vers fixes (findings_1PE.json)

- `priesterdom` -> `priesterschap` (carryover, freq=2): 1PE 2:5, 2:9.
- `Koning` -> `koning` (cap-asym, eerbiedskapitaal op AARDSE vorst — kanttekening
  2:13 noemt 'de Romeinse Keizer'): 1PE 2:13, 2:17. Geen HSV-stijlruis maar
  een inhoudelijke eerbiedskapitaal-fout (zie AGENTS.md / feedback_eerbiedskapitaal_validator);
  daarom bucket B i.p.v. de cap-asym-default (A).

## Bucket-overzicht

- B (per-vers fixes): 4 issues over 1 hoofdstuk (1PE 2) — zie `findings_1PE.json`
- C (scaffolding-deltas): 1 toegepast, 0 afgewezen
- A (noise): 0
