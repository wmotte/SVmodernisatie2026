---
name: sv-validate
description: Valideer een gemoderniseerde vers-range tegen het origineel. Controleert kanttekeningaantal, vierkante haken, hoofdletterdiscipline, bijbelverwijzingsformaat, archaisme-blacklist, en source_text-onveranderlijkheid. Roep aan ná het schrijven van de uitvoer-JSON; corrigeer en herhaal bij een fout (maximaal 3x per vers).
---

# sv-validate — modernisatie-controle

Wrapper rond `scripts/validate.py`. Werkdirectory:
`/Users/wmotte/Desktop/projects/SVmodernisatie2026/`.

## check

```bash
python scripts/validate.py check \
  --input input.sv/LUK/LUK.1.json \
  --output output/LUK/LUK.1.json \
  --verses 1,2,3 \
  --sections intro,epilogue \
  --terse
```

Argumenten:
- `--input`: pad naar het originele input-JSON.
- `--output`: pad naar de gemoderniseerde output-JSON.
- `--verses`: komma-gescheiden lijst vers-nummers (default: alle in
  output).
- `--sections`: komma-gescheiden meta-secties (`intro` en/of
  `epilogue`). Voeg een sectie alleen toe als die in deze run is
  (her)gemoderniseerd. Standaard: geen.
- `--terse`: compacte tekstuele output ipv. JSON. Bevat 1 statusregel
  (`PASS|FAIL <pass>/<checked> <fails>F <warnings>W`) plus 1 regel per
  fail. Gebruik dit binnen pijpleidingen om orchestrator-context te
  besparen; laat het weg voor volledige JSON bij debug.

Uitvoer (stdout, JSON — zonder `--terse`):

```json
{
  "checked": 5,
  "passed": 3,
  "failed": 2,
  "warnings_total": 4,
  "verses": [
    {
      "verse": 1,
      "passes": true,
      "issues": [],
      "warnings": ["hoofdletter (hoofdtekst): 'NAdemael' uit origineel niet gevonden in modernisatie"]
    },
    {
      "verse": 2,
      "passes": false,
      "issues": [
        "kanttekeningen: origineel heeft 2, modern heeft 1 (moet >= origineel)",
        "archaïsme: 'ende' (regex=\\bende\\b) in moderne hoofdtekst"
      ],
      "warnings": []
    }
  ],
  "sections": [
    {
      "section": "introduction",
      "passes": true,
      "issues": [],
      "warnings": []
    }
  ],
  "chapter_checks": [
    {
      "check": "per-vers loop",
      "passes": false,
      "issues": [
        "per-vers loop: verzen [1, 2, 3] delen generated_at='2026-05-09T04:43:12Z' — modernisatie was waarschijnlijk een batch ipv. één-vers-per-cyclus (SKILL.md). Memory-query tussen verzen is gemist; concordantie kan eronder lijden."
      ],
      "warnings": []
    }
  ]
}
```

Exitcode: `0` als alles passeert, `1` als minstens één vers / sectie /
hoofdstukcontrole een harde fout heeft. Waarschuwingen tellen niet als fout.

## Wat wordt gecheckt?

**Per vers** (`--verses`):

| # | Check                          | Aard      |
|---|--------------------------------|-----------|
| 1 | `<...>` blok-aantal in modern ≥ origineel | hard |
| 2 | `[...]` blok-aantal modern == origineel   | hard |
| 3a | SV-hoofdletter **hoofdtekst** met andere hoofdletterstand in modern (hoofdletterwisseling, bv. "Engel" → "engel") | **hard** |
| 3b | SV-cap **hoofdtekst** helemaal afwezig in modern (zin geherformuleerd)            | warning  |
| 3c | SV-hoofdletter **kanttekening** met andere hoofdletterstand in modern (hoofdletterwisseling, bv. "Leeraers" → "leraars") | **hard** |
| 3d | SV-cap **kanttekening** helemaal afwezig in modern                                | warning  |
| 4 | `$...$` refs matchen modern formaat        | hard |
| 4b | Geen losse verwijzingen binnen `<kanttekeningen>` (alle refs moeten in `$...$`) | **hard** |
| 5 | Archaïsme-blacklist in moderne hoofdtekst (buiten kanttekeningen) | hard |
| 5b | §2.3 participium-check: SV-finiete tgw. participia (`zeggende`, `ziende`, `weidende[,:;]`, `Dit zeggend,` …) moeten ontvouwd zijn naar finiete bijzin | **hard** |
| 6a | `source_text` semantisch gewijzigd (NFC-vergelijking)   | **hard**  |
| 6b | `source_text` byte-anders maar NFC-equivalent (kopieer-fout) | warning |

