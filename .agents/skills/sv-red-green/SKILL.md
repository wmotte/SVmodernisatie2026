---
name: sv-red-green
description: Iteratief, gelijk-machtig adversarieel debat over twee NT-boeken heen. Een red team kiest (worst-first) twee boeken en stelt de ≤10 zwakste punten op — zowel op modernisatie-niveau als between-book consistentie; een green team pareert elk punt; een arbiter beslecht deadlocks (red-wint / green-wint / regelwijziging). Geaccepteerde verbeteringen worden NT-breed toegepast (volledig auto-merge). Notulen (output/META/debate/) worden elke sessie eerst gelezen en meegenomen; herhaalt tot het red team niets nieuws meer vindt. Roep aan via "red-green review", "start red vs green", "debatronde", of "red-green apply".
---

# sv-red-green — red team vs green team, cross-book, NT-breed

Deze skill draait **in de orchestratorcontext**. De drie rollen (red,
green, arbiter) draaien elk in een **aparte `Agent`-subagent met schone
context** zodat de orchestrator-context niet volloopt. De orchestrator
houdt enkel compacte ronde-samenvattingen vast; al het zware lezen en
redeneren gebeurt in de subagents, die naar disk schrijven.

Werkdirectory: repo-root (`git rev-parse --show-toplevel`).

Eén **ronde** = één volledig debat over één boekenpaar. Een **sessie** =
default 3 rondes (of stop zodra het red team 0 nieuwe punten levert).

## Vaste keuzes (niet heronderhandelen)

1. **Tie-break:** een aparte **arbiter-subagent** beslist per punt. Green
   wint alleen als de rebuttal de **rebuttal-gate** haalt (≥2 van: §-regel,
   concrete Griekse term, vers-specifiek argument — zie
   `sv-adversarial-review` Stap 2b). Anders red-wint. Structureel patroon
   (komt NT-breed voor) → `rule_change`.
2. **Boekkeuze:** worst-first via `scripts/redgreen_select.py` (alleen
   100%-boeken).
3. **Apply:** volledig auto-merge — regel-deltas én geraakte verzen
   NT-breed, auto-merge bij groene validatie.
4. **Loop:** N rondes per aanroep (default 3); notulen bewaren; volgende
   aanroep leest ze en gaat door.

## Stap 0 — Notulen lezen (verplicht, elke sessie)

```bash
uv run python scripts/redgreen_minutes.py init      # idempotent
uv run python scripts/redgreen_minutes.py summary    # compacte status
```

`summary` geeft `rounds_done`, laatste paren, `closed_keys`-aantal,
`debate_count`. Lees **nooit** de volledige `minutes.md` inline; gebruik
`summary` en (voor red) `closed-keys`.

## Stap 1 — Boekenpaar kiezen (per ronde)

```bash
uv run python scripts/redgreen_select.py
```

Output: `{"pair": ["REV","JHN"], "round_no": N, "reason": "...", "scores": {...}}`.
Bewaar `pair` en `round_no`. Bij `{"error": ...}` (minder dan 2 afgeronde
boeken): stop, meld aan gebruiker.

## Stap 2 — Concord-seed (between-book consistentie)

```bash
uv run python scripts/redgreen_concord.py --books <B1> <B2> \
    --top 25 --out output/META/debate/concord_<N>.json
```

Bounded lexicale seed van kandidaat-divergenties (zelfde Griekse token →
uiteenlopende NL-rendering). Geen oordeel; het red team verifieert in
context. De orchestrator leest dit bestand **niet** zelf — het pad gaat
mee als context naar de red-subagent.

## Stap 3 — RED subagent (schone context)

Spawn een `Agent` (general-purpose). Geef in de prompt mee:

- de twee boekcodes + `round_no`;
- de paden: `output/<B1>/` en `output/<B2>/`, `docs/diff_hsv_<B>_*.json`,
  `output/META/debate/concord_<N>.json`;
- de **closed-keys** zodat red niets herhaalt:
  ```bash
  uv run python scripts/redgreen_minutes.py closed-keys
  ```
  (geef de lijst mee in de prompt);
