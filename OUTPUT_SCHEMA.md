# Output JSON-schema — SVmodernisatie2026

Schema voor `output/<BOEK>/<BOEK>.<H>.json`. Aanvulling op `AGENTS.md`
(sectie "Output JSON-schema").

## Volledig schema

```json
{
  "book": "LUK",
  "chapter": 1,
  "introduction": {
    "original":     "<originele introductie>",
    "modernized":   "<moderne introductie>",
    "generated_at": "2026-05-08T12:34:56Z",
    "model":        "<agent-model-id>"
  },
  "verses": [
    {
      "verse_number": 1,
      "original": "<originele tekst incl. <kanttekeningen> en $bijbelrefs$>",
      "modernized": "<moderne tekst incl. moderne <kanttekeningen> en $bijbelrefs$>",
      "source_text": "<Textus Receptus, BYTE-EXACT uit invoer>",
      "generated_at": "2026-05-08T12:34:56Z",
      "model": "<agent-model-id>",
      "memory_examples_used": 0,
      "notes": [
        {
          "type": "twijfel",
          "subject": "<korte aanduiding>",
          "context": "<bv. 'kanttekening 2'>",
          "choice": "<wat ik koos>",
          "alternatives": ["<optie A>", "<optie B>"],
          "reason": "<waarom>"
        }
      ]
    }
  ],
  "epilogue": {
    "original":     "<originele epiloog>",
    "modernized":   "<moderne epiloog>",
    "generated_at": "2026-05-08T12:34:56Z",
    "model":        "<agent-model-id>"
  }
}
```

## Velden

`introduction` is altijd aanwezig (elk hoofdstuk heeft er één).
`epilogue` is alleen aanwezig als het invoerbestand het veld heeft
(d.w.z. het laatste hoofdstuk van een bijbelboek).

`source_text` moet **byte-exact** uit de invoer gekopieerd worden (niet
hertypen). SV-invoer bevat polytonische Griekse codepoints die door
Write-tools soms NFC-genormaliseerd worden — de validator detecteert dat
en raadt rechtstreeks kopiëren aan.

`notes` is **optioneel**: alleen toevoegen wanneer er een twijfel,
bewuste afwijking, of context is die een beoordelaar moet zien. `type` is
een van `twijfel`, `afwijking`, `context`. Notes gaan **niet** in
het geheugen — alleen vertaalkeuzes wel.

**Notes zijn ALTIJD een lijst van objecten — nooit een losse string of
array van strings.** Ook één enkele note moet als `[{...}]` worden
geschreven. String-notes breken de documentatieweergave
(`notes.map is not a function`); de validator vangt dit als HARDE fout
(`_check_notes_shape`). Minimaal verplicht veld per object: `type`
(één van de drie waarden hierboven). Aanbevolen velden: `subject`,
`context`, `choice`, `alternatives`, `reason`.

**Geen modelmerken in notes.** De inhoud van notes-velden (`subject`,
`context`, `choice`, `reason`, `alternatives`) wordt door de
documentatieweergave onder een "Notes"-paneel getoond. Verwijs daarin nooit
naar specifieke modelnamen ("claude", "gemini", "GPT", "Opus", etc.).
Gebruik neutrale formuleringen: "het taalmodel", "de modernisatie",
of beschrijf de keuze zonder naar de keuzemaker te verwijzen.

## Incrementeel gedrag

**Incrementeel.** Bij een nieuwe aanroep ("LUK 1:4-10") voeg je verzen
toe aan het bestaande `verses`-array; eerder gemoderniseerde verzen
blijven onaangeraakt. Bij heraanroep van bestaande verzen overschrijf je
op `verse_number`. **Bij de eerste aanroep voor een hoofdstuk
moderniseer je ook automatisch de introductie** (en de epiloog als
aanwezig). Staan ze al in output: laten staan tenzij de gebruiker
expliciet vraagt om opnieuw moderniseren.

De gebruiker kan ze ook gericht aanvragen:
- "moderniseer LUK 1 introductie"
- "moderniseer LUK 24 epiloog"

## Bijbestanden in `output/<BOEK>/`

Naast het primaire `<BOEK>.<H>.json` schrijven downstream-skills extra
artefacten in dezelfde map:

| Pad | Beheerd door | Inhoud | Lifecycle |
|---|---|---|---|
| `<BOEK>.<H>.json` | `sv-modernize` via `scripts/upsert_verse.py` | Gemoderniseerde verzen + intro + epilogue. | Permanent. Groeit per batch (upsert op `verse_number`). |
| `review.<H>.json` | `sv-adversarial-review` via `scripts/adversarial_scan.py` | Adversariële bevindingenlijst per hoofdstuk + verify-pass-actions. | Permanent, getrackt in git. Wordt aangevuld bij elke nieuwe pass (`passes`-array); issues blijven met `status: fixed|rebutted|reopened`. Niet opschonen — historiek heeft auditwaarde. |
| `META/decisions.jsonl` (op `output/META/`) | `scripts/extract_decisions.py` | Geaggregeerde fix/rebuttal-beslissingen uit alle `review.*.json` + notes uit `<BOEK>.<H>.json`. | Regenereerbaar; opnieuw bouwen met `extract_decisions.py --root output --book <BOEK>`. |
| `META/candidates_<BOEK>.json` | `scripts/meta_diff_aggregate.py` | Cross-chapter patronen uit `docs/diff_hsv_<BOEK>_*.json` voor meta-review. | Regenereerbaar; per meta-review-aanroep. |
| `META/rule_curator_report.json` | `scripts/rule_curator.py` | Dry-run drift-rapport (stoplist/blacklist/rebuttal). | Wegwerp; herbruikbaar pad. |

Alleen `<BOEK>.<H>.json` en `review.<H>.json` zijn primaire artefacten;
de `META/`-bestanden zijn afgeleid en mogen opnieuw worden gebouwd
vanuit primaire data.
