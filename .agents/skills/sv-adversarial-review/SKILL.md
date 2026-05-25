---
name: sv-adversarial-review
description: 'Adversariële beoordelaar per hoofdstuk. Schrijft een bevindingenlijst (output/<BOEK>/review.<H>.json) waarop de orchestrator MOET reageren — fixen of inhoudelijk weerleggen. Uitgangspunt is overtreding; luiheid wordt gestraft. Roep aan na CHAPTER_COMPLETE binnen sv-batch-orchestrate, of expliciet ("review hoofdstuk 8" / "adversarial review LUK 8"). Twee modi: scan (eerste ronde) en verify (tweede ronde na fixes/weerleggingen).'
---

# sv-adversarial-review — adversariële hoofdstukbeoordeling

Werkdirectory:
`/Users/wmotte/Desktop/projects/SVmodernisatie2026/` (of de actieve
worktree-hoofdmap). Twee aanroepvormen:

1. **Auto** vanuit `sv-batch-orchestrate` Stap 6.5 — direct na
   `CHAPTER_COMPLETE`-detectie, vóór de eindrapportage.
2. **Expliciet** — gebruiker zegt "adversarial review LUK 8",
   "review hoofdstuk 8", "review LUK 8 streng".

Rol: deze skill is *adversarieel*. **Uitgangspunt = overtreding.**
Een -ende-, infinitief-, of vocatief-vorm uit de pre-scan staat als
issue genoteerd, *tenzij* de skill expliciet kan motiveren waarom hij
acceptabel is (attributief gevolgd door zelfst.naamwoord, gestolde
uitdrukking, vakterm). Geen goedkeuring uit naïviteit. Geen
"waarschuwing"-categorie.

## Stap 1 — pre-scan

Draai de deterministische scanner. Hij schrijft
`output/<BOEK>/review.<H>.json`.

```bash
uv run python scripts/adversarial_scan.py scan \
    --book <BOEK> --chapter <H> --terse
```

`--terse` levert één regel: `scan <BOEK> <H>: N issues (M open)
sev=[hard:X soft:Y] -> review.<H>.json`. Niet-nul-exitcode als er
issues zijn — verwacht. Laat `--terse` weg voor `by_category`-breakdown.

Bij heraanroep van `scan` wordt een bestaande bevindingenlijst met
`status`/`fix_commit`/`rebuttal` waardes geërfd voor identieke
issues. Voor een verse start:

```bash
uv run python scripts/adversarial_scan.py scan \
    --book <BOEK> --chapter <H> --fresh --terse
```

## Stap 2 — in-context aanvulling

Lees de net-geschreven `output/<BOEK>/review.<H>.json` plus:

- `output/<BOEK>/<BOEK>.<H>.json` — het hoofdstuk zelf
- `MODERNISATIE.md` (vooral §2.3, §2.3b, §2.7)
- `ARCHAISMEN.md`
- `KANTTEKENINGEN.md`

Raadpleeg bij terugkerende patronen ook de decision-memory:

```bash
uv run python scripts/query_decisions.py "<woord of issue-categorie>" \
    --book <BOEK> --limit 5
```

Als `output/META/decisions.jsonl` ontbreekt:

```bash
uv run python scripts/extract_decisions.py --root output --book <BOEK>
```

Decision-hits mogen een eerdere rebuttal-context leveren, maar nemen de
bewijslast niet over. Elke nieuwe rebuttal moet nog steeds aan de
criteria hieronder voldoen met versspecifiek regel- of brontekstbewijs.

Doe twee dingen:

### 2a. Aanvullende issues vinden

De scanner is regex-gebaseerd en mist contextgevoelige overtredingen.
Loop het hoofdstuk vers-voor-vers door en flag eigen vondsten in deze
categorieën die de regex niet vangt:

- **Idiomatische Latinaat-resten** zoals "het is geschiedt", "het
  geviel", "voorwaar zeg ik u" (afhankelijk van reikwijdte). Citeer letterlijk
  + regelreferentie.
- **Drempel-archaïsmen** uit §2.7 die niet in `DREMPEL_ARCHAISMEN`
  staan: woorden die de productiviteits- of verwarringtest zakken.
- **Kanttekening-redundantie** die niet als 4-token-sliding-window-match
  is opgepikt: parafrastische herhaling van de hoofdtekst.
- **Concordantietwijfel met bewijs**: na `scripts/memory.py query`
  blijkt dat eerdere boeken/hoofdstukken hetzelfde origineel-woord
  consistent anders weergeven. Voeg de match toe als bewijs.
