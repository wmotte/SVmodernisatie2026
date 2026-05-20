# Vergelijking met Statenvertaling 2027 (SV27)

**Bron:** `research/Toelichtingen-Lukasevangelie-Statenvertaling-2027.pdf` (9 p.,
"Toelichtingen bij Lukas", initiatief *Statenvertaling 2027*).
**Status:** SV27 is **niet normatief** voor dit project — een vergelijkbaar,
zelfstandig modernisatie-initiatief. Deze notitie toetst onze aannames eraan en
legt per thema vast of we **verdedigen** of **herzien**.

## Twee uitgangspunten die de verschillen verklaren

1. **Brontekst.** SV27 vertrekt van de **NBG-editie 1886** (basis van de gangbare
   SV-uitgaven) en raadpleegt daarnaast SV1657, de grondtekst, NBG-1977 en de
   GBS-uitgave. Dit project neemt **SV1657 (2e druk)** als enige bron. Ons
   uitgangspunt is puristischer/historischer; SV27 moderniseert feitelijk een al
   deels gemoderniseerde 1886-tekst. Een deel van de woordverschillen volgt
   hieruit. Ongewijzigd.
2. **Voetnoten.** SV27 voegt waar nodig **nieuwe verklarende voetnoten** toe
   (`D.i. dokter`, `Gr. geschiedde`). Dit project voegt **geen** verzonnen
   kanttekeningen toe (aantal ≥ origineel, maar niet uit het niets). Waar SV27
   een keuze met een eigen noot oplost, is die route voor ons afgesloten.

---

## Sterk bevestigd → VERDEDIGEN (geen wijziging)

| Thema | SV27-toelichting | Ons principe | Oordeel |
|---|---|---|---|
| Zinsvolgorde zo min mogelijk wijzigen | "zo min mogelijk veranderd in de zinsvolgorde" | kern-aanname formele equivalentie | **bevestigd** |
| Deelwoorden → finiete (bij)zinnen | "bijna alle deelwoorden omgezet in gewone (bij)zinnen" (lemma *Zeggende*) | §2.3 + PARTICIPLE_ALWAYS_BAD | **bevestigd** |
| Concordantie / Grieks-onderscheid bewaren | *De schare* (`schare`≠`menigte`, ander Grieks woord); `Simons schoonmoeder` consistent doortrekken; `rover` cross-evangelie | concordantie-vectors §5.3 | **bevestigd** |
| Letterlijke betekenis in noot, leesbare hoofdtekst | boekrol Jes. (Lk 4:17,20): "met de noten erbij weet de lezer wat letterlijk in het Grieks staat" | kanttekening-aanpak | **bevestigd** |
| Hebraïsmen letterlijk + (bestaande) noot, geen parafrase | Lk 21:19 "bezit uw zielen": tekst *precies hetzelfde* gelaten | §geen-exegese | **bevestigd** |
| Morfologie moderniseren, lexeem behouden | `tabernakelen`→`tabernakels`, maar `tabernakel` blijft | spelling/morfologie | **bevestigd** (zie wijziging 2) |
| Grondtekst voor syntactische verheldering | Lk 24:18 καί onderschikkend → `die`; Lk 24:18 `alleen`=`als enige` | §2.3b | **bevestigd** |

Deze punten tonen dat de twee projecten dezelfde grondhouding delen: **renovatie,
geen hervertaling**, met concordantie en formele equivalentie als ankers.

---

## Verdedigen mét documentatie (bewuste afwijking)

### `edik` → `azijn` (Lk 23:36)
SV27 **behoudt** `edik` + voetnoot, met als argument dat `azijn` "te veel
aandacht naar zich toe trekt". Dat argument achten wij zwak: `azijn` is helder,
correct (Gr. ὄξος) en volledig modern; `edik` faalt de productiviteitstest (§2.7)
hard. Wij **moderniseren naar `azijn`** en voegen geen noot toe. Bewuste afwijking.

### `neen` / `nee` (Lk 13:5; 16:30)
SV27 **differentieert op register**: `neen` in plechtige context, `nee` in dialoog.
Wij vlakken af naar `nee` overal — `neen` faalt de productiviteitstest, en
concordantie-eenvoud (één moderne vorm) weegt voor ons zwaarder dan een
register-nuance die de lezer nauwelijks opmerkt. Bewuste afwijking.

