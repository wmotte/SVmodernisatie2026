# Scaffolding-deltas — meta-review 1CO hoofdstukken 1-16

Gegenereerd: 2026-05-26T00:00:00+00:00 (her-run over volledige 16 hoofdstukken)
Eerste run: 2026-05-25T20:12:43Z (dekte ch 1,2,6,7,8,9,10,15,16 — ch 3-5,11-14 hadden nog geen diff)
Aggregator: scripts/meta_diff_aggregate.py --book 1CO --chapters 1-16 --min-freq 2
Modus: analyse-only (geen edits toegepast)

## Status t.o.v. eerste run

Alle 16 HSV-diffs zijn nu aanwezig (ch 3-5, 11-14 toegevoegd). De her-run
over de volledige 16 hoofdstukken levert **geen nieuwe bucket-B/C** boven
de eerste run. De enige bucket-B-fix (10:28 'om diens wille die') is
gefixt en gemerged via PR #687.

## Auto-toegepaste deltas (bucket C)

Geen. Geen pattern haalt de C-drempel (N>=3 + bestaande lint had het moeten
vangen) zonder al door bewuste whitelist/keuze gedekt te zijn.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `des heeren` (9×) | fossiel-lidwoord | `(des, heeren)` in `FOSSIL_GENITIVE_PAIRS` (rules_data.py:84). Bewuste fossiel; validator laat door. HSV 'van de Heere' is HSV-keuze. |
| `der wereld` (2×) | fossiel-lidwoord | `(der, wereld)` in `FOSSIL_GENITIVE_PAIRS` (rules_data.py:95). Parallel aan behouden `des Heeren` in zelfde verzen 7:32-34. |
| `ongetrouwde` (2×) | carryover | productiviteits-test andersom: 'ongetrouwd' is gangbaar modern NL. HSV 'ongehuwde' is stijlkeuze. |
| `ter wille van` (4×) | carryover | 'ter wille van het geweten/de Engelen' komt voor in modern zakelijk NL. Geen archaïsme. (Losse 10:28 'om diens wille die' was wél bucket B — gefixt PR #687.) |
| `sticht` / `stichting` (8:1, 14:4 + kanttekeningen 14:6,17,39) | carryover | oikodomeo-concordantie. 'stichten/stichting' is de traditionele NL theologische term (vgl. 'stichtelijk'); consistent door hoofdtekst én kanttekeningen. Bewuste renovatie-keuze, geen false friend in deze register-context. |
| `vermengen` (5:9, 5:11) | carryover | 'zich vermengen met' (synanamignymi) is begrepen SV-register; behoud verdedigbaar. HSV 'zich inlaten met' is HSV-keuze. |
| `hoereerders` (5:9,10; 6:10) | carryover | drempel-archaïsme maar bijbels-transparant (pornos); register-behoud consistent met projectlijn. HSV 'ontuchtplegers' is HSV-keuze. |

## Observaties (geen edit, semantisch oordeel)

| Kind | Waarneming |
|---|---|
| cap-asym `Apostel(en)`/`Profeten`/`Leraars`/`Engelen` | SV2026 kapitaliseert ambtsnamen mid-zin consistent (1:1, 4:9, 9:1-2, 12:28-29, 14:32, 15:7,9); HSV schrijft klein. SV-intern consistent → bucket A. Eerbiedskapitaal-regel betreft deity-voornaamwoorden, niet ambtsnamen. Brede ambtsnaam-normalisatie is buiten meta-scope. |
| carryover `ben`/`ten`/`minst`/`afgesneden` | detector-ruis: gewone werkwoorden / HSV-parafrase / idiomen ('ten hoogste', 'ten laatste'), geen archaïsme. |

## Noise (bucket A — HSV-keuze / whitelist / window-dup, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 5 patterns (16 occ) | 'Apostel(en)', 'Profeten', 'Leraars', 'Engelen' |
| fossiel-lidwoord (whitelisted) | 2 patterns (11 occ) | 'des Heeren', 'der wereld' |
| carryover (modern/register/false-pos) | 7 patterns | 'wille', 'hoereerders', 'ten', 'afgesneden', 'ben', 'minst', 'ongetrouwde', 'sticht', 'vermengen' |
| latinaat-window (dup) | 3 patterns | window-dups van fossiel/wille-patterns (7:33-34, 10:25-28) |

## Bucket-overzicht

- B (per-vers fixes): 1 issue (10:28) — gefixt + gemerged PR #687; geen nieuwe in her-run
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen op §2.7 (fossiel-patterns vallen onder bestaande whitelist)
- A (noise): 17 patterns
