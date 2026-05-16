---
name: sv-batch-orchestrate
description: Orchestrator voor de SV-modernisatie. Activeer wanneer de gebruiker zegt "moderniseer de volgende drie verzen" of vergelijkbaar (zonder expliciete vers-range). Wordt ook aangeroepen als afvang door sv-modernize wanneer een expliciete maar volledig-onafgewerkte vers-range groter dan 3 verzen blijkt. Detecteert het volgende blok van 3 verzen, start een modernisatie-subagent met schone context die sv-modernize uitvoert, evalueert kritisch, doet evt. aanscherpingen van regelbestanden, en commit+pusht+PRt+mergt per batch naar main — totdat het hoofdstuk (of de doorgegeven range) klaar is.
---

# sv-batch-orchestrate — orchestrator-protocol

Activeer dit protocol bij elke aanroep waarin de gebruiker vraagt om
"de volgende drie verzen" zonder expliciete vers-range op te geven —
bijvoorbeeld "moderniseer de volgende drie verzen", "ga door met de
volgende batch", "doe de volgende drie".

**Verantwoordelijkheid van de orchestrator (= jij, hoofdagent in deze
conversatie):** detecteren → starten → beoordelen → git → herhalen. **Niet** zelf
modernisteren — dat doet de subagent met schone context.

Werkdirectory voor alle commando's: de **huidige repositoryhoofdmap**, te
bepalen via `git rev-parse --show-toplevel`. Bij een directe sessie
in de hoofdrepository is dat `/Users/wmotte/Desktop/projects/SVmodernisatie2026/`.
Bij een sessie in een worktree (zie `WORKTREE_WORKFLOW.md`) is dat
`/Users/wmotte/Desktop/projects/SVmodernisatie2026.wt/<suffix>/`. Alle
git-acties, scripts en het starten van de subagent gebruiken dit pad.

## Pre-flight bij parallelle sessies

Als er meerdere agent-sessies op deze repository draaien (worktrees),
draai vóór Stap 0:

```bash
clash status
```

Toont een andere worktree die aan dezelfde `output/<BOEK>/<H>.json`
werkt? Stop en kies een ander hoofdstuk, of wacht tot die worktree
klaar is. Vuistregel: één worktree per hoofdstuk. Geen melding =
veilig om door te gaan.

## Stap 0 — bepaal het actieve hoofdstuk

**Doorgegeven range (afvang vanuit `sv-modernize`).** Is deze skill
aangeroepen met `args="<BOEK> <H> verzen <V_START>-<V_EIND>"`? Sla de
detectie hieronder over: gebruik die `<BOEK> <H>` direct, en zet
`V_CEIL = <V_EIND>` in Stap 1 — dat plafond zorgt dat nooit verzen
`> V_EIND` worden opgepakt. De hoofdlus stopt zodra alle verzen
`≤ V_EIND` klaar zijn (`CHAPTER_COMPLETE` = "range klaar", niet per se
hoofdstukeinde). Sla Stap 6.5 (adversarial pass) over tenzij de range
tot het laatste vers van het hoofdstuk loopt — een gedeeltelijk
hoofdstuk review je niet adversarieel.

Zonder expliciete `<BOEK> <H>` van de gebruiker: gebruik het laatst
actieve hoofdstuk uit `output/`. Heuristiek:

```bash
ls output/*/ -t | head -1   # meest recent gewijzigd boek
```

en daarbinnen het bestand met de hoogste `<H>` dat **niet volledig is**
(`len(verses) < len(input.verses)`). Als alleen `LUK/LUK.1.json`
bestaat: dat is het actieve hoofdstuk. Bij ambiguïteit: vraag de
gebruiker, anders ga door.

## Hoofdlus — itereer tot hoofdstuk klaar

Per iteratie:

### Stap 0.5 — synchroniseer de geheugen-DB

Vóór elke batch: zorg dat de vectordatabase consistent is met de huidige
uitvoer-JSON's. Remodernisaties, semantic-review-wijzigingen en handmatige
correcties kunnen de DB verouderd maken; voorbeeldselectie zou dan oude paren
ophalen — wat het concordantie-doel van de DB teniet doet.

```bash
uv run python scripts/memory.py sync --root output/ --terse
```

Detectie via tekstvergelijking (`original`, `modernized`, `source_text`
per vers JSON↔DB). Alleen verschillen worden opnieuw geëmbed via
de embeddings-service (nu Gemini, verwisselbaar via `scripts/memory.py`).

