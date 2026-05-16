---
name: sv-modernize
description: Moderniseer een vers-range, een hoofdstukintroductie, of een boekepiloog uit de Statenvertaling 1657 (2e druk). Activeer wanneer de gebruiker zegt "moderniseer LUK X:Y-Z", "moderniseer LUK 1 introductie", "moderniseer LUK 24 epiloog", of vergelijkbaar. Leest input.sv/<BOEK>/<BOEK>.<H>.json, gebruikt sv-memory voor voorbeeldparen, sv-bibref voor verwijzingen, sv-validate voor controle, en schrijft output/<BOEK>/<BOEK>.<H>.json. Eén model doet het hele werk volgens AGENTS.md.
---

# sv-modernize — protocol per aanroep

Activeer dit protocol bij elke aanroep zoals "moderniseer LUK 1:1-3",
"moderniseer LUK 1 introductie", of "moderniseer LUK 24 epiloog".

## Stap 0 — ontleed de aanroep

Bepaal:
- `BOEK`: 3-letterige projectcode (`LUK`, `MAT`, ...). Map "Lucas" → `LUK`,
  "Mattheüs"/"Mattheus" → `MAT`, etc.
- `H`: hoofdstuknummer.
- `MODE`:
  - `verses` — vers-range gegeven (bv. "LUK 1:1-3"). Bepaal ook
    `V_START`, `V_EIND` (bij enkele vers: `V_START == V_EIND`).
  - `introduction` — gebruiker vroeg expliciet om de introductie
    ("moderniseer LUK 1 introductie").
  - `epilogue` — gebruiker vroeg expliciet om de epiloog
    ("moderniseer LUK 24 epiloog").

Werkdirectory voor alle commando's: `/Users/wmotte/Desktop/projects/SVmodernisatie2026/`.

## Stap 0.5 — batch-handoff-afvang (verplicht, vóór Stap 1)

Een expliciete vers-range zoals "LUK 16:17-31" is qua werk identiek aan
"doe de volgende" — als die verzen nog niet bestaan. Inline verwerken
dumpt elke `memory.py query` / `bibref.py` / `validate.py` stdout in de
hoofd-context; over 15 verzen wordt dat onleesbaar verbose. De gebruiker
bedoelt "volgende", maar geeft de range om behulpzaam te zijn. Vang dat
af.

Bij `MODE=verses`: lees `output/<BOEK>/<BOEK>.<H>.json` (mag ontbreken).
Bepaal `done = {verse_number in output.verses}`. **Draag over aan
`sv-batch-orchestrate`** als ALLE volgende waar zijn:

- range telt **> 3 verzen** (`V_EIND - V_START + 1 > 3`);
- **geen enkel** vers in `[V_START..V_EIND]` staat al in `done`
  (volledig onafgewerkte range — geen her-modernisatie);
- `MODE` is niet `introduction`/`epilogue`.

Overdracht: roep de `Skill`-tool aan met
`skill="sv-batch-orchestrate"`, `args="<BOEK> <H> verzen <V_START>-<V_EIND>"`.
Stop daarna `sv-modernize` onmiddellijk — de orchestrator neemt het over
en verwerkt de range in batches van 3 met schone-context-subagents.

**Niet** overdragen (blijf inline) bij:
- range ≤ 3 verzen — één batch, inline kost geen extra context;
- één of meer verzen in de range bestaan al in output —
  her-modernisatie moet inline (zie orchestrator "Wanneer NIET");
- `MODE=introduction`/`epilogue`.

## Stap 1 — lees input + bestaande output

```
input.sv/<BOEK>/<BOEK>.<H>.json
output/<BOEK>/<BOEK>.<H>.json   (mag ontbreken bij eerste aanroep)
```

Invoerobject:
- `introduction` (string, altijd aanwezig).
- `verses` (array): `verse_number`, `text` (met `<kanttekeningen>` en
  `$bijbelrefs$`), `source_text` (Textus Receptus).
- `epilogue` (string, alleen in laatste hoofdstuk van een bijbelboek).

Bij `MODE=verses`: isoleer entries waar `verse_number ∈ [V_START, V_EIND]`.

### Her-modernisatie

Heraanroep voor een vers dat al in de uitvoer-JSON staat is een normale
stroom — niet een aparte trigger. "moderniseer LUK 1:1-3" werkt of het
nu de eerste keer is of niet:

- **Uitvoer-JSON**: Stap 1e doet upsert op `verse_number` (overschrijft
  het bestaande vers, behoudt andere verzen + introduction/epilogue).
- **Memory**: `memory.py add` doet upsert via `ON CONFLICT(book,
  chapter, verse) DO UPDATE` — oude embedding wordt vervangen.
- **Voorbeeldparen**: het `--exclude-book/chapter/verse`-filter in Stap 2a
  voorkomt dat het te-her-moderniseren vers zichzelf als voorbeeld
  terugziet.

Versiebeheer = git. Geen `previous_modernized` of versieteller in
de JSON.

## Stap 1b — introductie en epiloog (auto + expliciet)

**Automatische modernisering:** als de uitvoer-JSON nog niet bestaat (eerste
aanroep) of `introduction.modernized` mist, moderniseer dan automatisch
óók de introductie — ook als de gebruiker alleen om verzen vroeg. Idem
voor de epiloog als input een `epilogue` heeft.

Als modernisatie van introductie/epiloog al in de uitvoer staat: laten staan.
Alleen overschrijven bij `MODE=introduction` / `MODE=epilogue`.

### Modernisatie van introductie

```
Origineel: "1 De voorreden Luce over sijn Euangelium. 5 Zacharie ende Elisabets..."
Modern:    "1 De voorrede van Lucas over zijn Evangelie. 5 Het geslacht en leven van Zacharia..."
```

Regels:
- Versnummerverwijzingen (cijfers vooraan elke deelzin) blijven exact.
- Geen kanttekeningen, geen `$bijbelrefs$`, geen `[…]` toevoegen
  (SV1657-introducties bevatten ze niet).
- Eigennamen modern conform NBV21 (Ioannes → Johannes, Luce → Lucas,
  Zacharias → Zacharia).
- Archaïsmen weg ("ende" → "en", "sulcks" → "zulks", "voorseght" →
  "voorzegt", "d'ontfangenisse" → "de ontvangenis").
- **Hoofdletter-pattern volgen** (AGENTS.md): "Engel" blijft "Engel",
  niet "engel". Geldt voor élke SV-cap, niet alleen eerbiedshoofdletters.

### Modernisatie van epiloog

```
Origineel: "Eynde des Heyligen Euangeliums, na [de beschrijvinge] LUCAE."
Modern:    "Einde van het Heilige Evangelie, naar [de beschrijving] van LUCAS."
```

Regels:
- Vierkante haken `[…]` blijven staan (zelfde aantal, inhoud
  gemoderniseerd indien archaïsch).
- "LUCAE" (Latijnse genitief) → "LUCAS" (boekslotmarkering modern, in
  hoofdletters volgens SV-traditie).

### Geheugen bij intro/epiloog

Geen `memory.py query` en geen `memory.py add` voor introductie/epiloog —
die zijn structureel geen verzen en horen niet in de voorbeeldverzameling. Wel
valideren (zie hierna).

## Stap 2 — per-vers loop

**Belangrijk**: doe één vers per cyclus (niet alle verzen tegelijk
moderniseren en pas daarna valideren). Voordeel: vers N+1 kan vers N
als voorbeeld uit het geheugen ophalen — concordantie wint.

**Detectie**: `validate.py` heeft een `chapter_checks`-stap die faalt
als twee verzen exact dezelfde `generated_at`-timestamp delen — dat
verraadt batchmodernisatie. Bij die fout: doe het bereik opnieuw, één vers per
cyclus. Gebruik per cyclus een verse `datetime.utcnow()` in plaats van
één gedeelde timestamp.

Voor elk vers `N` in `[V_START..V_EIND]` (oplopend):

### a. Geheugenquery

```bash
uv run python scripts/memory.py query \
    --text "<originele tekst uit invoer>" --k 5 --axis sv \
    --exclude-book <BOEK> --exclude-chapter <H> --exclude-verse <N> \
    --terse
```

`--terse` laat `source_text` (Griekse brontekst) uit elke hit weg —
de voorbeeldpaar-waarde zit in `sv` + `modern`. Bespaart ~33% per call.
Bij twijfel over een Grieks lemma: herhaal zonder `--terse`.

De `--exclude-*` argumenten staan altijd aan: bij eerste modernisatie
zijn ze een no-op (vers staat nog niet in de database), bij her-modernisatie
voorkomen ze dat het vers zichzelf als voorbeeld terugziet
(zelf-bevestigend).

