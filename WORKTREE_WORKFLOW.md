# Worktree-workflow — parallelle agent-sessies

Leidend document voor het draaien van **meerdere agent-sessies
naast elkaar** op deze repository, zonder dat ze elkaars featurebranches
of gedeelde bronnen (geheugen-DB, uitvoer-JSON's) corrumperen. Conflict-
detectie loopt via [`clash`](https://github.com/clash-sh/clash) — de
TUI/CLI die specifiek voor deze gebruikssituatie is gemaakt.

Dit document is leidend voor alles wat met worktrees te maken heeft.
Bij conflict met `GIT_WORKFLOW.md`: de regels uit `GIT_WORKFLOW.md`
(branchbeleid, commitattributies, push→PR→merge-volgorde) blijven
onverkort gelden; dit document beschrijft alleen *waar* het werk plaatsvindt.

## TL;DR — hoe start ik een tweede agent-sessie?

```bash
cd ~/Desktop/projects/SVmodernisatie2026
./scripts/wt.sh new luk4-parallel        # maakt worktree + branch + symlinks
cd ~/Desktop/projects/SVmodernisatie2026.wt/luk4-parallel
# start de agent-CLI hier — tweede sessie, eigen branch
```

Als de tweede sessie klaar is en de branch is samengevoegd:

```bash
~/Desktop/projects/SVmodernisatie2026/scripts/wt.sh rm luk4-parallel
```

## Indeling

```
~/Desktop/projects/
├── SVmodernisatie2026/                 ← hoofdrepository (branch: main)
│   ├── memory/                         ← canonieke vectordatabase
│   ├── output/
│   ├── scripts/wt.sh                   ← helper
│   └── ...
└── SVmodernisatie2026.wt/              ← worktree-root (sibling)
    ├── luk4-parallel/                  ← worktree, branch feature/luk4-parallel
    │   ├── memory → ../../SVmodernisatie2026/memory  (symlink)
    │   ├── .env                        ← gekopieerd uit main
    │   ├── .agents/settings.local.json ← gekopieerd uit main (allowlist, hooks)
    │   └── output/, scripts/, ...      ← eigen checkout van de werkboom
    └── luk5-parallel/
        └── ...
```

Waarom naastliggend i.p.v. genest in de hoofdrepository:

- Geen `.gitignore`-pijn (een geneste worktree zou alle ignores moeten
  uitsluiten via padspecificaties).
- `git worktree list` blijft overzichtelijk.
- Een `find ./output ...` in de hoofdrepository loopt niet per ongeluk de
  parallelle checkouts in.

## Regels voor gelijktijdigheid

Alleen onderstaande paren mogen tegelijk lopen. Wie deze regels breekt
loopt tegen `clash status`-meldingen aan (zie hieronder), en in het
ergste geval tegen een verloren update / SQLite-corruptie.

### Veilig parallel

| Sessie A | Sessie B | Waarom OK |
|---|---|---|
| LUK 3 batches | LUK 4 batches | Verschillende `output/<BOEK>/<H>.json` |
| LUK 3 modernisatie | werk aan regelbestanden (linterscript, documentatie-update) | Geen bestandsoverlap |
| Boekvertaling | README/docs/research-werk | Gescheiden mappen |

### NIET parallel

| Sessie A | Sessie B | Reden |
|---|---|---|
| LUK 3 batch 4-6 | LUK 3 batch 7-9 | Beide upserten `output/LUK/LUK.3.json` |
| Twee `memory.py sync`-runs | idem | SQLite write-write-race in `memory/*.db` |
| Twee blacklist-uitbreidingen op `validate.py`/`lint_carryovers.py` | idem | Merge-conflict op zelfde regio |

Vuistregel: **één worktree per hoofdstuk.** Wil je twee batches uit
hetzelfde hoofdstuk parallel doen? Doe het serieel — de winst is klein
en de kosten van een corrupte JSON groot.

## Geheugen-DB: gedeeld via symlink

`memory/sv_modern.db`, `memory/verses.db`, `memory/memory.db` zijn
SQLite-bestanden. Het zijn gedeelde bronnen — concordantie kàn alleen
werken als alle batches dezelfde DB voeden. Daarom:

- Elke worktree heeft `memory/` als **symlink** naar de hoofdrepository
  `memory/`. `wt new` zet die symlink automatisch.
- SQLite-WAL handelt gelijktijdige **leesacties** (query's naar voorbeeldparen) prima af.
- Gelijktijdige **schrijfacties** (memory.py `add`/`sync`) zijn de risicobron.
  De orchestrator-skill draait deze schrijfacties onder `flock` op
  `memory/.lock` — kort wachten in plaats van een corrupte WAL.
- Symlinks worden niet door git getrackt: in elke worktree blijft
  `memory/` voor git "untracked"; dat is de bedoeling. Niet committen.

Dit betekent ook: een commit op een featurebranch in worktree B
schrijft géén DB-blobs mee; de DB blijft van de hoofdrepository. Dat is goed, want
DB's hoorden sowieso niet in versiebeheer.

## Clash — conflict-detectie

`clash` weet welke bestanden in welke worktree open staan en welke
recent zijn aangeraakt. Drie nuttige commando's:

```bash
clash status            # tabel: welke worktrees, welke bestanden, welke conflicten
clash status --json     # idem, machineleesbaar (voor hooks/agents)
clash watch             # live TUI — handig in een aparte terminal
clash check <pad>       # is er een andere worktree die dit bestand actief heeft?
```

**Voor je een batch start** in een worktree:

```bash
clash status
```

Zie je een andere worktree die aan dezelfde JSON werkt? Wacht of kies
een ander hoofdstuk.

### Clash als PreToolUse-hook (optioneel, opt-in)

Je kunt `clash check` als PreToolUse-hook aanzetten zodat elke
`Write`/`Edit` automatisch controleert of een andere worktree hetzelfde bestand
actief heeft. Bij conflict wordt de toolaanroep geblokkeerd. Dat is een
vangnet — niet de eerste verdediging. De eerste verdediging blijft:
één worktree per hoofdstuk.

Voeg dit handmatig toe aan `.agents/settings.local.json` als je de
hook wilt:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "clash check" }
        ]
      }
    ]
  }
}
```

`clash check` leest het `file_path` uit hook-stdin (`{"tool_input":
{"file_path": "..."}}`) en eindigt met een niet-nul-exitcode als een andere worktree het
bestand open heeft. Geen `file_path` → geen actie (exit 0). Veilig voor
Write/Edit op nieuwe bestanden.

## Subagent draait IN de worktree

Belangrijke afwijking van de oude `sv-batch-orchestrate`-instructies
("subagent werkt op `main`"):

Met worktrees draait de subagent in **de worktree, op de featurebranch**.
De orchestrator zit zelf óók in die worktree (dezelfde
agent-sessie). De werkmap die de Agent-tool meegeeft
is daarom NIET `~/Desktop/projects/SVmodernisatie2026/` maar het pad
van de huidige worktree.

Bepaal het werkelijke pad bij start van de orchestrator:

```bash
git rev-parse --show-toplevel    # is de worktree-hoofdmap
```

Geef dat pad mee in de subagent-prompt. De subagent committeert nog
steeds niet — dat blijft de orchestrator. Maar hij schrijft wel binnen
de worktree, op de actieve featurebranch.

## Branch-aanmaak — workflow per batch

Het oude patroon ("subagent schrijft op main, orchestrator maakt daarna
de branch") werkt niet in een worktree, want de worktree heeft per
definitie zijn eigen branch die niet `main` is. Nieuw patroon:

1. **Bij start van de agent-sessie** zit de worktree al op zijn
   featurebranch (bv. `feature/luk4-parallel`). Die branch is bedoeld
   als *werkbranch* voor deze sessie, niet als batchbranch.
2. **Per batch** (orchestrator-stap 5) maakt de orchestrator de
   batchbranch van een verse `main`:

   ```bash
   git fetch origin main --quiet
   git checkout -b feature/luk4-batch-1-3 origin/main
   # commit + push + PR + merge zoals normaal
   git checkout main
   git pull --ff-only origin main
   ```
3. **Tussen batches door** (na merge) blijft de worktree op `main`
   staan totdat de volgende batch begint. Niet terug naar de
   sessiebranch — die is alleen voor werk aan regelbestanden dat losstaat van
   batch-PR's (bv. een linteruitbreiding die je aan het einde apart
   wilt PR'en).

Voor wie alléén batches doet binnen een worktree: de sessiebranch
mag dood blijven. `wt new` maakt 'm aan zodat de worktree iets vasts
heeft om in te zitten; je hoeft 'm niet te gebruiken.

## Helper-script `scripts/wt.sh`

Volledige documentatie staat in het script zelf (`scripts/wt.sh help`). Kort:

- `wt new <suffix> [base]` — maakt `~/...wt/<suffix>/` met branch
  `feature/<suffix>` vanaf `base` (standaard `main`), zet
  `memory/`-symlink, kopieert `.env` en `.agents/settings.local.json`
  (allowlist + hooks — zonder die kopie hangen subagents in de worktree
  op routine-permission-prompts).
- `wt list` — toont `git worktree list` + `clash status`.
- `wt rm <suffix>` — verwijdert worktree (branch blijft staan,
  conform `GIT_WORKFLOW.md` verboden patronen).
- `wt clash [args]` — geeft argumenten door aan `clash status`.

## Stopregels voor parallelle sessies

- **Voorcontrole**: vóór elke batch in worktree X — `clash status` en
  scan op overlap. Als rood: kies een ander hoofdstuk of wacht.
- **Geheugenschrijfactie**: alleen via stap 0.5 van de orchestrator of de
  `sv-modernize` skill — beide gebruiken de standaard `memory.py`
  CLI die de flock-discipline respecteert. Niet handmatig in de DB
  prikken.
- **Geen worktree binnen een worktree**. Alle `wt new`-aanroepen
  gaan vanuit de hoofdrepository, niet vanuit een bestaande worktree.
- **Een blokker in worktree A pauzeert worktree A**, niet B. Sessies
  zijn onafhankelijk.

## Foutgevallen

- **`wt new` faalt op "branch already exists"**: branch bestaat lokaal
  of op de remote. Kies een andere suffix, of laat `wt.sh` de branch
  aankoppelen (gebeurt automatisch als de branch lokaal bestaat).
- **Symlink `memory/` is kapot of mist**: handmatig herstellen:
  `ln -sfn ~/Desktop/projects/SVmodernisatie2026/memory <wt>/memory`.
- **Subagent in worktree hangt op Edit/Bash-prompts** (bv. `Edit` op
  `scripts/lint_carryovers.py`): de worktree mist
  `.agents/settings.local.json`. Worktrees aangemaakt vóór deze
  fix hebben alleen `settings.local.example.json`. Herstellen:
  `cp ~/Desktop/projects/SVmodernisatie2026/.agents/settings.local.json <wt>/.agents/`.
  Daarna agent-CLI-sessie herstarten (settings worden alleen bij sessie-start
  gelezen).
- **`clash status` toont conflicten die er niet meer zijn**: clash
  baseert zich op recent aangeraakte bestanden; geef het 30s of herstart de
  betreffende sessie.
- **Branchbescherming weigert merge in een worktree**: dezelfde
  fallback als in `sv-batch-orchestrate` Stap 5 (lokaal mergen +
  push) werkt prima vanuit een worktree.