Verwacht resultaat (`--terse` regel: `sync <N>v <C>c <D>d <M>m <O>o api=<N>`):
- `c == v`, `d == 0`, `m == 0`, `api == 0`: alles consistent, ga door
  naar Stap 1.
- `d > 0` of `m > 0`: sync embedt automatisch opnieuw (2 API-aanroepen
  per vers). Wacht tot dit klaar is (synchroon), ga dan door naar Stap 1.
- `o > 0`: de database heeft items waar geen uitvoer-JSON-vers bij hoort
  (bv. file-rename, branch-checkout). Niet auto-deleted — onthoud
  voor het eindrapport, ga door.
- Exitcode ≠ 0: blokker (embeddings-API onbereikbaar, corrupte JSON in output/).
  Stop de hoofdlus, rapporteer. Laat `--terse` weg voor `details`-payload.

### Stap 1 — detecteer de volgende 3

Eén Bash-regel (`--ceil` alleen bij doorgegeven range uit Stap 0; anders weglaten):

```bash
uv run python scripts/next_batch.py --book LUK --chapter 17 --ceil 18
```

Uitvoer is precies één regel: `NEXT=<V_START>-<V_EIND>` of `CHAPTER_COMPLETE`.

- `CHAPTER_COMPLETE` → ga naar **Eindrapport**, stop de hoofdlus. (Bij
  een doorgegeven range betekent dit "range klaar", niet per se
  hoofdstuk klaar.)
- `NEXT=V_START-V_EIND` → ga door naar stap 2 met deze grenzen.

### Stap 2 — start modernisatie-subagent

**Pre-flight: maak de batch-branch.** De modernisatie-subagent werkt op
de actieve branch en mag géén git-acties doen, dus de orchestrator
moet de branch zelf klaarzetten vanaf verse `origin/main`. Dit
voorkomt vuile werkbomen bij branchwissels en is verplicht
binnen worktrees (een worktree zit nooit op `main`).

```bash
scripts/mkbatch.sh <boek-lowercase> <H> <V_START> <V_EIND>
```

Het script bepaalt de branch-naam (`feature/<boek><H>-batch-<V_START>-<V_EIND>`,
suffix `-modernize` bij remote-collisie), fetcht `origin/main` en checkt
de branch uit. Uitvoer is één regel `BRANCH=<naam>`. Onthoud `$BRANCH`
voor Stap 5 — de git-subagent krijgt 'm mee.

**Start de modernisatie-subagent.** Roep de `Agent`-tool aan met:

- `subagent_type: "general-purpose"`
- `model: "opus"` — **dwingend**: het hoofdmodel, niet een lichter model.
- `run_in_background: false` — resultaat is nodig voor beoordeling.
- `description: "Moderniseer <BOEK> <H>:<V_START>-<V_EIND>"`
- `prompt`: een korte instructie die naar het template-bestand verwijst —
  zie **Subagent-prompts** onderaan.

De subagent schrijft naar `output/<BOEK>/<BOEK>.<H>.json` via
`scripts/upsert_verse.py` (verplicht; geen ad-hoc heredocs) en voegt
toe aan de memory-DB. Rapport is **max 2 regels**, gestructureerd:

```
DONE <BOEK> <H>:<V_START>-<V_EIND> verses=<N> validator=<PASS|FAIL_v<X>> lint=<0|N> notes=<0|N>
[BLOCKER: <vers + issue>]   # alleen bij hard residu
```

De orchestrator leest enkel deze twee regels:
- `validator=PASS` zonder `BLOCKER` → door naar Stap 3.
- `validator=FAIL_v<X>` of regel-2 `BLOCKER:` → ga naar Stap 4
  (foutpad). De BLOCKER-issuetekst wordt de retry-prompt-input.

### Stap 3 — kritische beoordeling (via review-subagent)

De orchestrator delegeert de hele beoordeling aan een **review-subagent**
met schone context. Reden: validator + 3 linters stdout + het
`sv-semantic-review`-protocol (dat zich anders ín de orchestrator-context
laadt) + memory-queries + HSV-diff-regeneratie zijn samen ~10-20k tokens
per batch; over een hoofdstuk van 25+ batches loopt de orchestrator-
context vol. Zelfde delegatiepatroon als Stap 2 (moderniseren) en Stap 5
(git). De onafhankelijkheid van de beoordeling blijft intact — de
review-subagent is een andere, schone-context-agent dan de modernisatie-
subagent.