**Per sectie** (`--sections intro,epilogue`):

| # | Check                          | Aard      |
|---|--------------------------------|-----------|
| 1 | `[...]` blok-aantal modern == origineel   | hard |
| 2 | Archaisme-blacklist in moderne sectie     | hard |
| 2b | §2.3 participium-check (zoals bij verzen) | **hard** |
| 3a | SV-cap met andere case in modern          | **hard** |
| 3b | SV-cap helemaal afwezig                   | warning  |

(Geen kanttekeningen-, bijbelref-, of source_text-check voor secties —
die concepten gelden niet voor introductie/epiloog.)

**Per hoofdstuk** (cross-vers, draait altijd):

| # | Check                          | Aard      |
|---|--------------------------------|-----------|
| 7 | Geen twee verzen delen exact dezelfde `generated_at`-timestamp (verraadt batchmodernisatie i.p.v. per-vers-loop; SKILL.md `sv-modernize` eist één-vers-per-cyclus) | **hard** |

Hard issues moet je oplossen; warnings noem je in het eindrapport.

## Werkrichtlijnen

- Draai **na** je de uitvoer-JSON hebt geschreven, **vóór** je memory.add
  aanroept. Slecht gevalideerde verzen mogen niet in de vectordatabase.
- Bij `failed > 0`: lees de issues, corrigeer het betreffende vers,
  schrijf output opnieuw, run validate opnieuw. Maximaal 3 iteraties
  per vers — daarna rapporteer je de resterende issues en sla je
  memory-add over voor dat vers.
- De hoofdlettercontrole is **gesplitst**:
  - *hoofdletterwisseling* (SV-woord aanwezig in modern maar met andere hoofdletterstand, bv.
    "Engel" → "engel") = **harde fout**, want AGENTS.md eist behoud van
    het SV-cap-patroon.
  - *ontbrekend* (SV-woord afwezig omdat de zin geherformuleerd is, bv.
    "NAdemael" → "Aangezien") = warning. Beoordeel of dat bewust was.
  - De check draait apart op **hoofdtekst** én **kanttekening-inhoud** —
    hoofdletterwisselingen als "Leeraers" → "leraars" binnen `<…>` blokken worden
    daardoor ook gevangen. Caps in beide locaties horen het origineel-
    patroon te volgen.
- De **per-vers-loopcontrole** (`chapter_checks`) markeert twee verzen die
  dezelfde `generated_at`-timestamp delen als harde fout. Dat verraadt
  batch-modernisatie zonder memory-query tussen verzen — concordantie
  lijdt eronder. Bij fout: doe de batch opnieuw, één vers per cyclus
  (memory query → schrijf → validate → memory add → volgende vers).
- De `source_text`-controle NFC-normaliseert vóór vergelijking. Byte-anders
  maar Unicode-equivalent (bv. polytonic vs monotonic Greek) = warning
  + advies om invoer rechtstreeks te kopiëren i.p.v. te hertypen.
- De archaïsme-blacklist zoekt alleen in de **moderne hoofdtekst** (de
  `<kanttekeningen>` worden eruit gestript voor deze check), zodat
  citaten en oude vormen binnen kanttekeningen geen vals alarm geven.
