---
name: sv-meta-review
description: Meta-adversariële review over alle HSV-diffs van een afgesloten boek of range. Aggregeert cross-chapter patronen uit `docs/diff_hsv_<BOEK>_*.json` (via `scripts/meta_diff_aggregate.py`), classificeert in drie buckets (A = HSV-keuze/noise, B = per-vers modernisatie-fix, C = scaffolding-gap), en kan een apply-modus draaien voor regel-deltas (3b) en per-hoofdstuk content-fixes (3a). Roep aan via "meta-review LUK", "draai meta-adversarial", "scan alle HSV-diffs voor patronen", of "meta-review LUK apply" (apply-modus).
---

# sv-meta-review — meta-protocol over cross-chapter HSV-diffs

Deze skill draait **in de orchestratorcontext** (het agent-model zelf).
Geen externe LLM-aanroep. Roept de deterministische aggregator
(`scripts/meta_diff_aggregate.py`) aan, classificeert de output, en
schrijft `output/META/findings.json` + `output/META/scaffolding_deltas.md`.

Werkdirectory:
`/Users/wmotte/Desktop/projects/SVmodernisatie2026/`.

## Wanneer aanroepen

- **Na afsluiting van een batch hoofdstukken** (typisch een heel boek of
  het eerste blok hoofdstukken). Trigger-zinnen:
  - "meta-review LUK"
  - "draai meta-adversarial"
  - "scan alle HSV-diffs voor patronen"
- **Apply-modus** (regel-deltas + content-fixes uitrollen):
  - "meta-review LUK apply"
  - "meta-review LUK apply rules" (alleen 3b)
  - "meta-review LUK apply content" (alleen 3a — pas ná merge 3b)

Niet voor: enkele verzen / hoofdstukken (gebruik dan `sv-semantic-review`
of `sv-adversarial-review`). Niet voor: introducties / epilogen (geen
HSV-equivalent).

## Stap 1 — Aggregatie draaien

Roep de aggregator aan:

```bash
uv run python scripts/meta_diff_aggregate.py \
    --book <BOEK> --chapters <RANGE> --min-freq 2
```

Standaard `--chapters 1-18` voor LUK. Output: `output/META/candidates.json`.

Lees `output/META/candidates.json` **met de Read-tool**, niet via inline
`cat`/`python3 -c` — dat dumpt het hele bestand in de orchestrator-stdout.

Top-level structuur:

```json
{
  "book": "LUK",
  "chapters": [1, 2, ..., 18],
  "min_freq": 2,
  "total_patterns": 47,
  "patterns_by_kind": {
    "carryover":        [ {pattern_id, key, frequency, hsv_alternatives, severity_hint, occurrences[]}, ... ],
    "fossiel-lidwoord": [ ... ],
    "latinaat-window":  [ ... ],
    "cap-asym":         [ ... ]
  }
}
```

## Stap 2 — Per pattern classificeren naar bucket A/B/C

| Bucket | Betekenis | Actie |
|---|---|---|
| **A** | HSV-keuze, parafrase, eerbiedshoofdletter, of vrije syntaxis — geen modernisatie-tekortkoming | Loggen in `scaffolding_deltas.md` onder `noise_filtered`. Geen edit. |
| **B** | Modernisatie-fix die wij gemist hebben (drempel-archaïsme, false friend, fossiel) | Per occurrence opnemen in `output/META/findings.json` met `review.<H>.json`-issue-schema. |
| **C** | Scaffolding-gap — pattern komt N≥3× voor, bestaande lint had het moeten vangen | Auto-apply in target-bestand (zie tabel hieronder) + audit-entry in `scaffolding_deltas.md`. |

### Classificatie-criteria per pattern-kind

**carryover**:
- `frequency ≥ 3` + HSV consistent modern alternatief + `severity_hint == "hard"` (dwz. woord staat al in `DREMPEL_ARCHAISMEN`) → **bucket C**
- `frequency ≥ 3` + HSV alternatief consistent, niet op DREMPEL → **bucket C** (uitbreiden `DREMPEL_ARCHAISMEN`/`ARCHAISMEN.md`)
- `frequency == 2` → **bucket B** (per-vers fix)
- Geen consistent HSV-alternatief → **bucket A** (HSV-keuze)

**fossiel-lidwoord**:
- Snippet bevat bijbeluitdrukking (zoon des mensen, koninkrijk der hemelen, dag des heren, woord des heren, geest des heren, engel des heren, etc.) → **bucket A**
- Niet-bijbels + `frequency ≥ 3` → **bucket C** (uitbreiden `DREMPEL_ARCHAISMEN` in `scripts/adversarial_scan.py`)
- Niet-bijbels + `frequency < 3` → **bucket B**

