# Scaffolding-deltas — meta-review 2TH hoofdstukken 1-3

Gegenereerd: 2026-05-29T00:00:00Z
Aggregator: scripts/meta_diff_aggregate.py --book 2TH --chapters 1-3 --min-freq 2

## Samenvatting

Bij de verplichte drempel `--min-freq 2` levert de aggregator **0 cross-chapter
patronen** op. 2TH is een kort boek (3 hoofdstukken); elk van de 29 ruwe
patronen (zichtbaar bij `--min-freq 1`) komt precies **één keer** voor en haalt
de recurrentie-drempel niet. Per de SKILL-criteria betekent dit:

- carryover `frequency == 1` (< 2) → bucket A (geen consistent recurrent HSV-alternatief over hoofdstukken)
- latinaat-window enkele HSV-herschikking → bucket A
- cap-asym enkele SV1657-interne keuze → bucket A

Geen enkel patroon bereikt bucket B (vereist `frequency == 2`) of bucket C
(vereist `frequency >= 3`). Daarom: geen findings, geen scaffolding-deltas,
geen VOORSTEL-tabel. Alles is noise (bucket A).

Aanvullende controle uitgevoerd (root-cause): de in het oog springende
carryover-kandidaten (`gewrocht` 2:7, `verdoen`/`ongerechtige` 2:8,
`vertrooste` 2:17, `geve` 3:16) zijn getoetst tegen `DREMPEL_ARCHAISMEN` in
`scripts/rules_data.py` — **geen** ervan staat op de drempellijst, dus er is
geen scaffolding-gap (een al-gelijste term die door de lint ontsnapt). De
decision-memory hit voor `geve` (2TH-3-16-001, `§2.3b`, status `rebuttal`)
bevestigt adviserend dat `de Heere ... geve u vrede` een bewuste, eerder
verdedigde keuze is (indirect object bij finiet werkwoord, Griekse datief
ὑμῖν). HSV-bewijs alleen is hier nooit normatief geweest.

## Auto-toegepaste deltas (bucket C)

| Pattern | Kind | Freq | Target | Wijziging | Bewijs |
|---|---|---|---|---|---|
| _(geen)_ | — | — | — | Geen patroon haalt freq >= 3 bij min-freq 2 | — |

## Voorstel-deltas (bucket C — NIET uitgevoerd, analyse-modus)

| Pattern | Kind | Freq | Voorstel | Bewijs (3 citaten) |
|---|---|---|---|---|
| _(geen)_ | — | — | Geen kandidaat bereikt de bucket-C-drempel | — |

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| _(geen)_ | — | Geen patroon kwam in aanmerking voor §2.7-toets (alle freq == 1) |

## Noise (bucket A — HSV-keuze / enkele occurrence, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| latinaat-window | 21 | "broeders staat vast houdt inzettingen" (2:15), "geve vrede allen tijde" (3:16), "verlost worden van onredelijke boze" (3:2) — HSV-herschikkingen, geen Latinaat-rest in SV2026 |
| carryover | 5 | "geve" (3:16, rebuttal §2.3b), "gewrocht" (2:7), "verdoen"/"ongerechtige" (2:8), "vertrooste" (2:17) — alle freq 1, niet op DREMPEL_ARCHAISMEN |
| cap-asym | 3 | "Gemeente" (1:1), "Gemeenten" (1:4), "Engelen" (1:7) — SV1657-interne hoofdletterkeuze, eerbieds-/instelling-cap |

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken — zie `findings_2TH.json` (leeg)
- C (scaffolding-deltas): 0 toegepast, 0 voorgesteld, 0 afgewezen
- A (noise): 29 (latinaat-window 21, carryover 5, cap-asym 3) — bij min-freq 2 allemaal sub-drempel