- adviserend: `uv run python scripts/query_decisions.py "<term>" --limit 5`
  voor eerdere besluiten.

Opdracht aan red: lees de bronnen en stel **≤10** zwakste punten op.
Default-stance = overtreding (zoals `sv-adversarial-review`: luiheid wordt
gestraft, uitgangspunt is dat het punt terecht is). Twee klassen:

- `class: "modernisatie"` — fout op modernisatie-niveau in één boek
  (drempel-archaïsme, finiet participium §2.3, Latinaat-syntax §2.3b,
  false friend, fossiel lidwoord, imperatief-`-t`, eerbiedskapitaal,
  kanttekening-luiheid).
- `class: "consistentie"` — zelfde Grieks/idioom verschillend
  gemoderniseerd **tussen** de twee boeken (concordantie-drift).

Red **mag <10 of 0 punten** teruggeven (geen quota-vulling met ruis).
Punten waarvan de `point_key` al in closed-keys staat: **niet** opnieuw
inbrengen. Red schrijft naar `output/META/debate/round_<N>.json`:

```json
{
  "round_no": <N>,
  "books": ["<B1>", "<B2>"],
  "red": [
    {
      "id": "RG<N>-001",
      "class": "modernisatie | consistentie",
      "books": ["<B>"],
      "chapter": <int>,
      "verse": <int>,
      "quote": "<gemoderniseerd fragment>",
      "rule_reference": "MODERNISATIE.md §2.3 / §2.7 / etc.",
      "explanation": "<korte motivatie>",
      "proposed_fix": "<suggestie>",
      "severity": "hard | soft"
    }
  ]
}
```

Red returnt aan de orchestrator **alleen** een telling (`N punten,
klassen x/y`), niet de volle lijst.

## Stap 4 — GREEN subagent (schone context)

Spawn een `Agent`. Geef mee: het pad `round_<N>.json`, de twee
boekcodes, en de regelbestanden (`MODERNISATIE.md`, `ARCHAISMEN.md`,
`KANTTEKENINGEN.md`). Green is **even sterk** als red: het mag elk punt
volledig wegnemen.