**Spawn de review-subagent.** Roep de `Agent`-tool aan met:

- `subagent_type: "general-purpose"`
- `model: "opus"` — **dwingend**: `sv-semantic-review` is inhoudelijk
  oordeelswerk; het hoofdmodel, niet een lichter model.
- `run_in_background: false` — orchestrator heeft het verdict nodig voor
  Stap 4/5.
- `description: "review <BOEK> <H>:<V_START>-<V_EIND>"`
- `prompt`: een korte instructie die naar het template-bestand verwijst —
  zie **Subagent-prompts** onderaan.

**Verwachte uitvoer** (6 regels, niets anders):

```
VALIDATOR: <verdict-regel van validate.py --terse>
LINT: <1-regel samenvatting carryovers/archaismen/false-friends>
SEMANTIC: <per gewijzigd vers 1 frase; of "geen actie">
HSV-SPIEGEL: <1 regel uitkomst; of "geen bestand">
REGELBESTAND: <STOPLIST/ARCHAISMEN-delta's met motivatie; of "geen">
BLOKKER: <nee | ja — vers <N>: <issuetekst>>
```

De orchestrator leest **alleen de `BLOKKER`-regel** voor zijn beslissing:

- `BLOKKER: nee` → door naar Stap 5 (commit).
- `BLOKKER: ja — ...` → door naar Stap 4 (foutpad).

De review-subagent heeft de flag-arbitrage (`sv-semantic-review` Stap
3.7) al verwerkt: validator-hardfouten in `hoofdletter-discipline` of
`§2.3-participium` die de arbiter als `overruled` markeerde, staan
**niet** in de `BLOKKER`-regel. Andere harde fouten (kanttekeningen,
vierkante haken, bibref-formaat, archaïsme-blacklist, source_text) staan
er altijd wél in.

Bewaar de `REGELBESTAND`-, `SEMANTIC`- en `HSV-SPIEGEL`-regels voor het
eindrapport.

### Stap 4 — foutpad (alleen bij `BLOKKER: ja`)

Eén nieuwe poging, daarna stop. De review-subagent heeft de flag-
arbitrage al verwerkt — de `BLOKKER`-regel is post-arbitrage, dus elke
daarin genoemde blokker is echt en vereist actie.

- Spawn de modernisatie-subagent opnieuw via de Agent-tool met
  **scherpere prompt**: voeg toe: "Vorige poging faalde op vers <N>.
  Issue: <issuetekst uit de BLOKKER-regel>. Pak deze gericht aan,
  schrijf opnieuw, valideer."
- Draai daarna opnieuw Stap 3 (review-subagent) op de batch.
- Als de nieuwe poging óók `BLOKKER: ja` geeft: stop de hoofdlus. Eindrapport vermeldt:
  - Welk vers blokker is
  - Welke issue blijft staan
  - Welke verzen wél succesvol waren
  - Géén commit voor deze batch (vermijd halve state op main)

### Stap 5 — commit + push + PR + merge (via git-subagent)

Alleen als de batchbeoordeling groen is. De orchestrator delegeert het hele
git-ceremonieel (statuscontrole, diffcontrole, add, commit, push, PR,
merge) aan een **git-subagent** met schone context. Reden:
`gh pr create` + `gh pr merge` + `git push` produceren samen ~5-10k
tokens stdout per batch; over een hoofdstuk van 25+ batches is dat
significant. De orchestrator zelf ontvangt alleen een 3-regel-rapport
terug.

**Branch-naam bepalen** (door orchestrator, want batch-branch is óók al
in Stap 2 vóór de modernisatie-subagent aangemaakt): standaardpatroon
`feature/<boek-lowercase><H>-batch-<V_START>-<V_EIND>`. Bij collisie
met een bestaande remote branch: suffix `-modernize`. De pre-flight
voor de modernisatie-subagent maakt deze branch al — zie Stap 2.

**Spawn de git-subagent.** Roep de `Agent` tool aan met:

- `subagent_type: "general-purpose"`
- `model: "sonnet"` — mechanisch git-werk; het secundaire (goedkopere)
  model volstaat en is goedkoper dan het hoofdmodel.
- `run_in_background: false` — orchestrator heeft de uitkomst direct
  nodig voor Stap 6.
- `description: "git: commit+push+PR+merge <BOEK> <H>:<V_START>-<V_EIND>"`
- `prompt`: een korte instructie die naar het template-bestand verwijst —
  zie **Subagent-prompts** onderaan.