- **Verbogen-lidwoord-fossielen**: de scanner flagt élk `der/des/den +
  woord` als hard. Voor gevallen die in modern bijbels Nederlands
  productief zijn (`Zoon des mensen`, `Koninkrijk der hemelen`,
  `vrees des Heeren`) is een rebuttal mogelijk — maar alleen met
  expliciet fossiel-argument plus regel-/Grieks-referentie. Een
  rebuttal als "vaste bijbeluitdrukking" zonder bron faalt verify.

Voeg elke nieuwe issue toe aan `output/<BOEK>/review.<H>.json`:

```python
import json, datetime
path = "output/LUK/review.8.json"
data = json.load(open(path))
verse = 24
existing_for_verse = sum(1 for i in data["issues"] if i["verse"] == verse) + 1
data["issues"].append({
    "id": f"LUK-8-{verse}-{existing_for_verse:03d}",
    "verse": verse,
    "category": "§2.7 drempel-archaïsme",
    "severity": "hard",
    "quote_modernized": "...vermits hij sliep...",
    "rule_reference": "MODERNISATIE.md §2.7",
    "explanation": "'vermits' faalt productiviteitstest (niet meer in modern zakelijk NL).",
    "proposed_fix": "...omdat hij sliep...",
    "location": "hoofdtekst",
    "status": "open",
})
json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
open(path, "a").write("\n")
```

### 2b. Pre-scan-issues kritisch wegen

Voor elk pre-scan-issue: lees de quote in context, oordeel of het
echt een overtreding is. Acceptabel = `status: "rebutted"` met een
substantief argument; default blijft `status: "open"`.

**Rebuttal-criteria (hard)** — een rebuttal is alleen substantief als
hij minstens twee van:

- Verwijst naar regel (`§2.3`, `§2.7`, `KANTTEKENINGEN.md`,
  `MODERNISATIE.md`, etc.) of een concrete Griekse term (bv.
  `λέγων`, `ἰδών`).
- Geeft een vers-specifiek argument (de constructie is hier
  attributief, of de uitdrukking is gestold zoals 'vallende ziekte').
- Onderscheidt zich van de andere issues (rebuttal kan niet identiek
  toegepast worden op alle pre-scan-hits in de batch).

Standaardformules zoals "we behouden SV-stijl", "formele equivalentie",
"geen actie nodig" zonder verdere onderbouwing zijn **niet**
voldoende. De `verify`-pass gooit ze terug op `reopened`.

Issues die de skill zelf met bewijs kan weerleggen in deze stap, zet
direct op `rebutted` met de juiste rebuttal in het JSON-veld:

```python
issue["status"] = "rebutted"
issue["rebuttal"] = (
    "'vallende ziekten' (LUK 8:29 kanttekening) is een gestolde "
    "uitdrukking voor epilepsie (vgl. WNT 'vallende ziekte') — niet "
    "een adverbiaal participium. §2.3 geldt niet voor lexicale "
    "fossielen die als zelfstandig adjectief functioneren."
)
```

## Stap 3 — eindrapport ronde 1

Schrijf 4-8 regels naar de orchestrator:

```
Adversarial review LUK 8 (pass 1):
- 12 issues open: 4× §2.3b, 1× §2.7, 7× concordantie-drift
- 3 issues vooraf gerebuteerd door de beoordelaar (gestolde uitdrukkingen)
- Pad: output/LUK/review.8.json
Orchestrator: kies per open issue fix of rebuttal, daarna verify.
```

## Stap 4 — orchestrator-acties (binnen orchestrator-flow)

De orchestrator (niet deze skill) doet per `open` issue:

1. **Fix-pad**: pas `output/<BOEK>/<BOEK>.<H>.json` aan (Edit-tool).
   Re-validate via `scripts/validate.py check` op het gewijzigde vers.
   Update `review.<H>.json`:
   ```python
   issue["status"] = "fixed"
   issue["fix_commit"] = "<sha-na-commit>"  # vul in na commit
   ```
2. **Rebuttal-pad**: zet `status: "rebutted"` met `rebuttal: "<argument>"`
   conform de criteria boven.

Commit alle fixes in één branch:
`feature/<boek>-<h>-adversarial-fix`. PR + merge volgens
`sv-batch-orchestrate` Stap 5.

## Stap 5 — verify en eindrapport ronde 2

Wanneer alle open issues zijn afgehandeld, open `references/verify_protocol.md`. Dat detailprotocol bevat het verify-commando, de heropeningscriteria, de verplichte tweede pass en het eindrapportformaat.
