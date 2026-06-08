# Scaffolding-deltas — meta-review ACT hoofdstukken 1-28

Gegenereerd: 2026-06-08T04:29:29Z
Aggregator: scripts/meta_diff_aggregate.py --book ACT --chapters 1-28 --min-freq 2

Voorbereiding: 10 ontbrekende HSV-diffs gegenereerd
(`scripts/compare_hsv.py ACT {1,3,5,6,11,14,15,18,21,23}`) zodat de
aggregatie alle 28 hoofdstukken dekt (76 patterns i.p.v. 48 bij
gedeeltelijke dekking).

## Auto-toegepaste deltas (bucket C)

Geen. ACT levert geen scaffolding-gap op: alle recurrente patronen zijn
óf al door bestaande regels gedekt (DREMPEL/FOSSIL_GENITIVE_PAIRS), óf
HSV-keuze (bucket A), óf per-vers content (bucket B).

## Afgewezen deltas (rejected, §2.7-toets / renovatie-principe)

| Pattern | Kind | Freq | Reden afwijzing |
|---|---|---|---|
| `met name` | carryover | 18 | Lijkt false friend (modern 'met name' = 'vooral'), maar in SV-constructie staat het steeds in appositie ("een zeker man, met name Ananias") die de betekenis 'genaamd' ondubbelzinnig maakt. Reverteren van consistent SV-idioom = hervertaling, niet renovatie. Zie feedback_false_friend_overrulet_renovatie. |
| `prijs` (opbrengst-zin) | carryover | 3 | severity_hint=hard omdat bare token 'prijs' in DREMPEL staat — maar die DREMPEL-entry richt zich op de 'lof/prijzing'-betekenis (Gr. ἔπαινος, meta-review EPH 1:6). In ACT 4:34/5:2/5:3 is het de proceeds-betekenis (Gr. τιμή) en "de prijs van de verkochte goederen" is modern leesbaar. Geen rule-uitbreiding; geen hard content-fix. |
| `geschiedde` | carryover | 8 | 'geschieden'-paradigma is al geregeld (γίνομαι→gebeuren-concordantie + narratief "het geschiedde" bewust bewaard). Geen gap. |

## cap-asym — interne inconsistentie (doc-only)

Geen auto-edit (semantisch oordeel vereist). Alle 26 cap-asym-patronen
(Heidenen, Apostelen, Koning, Synagoge, Overste, Keizer, Stadhouder,
Engel, Ouderlingen, …) zijn SV1657-interne hoofdletters die HSV
kleinletterd. Conform de regel "alleen TOEGEVOEGDE caps zijn verboden;
lowercasing van SV-nouncaps faalt de validator" (feedback
sv_cap_preservation_vs_eerbied) blijven deze ongewijzigd. Bucket A.

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 26 | Heidenen (28×), Apostelen (18×), Koning (12×), Synagoge (12×), Overste (11×), Keizer (10×), Stadhouder (10×) |
| fossiel-lidwoord (whitelisted) | 3 | "der Joden", "des Heeren", "der aarde" — alle in FOSSIL_GENITIVE_PAIRS (by-design bewaard) |
| latinaat-window | 8 | "een zeker man met name", "afgoden geofferd van bloed van", "men hem legerplaats zou brengen" — HSV-herschikking, geen Latinaat-residu |
| carryover (HSV-parafrase) | ~33 | "geschiedde", "met name", "toe", "handelde", "ter", "men", "voegen", "streden", "zeden", "tabernakel", … |

## Bucket-overzicht

- B (per-vers fixes): 4 issues over 2 hoofdstukken — zie `findings_ACT.json`
  (broederen 3:22 & 7:37; schiplieden 27:27 & 27:30)
- C (scaffolding-deltas): 0 toegepast, 3 afgewezen (§2.7 / renovatie)
- A (noise): 70 patterns