**Verwachte uitvoer** (3-4 regels, niets anders):

```
BRANCH: <branch-naam>
PR: <github-pr-url>
MERGED: yes
SHA: <commit-sha>
```

Bij mislukte merge: `MERGED: no — <reden>`; behandel als blokker
(failure-pad in Stap 4 is hier niet van toepassing — er is niets te
re-modernisteren — meld het in het eindrapport en stop de hoofdlus).

Bij `git diff --stat` méér dan ~50 regels op `output/<BOEK>/<BOEK>.<H>.json`
voor 3 verzen: de subagent reformatteert zelf naar 2-space-indent vóór
commit en vermeldt dat in de uitvoer (`REFORMATTED: yes`).

### Stap 6 — compact-hint + loop

**Emit één compact-hint regel** vóór de volgende iteratie zodat de
gebruiker (die meekijkt) zelf kan beslissen om `/compact` te typen
wanneer context groeit. De assistant kan `/compact` namelijk niet zelf
triggeren — slash commands zijn user-side. Format:

```
[COMPACT-HINT] batch <V_START>-<V_EIND> gemerged (PR <url>). Voltooid <N>/<TOTAAL> verzen in <BOEK> <H>. Typ `/compact behoud per-batch PR-links, validate-verdict, regelbestandwijzigingen; gooi verbose tool-uitvoer weg` als context > ~150k.
```

Print precies deze regel als gewone tekst (geen tool-call). De
orchestrator pauzeert **niet** — hij gaat direct door naar de volgende
iteratie. De compact-instructies in `AGENTS.md` zorgen dat zowel
handmatige als auto-compactie het juiste behoudt.

Terug naar **Stap 1**. Géén stop-en-wacht — de orchestrator-flow loopt
autonoom door totdat het hoofdstuk klaar is (gebruiker heeft dit
geaccordeerd; zie `GIT_WORKFLOW.md` orchestrator-uitzondering).

### Stap 6.5 — adversarial pass (alleen bij CHAPTER_COMPLETE)

Zodra Stap 1 `CHAPTER_COMPLETE` rapporteert, **vóór** de eindrapportage,
draai de adversariële hoofdstukbeoordeling. Deze stap is verplicht en
standaard streng — "luiheid wordt gestraft": elk gevonden issue moet
worden gefixt of inhoudelijk weerlegd.

1. **Pre-scan + in-context aanvulling.** Roep de skill aan:

   ```
   Skill(skill="sv-adversarial-review", args="<BOEK> <H>")
   ```

   De skill draait `scripts/adversarial_scan.py scan` en vult dan
   in-context aan (zie de skill-SKILL.md voor protocol). Resultaat staat
   in `output/<BOEK>/review.<H>.json`.

2. **Per `open` issue beslissen.** Lees het tracker-bestand en kies per
   issue:

   - **Fix-pad**: pas `output/<BOEK>/<BOEK>.<H>.json` aan via Edit-tool.
     Re-validate het gewijzigde vers (`scripts/validate.py check`).
     Update issue: `status: "fixed"`, `fix_commit: "<sha>"`.
   - **Rebuttal-pad**: zet `status: "rebutted"` met `rebuttal: "<argument>"`.
     Het argument moet (a) een regel of Griekse term noemen
     (`§2.3`, `§2.7`, `λέγων`, `attributief`), (b) vers-specifiek zijn,
     (c) ≥60 tekens, (d) niet identiek toepasbaar op andere issues.
     Generieke "behoud van SV-stijl" of "formele equivalentie" zonder
     onderbouwing wordt door pass 2 heropend.

   Let op: prescan-issues die al door de skill zelf met bewijs zijn
   weerlegd (status `rebutted` na in-context aanvulling) hoeft de
   orchestrator niet opnieuw te wegen — alleen de issues die in pass
   1 op `open` blijven staan, vereisen orchestrator-actie. Concordantie-
   drift-issues die de skill als false-positive heeft gerebutted
   (scanner-prefix-heuristiek mist orthografische overgang s→z, sch→g,
   etc.) zijn definitief afgehandeld.

