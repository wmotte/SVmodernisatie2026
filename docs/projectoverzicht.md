# Projectoverzicht — SVmodernisatie2026

*Van initiatie tot heden. Bijgewerkt: 22 mei 2026.*

Modernisering van de Statenvertaling 1657 (2e druk) met maximaal behoud
van de SV-eigenheid, volledig uitgevoerd door taalmodellen volgens de
methode in [`MODERNISATIE.md`](../MODERNISATIE.md).

---

## Voortgang: vertaalde verzen t.o.v. het hele NT

| | Verzen |
|---|---:|
| **Gemoderniseerd** | **2.134** |
| **Totaal NT (SV1657-corpus, `input.sv/`)** | **7.959** |
| **Voortgang** | **26,8 %** |

```
[███████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 26,8 %
```

### Per boek

| Boek | Hoofdstukken | Verzen gedaan | Verzen totaal | Status |
|---|---|---:|---:|---|
| Markus (MRK)   | 16 / 16 | 678   | 678   | ✅ compleet |
| Lukas (LUK)    | 24 / 24 | 1.151 | 1.151 | ✅ compleet |
| Filemon (PHM)  | 1 / 1   | 25    | 25    | ✅ compleet |
| Romeinen (ROM) | 10 / 16 | 280   | 434   | 🔧 in uitvoering |
| **Subtotaal**  |         | **2.134** | **2.288** | |

Resterende NT-boeken (nog niet gestart): MAT, JHN, ACT, 1CO, 2CO, GAL,
EPH, PHP, COL, 1TH, 2TH, 1TI, 2TI, TIT, HEB, JAS, 1PE, 2PE, 1JN, 2JN,
3JN, JUD, REV — samen 5.671 verzen.

---

## Tijdlijn

| Datum | Mijlpaal |
|---|---|
| **16 mei 2026** | Initiatie: `Initial snapshot`. Eerste modernisatie `MRK 2:1-3`. Pijplijn (modernize → validate → semantic-review → adversarial-review) en parallelbijbel-PDF opgezet. |
| **17 mei 2026** | Markus volledig afgerond (16 hoofdstukken). Drukste dag: 215 commits. |
| **18 mei 2026** | Lukas afgerond (24 hoofdstukken). Filemon gestart. Meta-review-aggregator (cross-chapter HSV-diff bucketing) toegevoegd. |
| **19 mei 2026** | Romeinen gestart (`ROM 1:1-3`). |
| **20 mei 2026** | Romeinen t/m hoofdstuk 8. Eerbiedskapitaal- en genitief-archaïsme-checks HARD in validator. SV27-vergelijking toegevoegd. |
| **22 mei 2026** | Romeinen hoofdstuk 9 en 10 afgerond (t/m ROM 10). Adversariële genitief- en participium-opschoning in kanttekeningen. |

Looptijd tot heden: **7 dagen** (16–22 mei 2026).

---

## Productie-statistieken

| Metriek | Waarde |
|---|---:|
| Commits totaal | 797 |
| Gemergede pull requests | 403 |
| Commits per dag | 139 / 215 / 175 / 104 / 120 / 44 |
| Boeken compleet | 3 (MRK, LUK, PHM) |
| Verzen per dag (gem.) | ~356 |

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
