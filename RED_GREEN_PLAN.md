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

- [x] Ronde 17: `PHM + JUD`
- [x] Ronde 18: `1JN + 2PE`
- [x] Ronde 19: `1PE + JAS`
- [x] Ronde 20: `1TH + 2TH`
- [x] Ronde 21: `1TI + 2TI`
- [x] Ronde 22: `COL + EPH`
- [x] Ronde 23: `GAL + PHP`
- [x] Ronde 24: `HEB + TIT`

Acceptatie voor Fase 1:

- [x] Alle 26 volledige boeken staan minstens 1x in `debate_count`.
- [x] `open_keys` is nog steeds `0`.
- [x] Alle `round_<N>.json`-bestanden hebben red, green en verdicts.
- [x] Alle toegepaste verdicts hebben `applied: true`.
- [x] `uv run python scripts/redgreen_minutes.py summary` toont geen anomalieën.

## Fase 2 - Clusterdekking

Na de basisdekking moeten inhoudelijk verwante boeken nog tegen elkaar worden
gezet. Sla een paar alleen over als de vorige ronde op exact dat paar niets
nieuws opleverde.

Johannes-cluster:

- [x] `JHN + 1JN` — R25 (7 red_wins)
- [x] `1JN + 2JN` — R26 (1 red_wins + 2 rule_change + 1 verse-fix)
- [x] `2JN + 3JN` — R27 (1 red_wins nt-wide: kanttekening-opener-norm)

Paulus korte brieven:

- [x] `EPH + COL` — gedekt door R22 (COL+EPH)
- [ ] `PHP + PHM`
- [x] `1TH + 2TH` — gedekt door R20
- [x] `1TI + 2TI` — gedekt door R21
- [x] `TIT + PHM` — R29 (2 red_wins + 1 rule_change deftig + 1 green_wins)

Algemene brieven:

- [x] `JAS + 1PE` — gedekt door R19
- [x] `1PE + 2PE` — R30 (7 red_wins + 2 rule_change: weersta→IMPERATIVE_T_STEMS, metterdaad→DREMPEL)
- [x] `JUD + 2PE` — R31 (4 red_wins: imperatief JUD 1:22, bibref-proza JUD 1:14, consistentie οὗτοί εἰσιν JUD↔2PE, Latinaat 2PE 2:1)
- [x] `HEB + JAS` — R32 (5 red_wins: 4× §2.3 finiet-participium HEB 13:21/8:8/13:7 + JAS 1:22, geenszins-note JAS 4:17)

Grote-boek kalibratie:

- [x] `ACT + ROM` — R33 (8 red_wins: 6× didactisch leren→onderwijzen, rechten→verordeningen ROM 10:19, ergernis→aanstoot ROM 14:21; ergernis NT-deferred 14×)
- [x] `MAT + MRK` — R34 (9 red_wins: synoptic imperatief-t Ziet toe/Gaat heen/weest/vreest/blijft→stem, ergernis→struikelen MRK 9:42; +2 synoptic-partner + 3 scanner-followup MRK 13)
- [x] `LUK + ACT` — R35 (5 red_wins + 1 rule_change RG35-006: der-Joden genitief kop-kwalificatie FOSSIL_GENITIVE_HEAD_PAIRS, NT-brede body-sweep 0 over; notes-residu Pascha/feest/Overste der Joden DEFERRED)
- [x] `REV + JUD` — R36 (5 red_wins + 1 rule_change RG36-006: πόλεμος→oorlog, richting omgekeerd t.o.v. red — moderniseren i.p.v. naar archaïsch `krijg` harmoniseren; der-doden 11:18, geduld→volharding 2:3, geenszins 3:5, wederom 10:8/10:11; JUD body schoon)
- [x] `REV + 2PE` — R37 (5 red_wins: στράτευμα heirleger→leger REV 19:19, leerde→onderwees REV 2:14, Koningen/kooplieden der aarde→van de aarde 1:5/17:2/18:3/18:9/21:24, ἀπώλεια verderving→verderf 2PE 3:7, πυρόω ontstoken→in brand 2PE 3:12; der-aarde allowlist-narrowing DEFERRED met user-confirm)

Acceptatie voor Fase 2:

- [x] Elk cluster hierboven is afgewerkt of gemotiveerd overgeslagen.
- [x] Minstens 3 rondes bevatten expliciete `consistentie`-punten of een
      gemotiveerd red-verdict dat er geen nieuwe consistentiepunten waren.
      (R33 οὗτοί/leren-drift, R35 ὄχλος/κλαίω/διδάσκω-drift, R36 ὑπομονή/πόλεμος,
      R37 στράτευμα/βασιλεῖς τῆς γῆς/ἀπώλεια — alle expliciete consistentie-punten.)
- [x] Kanttekeningen zijn in red-prompts expliciet meegenomen
      (`in_kanttekening` waar relevant; o.a. R36 πόλεμος-noot-sweep, R37 der-aarde noot-inventaris).

