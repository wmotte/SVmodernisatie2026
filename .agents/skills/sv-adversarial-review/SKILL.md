---
name: sv-adversarial-review
description: Adversariële beoordelaar per hoofdstuk. Schrijft een bevindingenlijst (output/<BOEK>/review.<H>.json) waarop de orchestrator MOET reageren — fixen of inhoudelijk weerleggen. Uitgangspunt is overtreding; luiheid wordt gestraft. Roep aan na CHAPTER_COMPLETE binnen sv-batch-orchestrate, of expliciet ("review hoofdstuk 8" / "adversarial review LUK 8"). Twee modi: scan (eerste ronde) en verify (tweede ronde na fixes/weerleggingen).
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

## Stap 5 — verify (ronde 2)

Wanneer alle `open` issues zijn afgehandeld (status `fixed` of
`rebutted`), draai de verifier:

```bash
uv run python scripts/adversarial_scan.py verify \
    --book <BOEK> --chapter <H> --terse
```

De verifier controleert:

- **Voor elke `fixed` issue**: scan het vers opnieuw op zijn categorie. Als
  het patroon nog matcht → `status: "reopened"` met
  `verify_note: "fix loste het patroon niet op"`.
- **Voor elke `rebutted` issue**: beoordeel de weerlegging. Criteria voor heropening:
  - weerlegging leeg
  - weerlegging < 60 tekens
  - weerlegging valt terug op luie formules zonder regel-/Grieks-referentie
  - weerlegging noemt geen regel én geen vers-specifiek argument
- Niet-gereopende rebuttals krijgen `status: "verified"` met
  `verified_at`.

Stdout: JSON-samenvatting met `by_status` en `actions`.
Exit-code 0 als geen `open`/`reopened` meer; 1 anders.

## Stap 6 — eindrapport ronde 2

```
Adversarial review LUK 8 (pass 2 / verify):
- 8 fixed → verified
- 3 rebutted → verified
- 1 rebutted → reopened (luie formule, geen Grieks/regel-ref)
- Geen open issues meer? Hoofdstuk klaar voor eindrapportage.
```

Bij `reopened` issues gaat de orchestrator nog één ronde fix/rebuttal
doen (max 2 fix-rondes totaal). Daarna belanden resterende issues in
het hoofdstuk-eindrapport.

## Issue-tracker schema

`output/<BOEK>/review.<H>.json`:

```json
{
  "book": "LUK",
  "chapter": 8,
  "reviewed_at": "2026-05-10T12:00:00+00:00",
  "passes": [
    {"pass": 1, "ran_at": "...", "mode": "scan", "issues_total": 12},
    {"pass": 2, "ran_at": "...", "mode": "verify", "actions": [...]}
  ],
  "issues": [
    {
      "id": "LUK-8-24-001",
      "verse": 24,
      "category": "§2.3 finiet participium",
      "severity": "hard",
      "quote_modernized": "...zeggende: Meester, ...",
      "rule_reference": "MODERNISATIE.md §2.3",
      "explanation": "...",
      "proposed_fix": "...zeiden: Meester, ...",
      "location": "hoofdtekst",
      "status": "fixed",
      "fix_commit": "abc1234"
    },
    {
      "id": "LUK-8-29-002",
      "verse": 29,
      "category": "kanttekening-luiheid (§2.3 in <…>)",
      "status": "rebutted",
      "rebuttal": "'vallende ziekte' is gestolde uitdrukking voor epilepsie (WNT) — geen adverbiaal participium. §2.3 geldt niet voor lexicale fossielen die als zelfst. adjectief functioneren.",
      "verified_at": "2026-05-10T12:30:00+00:00"
    }
  ]
}
```

`status` ∈ `{open, fixed, rebutted, verified, reopened}`.

## Waarborgen tegen luiheid

Deze skill bestaat omdat eerdere reviews te zacht waren. Concrete
waarborgen:

- **Uitgangspunt = overtreding**. Het feit dat een issue is gemarkeerd is
  voldoende reden om hem als open te behandelen.
- **Geen waarschuwingslaag**. Statussen zijn `open / fixed / rebutted /
  verified / reopened`. Geen "OK met opmerking".
- **Rebuttal moet substantief zijn**. Verifier reopent rebuttals die
  alleen leunen op stijl-formules ("formele equivalentie",
  "SV-eigenheid").
- **Verificatieronde is automatisch**. Orchestrator kan geen open issues
  doorlaten — `verify` exit-code blokkeert eindrapportage als er nog
  `open`/`reopened` zijn.
- **Skill is verplicht in orchestrator-flow**. `sv-batch-orchestrate`
  Stap 6.5 roept hem aan; overslaan = schending van de reikwijdte.