Opdracht: pareer elk red-punt. Een rebuttal is alleen substantief met
**≥2 van**: (a) §-regel of concrete Griekse term, (b) vers-specifiek
argument (constructie attributief / idioom gestold), (c) onderscheidend
(niet identiek toepasbaar op alle punten). Boilerplate ("we behouden
SV-stijl", "formele equivalentie") telt niet. Green schrijft `green[]` in
hetzelfde round-bestand:

```json
{ "point_id": "RG<N>-001", "stance": "rebut | concede",
  "rebuttal": "<argument>", "evidence": "§2.3b + λέγων" }
```

Green returnt alleen een telling (`R rebut, C concede`).

## Stap 5 — ARBITER subagent (schone context)

Spawn een `Agent`. Geef mee: het pad `round_<N>.json` (red + green secties).
Per punt, mechanisch oordeel:

- green's rebuttal **haalt de gate** (≥2-criterium) → `green_wins`;
- green concedeert of gate niet gehaald → `red_wins`;
- het punt blootlegt een **structureel** patroon dat NT-breed voorkomt en
  in een regelbestand thuishoort → `rule_change` (scope `nt-wide`).

Arbiter schrijft `verdicts[]`:

```json
{ "point_id": "RG<N>-001", "verdict": "red_wins | green_wins | rule_change",
  "rationale": "<beslissing + bewijs>", "scope": "verse | nt-wide",
  "applied": false }
```

Arbiter returnt de verdict-telling.

## Stap 6 — APPLY (volledig auto-merge)

Alleen bij trigger met `apply` (bv. "red-green apply"); een kale
"debatronde" doet Stap 0–5 + Stap 7 (analyse + notulen, geen edits).

Werk per worktree om gedeelde-checkout-resets te vermijden
(`scripts/wt.sh new redgreen-<N>`; zie `WORKTREE_WORKFLOW.md`). Git-ketens
**foreground/synchroon**, nooit background.

**Volgorde: regel-deltas (6a) vóór content-fixes (6b).**

### 6a — `rule_change` → regel-delta NT-breed

1. Bewerk de **bronlocatie** (nooit de linter zelf — zie `REGELBESTANDEN.md`):
   `scripts/rules_data.py` (`DREMPEL_ARCHAISMEN` / `FALSE_FRIENDS` /
   `FOSSIL_GENITIVE_PAIRS` / participium-lijsten), `scripts/stoplist.txt`,
   en houd de tabel in `ARCHAISMEN.md` synchroon.
2. NT-brede sweep om elk geraakt vers te vinden:
   ```bash
   uv run python scripts/lint_all.py --root output --terse   # of gerichte lint_*/adversarial_scan
   ```
3. Verzamel de volledige lijst geraakte verzen. **Geen silent cap** — log
   élk vers in de notulen (count moet kloppen met de sweep).

### 6b — `red_wins` (content) + de sweep-treffers uit 6a

Voor elk geraakt vers (alle boeken, niet enkel het paar):

1. Roep **`sv-modernize`** aan op precies dat vers, met het finding als context.
2. `sv-validate` op het vers.
3. `sv-semantic-review` op het vers.
4. Commit per hoofdstuk; **auto-merge bij groen**. Blokker → sla dat vers
   over, ga door, meld in eindrapport.

Zet `applied: true` in de verdicts voor wat is uitgerold.

## Stap 7 — Notulen + state wegschrijven (per ronde)

```bash
uv run python scripts/redgreen_minutes.py append \
    --round output/META/debate/round_<N>.json
```

Dit werkt `state.json` bij (ronde-cursor, paren, `debate_count`,
`closed_keys` voor dedup), vult `minutes.md` aan (één sectie per ronde), en
append de beslechte verdicts aan `output/META/decisions.jsonl`
(hergebruikt door `query_decisions.py`).

## Stap 8 — Loop + eindrapport

Herhaal Stap 1–7 tot **N rondes** (default 3) **of** het red team in een
ronde **0 nieuwe** punten levert (alles al in closed-keys). Daarna kort
eindrapport (≤15 regels):

```
Red-green sessie (rondes <gedaan>):
- paren: <B1+B2>, <B3+B4>, ...
- punten: red <N> totaal (modernisatie M / consistentie K)
- verdicts: red_wins X, green_wins Y, rule_change Z
- NT-brede deltas: <regel-edits + #geraakte verzen> (apply) | n.v.t. (analyse)
- geblokkeerde verzen: <lijst of "geen">
- notulen: output/META/debate/minutes.md (round_<N>.json per ronde)
```

## Stopregels

- Alleen 100%-boeken debatteren (pending verzen → `select` slaat ze over).
- Red vult geen quota: 0 punten is een geldig, gewenst einde.
- Green-wint vereist de gate; HSV-bewijs of "SV-stijl" alléén is nooit genoeg.
- Eigennamen NBV21 (Jezus, Johannes, ...): nooit als red-punt — hoort in
  `STOPLIST`/eigennaam-filter.
- Regel-deltas raken **alleen** de bronlocaties in `REGELBESTANDEN.md`;
  nooit de validator/scanner/linter zelf.
- Apply draait in een worktree; git foreground; review-bestand `rm` vóór
  een `git pull` van een fix-merge (untracked file blokkeert pull).
- Geen silent cap bij de NT-brede sweep: notulen-count == sweep-count.

## Context-discipline

- Elke rol = eigen subagent; orchestrator houdt enkel tellingen + paden.
- Subagents returnen ≤15 regels; ze schrijven detail naar disk.
- Orchestrator leest grote bestanden via de Read-tool of
  `redgreen_minutes.py summary`, nooit via inline `cat`/`python3 -c`.
- Bij `/compact` bewaren: eindrapport, gekozen paren, NT-brede deltas,
  geblokkeerde verzen, PR-URLs. Mag weg: round/concord-JSON (op disk),
  verbose subagent-output.
