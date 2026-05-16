# Scaffolding-deltas — meta-review LUK hoofdstukken 1-24

Gegenereerd: 2026-05-16
Aggregator: `scripts/meta_diff_aggregate.py --book LUK --chapters 1-24 --min-freq 2`
Totaal patterns: 28 (cap-asym 20, carryover 6, latinaat-window 1, fossiel-lidwoord 1)

## Auto-toegepaste deltas (bucket C)

Geen. Niet-apply-modus.

Geen bucket-C kandidaten met `frequency ≥ 3` + HSV-consistent modern alternatief.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen.

## Borderline — voor volgende boek (MAT, JOH, HAN, ...) overwegen voor DREMPEL

| Pattern | Kind | Freq LUK | Reden niet-C | Aanbeveling |
|---|---|---|---|---|
| `eer` (= 'voordat') | carryover | 2 | freq < 3 binnen één boek | Bij hit in volgend boek: opnemen in `DREMPEL_ARCHAISMEN` (`scripts/adversarial_scan.py` r.86–107). HSV-consistent → 'voordat'. Confusion-test zakt: dominant betekenis in modern NL is 'honor'. |

## Noise (bucket A — HSV-keuze / SV-interne consistentie, geen actie)

### cap-asym (20 patterns, 116 occurrences)

SV2026 capitaliseert religieus/ambtelijk lexicon waar HSV consistent kleine letter aanhoudt. SV2026 is intern consistent (audit: 22/23 caps `Profeten`, 12/13 caps `Synagoge`, rest 100% cap). HSV-keuze, geen modernisatie-tekortkoming.

| Key | Freq | SV2026 caps | SV2026 lowers | Status |
|---|---:|---:|---:|---|
| profeten | 12 | 22 | 1 | intern consistent (uitzondering: "valse profeten" LUK 6:26 — adjectief-context) |
| schriftgeleerden | 10 | 18 | 0 | consistent |
| profeet | 9 | 18 | 0 | consistent |
| sabbat | 9 | 23 | 0 | consistent |
| overpriesters | 7 | 13 | 0 | consistent |
| synagoge | 7 | 12 | 1 | intern consistent (uitzondering: KT "synagoge-overste" LUK 8 — samenstelling binnen `<…>`) |
| engelen | 6 | 14 | 0 | consistent |
| engel | 5 | 23 | 0 | consistent |
| koning | 4 | 15 | 0 | consistent |
| synagogen | 4 | 8 | 0 | consistent |
| wetgeleerden | 4 | 7 | 0 | consistent |
| heidenen | 3 | 14 | 0 | consistent |
| keizer | 3 | 11 | 0 | consistent |
| koninkrijk | 3 | 54 | 0 | consistent |
| mammon | 3 | 4 | 0 | consistent |
| viervorst | 3 | 7 | 0 | consistent |
| apostelen | 2 | 15 | 0 | consistent |
| hoofdman | 2 | 4 | 0 | consistent |
| koningen | 2 | 5 | 0 | consistent |
| stadhouder | 2 | 6 | 0 | consistent |

Note: "valse profeten" LUK 6:26 (kleine letter) en "synagoge-overste" LUK 8 KT (kleine letter in samenstelling): context-specifiek, geen normbreuk. Geen actie.

### fossiel-lidwoord (1 pattern, 3 occurrences)

| Key | Freq | Verzen | Reden |
|---|---:|---|---|
| `der joden` | 3 | LUK 23:3, 23:37, 23:38 | "Koning der Joden" — vaste bijbelse uitdrukking (titulus crucis), ook in NBV21 zo behouden. Bucket A per skill ("bijbeluitdrukking → A"). |

### latinaat-window (1 pattern, 2 occurrences)

| Key | Freq | Verzen | Reden |
|---|---:|---|---|
| `lijkt een mens die een` | 2 | LUK 6:48, 6:49 | SVO-vergelijkingsformule (parallelle structuur in gelijkenis). Geen bewijs van Latinaat-rest in SV2026; HSV expandeert syntactisch ("Hij is gelijk aan een man die..."). Bucket A. |

### carryover (5 van 6 patterns, 13 occurrences)

| Key | Freq | Verzen | Reden bucket A |
|---|---:|---|---|
| `hoe` | 5 | LUK 8:47, 9:41, 10:26, 16:2, 22:2 | "hoe" is normaal modern NL. HSV-alternatieven zijn random (`nadat`, `onopgemerkt`, ...) — aggregator-noise: HSV-verzen hebben hertaalde syntaxis waarin "hoe" niet voorkomt, niet omdat "hoe" archaïsch is. SV2026 vormen ("hoe lang", "hoe leest u", "zochten hoe") modern grammaticaal. |
| `gaf` | 2 | LUK 7:21, 23:25 | Normaal verleden-tijd "geven". HSV-alternatieven (`schonk`, `aandoeningen`, ...) random. |
| `man` | 2 | LUK 13:6, 19:12 | "Een zeker man / hooggeboren man" modern NL. HSV parafrase ("Iemand", "Een zeker mens van hoge geboorte") is stijlkeuze, geen modernisatie. |
| `toe` | 2 | LUK 12:15, 15:20 | Partikel "zie toe" / "liep toe" modern NL. |
| `toonde` | 2 | LUK 4:5, 24:40 | "toonde" modern NL preteritum van "tonen". HSV "liet zien" alternatief stijlkeuze. |

## Bucket-overzicht

- **A** (noise / HSV-keuze): 27 patterns — 134 occurrences
- **B** (per-vers findings): 1 pattern — 2 issues (LUK 22:15, 22:61, lemma `eer` = 'voordat')
- **C** (scaffolding-deltas): 0 toegepast, 0 afgewezen