**latinaat-window**:
- HSV-herschikking als enige verschil (geen bewijs van Latinaat in SV2026) → **bucket A**
- Recurrente Latinaat-rest (zelfde patroon-vorm ≥3 hoofdstukken) → **bucket C** (entry in `FALSE_FRIENDS` of `MODERNISATIE.md §2.3b`)
- Eenmalige rest-Latinaat → **bucket B**

**cap-asym**:
- HSV-keuze (consistent SV1657-interne case) → **bucket A** (standaard)
- SV-intern inconsistent (zelfde woord met én zonder hoofdletter binnen LUK 1–18) → **bucket C** (note in `scaffolding_deltas.md`; geen auto-edit — semantisch oordeel nodig)

### Productiviteits/verwarringtest §2.7 toets

Voor elke bucket-C-delta vóór toepassen:

1. **Productiviteits-test**: zou het modern alternatief in hedendaags zakelijk Nederlands voorkomen?
2. **Constructie-test**: werkt het in zijn SV-constructie ook in modern NL?
3. **Verwarringtest**: heeft het modern alternatief geen dominant andere betekenis (false friend in spiegel)?

Zakt op een van de tests → opnemen in `scaffolding_deltas.md` onder
`rejected` met motivatie; niet toepassen.

## Stap 3 — Output schrijven

### `output/META/findings.json` (bucket B)

```json
{
  "book": "LUK",
  "generated_at": "<ISO timestamp>",
  "min_freq": 2,
  "issues": [
    {
      "id": "META-LUK-<CH>-<V>-001",
      "verse": <V>,
      "chapter": <CH>,
      "category": "carryover | fossiel-lidwoord | latinaat-window | cap-asym",
      "severity": "hard | soft",
      "quote_modernized": "<sv2026-excerpt>",
      "hsv_quote": "<hsv-excerpt>",
      "rule_reference": "MODERNISATIE.md §2.7 / §2.3b / etc.",
      "explanation": "<korte motivatie>",
      "proposed_fix": "<modernisatie-suggestie of null>",
      "location": "hoofdtekst | kanttekening",
      "status": "open"
    },
    ...
  ]
}
```

Eén issue per `(pattern, occurrence)`. Gegroepeerd op `chapter` in
toepassings-tijd door 3a.

### `output/META/scaffolding_deltas.md`

Markdown-bestand met drie secties:

```markdown
# Scaffolding-deltas — meta-review <BOEK> hoofdstukken <RANGE>

Gegenereerd: <ISO timestamp>
Aggregator: scripts/meta_diff_aggregate.py --book <BOEK> --chapters <RANGE>

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| `<key>` | carryover | 5 | `ARCHAISMEN.md` + `lint_carryovers.STOPLIST` | toegevoegd als trigger; alternatief 'omdat' | LUK 3:12, 7:4, 11:8 |
| ... |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `<key>` | latinaat-window | productiviteits-test gezakt: HSV-alternatief 'XYZ' is zelf archaïsch |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 23 | "Engel" (LUK 1), "Apostelen" (LUK 6), ... |
| fossiel-lidwoord bijbels | 12 | "zoon des mensen" (LUK 5,6,9,...) |
| ... |

## Bucket-overzicht

- B (per-vers fixes): <N> issues over <M> hoofdstukken — zie `findings.json`
- C (scaffolding-deltas): <N> toegepast, <M> afgewezen
- A (noise): <N>
```

## Stap 4 — Apply-modus

Alléén bij expliciete trigger (`"... apply"` / `"apply rules"` / `"apply content"`).
Standaard-trigger zonder `apply` doet alleen Stap 1–3 (analyse, geen edits).

### Stap 4a — Bucket C (regel-deltas) — `feature/meta-review-rules`

**Volgorde verplicht: 4a vóór 4b** — regels eerst aanscherpen, dan
content-fixes met de nieuwe regels actief.

1. Maak/checkout branch `feature/meta-review-rules` vanuit `main`.
2. Voor elke bucket-C-delta die §2.7-toets passeert: pas Edit toe
   volgens de mapping:

| Delta-kind | Target | Wijze |
|---|---|---|
| `carryover` met HSV-modern alternatief | `ARCHAISMEN.md` tabel-uitbreiding (Oud → Modern rij) **en** `DREMPEL_ARCHAISMEN` in `scripts/adversarial_scan.py` (regel 86–105) | Edit beide |
| `fossiel-lidwoord` niet-bijbels | `DREMPEL_ARCHAISMEN` in `scripts/adversarial_scan.py` (regel 86–105) — voeg `"<artikel>"` toe of een nieuwe `FOSSIL_LIDWOORD_PATTERNS`-tuple als de validatie woordcombinatie nodig heeft | Edit |
| `latinaat-window` recurrent | `FALSE_FRIENDS` in `scripts/lint_false_friends.py` (regel 27) — nieuwe entry met `pattern`, `sv`, `modern`, `advies` | Edit |
| `cap-asym` interne inconsistentie | Geen auto-edit. Voeg note toe in `scaffolding_deltas.md` met de verzen die alignen, en welke kant de norm zou moeten zijn | doc-only |

