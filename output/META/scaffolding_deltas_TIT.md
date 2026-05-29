# Scaffolding-deltas — meta-review TIT hoofdstukken 1-3

Gegenereerd: 2026-05-29T04:50:21Z
Aggregator: scripts/meta_diff_aggregate.py --book TIT --chapters 1-3 --min-freq 2

> **Hoofdbevinding:** op de voorgeschreven `--min-freq 2` levert de
> aggregator **0 patterns** (`total_patterns: 0`). TIT 1-3 is te kort
> voor cross-chapter recurrentie; vrijwel elk verschil komt één keer voor.
> Een controle-run op `--min-freq 1` toont 38 single-occurrence patterns
> (carryover 9, latinaat-window 20, cap-asym 9), alle `frequency: 1` en
> `severity_hint: soft`. Hieronder zijn die freq-1-patterns gewogen voor
> volledigheid; de bucket-B/C-classificatie is uitgevoerd los van de
> harde freq≥2-poort omdat een residu-archaisme óók bij freq=1 een
> gemiste fix is.

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| _(geen)_ | — | — | — | Geen pattern haalt freq ≥ 3 over TIT 1-3; geen scaffolding-gap aantoonbaar als recurrent. | — |

## VOORSTEL — kandidaat bucket-C-deltas (NIET uitgevoerd; analyse-modus)

Geen kandidaat haalt de freq≥3-drempel van een scaffolding-gap. Eén
borderline-geval is opgenomen als **voorstel** ter overweging bij een
latere multi-boek-meta-review (gecombineerd met andere Paulusbrieven),
mét 3 bewijs-citaten. Toepassing nu afgeraden: enkel 1 occurrence in TIT.

| Pattern | Kind | Voorstel-target | Wijze | Bewijs-citaten (3) | §2.7-oordeel |
|---|---|---|---|---|---|
| `wederleggen` → `weerleggen` | carryover | `DREMPEL_ARCHAISMEN` in `scripts/rules_data.py` + rij in `ARCHAISMEN.md` (weder- > weer-) | Edit (alleen bij ≥3 over meerdere boeken) | (1) TIT 1:9 hoofdtekst: "de tegensprekers ... te **wederleggen**" — archaisch behouden. (2) TIT 1:11 kanttekening: "met **weerlegging** van hun valse leringen" — modern toegepast door dezelfde modernisatie (SV-interne inconsistentie). (3) HSV TIT 1:9: "de tegensprekers te **weerleggen**". | Slaagt: productiviteit (weerleggen is courant zakelijk NL), constructie (werkt identiek), verwarring (geen dominante andere betekenis). Toch NIET nu auto-toepassen: freq=1 binnen TIT; behandeld als bucket-B per-vers-fix i.p.v. regel-delta. |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `nuchter` (TIT 2:2) | carryover | Geen archaisme: 'nuchter' is courant modern Nederlands; HSV 'beheerst' is een concordantie-/parafrasekeuze, geen bewijs van drempel-archaisme. Bucket A. |
| `betaamt`, `bezonnen`, `vermaan`, etc. (latinaat-window 2:x/3:x) | latinaat-window | Verschil = HSV-herschikking/synoniemkeuze, geen aantoonbaar Latinaat-residu in SV2026. Bucket A. |
| `fabelen`, `onderwijst`, `vechters`, `overwinteren`, `ontbreke` | carryover | Eenmalig; modern alternatief is HSV-parafrase of stilistische keuze, geen drempel-archaisme. Geen recurrentie. Bucket A. |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym | 9 | "Apostel"/"Dienstknecht" (TIT 1:1), "Opziener" (1:7), "Ouderlingen" (1:5), "Profeet" (1:12), "Overheden"/"Machten" (3:1), "Wetgeleerde" (3:13), "Daarom" (1:13). Alle = SV-interne ambts-/rol-/reverence-caps of zinsbegin; HSV lowercaset. Geen toegevoegde reverence-cap → behouden. |
| latinaat-window | 20 | "betaamt dat zij geen lasteressen" (2:3), "geen vechters zijn maar inschikkelijk" (3:2), "want heb daar voorgenomen overwinteren" (3:12), "goede werken voor staan tot" (3:14). Alle freq=1; HSV-herschikkingen. |
| carryover (freq=1, niet-archaisch) | 8 | "fabelen" (1:14), "nuchter" (2:2), "onderwijst" (2:12), "vechters" (3:2), "overwinteren"/"nicopolis" (3:12), "ontbreke" (3:13), "lasteressen" (2:3). |

## Bucket-overzicht

- B (per-vers fixes): 1 issue over 1 hoofdstuk (TIT 1:9 `wederleggen`→`weerleggen`) — zie `findings_TIT.json`
- C (scaffolding-deltas): 0 toegepast, 0 afgewezen-op-§2.7; 1 VOORSTEL gelogd (freq onvoldoende voor regel-delta binnen TIT alleen)
- A (noise): 37 (cap-asym 9, latinaat-window 20, carryover-niet-archaisch 8) van de 38 freq-1-patterns
