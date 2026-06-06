# Scaffolding-deltas — meta-review MAT hoofdstukken 1-28

Gegenereerd: 2026-06-06T19:23:49Z
Aggregator: scripts/meta_diff_aggregate.py --book MAT --chapters 1-28 --min-freq 2 --refresh

## Auto-toegepaste deltas (bucket C)

Geen. Er waren geen regelbestand-wijzigingen nodig.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `nabij gekomen` | latinaat-window | Niet hard genoeg voor scaffolding: eerdere MAT-review classificeerde dit als bijbels-register/noise; een generieke regel zou veel false positives geven. |
| `kome` | carryover | Niet blanket-toepasbaar: `Uw Koninkrijk kome` blijft liturgisch. Niet-liturgische occurrences zijn als content-fix afgehandeld. |
| `daarbij gewonnen` | latinaat-window | Na fix resteert HSV-verschil alleen doordat HSV vrijer `verdiend` kiest; `gewonnen` behoudt SV/Grieks formeel-equivalent. |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---:|---|
| cap-asym (SV-hoofdletters behouden) | 23 | `Schriftgeleerden`, `Profeet`, `Profeten`, `Engelen`, `Overpriesters`, `Koning`, `Hogepriester`, `Stadhouder` |
| carryover (productief/formeel of contextueel correct) | 4 | `toe` (`deugt nergens meer toe`, `ging naar hem toe`, `tot de dag toe`), `hoe`, `aldus`, `binden` |
| fossiel-lidwoord (allowlist / bijbels-register) | 3 | `knersing der tanden`, `Koning der Joden`, `dag des oordeels` |
| latinaat-window (HSV-herstructurering/noise) | 8 | `wening zijn en knersing der tanden`, `Koninkrijk der hemelen nabij gekomen`, stormconstructies in MAT 7:25,27, `dag des oordeels` |

### Toelichting per noise-groep

- **cap-asym:** Alle patronen volgen SV1657-interne hoofdletters. HSV lowercaset
  titels en soortnamen; dat is voor dit project geen bewijs voor een fix.
- **fossiel-lidwoord:** `der joden`, `des oordeels` en `der tanden` staan al in
  `scripts/rules_data.py` `FOSSIL_GENITIVE_PAIRS` en worden in
  `MODERNISATIE.md §2.3c` als bijbels-fossiele formules verantwoord.
- **carryover:** De harde carryovers uit de eerste scan (`verlatene`,
  `gracht`, niet-liturgisch `kome/kere`, `kwamen zij toe`) zijn gefixt.
  Resterende `toe`-occurrences zijn modern Nederlands.
- **latinaat-window:** Resterende patronen zijn HSV-herstructurering of
  bewust SV-register. `daarbij gewonnen` blijft als formeel-equivalente
  renovatie staan; HSV's `verdiend` is vrijer.

## Bucket-overzicht

- B (per-vers fixes): 8 issues over 7 hoofdstukken — alle fixed, zie `findings_MAT.json`
- C (scaffolding-deltas): 0 toegepast, 3 afgewezen
- A (noise): 38 huidige patronen

## Apply-resultaat

| Hoofdstuk | Verzen | PR | Validate |
|---|---:|---|---|
| MAT 5 | 32 | https://github.com/wmotte/SVmodernisatie2026/pull/2573 | PASS 2/2 0F 0W |
| MAT 10 | 13 | https://github.com/wmotte/SVmodernisatie2026/pull/2574 | PASS 2/2 0F 0W |
| MAT 12 | 11 | https://github.com/wmotte/SVmodernisatie2026/pull/2575 | PASS 2/2 0F 0W |
| MAT 15 | 14 | https://github.com/wmotte/SVmodernisatie2026/pull/2577 | PASS 2/2 0F 0W |
| MAT 23 | 35 | https://github.com/wmotte/SVmodernisatie2026/pull/2578 | PASS 2/2 0F 5W |
| MAT 25 | 20,22 | https://github.com/wmotte/SVmodernisatie2026/pull/2579 | PASS 3/3 0F 0W |
| MAT 26 | 50 | https://github.com/wmotte/SVmodernisatie2026/pull/2580 | PASS 2/2 0F 0W |