Lege database (`{"results": [], "total_in_db": 0}`) is OK — eerste run, ga
verder zonder voorbeeldparen. Bij gevulde database: gebruik de paren voor consistente
woordkeus en zinsbouw.

### b. Modernisatie schrijven

Volg `AGENTS.md`: archaïsme-tabel, kanttekening-conventies,
hoofdletterdiscipline (alle SV-hoofdletters bewaren, niet alleen
eerbiedshoofdletters), `[…]` bewaren, eigennamen-mapping, geen exegese
in hoofdtekst. Renovatie, geen hervertaling — formele equivalentie t.o.v.
`source_text` blijft leidend.

Pas archaïsme-substituties **niet blind** toe — herformuleer waar de
zinsbouw daarom vraagt.

**Drempelcontrole vóór je het vers wegschrijft** (zie `MODERNISATIE.md
§2.7`): loop alle inhoudswoorden langs en vraag per woord:

1. *Productiviteits-test* — gebruikt iemand dit woord nog spontaan in
   modern zakelijk/journalistiek Nederlands? "Vertoefde", "hoedanig",
   "aanschouwers", "nochtans", "alsdan" → nee → moderniseer.
2. *Constructie-test* — werkt de SV-constructie nog grammaticaal in
   modern NL? "U zult zijn naam X heten/noemen" (heten + accusatief
   van naam) werkt niet meer; herformuleer naar "u zult hem X noemen"
   of "u zult hem de naam X geven". "Waaraan zal ik dat weten" werkt
    niet (verkeerd voorzetsel); herformuleer naar "Waardoor / hoe zal
   ik dat weten". **Spiegelregel**: als de SV-constructie modern wél
   werkt, herformuleer dan **niet** naar een explicietere variant —
   ook niet als het Grieks dat suggereert of HSV het doet. Voorbeeld:
   Lk. 1:60 `hy sal Ioannes heeten` → `hij zal Johannes heten`, niet
   `genoemd worden` (Gr. `κληθήσεται` is passief, maar modern `heten`
   is productief intransitief; de explicitering is hervertaling, niet
   renovatie — zie `MODERNISATIE.md §3.1a`).
3. *Verwarringtest* — heeft het woord een dominant *andere* moderne
    betekenis (false friend)? Zo ja: zie `ARCHAISMEN.md` False friends.

Bij twijfel: kijk naar `docs/diff_LUK_*.json`. SV2027 is **niet
normatief** (hoofdletters, kanttekening-aantal, ref-formaat, intro-
stijl volgen wij ánders), maar wanneer SV2027 een woord moderner
oplost zonder zinsbouw of inhoud te wijzigen, is dat een sterk signaal
dat ons woord een conservatief-issue is.

### c. Bijbelverwijzingen normaliseren

```bash
uv run python scripts/bibref.py normalize \
    --current-book <BOEK> --include-kanttekeningen \
    "<moderne-tekst>"
```

`--include-kanttekeningen` zorgt dat ook losse verwijzingen binnen `<...>`
blokken (zoals `1.Cor. 14. vers 19.`) automatisch genormaliseerd worden
naar moderne notatie **én gewrapt in `$...$`**, net als hoofdtekst-refs.
De validator dwingt dit af als harde fout (`loose bibref in
kanttekening`). Zonder de flag doe je het met de hand. Idempotent.
Vervang de tekst in je werkbuffer door de output.

### d. Uitvoervers samenstellen

```json
{
  "verse_number": <N>,
  "original":     "<originele tekst uit invoer>",
  "modernized":   "<gemoderniseerde tekst na bibref-normalisatie>",
  "source_text":  "<source_text uit invoer, BYTE-EXACT gekopieerd>",
  "generated_at": "<UTC ISO 8601 timestamp>",
  "model":        "<agent-model-id>",
  "memory_examples_used": <aantal-uit-stap-a>,
  "notes": [<optioneel — zie hieronder>]
}
```

**`source_text` byte-exact**: kopieer rechtstreeks uit input, hertyp
nooit. SV-invoer bevat polytonische Griekse codepoints (U+1F75 ή) die door
Write-tools soms NFC-genormaliseerd worden naar monotonic (U+03AE ή).
Validator detecteert dit, maar je voorkomt het door direct kopiëren
(of een Python-helper te gebruiken die de input leest en in output zet).

