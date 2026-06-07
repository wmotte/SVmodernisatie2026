# Red-Green Dekkingsplan

Doel: alle volledig gemoderniseerde NT-boeken dekkend door red-green halen,
met genoeg cross-book druk om echte concordantie- en modernisatieproblemen te
vinden, maar zonder eindeloos rond te draaien op dezelfde grote boeken.

Laatste nulmeting: 2026-06-07.

- `rounds_done`: 16
- `closed_keys`: 108
- `open_keys`: 0
- laatste paren: `MAT+ROM`, `ACT+JHN`, `2JN+3JN`
- automatische volgende selector-keuze: ronde 17 `REV+ACT`

## Werkregel

- [ ] Gebruik dit plan als dekkingslaag bovenop `sv-red-green`.
- [ ] Lees per sessie alleen compacte notulen via scripts, niet het hele
      `minutes.md` inline:
      `uv run python scripts/redgreen_minutes.py summary`
- [ ] Laat red geen quota vullen: minder dan 10 punten, of 0 punten, is geldig.
- [ ] Herhaal geen gesloten punten: geef red altijd de output van
      `uv run python scripts/redgreen_minutes.py closed-keys`.
- [ ] Green wint alleen met een inhoudelijke rebuttal die de gate haalt
      (minstens 2 van: concrete regel/Grieks, versspecifiek argument,
      onderscheidend argument).
- [ ] Pas alleen `red_wins` en `rule_change` toe.
- [ ] Schrijf na elke ronde notulen weg; een ronde zonder append telt niet als
      afgewerkt.

## Fase 1 - Basisdekking Afdwingen

Werkset van volledig beschikbare boeken:

`1CO, 1JN, 1PE, 1TH, 1TI, 2CO, 2JN, 2PE, 2TH, 2TI, 3JN, COL, EPH, GAL, HEB, JAS, JHN, JUD, LUK, MAT, MRK, PHM, PHP, REV, ROM, TIT`

Nog nooit besproken bij de nulmeting:

`1JN, 1PE, 1TH, 1TI, 2PE, 2TH, 2TI, COL, EPH, GAL, HEB, JAS, JUD, PHM, PHP, TIT`

Draai eerst deze handmatige paren voordat `redgreen_select.py` weer leidend
wordt:

- [ ] Ronde 17: `PHM + JUD`
- [ ] Ronde 18: `1JN + 2PE`
- [ ] Ronde 19: `1PE + JAS`
- [ ] Ronde 20: `1TH + 2TH`
- [ ] Ronde 21: `1TI + 2TI`
- [ ] Ronde 22: `COL + EPH`
- [ ] Ronde 23: `GAL + PHP`
- [ ] Ronde 24: `HEB + TIT`

Acceptatie voor Fase 1:

- [ ] Alle 26 volledige boeken staan minstens 1x in `debate_count`.
- [ ] `open_keys` is nog steeds `0`.
- [ ] Alle `round_<N>.json`-bestanden hebben red, green en verdicts.
- [ ] Alle toegepaste verdicts hebben `applied: true`.
- [ ] `uv run python scripts/redgreen_minutes.py summary` toont geen anomalieën.

## Fase 2 - Clusterdekking

Na de basisdekking moeten inhoudelijk verwante boeken nog tegen elkaar worden
gezet. Sla een paar alleen over als de vorige ronde op exact dat paar niets
nieuws opleverde.

Johannes-cluster:

- [ ] `JHN + 1JN`
- [ ] `1JN + 2JN`
- [ ] `2JN + 3JN` alleen herhalen bij nieuwe aanwijzingen.

Paulus korte brieven:

- [ ] `EPH + COL`
- [ ] `PHP + PHM`
- [ ] `1TH + 2TH`
- [ ] `1TI + 2TI`
- [ ] `TIT + PHM`

Algemene brieven:

- [ ] `JAS + 1PE`
- [ ] `1PE + 2PE`
- [ ] `JUD + 2PE`
- [ ] `HEB + JAS`

Grote-boek kalibratie:

- [ ] `ACT + ROM`
- [ ] `MAT + MRK`
- [ ] `LUK + ACT`
- [ ] `REV + JUD`
- [ ] `REV + 2PE`

Acceptatie voor Fase 2:

- [ ] Elk cluster hierboven is afgewerkt of gemotiveerd overgeslagen.
- [ ] Minstens 3 rondes bevatten expliciete `consistentie`-punten of een
      gemotiveerd red-verdict dat er geen nieuwe consistentiepunten waren.
- [ ] Kanttekeningen zijn in red-prompts expliciet meegenomen
      (`in_kanttekening` waar relevant).

## Fase 3 - Worst-First Naloop

Wanneer Fase 1 en Fase 2 klaar zijn, laat de selector weer kiezen:

- [ ] Draai `uv run python scripts/redgreen_select.py`.
- [ ] Neem het voorgestelde paar over, tenzij het exact net is afgerond zonder
      nieuwe punten.
- [ ] Draai standaard 3 selector-rondes.
- [ ] Stop eerder als red in een ronde 0 nieuwe punten vindt.
- [ ] Draai 2 extra selector-rondes als een van de 3 rondes een `rule_change`
      oplevert, omdat een regelwijziging NT-brede neveneffecten kan hebben.

Acceptatie voor Fase 3:

- [ ] De laatste selector-sessie van 3 rondes levert samen minder dan 3
      `red_wins` op, of red levert een ronde met 0 nieuwe punten.
- [ ] Geen nieuw `rule_change`-verdict staat nog open.

## Per-Ronde Checklist

Gebruik deze lijst voor elke handmatige of selector-ronde.