3. Commit op feature-branch. Boodschap: `chore: meta-review scaffolding deltas LUK 1-18`.
4. Push, open PR via `gh pr create`. PR-titel: `meta-review: scaffolding deltas LUK 1-18`.
5. **PR NIET auto-mergen.** User-review verplicht voor regelbestand-wijzigingen.
   Stop hier; wacht op user voor verder werk.
6. PR-body bevat het `scaffolding_deltas.md` inhoud (audit-log met per
   delta 3 bewijs-citaten via vers-referenties + diff-samenvatting).

### Stap 4b — Bucket B (content-fixes) — per-hoofdstuk PRs

**Pre-conditie:** Stap 4a-PR is gemerged door user, of expliciet
`apply content` is gevraagd zonder 4a (override; orchestrator
vermeldt risico in eindrapport).

Voor elk hoofdstuk H met findings in `findings.json`:

1. Branch `feature/luk<H>-meta-fix` (boekcode+H aaneen, conform bestaande
   convention `feature/luk8-batch-1-3`).
2. Roep `sv-modernize` aan met **alleen** de specifieke verzen met findings
   (niet het hele hoofdstuk). Pass de findings-lijst als context mee.
3. Run `sv-validate` op de aangeraakte verzen.
4. Run `sv-semantic-review` op de aangeraakte verzen.
5. Commit. Boodschap: `meta-fix: LUK <H> verzen <lijst>`.
6. Push, open PR `meta-fix: LUK <H>`.
7. **Auto-merge** ná validate+semantic groen (consistent met orchestrator
   batch-flow). Indien blokker: stop dat hoofdstuk, ga door met de rest.
   Eindrapport noemt geblokkeerde hoofdstukken.

**Parallel**: hoofdstukken zijn onafhankelijk; gebruik worktrees voor
parallelle verwerking — één hoofdstuk per worktree
(`scripts/wt.sh new luk<H>-meta`). Volg `WORKTREE_WORKFLOW.md`.

## Stap 5 — Eindrapport

Aan het einde van de skill (na Stap 3 of na 4a / 4b): kort rapport (max
15 regels) aan de gebruiker:

```
Meta-review <BOEK> <CHAPTERS>:
- aggregator: <total_patterns> patterns (carryover N, fossiel-lidwoord M, latinaat-window K, cap-asym L)
- bucket B (findings): <N> issues over <M> hoofdstukken
- bucket C (scaffolding): <N> toegepast, <M> afgewezen (§2.7)
- bucket A (noise): <N>

apply-modus: <not-run | 4a-PR <url> open | 4a merged + 4b N/M hoofdstukken klaar>
geblokkeerde hoofdstukken: <lijst of "geen">

bestanden:
- output/META/candidates.json
- output/META/findings.json
- output/META/scaffolding_deltas.md
```

## Stopregels

- Bucket-C deltas die §2.7-toets zakken: nooit auto-toepassen — meld in
  `scaffolding_deltas.md` onder `rejected` met motivatie.
- 4a-PR (regel-deltas): nooit auto-merge. 4b-PRs (content-fixes): wel
  auto-merge bij groen.
- Per hoofdstuk maximaal 1 4b-PR. Blokker op een hoofdstuk → stop dat
  hoofdstuk, ga door met de rest.
- HSV-bewijs alléén nooit genoeg voor een wijziging. Onafhankelijke
  verificatie tegen SV1657 + Grieks blijft verplicht voor bucket B/C
  (zie `MODERNISATIE.md §2.7` en `sv-semantic-review` Stap 2.5).
- Eigennamen NBV21 (Jezus, Johannes, Lucas, ...): nooit als bucket-B/C
  flag — hoort in `STOPLIST` of expliciete eigennaam-filter.
- Pending verzen (`status != "modernized"`) worden door aggregator
  overgeslagen; meta-review draait alleen op afgesloten hoofdstukken.

## Compactie-instructies

Na deze skill kan de orchestrator-context groot zijn. Bewaar bij `/compact`:

- Eindrapport-fragment (Stap 5).
- PR-URLs (4a + per-hoofdstuk 4b).
- Lijst van auto-toegepaste deltas (1 regel per delta).
- Geblokkeerde hoofdstukken.

Mag weg:

- Volledige `candidates.json` / `findings.json` / `scaffolding_deltas.md`
  (staan op disk).
- Verbose aggregator-stdout.
- Volledige PR-create-output (alleen URL bewaren).