## Categorieën die de scanner dekt

| Categorie | Source | Severity |
|---|---|---|
| §2.3 finiet participium (`-ende`) | `validate.py` always-bad + context + adversarial fallback | hard / soft |
| §2.3 finiet participium (`-end,`) | `validate.py` PARTICIPLE_BAD_END_STEMS | hard |
| §2.3b passief van zien | regex `\b(werd\|is\|wordt)\s+\w*gezien\b` | hard |
| §2.3b vocatief-u | regex aan clause-begin | soft |
| §2.3b bijwoord-coda (`…lijk[.,;:]`) | regex aan zinseind | soft |
| §2.3b infinitief met nageschoven object | regex `om … te VERB OBJECT` | soft |
| §2.7 drempel-archaïsmen | `DREMPEL_ARCHAISMEN` lijst | soft |
| verbogen lidwoord (der/des/den) | `\b(der\|des\|den)\s+\w+` (excl. `des te`, `Den <toponiem>`) — hoofdtekst + kanttekening | hard |
| SV-verbuiging (eenen/eener) | `\b(eenen\|eener\|eenes)\s+\w+` — verbogen onbep. lidwoord | hard |
| SV-verbuiging (demonstratief dezer/dien/...) | `\b(dezer\|dezes\|dezen\|dien\|dier\|gener\|genen)\s+\w+` (whitelist `dezer dagen`, `te dien einde`) | hard |
| archaïsch pronomen (dezelve/denzelven) | `\bden?zelve[nrs]?\b` — anaforisch `dezelve`, niet te verwarren met `dezelfde` | hard |
| archaïsch demonstratief (de gene) | `\bde\s+gene[nr]?\b`, `\bdengenen?\b` | soft |
| reflexief hem/haar (→ zich) | whitelist van werkwoordsvormen die in modern NL altijd reflexief zijn (bekeren/verheugen/voorzien/...) | hard |
| aanvoegende wijs (gebod) | `\b(die\|wie\|hij\|...)\s+(neme\|geve\|kome\|...)` — whitelist van bekende subjunctief-vormen | soft |
| dubbele negatie met clitisch en | `\b(niet\|geen\|...)\b ... \ben\s+\w+(t\|de\|den\|en)\b` — alleen hard bij direct opeen `niet en V` | hard / soft |
| voornaamwoordelijk bijwoord gesplitst | `\b(daar\|waar\|hier\|er)\s+(in\|aan\|op\|...)` mits niet gevolgd door lidwoord/voornaamwoord/numeriek | hard |
| SV-spelling-residu (-inge/-isse/-erye) | `\b\w+(?:inge\|isse\|erye)\b` (whitelist `geringe`/`enige`) | hard |
| diminutief op -ken/-kens | literal lemma-lijst (`kindeken`, `kinderkens`, `mannekens`, ...); regex te breed (false positives op `spreken`/`koninkrijken`) | hard |
| relativum welke/welken/hetwelk | na komma of voorzetsel (relatieve context); niet in vraagzinnen | soft |
| genitief pronomen wiens/wier | `\b(wiens\|wier)\s+\w+` (excl. `zeewier` etc. via context-check) | hard |
| concordantie-drift cross-vers | prefix-overlap heuristiek | soft |
| kanttekening-luiheid (-ende in <…>) | regex binnen kanttekening, uitgangspunt = overtreding (élk niet-attributief -ende) | hard / soft |
| kanttekening-luiheid (SV-archaisme in <…>) | `KANTTEKENING_ARCHAISMEN` regex | hard |
| kanttekening-redundantie | 4-token sliding window match hoofdtekst | soft |
| validator-leak | `validate.py ARCHAISM_BLACKLIST` re-match | hard |

## Foutgevallen

- **Output JSON ontbreekt**: scanner exit 2 met error-JSON. Stop, meld
  dat het hoofdstuk niet bestaat.
- **review.<H>.json corrupt**: gebruik `--fresh` om vanaf nul te
  beginnen. Status-historie gaat dan verloren — orchestrator moet
  alle fixes/rebuttals opnieuw doorlopen.
- **Verifier vindt issues open na 2 fix-rondes**: rapporteer in
  hoofdstuk-eindrapport, beschouw hoofdstuk als "klaar met X
  resterende issues"; orchestrator stopt loop.
- **Concordantie-drift-hits voelen als ruis**: ze zijn `soft`. De
  in-context skill kan ze in batch rebutten met één gedeelde
  motivatie ("origineel-stam X dekt verschillende contexten:
  bewuste woordkeuze") — die rebuttal moet wel per issue de
  vers-specifieke context noemen om verify niet te falen.
