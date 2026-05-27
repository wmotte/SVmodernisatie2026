# Projectoverzicht — SVmodernisatie2026

*Van initiatie tot heden. Bijgewerkt: 24 mei 2026.*

Modernisering van de Statenvertaling 1657 (2e druk) met maximaal behoud
van de SV-eigenheid, volledig uitgevoerd door taalmodellen volgens de
methode in [`MODERNISATIE.md`](../MODERNISATIE.md).

---

## Voortgang: vertaalde verzen t.o.v. het hele NT

| | Verzen |
|---|---:|
| **Gemoderniseerd** | **2.462** |
| **Totaal NT (SV1657-corpus, `input.sv/`)** | **7.959** |
| **Voortgang** | **30,9 %** |

```
[████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 30,9 %
```

### Per boek

| Boek | Hoofdstukken | Verzen gedaan | Verzen totaal | Status |
|---|---|---:|---:|---|
| Markus (MRK)    | 16 / 16 | 678   | 678   | ✅ compleet |
| Lukas (LUK)     | 24 / 24 | 1.151 | 1.151 | ✅ compleet |
| Filemon (PHM)   | 1 / 1   | 25    | 25    | ✅ compleet |
| 2 Johannes (2JN)| 1 / 1   | 13    | 13    | ✅ compleet |
| 3 Johannes (3JN)| 1 / 1   | 15    | 15    | ✅ compleet |
| Judas (JUD)     | 1 / 1   | 25    | 25    | ✅ compleet |
| Romeinen (ROM)  | 13 / 16 | 351   | 434   | 🔧 in uitvoering |
| 1 Korinthe (1CO)| 8 / 16  | 189   | 437   | 🔧 in uitvoering |
| 2 Korinthe (2CO)| 0 / 13  | 9     | 256   | 🔧 in uitvoering |
| 1 Petrus (1PE)  | 0 / 5   | 6     | 105   | 🔧 in uitvoering |
| **Subtotaal**   |         | **2.462** | **3.139** | |

Resterende NT-boeken (nog niet gestart): MAT, JHN, ACT, GAL, EPH, PHP,
COL, 1TH, 2TH, 1TI, 2TI, TIT, HEB, JAS, 2PE, 1JN, REV — samen 4.820 verzen.

---

## Omvang van het NT-broncorpus

Woordtelling van het volledige SV1657-corpus in `input.sv/`, opgesplitst
naar hoofdtekst (de versproza), kanttekeningen (`<…>`-blokken) en
introductie (de hoofdstuksamenvattingen plus boekepilogen). De laatste twee
kolommen tellen de bijbelverwijzingen (`$…$`): het aantal `$…$`-blokken in
de marge, en een schatting van de losse verwijzingen daarin (één blok kan er
meerdere bundelen, bv. `Ierem. 31.33. Ezech. 11.19. ende 36.26.`).
Verwijzingen tellen niet mee in de woordkolommen. Een woord = een
aaneengesloten reeks letters/cijfers.

| Boek | Hoofdtekst | Kanttekeningen | Introductie | Woorden totaal | Verwijzingen (`$…$`) | Losse refs |
|---|---:|---:|---:|---:|---:|---:|
| Mattheüs (MAT) | 24.391 | 21.172 | 2.618 | 48.181 | 610 | 1.327 |
| Markus (MRK) | 15.189 | 8.673 | 1.742 | 25.604 | 340 | 816 |
| Lukas (LUK) | 25.854 | 16.344 | 2.948 | 45.146 | 545 | 1.331 |
| Johannes (JHN) | 19.611 | 21.959 | 2.910 | 44.480 | 500 | 1.189 |
| Handelingen (ACT) | 24.415 | 33.357 | 4.220 | 61.992 | 448 | 931 |
| Romeinen (ROM) | 9.685 | 34.379 | 2.643 | 46.707 | 279 | 545 |
| 1 Korinthe (1CO) | 9.666 | 32.286 | 2.987 | 44.939 | 232 | 492 |
| 2 Korinthe (2CO) | 6.248 | 13.929 | 1.978 | 22.155 | 139 | 274 |
| Galaten (GAL) | 3.185 | 14.237 | 1.080 | 18.502 | 101 | 203 |
| Efeze (EPH) | 3.012 | 11.360 | 1.068 | 15.440 | 126 | 339 |
| Filippenzen (PHP) | 2.205 | 8.842 | 678 | 11.725 | 66 | 150 |
| Kolossenzen (COL) | 2.035 | 9.452 | 671 | 12.158 | 94 | 198 |
| 1 Thessalonicenzen (1TH) | 1.876 | 4.730 | 687 | 7.293 | 59 | 139 |
| 2 Thessalonicenzen (2TH) | 1.044 | 3.908 | 413 | 5.365 | 40 | 77 |
| 1 Timotheüs (1TI) | 2.288 | 7.987 | 765 | 11.040 | 93 | 197 |
| 2 Timotheüs (2TI) | 1.674 | 6.662 | 642 | 8.978 | 50 | 125 |
| Titus (TIT) | 939 | 2.703 | 460 | 4.102 | 40 | 104 |
| Filemon (PHM) | 450 | 1.167 | 21 | 1.638 | 13 | 28 |
| Hebreeën (HEB) | 7.119 | 26.353 | 2.114 | 35.586 | 216 | 419 |
| Jakobus (JAS) | 2.409 | 9.973 | 870 | 13.252 | 68 | 150 |
| 1 Petrus (1PE) | 2.426 | 8.280 | 768 | 11.474 | 115 | 261 |
| 2 Petrus (2PE) | 1.570 | 5.293 | 562 | 7.425 | 50 | 83 |
| 1 Johannes (1JN) | 2.640 | 7.971 | 860 | 11.471 | 80 | 188 |
| 2 Johannes (2JN) | 324 | 723 | 0 | 1.047 | 5 | 16 |
| 3 Johannes (3JN) | 299 | 816 | 0 | 1.115 | 3 | 2 |
| Judas (JUD) | 611 | 2.401 | 6 | 3.018 | 22 | 47 |
| Openbaring (REV) | 11.951 | 49.625 | 3.326 | 64.902 | 306 | 453 |
| **Totaal NT** | **183.116** | **364.582** | **37.037** | **584.735** | **4.640** | **10.084** |

