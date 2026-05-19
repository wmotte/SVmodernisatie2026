# SVmodernisatie2026 — Statenvertaling 1657 (2e druk)

## Projectdoel

Modernisering van de Statenvertaling 1657 met **maximaal behoud van de
eigenheid** van de SV: theologische precisie, formele equivalentie t.o.v.
de brontekst, kanttekeningen, vierkante haken voor toevoegingen door de
SV-vertalers, en hoofdletterdiscipline. Eerste focus: **Lucas** (24
hoofdstukken; de invoer staat klaar in `input.sv/LUK/`).

> **Wat is "modernisatie" in dit project?** Voor de definitie, methode en
> aannames die onder dit hele project liggen: zie `MODERNISATIE.md`.
> Bij twijfel over reikwijdte of vertaalkeuze is dat document leidend.

## Hoe doet de gebruiker een aanroep?

Twee aanroepvormen, elk met een eigen skill:

**1. Expliciete vers-range** → `sv-modernize` (inline in deze conversatie)

- "moderniseer LUK 1:1-3"
- "moderniseer Lucas 1 vers 1 t/m 3"
- "moderniseer LUK 1 introductie" / "moderniseer LUK 24 epiloog"

**2. Impliciet "de volgende"** → `sv-batch-orchestrate` (orchestrator
start een modernisatie-subagent met schone context per batch)

- "moderniseer de volgende drie verzen"
- "ga door met de volgende batch"
- "doe de volgende drie"

Boekcode is altijd 3-letterig conform de bestandsnamen in `input.sv/`:
`LUK`, `MAT`, `MRK`, `JHN`, `ACT`, `ROM`, `HEB`, etc. Het `book`-veld in
de invoer-JSON kan afwijken (bv. `LUCA`); leidend zijn de bestandsnamen.

## Architectuur

Bij vorm 1 doet één agent-model het hele werk inline. Bij vorm 2
start de hoofdagent (orchestrator) per batch een verse modernisatie-
subagent — schone context, één batch, klaar — en doet daarna kritische
beoordeling + commit + PR + merge per batch totdat het hoofdstuk klaar is.