3. **Commit fixes via git-subagent.** Net als Stap 5: orchestrator maakt
   de branch klaar en delegeert het git-werk aan een subagent.

   ```bash
   scripts/mkbatch.sh <boek-lowercase> <H> adversarial-fix
   ```

   Spawn dan een `Agent` met het git-template-bestand (`prompts/git.txt`,
   zie **Subagent-prompts** onderaan), met als enige aanpassingen:
    - Toe te voegen bestanden: `output/<BOEK>/<BOEK>.<H>.json` én
     `output/<BOEK>/review.<H>.json` (niet `scripts/lint_carryovers.py`).
   - Commit-message: `adversarial fixes <BOEK> <H>`.
   - PR-title: `adversarial fixes <BOEK> <H>`.
    - PR-body: `Bevindingenlijst: output/<BOEK>/review.<H>.json. Fixes via sv-adversarial-review ronde 1.`

   Verwacht 3-4 regels terug (`BRANCH`/`PR`/`MERGED`/`SHA`).

4. **Verify (pass 2).** Roep de scanner in verify-modus aan:

   ```bash
   uv run python scripts/adversarial_scan.py verify \
       --book <BOEK> --chapter <H> --terse
   ```

   `--terse` levert één regel `verify <BOEK> <H>: status=[k:v ...] N
   actions -> review.<H>.json`. Exit 0 = klaar; exit 1 = nog
   `open`/`reopened` issues. Bij `reopened`-issues: nog één ronde
   fix/rebuttal (max 2 fix-rondes totaal). Daarna belanden resterende
   issues in het hoofdstuk-eindrapport. Laat `--terse` weg voor de
   volledige `actions`-lijst.

5. **Skip-criteria**. Deze stap mag NIET worden overgeslagen. "Geen
   issues gevonden" is een geldige uitkomst (pass 1 exit 0 én alle
   pre-scan-categorieën nul). Maar de skill-aanroep zelf moet in het
   transcript staan.

## Caveman mode

Als caveman mode actief is (session-hook injecteert `CAVEMAN MODE ACTIVE`),
rendert de orchestrator zijn **eigen** user-facing tekst terse: tussen-
batch-updates, compact-hint regel, en eindrapport. Fragmenten OK,
articles/filler/hedging eruit. Technische substantie blijft intact:
PR-URL, vers-nummers, SHA, validator-verdict, blokker-tekst exact.

**Niet** caveman:

- Subagent-prompts (modernisatie + review + git): templates blijven
  woordelijk zoals onderaan staan. Subagents werken niet onder caveman;
  hun output-eisen zijn strikt.
- Commit-messages, PR-titles, PR-bodies: normaal Nederlands (zie
  `GIT_WORKFLOW.md`).
- Code in skill-bestanden, scripts, output-JSON: ongewijzigd.
- Validator/lint stdout-citaten: exact zoals tool ze geeft.

Caveman compact-hint voorbeeld:

```
[COMPACT-HINT] batch 7-9 gemerged (PR <url>). 9/80 LUK 1. /compact bij >150k.
```

Caveman eindrapport voorbeeld:

```
LUK 1 klaar. 80/80, 22 batches, 22 PRs.
Adversarial: 12 issues — 8 fixed, 3 rebutted, 1 reopened.
Regels: STOPLIST +12, ARCHAISMEN +2.
Blokkers: geen.
```

## Eindrapport (na hoofdstuk klaar of bij stop)

Korte tekst (4-8 regels):

```
LUK 1 voltooid. 80/80 verzen, 22 batches, 22 PRs gemerged.
Adversarial review: 12 issues — 8 fixed, 3 rebutted-verified, 1 reopened.
Regelbestandwijzigingen: STOPLIST +12 items; ARCHAISMEN.md +2 patronen.
Blokkers: geen.
```

Of bij failure-stop:

```
LUK 1: 16/80 verzen voltooid in 5 batches.
Stop op blokker: LUK 1:18 — validator harde fout (kanttekeningaantal).
Subagent gaf na nieuwe poging: <samenvatting>.
Geen commit voor deze batch — uitvoer-JSON ongewijzigd op main.
```

## Subagent-prompts

De volledige prompt-templates voor de drie subagents staan **niet meer
inline** — ze zijn losse bestanden naast deze skill:

| Subagent | Stap | Template-bestand |
|---|---|---|
| Modernisatie | 2 | `.agents/skills/sv-batch-orchestrate/prompts/modernize.txt` |
| Review | 3 | `.agents/skills/sv-batch-orchestrate/prompts/review.txt` |
| Git | 5 / 6.5 | `.agents/skills/sv-batch-orchestrate/prompts/git.txt` |

