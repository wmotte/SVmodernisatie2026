# Scaffolding-deltas — meta-review LUK hoofdstukken 1-24

Gegenereerd: 2026-05-25T17:05:00Z
Aggregator: scripts/meta_diff_aggregate.py --book LUK --chapters 1-24 --min-freq 2
Modus: analyse-only (geen edits toegepast)

## Auto-toegepaste deltas (bucket C)

*Geen — analyse-only modus. Onderstaande C-kandidaat vereist menselijke
ratificatie vóór apply (register-gevoelig + rebuttal-conflict).*

## Bucket-C kandidaten — GERATIFICEERD ALS BUCKET A (geen actie)

| Pattern | Kind | Freq | Beslissing (user 2026-05-25) |
|---|---|---|---|
| `geschiedde` | carryover | 36 | **Behouden** als bewuste registerkeuze (verheven narratief "en het geschiedde", vgl. KJV "and it came to pass"). Rebuttals review.11/17 geratificeerd. Geen regel-delta, geen content-fix. Staat niet op `DREMPEL_ARCHAISMEN` → lint flagt niet, geen whitelist-edit nodig. |

### §2.7-toets `geschiedde`
- **Productiviteit**: "geschiedde" komt niet voor in modern zakelijk NL. ✅ zakt (= archaïsme).
- **Constructie**: "het geschiedde, dat …" → modern "het gebeurde dat …". ✅ werkt.
- **Verwarring**: "gebeuren" heeft geen dominant andere betekenis. ✅ veilig.

### ⚠️ Rebuttal-conflict (waarom NIET auto-apply)
Decision-memory bevat per-hoofdstuk rebuttals (review.11, review.17) die
claimen dat narratief `het geschiedde` → `het gebeurde` werd gemoderniseerd
en alleen de petitie-formule `uwe wil geschiede` (LUK 11:2) behouden blijft.
**Realiteit**: de surface-form `geschiedde` staat nog 36× in de output
(o.a. LUK 17:11 sv2026 = "En het geschiedde, toen hij naar Jeruzalem
reisde"). De rebuttal-claim is dus niet systematisch toegepast.

Dit is exact het cross-chapter gat waarvoor meta-review bestaat: een
per-hoofdstuk verweer zei "wordt gemoderniseerd", maar boekbreed bleef
het staan. Twee mogelijke uitkomsten — menselijke beslissing nodig:
1. **Moderniseren** (HSV-conform `gebeurde`): regel-delta + 36 bucket-B
   content-fixes. Aanbevolen op taalkundige gronden.
2. **Behouden als bewuste registerkeuze** (verheven narratief register
   "en het geschiedde", vgl. KJV "and it came to pass"): rebuttals
   ratificeren, `geschiedde` whitelisten zodat de drempel-lint niet
   herhaaldelijk flagt.

## Afgewezen / niet-actie (bucket A)

| Pattern | Kind | Freq | Reden |
|---|---|---|---|
| `der joden` | fossiel-lidwoord | 3 | **Defended fossil** (decision-memory LUK-23-3/37/38): gefossiliseerde Christologische/processuele titel "Koning der Joden" (Gr. ὁ βασιλεὺς τῶν Ἰουδαίων, syn-opt. parallel Mt/Mk/Jh). Genitief-uitzondering — geen fix. |
| `lijkt een mens die een` | latinaat-window | 2 | HSV-herschikking (LUK 6:48-49); geen Latinaat-rest in SV2026. Bucket A. |
| `hoe` | carryover | 4 | Modern NL (`hoe lang`, `hoe leest u`, `zochten hoe`); HSV parafraseert. Geen archaïsme. |
| `gaf` | carryover | 2 | `gaf` is modern; HSV-alternatieven zijn parafrase-ruis. |
| `man` | carryover | 2 | `man` is modern; "een zeker man" → HSV "iemand/mens" is stijlkeuze. |

## Cap-asym — systematische over-kapitalisatie (NOTE, geen auto-edit)

20 cap-asym-patterns, alle **SV-intern consistent** (zelfde woord overal
met hoofdletter binnen LUK 1-24) → per regel **bucket A** (geen auto-edit;
semantisch oordeel nodig). HSV schrijft ze consistent klein.

Soortnamen met SV1657-titelkapitaal die in modern NL klein horen:

| Woord | Freq | HSV |
|---|---|---|
| Profeten/Profeet | 12 / 9 | profeten / profeet |
| Schriftgeleerden | 10 | schriftgeleerden |
| Sabbat | 9 | sabbat |
| Synagoge/Synagogen | 7 / 4 | synagoge(n) |
| Overpriesters | 7 | overpriesters |
| Engelen/Engel | 6 / 5 | engelen / engel |
| Koning/Koningen/Koninkrijk | 4 / 2 / 3 | koning(en) / koninkrijk |
| Wetgeleerden | 4 | wetgeleerden |
| Heidenen | 3 | heidenen |
| Keizer | 3 | keizer |
| Mammon | 3 | mammon |
| Viervorst | 3 | viervorst |
| Apostelen | 2 | apostelen |
| Hoofdman | 2 | hoofdman |
| Stadhouder | 2 | stadhouder |

**Beslissing (user 2026-05-25)**: capitals **volgens origineel** (SV1657
titel-kapitaal behouden). Bucket A, geen normalisatie, geen lint. Cap-asym
blijft als detectie-categorie noise voor LUK.

## Bucket-overzicht

- B (per-vers fixes): 0 issues — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast (`geschiedde` geratificeerd → A, registerkeuze)
- A (noise/defended/geratificeerd): 6 patterns + 20 cap-asym

**Eindstatus: 0 edits. Meta-review LUK schoon — geen openstaande acties.**
