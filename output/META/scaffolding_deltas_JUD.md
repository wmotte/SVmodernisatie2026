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

## Auto-toegepaste scaffolding-deltas (bucket C — `apply rules`, branch feature/meta-rules)

| Gap | Kind | Bewijs | Target | Wijziging | Regressie |
|---|---|---|---|---|---|
| Archaïsche imperatief-meervoud `-t` | morfologie | v21 `Bewaart`, v23 `behoudt`/`grijpt` | nieuwe `scan_archaic_imperative_t` in `adversarial_scan.py` + `IMPERATIVE_T_STEMS`/`IMPERATIVE_OBJECT_TOKENS` in `rules_data.py` + ARCHAISMEN.md-rij | regex-anker = zinsbegin/leesteken/nevenschikker (sluit subject vóór `-t` uit → geen 3ev-presens), stam-gate, object-gate; severity soft | corpus-scan: 4 echte vondsten (Lk. 22:10 `volgt`, Mk. 12:15 `Brengt`, 14:13 `volgt`, 14:44 `grijpt`); 0 false positives (`denkt u dit` ROME 2:3 uitgesloten door `u` uit object-set) |
| Fossiele datief `ten/ter + …` | §2.4 | v21 `ten eeuwigen leven`, v12 `ter maaltijd` | 2 patterns in `DREMPEL_FOSSIELEN` (`rules_data.py`): `\bten\s+\w+en\s+leven\b`, `\bter\s+maaltijd\b` | gebonden aan zn `leven`/`maaltijd` → raakt geen compas-/vaste vormen | corpus-scan: 0 false positives (`ten oosten van`, `ter plaatse` niet geraakt) |
| Gesubstantiveerd `-enden`-participium | §2.3 | v16 `morrenden` | `morrenden` toegevoegd aan `DREMPEL_ARCHAISMEN` (exact-woord, soft) | lexicaal i.p.v. regex-verbreding (`\w+enden\b` zou `vrienden`/`benden` raken) | corpus-scan: 0 overige treffers |

> **§2.7-toets**: imperatief-`-t`, `ten/ter`-fossielen en `morrenden`
> passeren productiviteits-/constructie-/verwarringtest. Toegepast op
> branch `feature/meta-rules` (PR, géén auto-merge — user-review vereist).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `dragende` (v7) | §2.3-participium | Productiviteits-test gezakt: `dragende muur/constructie/rol` is productief modern NL → globale blacklist zou false-positiveren. Per-vers gefixt (`en dragen de straf`), geen globale regel |
| `dwalende` (v13) | §2.3-participium | Productiviteits-test gezakt: `dwalende schapen/ziel` productief modern (corpus: 1PE 2:25 `dwalende schapen` zou onterecht flaggen). JUD `dwalende sterren`→`dwaalsterren` bleef per-vers concordantiekeuze |
| Generiek `ten/ter + zn` (ongebonden) | §2.4 | Productiviteits-test gezakt: `ten goede/slotte/onrechte`, `ter plaatse/zake/sprake` zijn vaste moderne vormen. Daarom aan specifiek zn gebonden i.p.v. blanket |
| `De Heere bestraffe u` (v9) | carryover | Vaste subjunctief-formule; SV-constructie werkt modern — bucket A, geen delta |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| latinaat-window (zuivere woordvolgorde-herschikking, geen Latinaat-rest) | 34 | alle n-gram-vensters v4–v23; HSV herschikt, SV2026 niet aantoonbaar Latinaat |
| cap-asym (titel-/eerbiedshoofdletter, SV-intern consistent) | 3 | `Engelen` (v6), `Aartsengel` (v9), `Apostelen` (v17) — HSV kleine letter, SV-keuze |
| carryover zonder consistent modern alternatief / al modern | 5 | `ingeslopen` (≈binnengeslopen), `klagers`, `schande`/schanddaden, `bestraffe`, `handelde` (deels naar B) |

## Bucket-overzicht

- A (noise): 42 patterns (34 latinaat-window + 3 cap-asym + 5 carryover-noise)
- B (per-vers fixes): 10 issues, 1 hoofdstuk — zie `findings_JUD.json`
- C (scaffolding-deltas): 3 toegepast (imperatief-`-t`, `ten/ter`-fossielen, `morrenden`), 3 afgewezen (§2.7: `dragende`, `dwalende`, ongebonden `ten/ter`)