**`notes`** (optioneel): array van objecten voor twijfels, bewuste
afwijkingen, of context die een beoordelaar moet zien. Schema:
```json
{"type": "twijfel"|"afwijking"|"context",
 "subject": "<korte aanduiding>",
 "context": "<waar in het vers, bv. 'kanttekening 2'>",
 "choice": "<wat ik heb gekozen>",
 "alternatives": ["<optie A>", "<optie B>"],
 "reason": "<waarom deze keus>"}
```
Alleen toevoegen wanneer er iets te melden is — niet bij elk vers.
Notes gaan **niet** in het geheugen (alleen vertaalkeuzes wel).

**Altijd lijst van objecten, nooit een losse string.** Ook voor één
enkele observatie schrijf je `"notes": [{...}]` — niet
`"notes": "v42 'meer' i.p.v. 'het meest' ..."`. Een string-notes breekt
de documentatieweergave (`notes.map is not a function`); de validator vangt
dit als HARDE fout (`_check_notes_shape`). `type` is verplicht en moet
één van `twijfel`/`afwijking`/`context` zijn — geen andere waarden.

**Geen modelmerken in notes.** De inhoud van notes-velden (`subject`,
`context`, `choice`, `reason`, `alternatives`) wordt door de
documentatieweergave onder een "Notes"-paneel getoond. Verwijs daarin nooit
naar specifieke modelnamen ("claude", "gemini", "GPT", "Opus", etc.).
Gebruik neutrale formuleringen: "het taalmodel", "de modernisatie", of
beschrijf de keuze zonder naar de keuzemaker te verwijzen. Het
metadata-veld `model` blijft wel een specifieke string voor
reproduceerbaarheid — dat veld wordt niet in de Notes getoond.

### e. Schrijf uitvoer (upsert)

Pad: `output/<BOEK>/<BOEK>.<H>.json`. Wegschrijven gaat **uitsluitend**
via `scripts/upsert_verse.py` — niet via ad-hoc Python-heredocs of
`python -c`-eenregels. Dit script:

- Leest `input.sv/<BOEK>/<BOEK>.<H>.json` voor `original` (= `text`) en
  `source_text` byte-exact (geen NFC-drift).
- Bootstrapt de output-skeleton (`book`, `chapter`, `introduction`,
  `verses=[]`, evt. `epilogue`) als het bestand nog niet bestaat.
- Upsert op `verse_number`; behoudt andere verzen + intro/epiloog.
- Zet `generated_at` op een verse UTC ISO-8601-timestamp.
- Schrijft met `ensure_ascii=False`, **2-space indent** en afsluitende
  newline — zonder dat jij dat met de hand moet regelen.

Subcommands:

```bash
uv run python scripts/upsert_verse.py verse \
    --book <BOEK> --chapter <H> --verse <N> \
    --modernized "<gemoderniseerde tekst na bibref>" \
    --examples <K_uit_stap_a> \
    [--notes-json '[{"type":"...", "subject":"...", ...}]']

uv run python scripts/upsert_verse.py intro \
    --book <BOEK> --chapter <H> --modernized "<tekst>"

uv run python scripts/upsert_verse.py epilogue \
    --book <BOEK> --chapter <H> --modernized "<tekst>"
```

Stdout is één regel: `UPSERT <BOEK> <H>:<V> ok`. Exit non-zero bij fout
(vers buiten range, JSON-parse-fout in `--notes-json`, etc.). Doe één
upsert per vers, direct na de modernisatie; niet alle verzen
batch-gewijs aan het eind.

**Strikt verboden:** zelf JSON wegschrijven met
`json.dump`/`json.dumps` via een heredoc of inline-script. Dat
veroorzaakt indent-mismatches (1300-regel diffs), NFC-normalisatie van
de polytonische Griekse `source_text`, en ~20 regels ruis per vers in
de subagent-log. Het script bestaat exact om dat te voorkomen.

### f. Valideer dit vers

```bash
uv run python scripts/validate.py check \
    --input input.sv/<BOEK>/<BOEK>.<H>.json \
    --output output/<BOEK>/<BOEK>.<H>.json \
    --verses <N> \
    --sections intro,epilogue \
    --terse                       # alleen op de eerste vers van de loop, of bij MODE=intro/epilogue
```

`--terse` levert 1 statusregel + 1 regel per fail (compact tekstformaat
ipv. JSON; spaart orchestrator-context). Bij twijfel laat `--terse` weg
voor volledige JSON.

