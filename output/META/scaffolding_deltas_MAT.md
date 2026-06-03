# Scaffolding-deltas — meta-review MAT hoofdstukken 1-10 (afgewerkt: 1,2,3,7,8,9,10)

Gegenereerd: 2026-06-03T10:51:23Z
Aggregator: scripts/meta_diff_aggregate.py --book MAT --chapters 1-10 --min-freq 2

Hoofdstukken 4, 5 en 6 hebben (nog) geen `docs/diff_hsv_MAT_*.json` en zijn
overgeslagen. MAT is in wording (9 hoofdstukken af, 6 ontbreekt nog).

## Auto-toegepaste deltas (bucket C)

Geen. Geen enkel pattern haalde de bucket-C-drempel (carryover/fossiel met
freq ≥ 3 + consistent modern HSV-alternatief, of SV-interne cap-inconsistentie).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen kandidaten voorgelegd.

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym (behouden SV1657-nouncaps) | 8 | `Profeet` (1:22, 2:5,15,17, 3:3, 8:17, 10:41 — 7×); `Koning` (1:6, 2:1,3,22); `Engel` (1:24, 2:13,19); `Oosten` (2:1,2,9); `Wijzen` (2:1,7,16); `Heidenen` (10:5,18); `Hoofdman` (8:5,13); `Schriftgeleerden` (2:4, 7:29) |
| latinaat-window (SV-perfectum behouden / bijbels-fossiel) | 3 | `de winden hebben gewaaid … aangevallen/aangeslagen` (7:25,27); `het koninkrijk der hemelen is nabij gekomen` (3:2, 10:7); `slagregen neergevallen … waterstromen zijn gekomen … winden` (7:25,27) |

### Toelichting per noise-groep

- **cap-asym (8):** Alle 8 zijn SV1657-interne hoofdletters die de
  modernisatie behoudt; HSV kiest consistent voor kleine letter. Per
  `feature/sv_cap_preservation_vs_eerbied` is lowercasen hier fout — de
  regel verbiedt enkel TOEGEVOEGDE eerbiedskapitalen, niet bestaande
  SV-nouncaps. Geen SV-interne inconsistentie gedetecteerd. HSV-keuze.

- **latinaat-window (3):** Geen Latinaat-rest. Het zijn behouden
  SV-perfectumconstructies (`de winden hebben gewaaid, en zijn tegen
  datzelfde huis aangevallen`) waar HSV naar simpele verleden tijd
  parafraseert — renovatie ≠ hervertaling. `aangevallen` (7:25, Gr.
  προσέπεσαν, "vielen op") vs `aangeslagen` (7:27, Gr. προσέκοψαν,
  "sloegen tegen") is een correcte Griekse werkwoorddistinctie, geen
  concordantiefout. `koninkrijk der hemelen` is bijbels-fossiel (bucket A
  per fossiel-lidwoord-criterium); HSV behoudt het eveneens.

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken — zie `findings_MAT.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen
- A (noise): 11 patterns (cap-asym 8, latinaat-window 3)