### `medicijnmeester` in Jezus-teksten (Lk 4:23; 5:31)
SV27 behoudt `medicijnmeester` in bekende Jezus-teksten **met voetnoot
`D.i. dokter`**. Wij behouden het woord daar eveneens (bekende teksten, context
maakt de betekenis duidelijk), **maar zonder noot** — de noot-route gebruiken we
niet. Zie ook wijziging 3 voor de wél-aangepaste plaats.

---

## Herzien → DOORGEVOERD

### Wijziging 1 — `het geschiedde` als gefossiliseerde formule
**Aanleiding.** Onze `ARCHAISM_BLACKLIST` blokkeerde het hele `geschied*`-paradigma
HARD, wat 46 verzen tot `het gebeurde` dwong. SV27 (lemma *Geschieden*) **behoudt**
de Lukaanse formule `en het geschiedde` (καὶ ἐγένετο, Septuaginta-verteltoon) en
past alleen aan waar de betekenis concreet "komen/ontstaan" is (Lk 9:35
`geschiedde een stem` → `kwam`, met noot).

**Ons besluit: herzien naar de SV27-nuance** — analoog aan de gefossiliseerde
genitieven (§2.3c). De formule is voor ons nu een fossiel, vrijgesteld van §2.7.
- Regel: `scripts/rules_data.py` — `geschied*`-regex met lookbehind (`het `/`'t `)
  en lookahead (` het woord`); concrete `geschiedde een stem` blijft HARD.
- Beleid: nieuw `MODERNISATIE.md §2.3d`; `ARCHAISMEN.md` rij herschreven.
- Corpus: **46 verzen** (LUK 1,2,3,5,6,7,8,9,10,11,14,16,17,18,19,20,24; MRK 1,2,4)
  `het gebeurde` → `het geschiedde` hersteld. Lk 9:35 (`kwam`) bleef ongemoeid.

### Wijziging 2 — `tabernakelen` → `tabernakels` (morfologie)
SV27 behoudt het lexeem `tabernakel` (opvallende SV-keuze, Gr. σκηνή), maar
moderniseert het archaïsche meervoud. Wij hadden het archaïsche meervoud
`tabernakelen` laten staan. Gecorrigeerd in de modernisaties van **LUK 6:1, 9:33,
16:9** (origineel-velden onaangeroerd). MRK 9:5 had het meervoud al niet in de
modernisatie.

### Wijziging 3 — `medicijnmeester` → `artsen` waar het een gewone arts is (Lk 8:43)
SV27 past `medicijnmeester` aan naar `arts` waar het géén Jezus-titel betreft
(Lk 8:43, de vrouw die "al haar bezit aan artsen had besteed"). Wij volgden dat:
`medicijnmeesters` → `artsen` in Lk 8:43. Geen noot. De Jezus-teksten (4:23, 5:31)
bleven `medicijnmeester` (zie hierboven).

---

## Niet overgenomen van SV27

- **Voetnoten toevoegen** om een archaïsme leesbaar te houden (`edik`,
  `medicijnmeester`-titel, `geschiedde`-noot). Buiten ons mandaat (geen verzonnen
  kanttekeningen).
- **Register-differentiatie binnen één woord** (`neen`/`nee`): concordantie-eenvoud
  prevaleert.
- **Conservatieve default "bij twijfel behouden + noot"**: ons project kiest bij
  twijfel voor leesbaarheid (§2.7-productiviteitstest), behalve voor expliciet
  gefossiliseerde formules.

## Verificatie van de doorgevoerde wijzigingen
- `scripts/validate.py` op alle gewijzigde verzen: **schoon** (de chapter-brede
  `Gr.`/`Hebr.`-afkortingsflags zijn pre-existing en losstaand van deze wijziging).
- Regressietest geschiedde-regex: `geschiedde een stem` blijft HARD; formule-vormen
  niet (zie testset in commit).
- `grep "het gebeurde" output/LUK output/MRK`: alleen nog historische `review.*`-records.
- `grep "tabernakelen"` in modernized-velden: leeg.