## Fase 3 - Worst-First Naloop

Wanneer Fase 1 en Fase 2 klaar zijn, laat de selector weer kiezen:

- [x] Draai `uv run python scripts/redgreen_select.py`.
- [x] Neem het voorgestelde paar over, tenzij het exact net is afgerond zonder
      nieuwe punten.
- [x] Draai standaard 3 selector-rondes. (R38-R43: 6 selector-rondes gedraaid —
      de tail bleef twee systemische patronen opleveren tot de convergentie-sweep.)
- [x] Stop eerder als red in een ronde 0 nieuwe punten vindt. (R43 REV+ACT = 0 punten.)
- [x] Draai 2 extra selector-rondes als een van de 3 rondes een `rule_change`
      oplevert. (Geen rule_change in Fase 3; R36/R35-rule_changes lagen in Fase 2.
      Wel doorgedraaid t/m convergentie.)

Selector-rondes Fase 3:
- R38 REV+ACT — 5 red_wins (ontstoken, geenszins/Μηδαμῶς, ὄχλος)
- R39 REV+MAT — 2 red_wins + NT-brede afronding deferred wederom/geenszins (body=0)
- R40 REV+ACT — 11 red_wins (διδάσκω-cluster, ἀκούσατε, βοηθεῖτε, der heiligen)
- R41 REV+MAT — 4 red_wins (διδάσκω, der heiligen MAT 27:52)
- R42 convergentie-sweep — NT-brede διδάσκω (18) + fossiel-genitief-lek der aarde/wereld (13)
- R43 REV+ACT — **0 punten (convergentie bevestigd)**

Acceptatie voor Fase 3:

- [x] De laatste selector-sessie levert een ronde met 0 nieuwe punten op (R43).
- [x] Geen nieuw `rule_change`-verdict staat nog open. (Openstaand-DEFERRED, met
      user-confirm: kop-kwalificatie FOSSIL_GENITIVE_HEAD_PAIRS voor der aarde/der
      heiligen — validator-logica-wijziging, bewust niet autonoom doorgevoerd.)

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

- [x] R17 `PHM+JUD` - status: afgerond; 10 red-punten, 10 red_wins toegepast, 0 rule_change; validate/lint/semantic PASS.
- [x] R18 `1JN+2PE` - status: afgerond; 10 red-punten, 10 red_wins toegepast, 0 rule_change; validate/lint PASS; HSV-diffs en memory bijgewerkt.
- [x] R19 `1PE+JAS` - status: afgerond; 8 red-punten, 8 red_wins toegepast, 0 rule_change; validate/lint PASS; HSV-diffs en memory bijgewerkt.
- [x] R20 `1TH+2TH` - status: afgerond; 10 red-punten, 10 red_wins toegepast, 0 rule_change; validate/lint PASS; HSV-diffs en memory bijgewerkt.
- [x] R21 `1TI+2TI` - status: afgerond; 3 red-punten, 3 red_wins toegepast, 0 rule_change; validate/lint PASS; HSV-diffs en memory bijgewerkt.
- [x] R22 `COL+EPH` - status: afgerond; 6 red-punten, 4 red_wins (verse) + 2 rule_change (NT-breed) toegepast; validate/lint PASS; HSV-diffs + memory bijgewerkt. rule_change: μακροθυμία→lankmoedig(heid) (EPH4:2,COL3:12,1TH5:14,LUK18:7); Sendtbrief→Zendbrief colofon (1CO,1JN,1PE,2TH,COL,GAL,JUD,PHM,ROM).
- [x] R23 `GAL+PHP` - status: afgerond; 3 red-punten, 2 red_wins (GAL 5:16 wandelt→wandel; PHP 2:18 verblijdt u zich→verblijd u) + 1 green_wins (PHP 4:4 'ter vergelijking' — red-premisse weerlegd, ook in ROM 11:7); validate/lint PASS; HSV+memory bijgewerkt.
- [x] R24 `HEB+TIT` - status: afgerond; 3 red-punten, 3 red_wins toegepast (HEB 3:8 Verhardt→Verhard; HEB 10:5 + TIT-epiloog scaffolding-reparatie: ontbrekende <>-delimiters rond inline-glosse hersteld in input.sv én output, der Cretensen→van de Kretenzen); validate/lint PASS; HSV+memory bijgewerkt. FASE 1 COMPLEET: alle 26 boeken ≥1x, open_keys=0.
- [ ] Cluster Johannes - status:
- [ ] Cluster Paulus kort - status:
- [x] Cluster algemene brieven - status: COMPLEET (JAS+1PE R19, 1PE+2PE R30, JUD+2PE R31, HEB+JAS R32)
- [ ] Grote-boek kalibratie - status:
- [ ] Worst-first naloop - status:
