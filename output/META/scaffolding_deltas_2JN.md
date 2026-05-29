# Scaffolding-deltas — meta-review 2JN hoofdstuk 1

Gegenereerd: 2026-05-29T04:49:38Z
Aggregator: scripts/meta_diff_aggregate.py --book 2JN --chapters 1 --min-freq 2

2JN telt slechts 1 hoofdstuk; met `--min-freq 2` levert de aggregator
exact 1 pattern op (carryover `zijt`, freq=2). Geen fossiel-lidwoord,
latinaat-window of cap-asym boven de drempel.

## Auto-toegepaste deltas (bucket C)

Geen. Het enige pattern (`zijt`, freq=2) haalt de bucket-C-drempel
(carryover freq ≥ 3 met consistent HSV-modern alternatief) niet en is
bovendien als noise geclassificeerd (zie hieronder). Geen regel-edit.

## Voorgestelde deltas (bucket C — VOORSTEL, niet uitgevoerd)

Geen bucket-C-voorstellen. Het enige pattern valt onder bucket A.

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

Geen kandidaat-delta bereikte de §2.7-toets-fase (geen bucket-C-kandidaat).

## Noise (bucket A — HSV-keuze / vrije syntaxis, geen actie)

| Kind | Aantal | Voorbeelden | Motivatie |
|---|---|---|---|
| carryover | 1 | `zijt` — "Zijt gegroet" (2JN 1:10, 1:11) | Vaste groetformule (Grieks χαίρειν, in de kanttekening v10 geglosseerd als "blijde zijn"). "Zijt gegroet" is een herkenbaar staand idioom in modern NL (vgl. "Wees gegroet"); de constructie werkt modern. HSV lost de directe-rede-groet op in de omringende zin ("begroet hem niet" v10; collaps in v11) — een vrije syntactische herschikking, geen consistent lexicaal modern alternatief voor `zijt`. Geen gemiste modernisatie. |

### Onderbouwing classificatie `zijt` → bucket A

- **Frequentie/severity**: carryover, freq=2, severity_hint=soft. `zijt`
  staat niet in `DREMPEL_ARCHAISMEN` (geverifieerd in `scripts/rules_data.py`).
- **Geen consistent HSV-alternatief**: HSV v10 → "begroet"; HSV v11 →
  parafrase zonder eigen groetwoord. Twee verschillende, parafraserende
  oplossingen → carryover-criterium "geen consistent HSV-alternatief →
  bucket A".
- **Idioom**: `zijt` komt uitsluitend voor binnen de bevroren groet
  "Zijt gegroet"; het is geen vrij finiet werkwoord in moderne prozazin.
- **§2.7 (adviserend, niet beslissend hier)**: productiviteits- en
  constructie-test slagen ("Wees/Zijt gegroet" is hedendaags herkenbaar);
  geen verwarrende dominante nevenbetekenis. Renovatie ≠ hervertaling —
  geen reden de staande groet te herschrijven.

## Bucket-overzicht

- B (per-vers fixes): 0 issues over 0 hoofdstukken — zie `findings_2JN.json` (issues: [])
- C (scaffolding-deltas): 0 toegepast, 0 voorgesteld, 0 afgewezen
- A (noise): 1 (carryover `zijt`)