- Statusregel begint met `PASS` → ga door naar (g).
- Statusregel begint met `FAIL` → lees fail-regels, corrigeer
  modernisatie, herhaal (e) + (f). Maximaal 3× per vers. Daarna:
  schrijf het vers toch weg, sla (g) over, rapporteer issue in
  eindrapport.

**Harde fouten** (validatiefout):
- aantal `<...>` blokken < origineel
- aantal `[...]` blokken ≠ origineel
- archaïsme uit blacklist in hoofdtekst (`ende`, `ghy`, `daer`, etc.)
- bijbelref niet in modern formaat
- losse bijbelverwijzing binnen `<kanttekening>` (alle refs moeten in `$...$`)
- `source_text` semantisch gewijzigd (NFC-vergelijking)
- **hoofdletter-discipline**: SV-cap met andere case in modernisatie
  (bv. "Engel" → "engel" — moet "Engel" blijven)

**Waarschuwingen** (passeren wel, melden in eindrapport):
- hoofdletter-woord helemaal afwezig (zin geherformuleerd, vaak bewust)
- `source_text` byte-anders maar NFC-equivalent (kopieer-fout)

### g. Voeg toe aan het geheugen

```bash
uv run python scripts/memory.py add --from-output output/<BOEK>/<BOEK>.<H>.json --verse <N> --terse
```

`--terse` levert één regel `<BOEK> <H>:<N> -> <total>` ipv. een JSON-blok.

`--from-output` voorkomt shell-quoting voor lange teksten met
kanttekeningen. Upsert op `(book, chapter, verse)`.

Doe dit **direct na een gepasseerd vers** zodat het volgende vers in de
loop al in de voorbeeldverzameling zit (concordantie!).

## Stap 3 — slotvalidatie + carry-over-linter

Draai de hele set nog eens:

```bash
uv run python scripts/validate.py check \
    --input input.sv/<BOEK>/<BOEK>.<H>.json \
    --output output/<BOEK>/<BOEK>.<H>.json \
    --verses <V_START>,...,<V_EIND> \
    --sections intro,epilogue \
    --terse
```

Daarna **carry-over-linter** — vangt grensgevallen van archaïsmen die de
blacklist mist (zoals "Doch", "nochtans", "alsdan", participia als
"hebbende"):

```bash
uv run python scripts/lint_carryovers.py lint \
    --output output/<BOEK>/<BOEK>.<H>.json \
    --verses <V_START>,...,<V_EIND> \
    --terse
```

`--terse` geeft één regel: `lint N candidates: word1(v3) word2(v1,v5) ...`
(of `lint 0 candidates (...)` als alles schoon is).

Per gerapporteerd kandidaat-woord drie opties:
1. **Echt archaïsme** → modernisatie aanpassen, woord op
   `validate.py` blacklist + AGENTS.md archaïsme-tabel zetten.
2. **Legitieme carry-over** (eigennaam, theologische term, gewoon Nederlands
   woord) → toevoegen aan `STOPLIST` in `lint_carryovers.py`.
3. **Bewuste twijfel** (zoals "Hebr." in V2) → opnemen in `notes`
   veld van het vers.

Tip: de linter zonder argumenten doorzoekt het hele hoofdstuk, niet alleen
deze batch — handig voor consistentiecontroles na meerdere modernisatie-
sessies in hetzelfde hoofdstuk.

## Stap 4 — eindrapport

Eindrapport (2-4 regels):
```
LUK 1:1-3 + introductie gemoderniseerd. 4/4 gepasseerd, 0 fails, 2 warnings.
Memory: 3 toegevoegd (totaal nu 47). Lint: alleen 'hebr' als bekende twijfel.
Twijfel: vers 2 — opgenomen als note in output JSON ('Hebr.'-abbreviatie).
```

Geen lange uitleg. Output-JSON spreekt voor zich.

## Foutgevallen

- `input.sv/<BOEK>/<BOEK>.<H>.json` bestaat niet → meld pad en stop.
- Vers-nummer buiten range → meld beschikbare nummers en stop.
- `memory.py` faalt op `GOOGLE_API_KEY` → meld dat `.env` ontbreekt.
- Validate faalt 3× op hetzelfde vers → schrijf vers weg, **niet** in
  memory, rapporteer expliciet welke issue blijft staan.
