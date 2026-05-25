# Scaffolding-deltas — meta-review 1CO hoofdstukken 1-16

Gegenereerd: 2026-05-25T20:12:43Z
Aggregator: scripts/meta_diff_aggregate.py --book 1CO --chapters 1-16 --min-freq 2
Beschikbare diffs: ch 1, 2, 6, 7, 8, 9, 10, 15, 16 (ch 3-5, 11-14 nog geen diff — overgeslagen)
Modus: analyse-only (geen edits toegepast)

## Auto-toegepaste deltas (bucket C)

Geen. Geen pattern haalt de C-drempel (N>=3 + bestaande lint had het moeten vangen)
zonder al door bewuste whitelist/keuze gedekt te zijn.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `des heeren` | fossiel-lidwoord | `(des, heeren)` staat expliciet in `FOSSIL_GENITIVE_PAIRS` (rules_data.py:84). Bewuste fossiel; validator laat door. HSV 'van de Heere' is HSV-keuze. Geen delta. |
| `der wereld` | fossiel-lidwoord | `(der, wereld)` staat in `FOSSIL_GENITIVE_PAIRS` (rules_data.py:95). Idem. |
| `ongetrouwde` | carryover | productiviteits-test andersom gehaald: 'ongetrouwd' is gangbaar modern NL. HSV 'ongehuwde' is stijlkeuze, geen archaïsme. |
| `ter wille van` | carryover | 'ter wille van het geweten' komt voor in modern zakelijk NL. Geen archaïsme. (Losse occurrence 10:28 'om diens wille die' wél bucket B — zie findings.) |

## Observaties (geen edit, semantisch oordeel)

| Kind | Waarneming |
|---|---|
| cap-asym `Apostel`/`Apostelen` | SV2026 kapitaliseert 'Apostel' mid-zin consistent (1:1, 9:1, 9:2, 15:7, 15:9); HSV schrijft klein. SV-intern consistent → bucket A. Eerbiedskapitaal-regel betreft deity-voornaamwoorden, niet ambtsnamen. Brede normalisatie ambtsnaam→kleine letter is buiten meta-scope; niet geflagd. |
| carryover `ben` | false-positive: gewoon werkwoord ('zoals ik zelf ben', 'deelachtig ben'). Detector-ruis. |

## Noise (bucket A — HSV-keuze / whitelist / window-dup, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 2 patterns (6 occ) | 'Apostel' (1:1, 9:1-2, 15:9), 'Apostelen' (15:7,9) |
| fossiel-lidwoord (whitelisted) | 2 patterns (7 occ) | 'des Heeren' (7:32,34; 10:21,26,28), 'der wereld' (7:33,34) |
| carryover (modern/false-pos) | 2 patterns | 'ben' (7:7, 10:30), 'ongetrouwde' (7:32,34) |
| latinaat-window (dup) | 3 patterns | window-dups van fossiel/wille-patterns (7:33-34, 10:25-28) |

## Bucket-overzicht

- B (per-vers fixes): 1 issue over 1 hoofdstuk (10:28) — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen op §2.7 (2 fossiel-patterns vallen onder bestaande whitelist, niet onder C)
- A (noise): 9 patterns