| Skill                   | Wanneer aanroepen                              |
|-------------------------|-------------------------------------------------|
| `sv-modernize`            | Expliciete vers-range, intro of epilogue.       |
| `sv-batch-orchestrate`    | "Volgende drie verzen" — orchestreert subagent. |
| `sv-memory`               | Vóór modernisatie van elk vers (voorbeeldparen) |
|                           | en ná modernisatie (toevoegen aan vectordatabase). |
| `sv-bibref`               | Voor elke `$...$` verwijzing in de moderne      |
|                           | tekst.                                          |
| `sv-validate`             | Ná het schrijven van de uitvoer-JSON, vóór de   |
|                           | memory-add. Bij fout: corrigeer en herhaal.     |
| `sv-semantic-review`      | In batch-flow ná validator + linters (Stap 3.6).|
|                           | False friends, idiomatische mismatches,         |
|                           | concordantie-twijfel, HSV-spiegel. Stap 3.7     |
|                           | doet flag-arbitrage: kan regex-kwetsbare        |
|                           | validatorflags (hoofdletterdiscipline,          |
|                           | §2.3-participium) overrulen met motivatie.      |
| `sv-adversarial-review`   | Strenge bevindingenlijst per hoofdstuk. Auto na |
|                           | CHAPTER_COMPLETE, of expliciet ("review         |
|                           | hoofdstuk 8"). Uitgangspunt = overtreding; weerleggingen |
|                           | moeten regel/Grieks-referentie hebben.          |
| `sv-meta-review`          | Meta-adversariële review over alle HSV-diffs    |
|                           | van een afgesloten boek/range. Aggregeert       |
|                           | cross-chapter patronen (carryover, fossiel-     |
|                           | lidwoord, latinaat-window, cap-asym) via        |
|                           | `scripts/meta_diff_aggregate.py`, classificeert |
|                           | A/B/C (noise/per-vers-fix/scaffolding-gap), en  |
|                           | kan apply-modus draaien (3b regel-deltas PR, 3a |
|                           | per-hoofdstuk content-fixes). Trigger: "meta-   |
|                           | review LUK" / "meta-review LUK apply".          |

## Vertaalprincipes (samenvatting)

Volledige tekst: `research/vertaalprincipes.txt`. Praktisch:

1. **Renovatie, geen hervertaling.** De SV-eigenheid blijft staan; we
   poetsen alleen de archaïsche schil weg.
2. **Formele equivalentie.** De `source_text` (Textus Receptus voor het
   NT) blijft leidend voor zinsbouw en woordkeus. Geen vrije
   parafrase, geen modernisering van theologische ladingen.
3. **Concordantie.** Hetzelfde Griekse woord → zoveel mogelijk
   hetzelfde Nederlandse woord. De vectordatabase (memory) helpt dit door
   eerdere vertaalkeuzes terug te halen — gebruik die keuzes consequent.
4. **Geen exegese in de hoofdtekst.** Alle interpretatie blijft binnen
   `<kanttekening>`-blokken. Voeg geen informatie uit een kanttekening
   toe aan de hoofdtekst.
5. **Hoofdletter-discipline.** Voeg NOOIT eerbiedshoofdletters toe (de
   SV doet dat namelijk wisselend en doelbewust). Verwijder ze ook
   niet. Patroon van het origineel volgen voor **alle** SV-hoofdletters, niet
   alleen eerbiedshoofdletters: "Engel" blijft "Engel", "Apostelen"
   blijft "Apostelen", "Christelicke Kercke" wordt "Christelijke Kerk"
   (hoofdletters op beide). Geldt zowel in hoofdtekst als binnen
   `<kanttekeningen>` — "Leeraers" wordt "Leraars", niet "leraars".
   **Uitzondering 1 — initiaalhoofdletters aan vers- of zinsbegin:**
   SV-typografische drop-caps (`NAdemael`, `IN de dagen`, `DE Sone Godts`)
   tellen niet als SV-hoofdletters; dat is een drukkersconventie van 1657.
   Modern Nederlands gebruikt zinsstijl: `Aangezien`, `In de dagen`, `De
   Zoon van God`.

   **Uitzondering 2 — ALL-CAPS mid-zin op heilige namen / auteursaanduiding:**
   SV-druk zet bepaalde eigennamen mid-zin in volledige kapitalen
   (`CHRISTI JESU`, `IEHOVAH`) of in brief-opener / colofon van een
   Sendtbrief de naam van de auteur (`PAULUS ... een gevangen CHRISTI JESU`;
   `Eynde van den Sendtbrief PAULI aen Philemon`). Dat is óók een
   drukkersconventie en wordt in modern Nederlands gewone zinsstijl:
   `Christus Jezus`, `Paulus`. Geldt zowel in vers-tekst als in epiloog/
   colofon. De naamvorm wordt daarbij wèl gemoderniseerd (genitief `PAULI`
   → nominatief `Paulus`, `IESU CHRISTO` → `Jezus Christus`).

   De validator markeert hoofdletterwisselingen als harde fout (apart op
   hoofdtekst en kanttekeningen).
6. **Vierkante haken `[…]` markeren toevoegingen** door de SV-vertalers
   (woorden niet in de Griekse brontekst). **Bewaar ze exact** — zelfde
   aantal, zelfde inhoud (tenzij de inhoud zelf een te-moderniseren
   archaïsme is, dan moderniseer je binnen de haken).

## Archaïsme-tabel

> **Volledige tabellen:** zie `ARCHAISMEN.md` (archaïsme-substituties +
> eigennamen-mapping NBV21).

Kort overzicht van de meest voorkomende substituties: `ende` → `en`,
`ghy/gy/gij` → `u`, `hy` → `hij`, `sy` → `zij`, `haer` → `haar`,
`onse` → `onze`, `daer` → `daar`, `soo` → `zo`, `dese/desen` → `deze`,
`welcke` → `welke`, `Doch` → `Maar`, `Sone` → `Zoon`. Eigennamen volgen
NBV21 (`Iesus` → `Jezus`, `Ioannes` → `Johannes`, etc.).

Geen letterlijke vervanging als de zinsbouw eronder lijdt; herformuleer
de zin zodat hij modern Nederlands oplevert.

## Kanttekening-conventies

> **Volledige conventies:** zie `KANTTEKENINGEN.md` (afkortingen-tabel
> + redundantie-regel).

Kern: `<…>` blokken **bewaren** (nooit verwijderen, nooit samenvoegen).
Aantal in de modernisatie ≥ aantal in het origineel. Standaard-vertalingen:
`<D. ...>` → `<dat is, ...>`, `<Gr. ...>` → `<Grieks: ...>`,
`<Hebr. ...>` → `<Hebreeuws: ...>`, `<Namelick, ...>` → `<Namelijk, ...>`,
`<Ofte, ...>` → `<Of, ...>`, `<Siet ...>` → `<Zie ...>`. Geen
redundantie tussen kanttekening en hoofdtekst.

## Bijbelverwijzingen

> **Volledig formaat + voorbeelden:** zie `BIJBELVERWIJZINGEN.md`.

Formaat na normalisatie: `$Boek H:V$`, `$Boek H:V,W$`, `$Boek H:V-W$`, of
samengesteld `$Boek H:V; H:W$` (boeknaam alleen bij wisseling). De
`sv-bibref` skill (wrapper rond `scripts/bibref.py`) doet de conversie,
inclusief losse verwijzingen binnen kanttekeningen via
`--include-kanttekeningen`.

**Geen sluitpunt na `$...$`:** SV1657 zet de terminator-punt binnen het
bibref-blok (`Luce 7.27.$`). In de modernisering eindigt het `$...$`-blok
zonder externe punt erbuiten — dus `… $Lk. 7:27$ Zie, ik zend …`, niet
`… $Lk. 7:27$. Zie, …`. Een renderer toont `$...$` als
superscript-letter, dus een spurieus extern punt levert `, a.` op in de
gerenderde tekst. `validate.py` check 4c vangt dit.

## Introductie en epiloog

> **Volledige regels:** zie `INTRO_EPILOOG.md`.

Kern: elk hoofdstukbestand heeft een `introduction`-veld; het laatste
hoofdstuk van een bijbelboek heeft daarnaast een `epilogue`-veld. Beide
worden gemoderniseerd volgens dezelfde principes als verzen
(archaïsmen, eigennamen, vierkante haken behouden), maar bevatten geen
kanttekeningen of `$bijbelrefs$`. Intro en epiloog gaan **niet** in de
vectordatabase (memory).

De gebruiker kan ze ook gericht aanvragen:
- "moderniseer LUK 1 introductie"
- "moderniseer LUK 24 epiloog"

## Output JSON-schema

> **Volledig schema + incrementeel gedrag + notes-conventies:** zie
> `OUTPUT_SCHEMA.md`.

Pad: `output/<BOEK>/<BOEK>.<H>.json`. Velden op hoofdniveau: `book`,
`chapter`, `introduction`, `verses`, `epilogue` (laatste alleen bij
boek-eind). Per vers: `verse_number`, `original`, `modernized`,
`source_text` (byte-exact uit input!), `generated_at`, `model`,
`memory_examples_used`, optioneel `notes`. **Incrementeel**: nieuwe
aanroepen voegen toe aan `verses` op `verse_number`-key (upsert), zonder
eerdere verzen aan te raken.

## Kalibratie tegen externe modernisaties (HSV + SV2027)

In `docs/` staan versgewijze vergelijkingen tussen onze modernisatie
en externe parallel-vertalingen. De **HSV (Herziene Statenvertaling)**
is boek-agnostisch beschikbaar en levert `docs/diff_hsv_<BOEK>_<H>.json`
— dit is de **in-loop spiegel** die `sv-semantic-review` Stap 2.5
gebruikt tijdens elke batch. Voor Lucas staat daarnaast SV2027 /
"Initiatief 2027" in `docs/diff_LUK_*.json` en
`docs/diff_all_LUK_*.json`, maar **alleen als post-hoc kalibratie-
archief**; SV2027 wordt buiten Lucas niet uitgegeven en niet meer in
de batch-pipeline gebruikt.

Beide parallelvertalingen zijn **niet normatief**. Ze maken andere keuzes voor
hoofdletters, kanttekening-aantal, intro-stijl, en parafrase-
vrijheid die wij niet overnemen. **HSV is bovendien vrijer dan
SV2027**: zij heeft regelmatig exegese in de hoofdtekst (subject of
object invullen, verklarende bijvoeglijke naamwoorden), eigen
kanttekeningen `<HSV: …>` / `<HSV-aant: …>` (die geen SV-kanttekening-
bewijs zijn), incidentele eerbiedshoofdletters, en herstructurering
van Latijns aandoende participia. Daarom heeft de HSV-spiegel strengere
waarborgen: HSV-bewijs alléén is nooit genoeg voor een wijziging — een
bevinding moet onafhankelijk verifieerbaar zijn tegen SV1657 + Grieks.
Zie `MODERNISATIE.md §2.7` en `sv-semantic-review` Stap 2.5 / 3
categorie 4 voor het volledige protocol.

Concreet: gebruik HSV/SV2027 **niet** om de eigen modernisatie naar
HSV/SV2027 toe te trekken op hoofdletters, verwijzingsformaat,
kanttekening-omvang, exegese-toevoegingen, structurele herbouw of
parafrase. Gebruik ze **wel** als bewijsbasis bij twijfel over
drempel-archaïsmen en aantoonbare lexicale of grammaticale fouten —
een handvol verzen verschil op één pagina kan latente archaïsmen
blootleggen ("vertoefde", "hoedanig", "aanschouwer").

## Stopregels

- Doe alleen wat gevraagd is. "Moderniseer LUK 1:1-3" = drie verzen,
  niet het hele hoofdstuk.
- Geen ongevraagde herstructurering van scripts of skills.
- Bij twijfel over een vertaalkeuze: noem de twijfel kort in het
  eindrapport en stop niet, kies een redelijke optie en ga door.
- Bij een hard validatie-issue: corrigeer en herhaal validate; doe dat
  maximaal 3× per vers, dan rapporteer je de resterende issue en stop
  voor dat vers.
- **Uitzondering binnen `sv-batch-orchestrate`-flow**: de orchestrator
  loopt autonoom door batch-cycli (push → PR → merge → volgende batch)
  totdat het hoofdstuk klaar is, of stopt na één nieuwe poging bij een
  harde blokker. Zie `GIT_WORKFLOW.md` orchestrator-uitzondering.

## Compactie-instructies

Geldt voor zowel automatische compactie (de agent-CLI knipt zelf context als de
limiet nadert) als handmatig `/compact <focus>`. De orchestrator geeft
na elke merge een `[COMPACT-HINT]`-regel; gebruiker kan dan handmatig
`/compact` typen als de context boven ~150k loopt. Wat moet **blijven**
bestaan na compactie:

- Actief `<BOEK> <H>` en de laatste batch-grenzen (`V_START-V_EIND`).
- Per voltooide batch in deze sessie: PR-URL + validator-verdict (1
  regel).
- Eventuele regelbestandwijzigingen die in deze sessie zijn toegepast
  (`STOPLIST`-uitbreidingen, `ARCHAISMEN.md`-entries) — 1 regel per
  delta, met motivatie.
- Lopende blokkers of openstaande adversarial-issues — 1 regel per
  item.
- Huidige worktree-pad / branch-naam.
- Eindrapport-fragmenten die al geschreven zijn.
- Synchronisatiestatus van de geheugen-DB (clean/dirty-aantallen), niet de volledige JSON.

Wat **mag weg**:

- Volledige bash-stdout van `validate.py`, `lint_*.py`, `memory.py
  query`, `compare_sv2027.py`.
- Volledige `git diff`, `git status`, `git log` outputs.
- Volledige output-JSON-inhoud (alleen vers-nummers + verdict bewaren).
- Volledige memory-query-resultaten (alleen het aantal volstaat).
- Volledige `gh pr create` / `gh pr merge` stdout — alleen de PR-URL.
- Subagentrapporten — alleen 1-regelverdict per batch bewaren.
- Eerdere `sv-semantic-review`- en `sv-adversarial-review`-protocols;
  alleen de uitkomst (fixes vs. weerleggingen + aantallen) bewaren.

Vuistregel bij `/compact`: schrijf in de focus-string "behoud per-batch
PR-links, validate-verdict, regelbestandwijzigingen; gooi verbose tooluitvoer
weg".

## Git-workflow

Voor commits, push, PR's en merges: zie `GIT_WORKFLOW.md` (feature
branches vanuit `main`, geen agent-attributietrailers, push-en-stop-patroon,
PR/merge alleen op expliciete vraag — behalve binnen orchestrator-
flow, waar push → PR → merge per batch autonoom mag).

## Parallelle agent-sessies — worktrees + clash

Voor het naast elkaar draaien van meerdere agent-sessies op
deze repo (zonder dat ze elkaars feature branches of memory-DB
corrumperen): zie `WORKTREE_WORKFLOW.md`. Kort: gebruik
`scripts/wt.sh new <suffix>` voor een nieuwe worktree (sibling-dir
met gedeelde `memory/`-symlink), en `clash status` om conflicten
tussen worktrees te detecteren. Vuistregel: **één worktree per
hoofdstuk** — verschillende boeken/hoofdstukken parallel mag,
twee batches uit hetzelfde hoofdstuk niet.

## Setup (eenmalig per nieuwe machine)

```bash
cd /Users/wmotte/Desktop/projects/SVmodernisatie2026
uv sync
cp .env.example .env   # vul GOOGLE_API_KEY in
```

Daarna kan elke aanroep direct.