Reproduceerbaar via `python3 scripts/count_words.py`.

---

## Tijdlijn

| Datum | Mijlpaal |
|---|---|
| **16 mei 2026** | Initiatie: `Initial snapshot`. Eerste modernisatie `MRK 2:1-3`. Pijplijn (modernize → validate → semantic-review → adversarial-review) en parallelbijbel-PDF opgezet. |
| **17 mei 2026** | Markus volledig afgerond (16 hoofdstukken). Drukste dag: 215 commits. |
| **18 mei 2026** | Lukas afgerond (24 hoofdstukken). Filemon gestart. Meta-review-aggregator (cross-chapter HSV-diff bucketing) toegevoegd. |
| **19 mei 2026** | Romeinen gestart (`ROM 1:1-3`). |
| **20 mei 2026** | Romeinen t/m hoofdstuk 8. Eerbiedskapitaal- en genitief-archaïsme-checks HARD in validator. SV27-vergelijking toegevoegd. |
| **22 mei 2026** | Romeinen hoofdstuk 9 en 10 afgerond (t/m ROM 10). Adversariële genitief- en participium-opschoning in kanttekeningen. Eerste Korinthe gestart (1CO 1). |
| **23 mei 2026** | 1 Korinthe loopt door; 2 Korinthe gestart (2CO 1). |
| **24 mei 2026** | Romeinen afgerond t/m hoofdstuk 13 (ROM 11–13). 1 Korinthe t/m hoofdstuk 8 compleet, hoofdstuk 9 in uitvoering. Drie korte brieven volledig afgerond: 2 Johannes, 3 Johannes en Judas. 1 Petrus gestart (1PE 1). Drukste inhaaldag: 144 commits. |
| **25 mei 2026** | 1 Korinthe en 1 Petrus afgerond; 2 Korinthe en de pastorale brieven verder uitgebouwd. |
| **26 mei 2026** | Titus, 2 Tessalonicenzen en 2 Petrus compleet; Kolossenzen gestart. Voortgang: 3.188 van 7.959 NT-verzen. |

Looptijd tot heden: **11 kalenderdagen** (16–26 mei 2026; 10 productiedagen met output-commits).

---

## Productie-statistieken

| Metriek | Waarde |
|---|---:|
| Commits totaal | 1.673 |
| Gemergede pull requests | 764 |
| Commits per dag | 89 / 151 / 88 / 51 / 52 / 26 / 54 / 157 / 225 / 189 |
| Boeken compleet | 12 (MRK, LUK, ROM, 1CO, 2TH, 1PE, 2PE, TIT, PHM, 2JN, 3JN, JUD) |
| Gemoderniseerde verzen | 3.188 / 7.959 (40,06%) |
| Verzen per productiedag (gem.) | ~319 |

---

## Methode in het kort

Elke vers-batch (max. 3 verzen) doorloopt een vaste keten, één PR per batch
naar `main`:

1. **sv-modernize** — modernisatie met voorbeeldparen uit `sv-memory`
   (vectordatabase van eerdere SV↔modern-paren) en bijbelverwijzing-normalisatie (`sv-bibref`).
2. **sv-validate** — harde controles: kanttekeningaantal, vierkante haken,
   hoofdletterdiscipline, verwijzingsformaat, archaïsme-blacklist,
   onveranderlijkheid van `source_text`.
3. **sv-semantic-review** — false friends, idioom-mismatch, spiegeling tegen HSV.
4. **sv-adversarial-review** — per hoofdstuk; bevindingen worden gefixt of weerlegd.
5. **sv-meta-review** — cross-chapter patronen over alle HSV-diffs per boek.

De methode is cumulatief: bevindingen scherpen de regelbestanden
(`MODERNISATIE.md`, `ARCHAISMEN.md`, validator) aan, zodat latere boeken
profiteren van eerdere correcties.

---

*Verzen geteld uit `output/<BOEK>/<BOEK>.<H>.json` (gemoderniseerd) en
`input.sv/<BOEK>/` (NT-totaal). Reproduceerbaar via het telscript onder
`scripts/`.*
