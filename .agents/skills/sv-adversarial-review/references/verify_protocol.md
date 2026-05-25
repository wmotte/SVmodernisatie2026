# sv-adversarial-review — verify-protocol

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
