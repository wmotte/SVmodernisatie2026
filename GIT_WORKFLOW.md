# Git workflow — SVmodernisatie2026

Regels voor alle git-acties in dit project. Afgeleid van de werkwijze uit
een eerder project, aangepast aan de structuur van dit project als enkele
repository (één repository, `main` als basisbranch).

## Remote: HTTPS via `gh`

Origin staat op **HTTPS** — niet op SSH:

```
https://github.com/wmotte/SVmodernisatie2026.git
```

Authenticatie loopt via de GitHub CLI (`gh`) als credential helper. Geen
SSH-sleutels nodig. Eenmalige inrichting op een nieuwe machine:

```bash
gh auth login          # of: gh auth status — om te controleren of je al ingelogd bent
gh auth setup-git      # registreert gh als credential helper voor https push/pull
```

Bij een bestaande kloon die nog op SSH (`git@github.com:...`) staat:

```bash
git remote set-url origin https://github.com/wmotte/SVmodernisatie2026.git
```

Daarna werken `git push`, `git pull` en `gh pr create` zonder verdere
sleuteldans.

## Parallelle sessies — worktrees

Voor het naast elkaar draaien van meerdere agent-sessies op
deze repo: zie `WORKTREE_WORKFLOW.md`. Het git-beleid hieronder
geldt onverkort — ook binnen worktrees. Worktree-specifieke punten:

- Een worktree zit per definitie op een eigen featurebranch
  (`feature/<suffix>`); je werkt nooit direct op `main` in een
  worktree.
- Per batch maakt de orchestrator een aparte batch-branch vanaf een
  verse `origin/main` (zie `WORKTREE_WORKFLOW.md` "Branch-aanmaak —
  workflow per batch").
- `git worktree remove` is OK; **branch-deletion blijft verboden**
  (zie verboden patronen).

## Branch-beleid

- Hoofdbranch: `main`.
- Maak een **featurebranch** aan voor elke wijziging die naar GitHub
  gepusht wordt — niet rechtstreeks op `main` committen.

```bash
git checkout main
git checkout -b feature/<beschrijvende-naam>
```

Voorbeelden van branchnamen:

- `feature/luk1-verzen`
- `feature/bibref-loose-refs`
- `feature/lint-stoplist-uitbreiding`

Eén featurebranch = één onderwerp. Splits bij twijfel.

## Commits

- Commits worden altijd gemaakt onder de naam van de gebruiker
  (`Wim Otte`).
- Voeg **geen** agent-attributietrailers toe aan commit-berichten (bv.
  `Co-Authored-By: …`, `Generated with …`) of vergelijkbare
  attribution-regels.
- Commit-berichten in het Nederlands, kort, met de focus op het *waarom*
  van de wijziging.
- **Nooit** `--no-verify` gebruiken. Bij een falende pre-commit hook:
  fix de oorzaak en maak een **nieuwe** commit (niet `--amend`).
- Stage gericht (`git add <bestand>`); vermijd `git add -A` of
  `git add .` om geheimen of grote binaire bestanden niet per ongeluk mee te
  nemen.

## Push naar GitHub — STOP daarna

```bash
git push -u origin feature/<naam>
```

**STOP hier.** Na het pushen doe je **niets** meer tenzij de gebruiker
**expliciet** vraagt om een PR of een merge.

Standaard werkwijze voor "commit en push":

1. Stage de relevante bestanden (geen `git add -A`).
2. Maak de commit (zonder agent-attributietrailers).
3. Push de featurebranch met `-u origin feature/<naam>`.
4. **Stop.** Wacht op een expliciete vervolgopdracht.

## Pull requests — alleen op expliciete vraag

Maak **alleen** een PR aan als de gebruiker daar **expliciet** om vraagt.

```bash
gh pr create --base main --title "<titel>" --body "<omschrijving>"
```

**STOP hier.** Na `gh pr create` doe je niets meer. Wacht op een
expliciete merge-opdracht.

## Merge naar main — alleen op expliciete vraag

```bash
git checkout main && git merge feature/<naam> && git push origin main
```

## Uitzondering: orchestrator-flow

De `sv-batch-orchestrate` skill mag binnen één aanroep autonoom de
volledige cyclus **push → PR → merge** per batch uitvoeren zonder
tussentijdse bevestiging — de gebruiker heeft dat geaccordeerd toen hij
de orchestrator triggerde ("moderniseer de volgende drie verzen"). De
volgorde 1 → 2 → 3 blijft dwingend; alleen de "STOP-na-push" /
"STOP-na-PR" wachten worden overgeslagen.

Buiten orchestrator-flow geldt het standaardpatroon "STOP-na-push"
onverkort. Alle verboden patronen hieronder blijven óók binnen de
orchestrator-flow van kracht (geen `--no-verify`, geen force-push op
`main`, geen agent-attributietrailers etc.).

## Volgorde is dwingend — nooit afwijken

```
1. git push -u origin feature/<naam>     ← featurebranch op remote
2. gh pr create --base main ...          ← PR bestaat op GitHub
3. git checkout main && git merge ...    ← code in main
```

> **Terugkerende fout:** mergen vóórdat de PR is aangemaakt. GitHub
> weigert dan een PR omdat de branches identiek zijn. Volgorde
> 1 → 2 → 3 is niet onderhandelbaar.

Bij een gecombineerde opdracht ("maak PR, merge"): voer de stappen
strikt in volgorde 1 → 2 → 3 uit. Sla stap 2 **nooit** over.

## Verboden patronen

- ❌ `git merge` vóórdat een PR is aangemaakt (als om een PR gevraagd is).
- ❌ `--delete-branch` bij `gh pr merge`.
- ❌ `git branch -d feature/...` of `git push origin --delete feature/...`
  — featurebranches worden **nooit** verwijderd.
- ❌ Agent-attributietrailers (bv. `Co-Authored-By: …`,
  `Generated with …`) in commits of PR's.
- ❌ `--no-verify` of het overslaan van pre-commit hooks.
- ❌ `git stash` + `git stash pop` over branches heen — gebruik in
  plaats daarvan een feature branch en pas wijzigingen direct toe op
  basis van het juiste basisbestand.
- ❌ `git push --force` op `main`.
- ❌ `git reset --hard` of `git checkout .` zonder expliciete opdracht.

## Geheimen nooit committen

- `.env` staat in `.gitignore` en mag **nooit** gecommit worden.
- API-sleutels (`GOOGLE_API_KEY` etc.) horen uitsluitend in `.env`,
  niet in code en niet in commit-berichten.
- Vóór elke commit: `git status` controleren om te bevestigen wat staged
  is. Bij twijfel niet committen.