Reden: de templates zijn lang en per batch identiek op enkele variabelen
na. Ze inline in elke `Agent`-spawn meesturen vult de orchestrator-context
onnodig vol. In plaats daarvan stuurt de orchestrator een **korte**
`prompt` die de subagent naar het bestand verwijst; de subagent leest het
zelf (in zijn eigen, geïsoleerde context).

**Spawn-prompt — modernisatie (Stap 2):**

```
Lees .agents/skills/sv-batch-orchestrate/prompts/modernize.txt en volg
het exact. Vervang de <...>-placeholders met:
  REPO_ROOT=<output van `git rev-parse --show-toplevel`>
  BOEK=<BOEK>  H=<H>  V_START=<V_START>  V_EIND=<V_EIND>
```

Bij een nieuwe poging (Stap 4): voeg toe dat het een retry is, met het
NIEUWE-POGING-ADDENDUM-blok onderaan `modernize.txt` ingevuld
(`<N>` = vers, `<validator-issue-tekst>` = de BLOKKER-issuetekst).

**Spawn-prompt — review (Stap 3):**

```
Lees .agents/skills/sv-batch-orchestrate/prompts/review.txt en volg het
exact. Vervang de <...>-placeholders met:
  REPO_ROOT=<git rev-parse --show-toplevel>
  BOEK=<BOEK>  H=<H>  V_START=<V_START>  V_EIND=<V_EIND>
  V_LIJST=<komma-gescheiden versnummers, bv. 10,11,12>
```

**Spawn-prompt — git (Stap 5 / Stap 6.5 stap 3):**

```
Lees .agents/skills/sv-batch-orchestrate/prompts/git.txt en volg het
exact. Vervang de <...>-placeholders met:
  REPO_ROOT=<git rev-parse --show-toplevel>
  BRANCH=<branch-naam van scripts/mkbatch.sh>
  BOEK=<BOEK>  H=<H>
  EXTRA_FILES=<extra te committen paden, regel per pad; of leeg>
  COMMIT_MESSAGE=<...>  PR_TITLE=<...>  PR_BODY=<...>
```

Voor de adversarial-fix-variant (Stap 6.5 stap 3): `EXTRA_FILES` =
`output/<BOEK>/review.<H>.json`, commit-message en PR-title
`adversarial fixes <BOEK> <H>`, PR-body zoals in Stap 6.5 beschreven.

## Wanneer NIET deze skill activeren

- Als de gebruiker een **expliciete vers-range** geeft (bv. "moderniseer
  LUK 1:14-16"): laat `sv-modernize` direct in deze conversatie draaien
  (oude inline-werkwijze). Daar is geen orchestrator nodig.
- Als de gebruiker **her-modernisatie** vraagt — d.w.z. bestaande verzen
  overschrijven (bv. "her-moderniseer LUK 1:1-3", "moderniseer LUK 1:1-3
  opnieuw"): laat `sv-modernize` direct draaien met de expliciete range.
  De orchestrator's Stap 1 ("next undone") is per definitie ongeschikt
  voor her-modernisatie. `sv-modernize` heeft de juiste flow (output
  upsert + memory-upsert + `--exclude-*`-filter tegen zelfselectie).
- Als de gebruiker vraagt om alleen de introductie of epiloog te doen:
  laat `sv-modernize` direct draaien.
- Als de gebruiker expliciet een ander boek/hoofdstuk noemt waar nog
  niets van staat: vraag of een nieuw hoofdstuk gestart moet worden, of
  ga door met expliciete `<BOEK> <H>`-grenzen.

## Foutgevallen

- **Hoofdstuk niet detecteerbaar** (geen output, meerdere boeken, geen
  duidelijke "actief hoofdstuk"): vraag de gebruiker welk hoofdstuk.
- **`gh` niet ingelogd**: meld dat `gh auth login` nodig is, stop.
- **Branch-protection op `main` weigert merge**: de git-subagent (Stap
  5) probeert de lokale fallback automatisch. Faalt die ook, dan
  retourneert hij `MERGED: no — <reden>` — behandel als blokker en
  stop met duidelijke melding.
- **Modernisatie-subagent geeft geen JSON-output / crasht**: behandel
  als blokker, ga naar het foutpad (stap 4).
- **Git-subagent retourneert `STATE_DRIFT` of een 3e regel anders dan
  `MERGED: yes`**: blokker — geen nieuwe poging mogelijk (er is niets te
  hermodernisteren); meld in eindrapport en stop.

