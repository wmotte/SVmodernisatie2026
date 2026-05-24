# Scaffolding-deltas — meta-review JUD hoofdstuk 1

Gegenereerd: 2026-05-24
Aggregator: scripts/meta_diff_aggregate.py --book JUD --chapters 1 --min-freq 1

> **Degeneratie-noot.** JUD is een één-hoofdstukboek. De meta-review leeft van
> cross-chapter recurrentie (pattern N≥3×). Die signaalbron ontbreekt hier:
> `--min-freq 2` gaf 0 patterns; met `--min-freq 1` zijn alle 47 patterns
> frequency=1. Bucket-C-auto-apply (op frequentie) kan dus niet vuren. De
> bucket-C-items hieronder zijn handmatig geïdentificeerde scaffolding-gaps
> waarvan de **categorie** boekoverschrijdend terugkeert; ze zijn als
> kandidaat-deltas gelogd, NIET toegepast (geen `apply`-trigger).

## Kandidaat scaffolding-deltas (bucket C — NIET toegepast, geen apply)

| Gap | Kind | Bewijs in JUD 1 | Voorgestelde target | Motivatie |
|---|---|---|---|---|
| Archaïsche imperatief-meervoud `-t` | morfologie | v21 `Bewaart`, v23 `behoudt`/`grijpt` | nieuwe lint in `scripts/adversarial_scan.py` (regex: hoofdtekst-imperatief op `-t` zonder onderwerp) | Geen enkele lint vangt dit nu; recurreert in elke vermaning/imperatief-passage door het hele NT |
| Adjectivisch/gesubstantiveerd `-ende`-participium | §2.3 | v7 `dragende`, v13 `dwalende`, v16 `morrenden` | uitbreiden §2.3-check in `scripts/validate.py` van finiet → ook attributief/gesubstantiveerd `-ende` | Bestaande §2.3 ving v14 (finiet) wél, deze drie niet. Gat in participium-detectie |
| Fossiele datief `ten/ter + (verbogen adj) + zn` | §2.4 | v21 `ten eeuwigen leven`, v12 `ter maaltijd` | `FOSSIL_LIDWOORD_PATTERNS`-tuple in `scripts/adversarial_scan.py` | Genitief/datief-archaïsme-lijn (zie memory genitief_archaisme) dekt `der/des/den` maar niet `ten/ter`-datief |

> **§2.7-toets**: alle drie passeren productiviteits-, constructie- en
> verwarringtest (moderne alternatieven 'Bewaar', 'dwaalsterren',
> 'tot het eeuwige leven' zijn neutraal zakelijk NL). Geen afwijzingen.
> Toepassing wacht op expliciete `meta-review JUD apply rules`.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `De Heere bestraffe u` (v9) | carryover | Vaste subjunctief-formule ('moge de Heere u bestraffen'); SV-constructie werkt modern — bucket A, geen delta |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| latinaat-window (zuivere woordvolgorde-herschikking, geen Latinaat-rest) | 34 | alle n-gram-vensters v4–v23; HSV herschikt, SV2026 niet aantoonbaar Latinaat |
| cap-asym (titel-/eerbiedshoofdletter, SV-intern consistent) | 3 | `Engelen` (v6), `Aartsengel` (v9), `Apostelen` (v17) — HSV kleine letter, SV-keuze |
| carryover zonder consistent modern alternatief / al modern | 5 | `ingeslopen` (≈binnengeslopen), `klagers`, `schande`/schanddaden, `bestraffe`, `handelde` (deels naar B) |

## Bucket-overzicht

- A (noise): 42 patterns (34 latinaat-window + 3 cap-asym + 5 carryover-noise)
- B (per-vers fixes): 10 issues, 1 hoofdstuk — zie `findings_JUD.json`
- C (scaffolding-deltas): 3 kandidaten, 0 toegepast (geen apply-trigger), 0 afgewezen