Voorbereiding:

- [ ] Initialiseer notulen idempotent:
      `uv run python scripts/redgreen_minutes.py init`
- [ ] Lees status:
      `uv run python scripts/redgreen_minutes.py summary`
- [ ] Bepaal `N = rounds_done + 1`.
- [ ] Kies `B1+B2` uit dit plan of via:
      `uv run python scripts/redgreen_select.py`
- [ ] Haal closed keys op:
      `uv run python scripts/redgreen_minutes.py closed-keys`

Concordantie-seed:

- [ ] Genereer concordantie voor body en kanttekeningen:
      `uv run python scripts/redgreen_concord.py --books <B1> <B2> --layer both --top 25 --out output/META/debate/concord_<N>.json`
- [ ] Geef het concord-bestand als seed aan red; beoordeel de seed niet in de
      orchestrator zelf.

Red:

- [ ] Laat red maximaal 10 nieuwe punten schrijven naar
      `output/META/debate/round_<N>.json`.
- [ ] Eis per punt: `class`, `books`, `chapter`, `verse`, `quote`,
      `rule_reference`, `explanation`, `proposed_fix`, `severity`.
- [ ] Eis `in_kanttekening: true` bij punten uit `<...>`-blokken.
- [ ] Controleer dat red geen `point_key` uit closed-keys herhaalt.

Green:

- [ ] Laat green elk punt pareren of conceden in hetzelfde round-bestand.
- [ ] Verwerp boilerplate-rebuttals zoals alleen "SV-stijl" of alleen
      HSV-bewijs.
- [ ] Tel `rebut` en `concede`.

Arbiter:

- [ ] Laat arbiter mechanisch beslissen: `red_wins`, `green_wins` of
      `rule_change`.
- [ ] Zet elk verdict initieel op `applied: false`.
- [ ] Tel verdicts en noteer de aantallen.

Apply:

- [ ] Pas `rule_change` eerst toe in de bronbestanden uit `REGELBESTANDEN.md`
      (`scripts/rules_data.py`, `scripts/stoplist.txt`, documentatie waar nodig).
- [ ] Draai daarna een gerichte of NT-brede sweep; geen silent cap op
      geraakte verzen.
- [ ] Pas `red_wins` per geraakt vers toe, inclusief sweep-treffers uit
      `rule_change`.
- [ ] Gebruik bij content-fixes de gewone modernisatie- en validatieregels;
      herschrijf geen JSON met ad-hoc scripts.
- [ ] Markeer alleen echt uitgerolde verdicts als `applied: true`.

Validatie per geraakt hoofdstuk:

- [ ] Valideer de gewijzigde verzen:
      `uv run python scripts/validate.py check --input input.sv/<B>/<B>.<H>.json --output output/<B>/<B>.<H>.json --verses <V> --sections intro,epilogue --terse`
- [ ] Draai gerichte linters:
      `uv run python scripts/lint_all.py --root output/<B> --terse`
- [ ] Voeg gewijzigde verzen toe aan memory:
      `uv run python scripts/memory.py add --from-output output/<B>/<B>.<H>.json --verse <V> --terse`
- [ ] Regenereer HSV-diffs:
      `uv run python scripts/compare_hsv.py <B> <H>`
- [ ] Bij twijfel over semantiek: laat `sv-semantic-review` op het vers of de
      kleine range lopen.

Afronding:

- [ ] Append notulen:
      `uv run python scripts/redgreen_minutes.py append --round output/META/debate/round_<N>.json`
- [ ] Controleer status:
      `uv run python scripts/redgreen_minutes.py summary`
- [ ] Controleer git-status en commit/merge alleen wanneer dat expliciet is
      gevraagd of binnen een workflow valt die dat toestaat.
- [ ] Eindrapport bevat: paar, ronde, red-punten, verdicts, toegepaste fixes,
      validatie, lint, memory, HSV-diffs en blokkades.

## Eindcriteria

Minimale dekking:

- [ ] Alle 26 volledige NT-boeken zijn minstens 1x besproken.
- [ ] Geen `open_keys`.
- [ ] Geen onafgewerkte `red_wins` of `rule_change`.

Goede dekking:

- [ ] Fase 1 is volledig afgerond.
- [ ] Fase 2 is volledig afgerond of per overgeslagen paar gemotiveerd.
- [ ] Alle kleine brieven zitten minstens 1x in een inhoudelijk passend
      cluster.

Sterke dekking:

- [ ] Fase 3 is afgerond.
- [ ] Laatste 3 selector-rondes leveren samen minder dan 3 `red_wins` op, of
      red vindt in een ronde 0 nieuwe punten.
- [ ] `uv run python scripts/lint_all.py --root output --terse` eindigt met
      `[OK] All linters passed`.
- [ ] Er is een laatste compact eindrapport in `output/META/debate/minutes.md`
      via de normale append-flow.

## Statuslog

Vul dit handmatig bij na elke afgeronde ronde.

- [ ] R17 `PHM+JUD` - status:
- [ ] R18 `1JN+2PE` - status:
- [ ] R19 `1PE+JAS` - status:
- [ ] R20 `1TH+2TH` - status:
- [ ] R21 `1TI+2TI` - status:
- [ ] R22 `COL+EPH` - status:
- [ ] R23 `GAL+PHP` - status:
- [ ] R24 `HEB+TIT` - status:
- [ ] Cluster Johannes - status:
- [ ] Cluster Paulus kort - status:
- [ ] Cluster algemene brieven - status:
- [ ] Grote-boek kalibratie - status:
- [ ] Worst-first naloop - status:
