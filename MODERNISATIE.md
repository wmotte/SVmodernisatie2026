# Modernisatie — wat het is, wat het niet is

Dit document legt vast wat in dit project onder "modernisatie" wordt
verstaan. Het is een normatief document: bij twijfel over een
vertaalkeuze, een herstructurering van een skill, of een uitbreiding van het
project moet de keuze passen binnen wat hieronder staat. Wijkt iets
hier substantieel van af, dan moet eerst dit document worden bijgesteld
— niet de praktijk stilzwijgend.

De andere documenten in deze repository (`AGENTS.md`, `ARCHAISMEN.md`,
`KANTTEKENINGEN.md`, `BIJBELVERWIJZINGEN.md`, `INTRO_EPILOOG.md`,
`OUTPUT_SCHEMA.md`) beschrijven *hoe* het werk uitgevoerd wordt. Dit
document beschrijft *wat* het werk is en *waarom*.

## 1. Eén-zin-definitie

Modernisatie in dit project is **het wegnemen van de archaïsche schil
van de Statenvertaling 1657 (2e druk), zodat de tekst leesbaar wordt
voor een eenentwintigste-eeuwse lezer, zónder de identiteit van de
Statenvertaling — haar formele equivalentie, haar concordantie, haar
kanttekeningen, haar typografische conventies, en haar
hoofdletter-discipline — aan te tasten.**

Dit is een renovatie, geen hervertaling.

## 2. Wat modernisatie *wel* is

### 2.1 Spellingnormalisatie

Zeventiende-eeuwse spelling wordt vervangen door hedendaagse spelling
volgens de Woordenlijst Nederlandse Taal (de norm van het Groene Boekje).
Voorbeelden: `ende` → `en`, `soo` → `zo`, `daer` → `daar`,
`welcke` → `welke`, `dese` → `deze`, `Sone` → `Zoon`. De volledige
tabel staat in `ARCHAISMEN.md`.

### 2.2 Lexicale modernisatie van verouderde woorden

Woorden die in modern Nederlands niet meer functioneren of een
substantieel andere betekenis hebben gekregen, worden vervangen door
hun naaste hedendaagse equivalent (`ergernisse` → `ergernis`,
`voortijts` → `eertijds`, `nagetracht` → `nagestreefd`). Het criterium
is functioneel, niet stilistisch: een woord dat een gemiddelde lezer
nog herkent maar wat plechtig vindt klinken, blijft staan.

### 2.3 Voorzichtige zinsbouw-aanpassing

Constructies die in 1657 idiomatisch waren maar nu onleesbaar zijn —
met name het Griekse participium dat door de Statenvertalers letterlijk
is omgezet (`gegaan zijnde`, `gehoord hebbende`, `zijnde …`) — worden
ontvouwd naar een moderne bijzin (`toen zij gingen`, `nadat zij hadden
gehoord`). Dit is de meest invasieve ingreep die we toelaten, en hij
geldt alléén waar de letterlijke constructie de zin onbegrijpelijk
maakt voor een moderne lezer.

Dat geldt ook voor het *finiete* tegenwoordige participium dat als
bijwoordelijke bepaling fungeert (`wandelende in alle de geboden`).
`Wandelend in al de geboden …` is een latinate carry-over die in modern
Nederlands stug leest. Ontvouw naar een nevenschikking met finiet
werkwoord: `… ze wandelden in al de geboden …`. Bewaar daarbij de
zinsvolgorde en de inhoud zo letterlijk mogelijk; dit is een
syntactische verschuiving, geen herformulering.

§2.3 geldt **ook binnen `<…>` kanttekeningen — zonder uitzondering voor
citatie-blokken**. Latinate participia (`evenals enige navolgende`,
`ziende gemaakt`, `daartoe strekkende dat`) worden óók in uitlegtekst
ontvouwd. Dat geldt ook voor `<Of, …>` / `<Gr. …>` / `<D. …>`-blokken:
SV-formuleringen die uit een SV-participium bestaan, worden ontvouwd
naar moderne Nederlandse syntaxis. Voor literale `<Gr. X-ende.>`-glossen
(één-woord-vorm-aanduidingen van een Grieks participium) is de standaard
het **infinitief-lemma**: `<Gr. werpende.>` → `<Grieks: werpen.>`,
`<Gr. staende.>` → `<Grieks: staan.>`, `<Gr. liggende.>` → `<Grieks:
liggen.>`. Validator draait dezelfde §2.3-check HARD over kanttekeningen
als over hoofdtekst (geen soft-pass meer). Adversarial review bevestigt.

### 2.3a Datief-bezit blijft datief-bezit

Een Griekse / Hebreeuwse datief-constructie van bezit (`u sal blijdtschap
… zijn`, "voor u zal er ... zijn") wordt **niet** vlotgetrokken naar het
eigenaar-perspectief (`u zult … hebben`). Dat is dynamische equivalentie
en valt onder §3.2. Bewaar de "voor u zal er ... zijn"-vorm; dat is
formele equivalentie, en de moderne lezer begrijpt het ook zo. Geldt
voor alle vergelijkbare patronen: `mij geschiedde …`, `hem werd …`,
`u zal … zijn`.

### 2.3b Latinaat-syntax — vier patronen die invariant moderniseren

Naast het participium (§2.3) zijn er vier SV-syntactische patronen die
in modern Nederlands stug-archaïsch lezen, ook al is elk los woord
modern. Deze ontvouwen we standaard:

**1. Infinitief met nageschoven object.**
SV plaatst het object van een infinitief er vaak achter: `om in orden
te stellen een verhael` (Lk. 1:1), `om te bekeeren de herten der vaderen`
(Lk. 1:17), `om te bereyden eenen wegh` (Lk. 1:76). Modern Nederlands
plaatst het object vóór de infinitief: `om een verslag op te stellen`,
`om de harten van de vaders te bekeren`, `om een weg te bereiden`. De
keuze geldt ook bij `om u dit op volgorde te schrijven` (Lk. 1:3) →
`om u dit geordend te schrijven`: hier is "op volgorde" zelf het
nageschoven element en werkt het idiomatisch niet meer met *schrijven*.

**2. Bijwoord-coda achteraf zonder werkwoord.**
SV laat een bijwoordelijke bepaling soms los achter de zin staan als
nageschoven karakteristiek: `wandelende in alle de geboden ende rechten
des Heeren onberispelick` (Lk. 1:6). Het ontvouwde participium (§2.3)
maakt daar `ze wandelden in al de geboden ... van de Heere,
onberispelijk` van — maar het bijwoord blijft als losse coda achter
de zin staan en leest stijf. Plaats `onberispelijk` ín de zin: `ze
wandelden onberispelijk in al de geboden ...`. Algemene regel: een
bijwoord dat de manier van een werkwoord karakteriseert hoort vlak
bij dat werkwoord, niet als appositie aan het einde van de zin.

**3. Passief `aan iem. werd ... gezien` (Gr. ὤφθη).**
De aoristus-passief van *zien* (`ὤφθη`) wordt door de SV letterlijk
omgezet als `aan hem werd gesien` / `wierd gesien een Engel des Heeren`
(Lk. 1:11). De moderne weergave is invariant **`verscheen aan iem.`**
— ook in Lk. 24:34 (`is gesien geweest van Simon` → `is verschenen aan
Simon`), Hd. 7:30 (`wert ... gesien een Engel` → `verscheen ... een
engel`), enz. Geldt door heel Lucas/Handelingen.

**4. Vocatief met "u + zelfstandig naamwoord".**
SV vormt anspreek-vocatieven als `u begenadigde` (Lk. 1:28),
`u kindeken` (Lk. 1:76), `u Theophile` (Lk. 1:3). In modern Nederlands
is `u + appositie` als anspreek geen productieve constructie;
modern is enkel het zelfstandig naamwoord (eventueel met titel) dat
als anspreek dient: `begenadigde`, `Theofilus`. Schrap de `u` in
deze constructies, behalve waar het een echt onderwerp is en geen
vocatief.

**Verhouding tot formele equivalentie.** Deze vier ingrepen wijzigen
de zinsvolgorde, niet de inhoud, het kanttekening-aantal, de vierkante
haken, of het concordantie-patroon. Ze vallen daarom onder
"voorzichtige zinsbouw-aanpassing" (§2.3) en niet onder
herformulering of dynamische equivalentie (§3.2).

### 2.3c Gefossiliseerde genitief-formules blijven staan

Het Nederlands van 1657 markeert de genitief nog flexief: `des Heeren`,
`der vaderen`, `Koninckrijcke Godts`, `Sone des menschen`. In het
hedendaags Nederlands is die naamval grotendeels vervangen door een
`van`-constructie (`van de Heer`, `van de vaders`, `van God`, `van de
mens`). De ontvouwing naar `van`-constructie is de standaardregel —
behalve voor een kleine groep formules die **gefossiliseerd** is in de
Nederlandse theologische en literaire traditie en daar tot vandaag in
gebruik is.

**Welke formules blijven flexief?**

| Formule (modern) | Origineel SV1657 | Niet: |
|------------------|------------------|-------|
| `Koninkrijk Gods` | `Coninckrijck Godts` | ~~Koninkrijk van God~~ |
| `Zoon Gods` / `Zoon van God`† | `Sone Godts` | (varieert in SV zelf) |
| `Zoon des mensen` | `Sone des menschen` | ~~Zoon van de mens~~ |
| `hand Gods` (in vaste uitdrukkingen) | `hant Godts` | ~~hand van God~~ |
| `Heer der heerscharen` (OT, indien geattesteerd) | `Heere der heyrscharen` | ~~Heer van de legermachten~~ |

† `Sone Godts` modernisteren we contextueel: vóór een bijvoeglijke
bepaling of als titel (`de eniggeboren Zoon Gods`, `Zoon Gods,
ontferm u`) blijft de genitief; als naamwoordelijk gezegde met
copula (`hij is de Zoon van God`) ontvouwt hij. Volg het patroon van
de SV zelf, die hier ook varieert.

**Waarom een uitzondering?** Drie redenen, in volgorde van gewicht:

1. **Herkenbaarheid.** `Koninkrijk Gods` en `Zoon des mensen` zijn in
   de Nederlandse traditie geen archaïsmen meer maar vaste
   uitdrukkingen — vergelijkbaar met `Staten-Generaal`, `Hof van
   Justitie`, `dag des oordeels`. Een hedendaagse lezer herkent ze;
   het zijn geen drempel-archaïsmen in de zin van §2.7.
2. **Formele equivalentie (§5).** De SV markeert hier een Grieks
   genitivus-attributief (Mt. 4:23 βασιλεία τοῦ θεοῦ, Mk. 8:31
   υἱὸς τοῦ ἀνθρώπου) met de Nederlandse genitief. De naamvalsvorm
   is informatie — geen archaïsche schil.
3. **Concordantie (§5.3).** SV1657 gebruikt `Koninckrijcke Godts`
   zo'n 60× in de evangeliën en `Sone des menschen` ruim 80×. Een
   één-op-één modernisatie naar `Koninkrijk van God` / `Zoon van de
   mens` ontkoppelt dit lexicale anker over honderden verzen.

**Wat dus *niet* fossielt:** losse possessief-genitieven zonder
formule-status (`de hant des Heeren was met hem`, Lk. 1:66) ontvouwen
normaal naar `de hand van de Heer was met hem`. De vuistregel: alleen
formules die in moderne theologische pers nog steeds zo geschreven
worden, blijven flexief. Bij twijfel: zoek de moderne kandidaatvorm
in NBV21 of HSV; wordt hij dáár ook nog flexief gespeld (zoals
`Koninkrijk van God` *niet*, maar in liturgisch gebruik wel), dan is
het een fossiel.

**Verschil met HSV en SV2027.** Beide ontvouwen alle genitieven naar
`van`-constructies (`Koninkrijk van God`, `Zoon van de mens`). Dat
hangt samen met hun bredere parafrase-vrijheid (zie §2.7) en is een
bewuste keuze van die projecten — wij volgen die keuze niet. De
HSV/SV2027-spiegel in `sv-semantic-review` mag deze categorie dus
**nooit** als afwijking flaggen.

### 2.4 Eigennamen volgens NBV21

Eigennamen worden gespeld conform de NBV21-conventie (`Iesus` →
`Jezus`, `Ioannes` → `Johannes`, `Mattheus` → `Matteüs`). Dit is een
bewuste keuze: de hedendaagse lezer die deze tekst naast een andere
moderne vertaling legt, moet de namen kunnen matchen. De volledige
mapping staat in `ARCHAISMEN.md`.

### 2.5 Bijbelverwijzingen genormaliseerd

SV1657-verwijzingen (`Iudic. 13.4.`, `Iesa. 9.1. ende 42.7.`) worden
omgezet naar een uniform modern formaat (`$Ri. 13:4$`,
`$Js. 9:1; 42:7$`). Het formaat is machine-leesbaar (`$...$` als
wrapper), zodat consumenten van deze data — apps, parallel-vertaling
viewers, search-indexes — refs in één regex kunnen vinden. Zie
`BIJBELVERWIJZINGEN.md`.

### 2.6 Kanttekening-vertaling

Kanttekening-blokken worden meegemoderniseerd: de standaard-afkortingen
(`D.`, `Gr.`, `Hebr.`, `Namelick`, `Ofte`, `Siet`) worden uitgeschreven
en de tekst zelf gemoderniseerd zoals de hoofdtekst. Het *aantal* en de
*positie* van de kanttekeningen blijft strikt gelijk. Zie
`KANTTEKENINGEN.md`.

### 2.7 Drempel — wanneer is een woord nog modern genoeg?

Het meest voorkomende risico in dit project is *te conservatief
moderniseren*: woorden die in 1657 én vandaag bestaan, maar die in
modern Nederlands feitelijk niet meer functioneren, blijven onbedoeld
staan. "Vertoefde", "hoedanig", "aanschouwers", "voorzichtigheid"
(in oude betekenis), "versmaadheid", "verheuging", "voortreffelijke"
(als anspreek), "noch X noch Y", "zwanger met": ze staan in Van Dale,
maar geen lezer van 2026 schrijft of zegt ze nog spontaan. De volledige
lijst staat in `ARCHAISMEN.md`; de syntactische varianten in §2.3b.

Het criterium is **functioneel**: een woord blijft staan als het in
hedendaags zakelijk of journalistiek Nederlands productief gebruikt
wordt. Een woord moderniseert zodra het stilistisch markeert als
"oud", "literair" of "Bijbels-formeel" — ook als het technisch nog in
het woordenboek staat.

Drie tests:

1. **Productiviteits-test**: zou een lezer dit woord zelf gebruiken in
   een zakelijke e-mail of nieuwsbericht in 2024+? Zo nee → moderniseer.
2. **Constructie-test**: werkt het woord in zijn SV-constructie ook in
   modern NL? "Heten + accusatief van naam" (`u zult zijn naam X heten`)
   werkt niet meer. Herformuleer.
3. **Verwarringtest**: heeft het woord in 2026 een dominant *andere*
   betekenis? Zo ja → false friend (zie `ARCHAISMEN.md` §False Friends).

Als kalibratie-bron staan in `docs/` versgewijze vergelijkingen
tussen onze modernisatie (SV2026) en externe parallelle vertalingen.
De **HSV (Herziene Statenvertaling)** is voor alle bijbelboeken
beschikbaar en levert `docs/diff_hsv_<BOEK>_<H>.json`. Voor Lucas
bestaat daarnaast een vergelijking met **SV2027 / "Initiatief 2027"**
(`docs/diff_LUK_*.json` en `docs/diff_all_LUK_*.json`); SV2027 is
buiten Lucas nog niet gepubliceerd. Beide parallelvertalingen zijn **niet
normatief** voor dit project — zij maken andere keuzes voor
hoofdletters, kanttekening-aantal, intro-stijl, en parafrase-
vrijheid die wij expliciet *niet* overnemen (zie §3 en §5). HSV is
daarbij **vrijer** dan SV2027 (exegese in de hoofdtekst, eigen
kanttekeningen `<HSV: …>`, soms herstructurering van zinsbouw) en
moet daarom voorzichtiger worden gebruikt: stilistische afwijkingen
zijn standaard HSV-keuze, geen bewijs.

Beide blijven wel een **nuttige spiegel** voor de drempelvraag: waar
een externe parallel een woord of constructie duidelijk moderner
oplost zonder zinsbouw of inhoud aan te tasten, signaleert dat een
conservatief-issue bij ons. Het uit de tabel halen van een archaïsme
of het ontvouwen van een SV-constructie is *binnen* onze reikwijdte;
toevoegen van eerbiedshoofdletters, weglaten van kanttekeningen, of
overnemen van exegetische glosses is dat *niet*.

*Operationeel:* `sv-semantic-review` Stap 2.5 leest
`docs/diff_hsv_<BOEK>_<H>.json` per batch en past deze drempel-tests
+ fout-detectie (taalfouten, semantische missers) toe op de
HSV-spiegel, met HSV-specifieke waarborgen (zie skill). Bevestigingen
moeten altijd onafhankelijk gecheckt worden tegen SV1657 + Grieks.
De SV2027-vergelijking blijft als **post-hoc archief** beschikbaar
in `docs/diff_<BOEK>_<H>.json` en `docs/diff_all_<BOEK>_<H>.json`
voor Lucas, maar wordt niet meer in de batch-pipeline gebruikt
(boekonafhankelijke spiegel binnen de loop = HSV). Terugkerende patronen lekken
via de bestaande regelbestandmechanismen (`ARCHAISMEN.md`,
`lint_false_friends.py`, `scripts/validate.py`-blacklist) terug naar
het hele proces.

## 3. Wat modernisatie *niet* is

### 3.1 Geen nieuwe vertaling

We vertalen niet opnieuw uit het Grieks of Hebreeuws. De `source_text`
(Textus Receptus voor het NT, Masoretische tekst voor het OT) staat in
elk vers-record als referentie, maar dient als **anker voor formele
equivalentie**, niet als bron voor een vrije hervertaling. Als de
SV-vertalers een Grieks woord met X vertaalden, en X is geen
archaïsme, dan blijft X staan — ook als een moderne lezer Y mooier of
preciezer zou vinden.

### 3.1a Geen "passief expliciteren" als de SV-constructie modern blijft werken

Een veelvoorkomende valkuil is om een SV-werkwoord dat in 17e-eeuws
Nederlands zowel intransitief als passief-achtig kon functioneren te
"verbeteren" naar een expliciete moderne passief — vooral wanneer het
Grieks zelf passief staat. Dat is geen renovatie maar een stap richting
hervertaling: we maken de Griekse stem zichtbaarder dan de SV zelf deed.

**Casus Lk. 1:60.** SV: `hy sal Ioannes heeten` (Gr. `κληθήσεται`,
futurum passief van `καλέω`). Modern `heten` is intransitief en
volledig productief: `hij zal Johannes heten` is goed Nederlands en
één-op-één de minimale renovatie. De variant `hij zal Johannes genoemd
worden` is grammaticaal correct en concordant met v. 61 (`genaemt
wort` → `genoemd wordt`), maar trekt v. 60 weg van het SV-eigen
onderscheid tussen `heeten` (v. 60) en `genaemt wort` (v. 61). De SV
maakte daar zelf verschillende keuzes; die distinctie bewaren we.

**Regel.** Als de SV-constructie in modern Nederlands grammaticaal én
idiomatisch werkt, blijft hij staan — ook als een naburig vers een
explicietere passief gebruikt, en ook als HSV of een andere parallel
hier de passief wél explicit maakt. Concordantie binnen het hoofdstuk
weegt zwaar (§5.3), maar nooit zwaarder dan SV's eigen variatie tussen
naburige verzen. Concordantie geldt voor **gelijke** SV-werkwoorden,
niet als nivelleerder van **verschillende** SV-werkwoorden.

Vergelijk met de actieve variant in v. 13: `ghy sult sijnen naem heeten
Ioannes` — daar werkt "heten + accusatief van naam" in modern NL niet
meer (zie constructie-test §2.7), dus daar moderniseren we wél naar
"noemen / de naam geven". Het verschil: in v. 60 werkt de
SV-constructie modern, in v. 13 niet.

### 3.2 Geen parafrase, geen "begrijpelijk maken"

Dit is geen Het Boek, geen Bijbel in Gewone Taal, geen NBV21-stijl
dynamisch-equivalente vertaling. Hebraïsmen en grecismen die door de
SV-vertalers bewust letterlijk in het Nederlands zijn gezet (`in het
zweet uws aanschijns`, `de bokkepruik op hebben`) blijven staan. De
lezer moet door deze tekst nog steeds de structuur van de brontekst
heen kunnen zien — dat is precies wat de SV-vertalers wilden, en wat
deze modernisatie behoudt.

### 3.3 Geen toevoeging van eerbiedshoofdletters

Hedendaagse vertalingen schrijven `Hij`, `Hem`, `Zijn` consequent met
hoofdletter wanneer ze naar God of Christus verwijzen. **De
Statenvertaling doet dat niet, en wij voegen dat niet toe.** De SV
gebruikt eerbiedshoofdletters wisselend en doelbewust; haar patroon is
betekenisdragend (zie sectie 5.4). We volgen het exact.

### 3.4 Geen verwijdering van vierkante haken

De SV-vertalers markeerden woorden die zij toevoegden voor het
Nederlands (en die niet in de brontekst stonden) tussen vierkante
haken `[…]`. Deze haken zijn een *kerneigenschap* van de SV en het
zichtbaarste teken van haar transparantie. Ze blijven exact behouden:
zelfde aantal, zelfde positie, zelfde inhoud (op modernisatie van de
inhoud na, als die zelf archaïsch is).

### 3.5 Geen exegese in de hoofdtekst

Alle interpretatie blijft binnen `<kanttekening>`-blokken. We voegen
geen verklarende clausule toe in de hoofdtekst, ook niet als de
oorspronkelijke zin obscuur is. Als een lezer hulp nodig heeft, vindt
hij die in de kanttekening — niet ingebakken in de Schrift.

### 3.6 Geen hertelling, geen herstructurering

Versindeling, hoofdstukindeling, en de volgorde binnen een vers blijven
identiek. Geen verzen samenvoegen, splitsen, of herordenen. Geen
toegevoegde tussenkopjes. Geen alinea-herstructurering buiten wat de
invoer aanlevert.

### 3.7 Geen tekstkritische correcties

Als de Textus Receptus afwijkt van moderne kritische edities (bv.
NA28), volgen wij de Textus Receptus. Het doel is een leesbare SV1657,
niet een SV1657 die stilzwijgend op latere tekstkritiek is bijgewerkt.
Tekstkritische verschillen kunnen — als het de moeite waard is — in
een kanttekening worden gesignaleerd, maar de hoofdtekst volgt de
brontekst zoals de SV-vertalers die kenden.

## 4. Methode

De methode is gestandaardiseerd in vier samenhangende skills (zie
`AGENTS.md` voor de orchestratie):

| Skill          | Wat het doet                                              |
|----------------|------------------------------------------------------------|
| `sv-modernize` | Orchestrator. Per vers: bevraag geheugen → moderniseer → normaliseer verwijzingen → schrijf uitvoer → valideer → voeg toe aan geheugen. |
| `sv-memory`    | Vectordatabase met eerder gemoderniseerde verzen, bevraagd vóór elke modernisatie voor consistente woordkeus (concordantie). |
| `sv-bibref`    | CSV-gedreven omzetter van SV-bijbelverwijzingen naar het moderne `$Boek H:V$`-formaat. Idempotent. |
| `sv-validate`  | Hard-issue-controle op kanttekening-aantal, vierkante haken, hoofdletters, ref-formaat, archaisme-blacklist, en byte-onveranderlijkheid van `source_text`. |

Drie methodische principes:

1. **Vers-voor-vers, niet hoofdstuk-voor-hoofdstuk.** Elk vers wordt
   afzonderlijk gemoderniseerd, gevalideerd, en aan memory toegevoegd
   vóór het volgende vers. Zo kan vers N+1 vers N als voorbeeld ophalen
   en groeit de concordantie binnen het hoofdstuk.
2. **Menselijke beoordeling bij twijfel.** Bij een vertaalkeuze die meer dan
   triviaal is, wordt de keuze in een `notes`-veld in de output-JSON
   vastgelegd (`type`, `subject`, `choice`, `alternatives`, `reason`).
    De beoordelaar ziet zo niet alleen *wat* er staat, maar ook *waarom*.
3. **Validatie blokkeert memory-toevoeging.** Een vers dat niet
    valideert komt niet in de voorbeeldverzameling. Slechte keuzes
   propageren niet naar volgende verzen.

Het volledige protocol staat in `.agents/skills/sv-modernize/SKILL.md`.

## 5. Aannames

Onder de methode liggen een aantal aannames die expliciet benoemd
moeten worden, omdat ze de uitkomst sturen.

### 5.1 De SV1657 (2e druk) is de bron, niet een afgeleide

We werken op de tekst van de tweede druk uit 1657, niet op latere
revisies (1888 Van Dale-correcties, GBS-uitgaven van de 19e/20e eeuw,
of de Herziene Statenvertaling). Verschillen tussen de 1657-tekst en
latere edities worden niet stilzwijgend overgenomen.

### 5.2 De doelgroep is een geïnteresseerde lezer, geen kerkganger of academicus

Dit is geen liturgische vertaling (waar voorlees-ritme dominant is) en
geen kritische editie (waar elke afwijking van de brontekst
gesignaleerd moet worden). De impliciete lezer is iemand die de
Statenvertaling wil léz​en, maar voor wie de zeventiende-eeuwse spelling
en grammatica een te hoge drempel is. Vertaalbeslissingen worden tegen
deze lezer afgewogen.

### 5.3 Concordantie weegt zwaarder dan stilistische variatie

Als hetzelfde Griekse woord tweemaal voorkomt, krijgt het tweemaal
hetzelfde Nederlandse woord — ook waar een literaire vertaler zou
afwisselen. Dit was het uitgangspunt van de Statenvertalers en het is
het uitgangspunt van deze modernisatie. De vectordatabase (`sv-memory`)
operationaliseert dit: bij elk vers worden eerdere modernisaties
opgehaald en hergebruikt.

### 5.4 Het hoofdletter-patroon van de SV is betekenisdragend

De SV gebruikt hoofdletters niet alleen voor zinsbegin en eigennamen,
maar ook voor begrippen die theologische lading hebben (`Engel`,
`Apostelen`, `Christelicke Kercke`, `Wet`). Dat patroon is wisselend
maar niet willekeurig. We **volgen het exact** — geen toevoegingen,
geen verwijderingen. De validator behandelt elke case-flip als een
harde fout. Dit is een van de scherpste verschillen tussen deze
modernisatie en bv. de HSV.

### 5.5 Vierkante haken zijn niet onderhandelbaar

`[…]`-blokken markeren waar de SV-vertalers afstand moesten nemen van
de brontekst om Nederlands te schrijven. Het verwijderen van die haken
zou de transparantie van de vertaling vernietigen — de lezer kan dan
niet meer zien wat brontekst is en wat aanvulling is. Dat is geen
optie.

### 5.6 Kanttekeningen zijn geen versiering

De kanttekeningen zijn waar de SV-vertalers exegetisch werk hebben
gedaan zonder de hoofdtekst te kleuren. Ze zijn integraal onderdeel
van de Statenvertaling, niet een appendix. Een modernisatie zonder
kanttekeningen is geen modernisatie van de Statenvertaling.

### 5.7 De Textus Receptus is de NT-brontekst

We volgen de SV-vertalers in hun keuze voor de Textus Receptus. We
"corrigeren" geen passages waar de TR afwijkt van NA28 / kritische
edities. Wie een NA28-gebaseerde tekst wil lezen, leest een andere
vertaling.

### 5.8 Modernisatie is een functie van tijd

Een tekst die in 2026 modern aanvoelt zal dat in 2076 niet meer doen.
Deze modernisatie pretendeert geen tijdloosheid; ze pretendeert
leesbaarheid voor de hedendaagse lezer. De methode (skills, archaisme-
tabel, validator) is zo opgezet dat een toekomstige iteratie op deze
uitvoer kan voortbouwen.

## 6. Wat er gebeurt bij een grensgeval

Niet elke beslissing is duidelijk. Als een keuze niet uit de
archaisme-tabel, de eigennamen-mapping of de kanttekening-conventies
volgt:

1. Volg het principe van **minste verandering**: als de SV-formulering
   nog leesbaar is voor een moderne lezer, blijft hij staan.
2. Bij meerdere acceptabele opties: kies degene die het dichtst bij
   eerder gemoderniseerde verzen ligt (concordantie via memory).
3. Leg de keuze vast in `notes` op het vers, met de overwogen
   alternatieven en de reden.
4. Stop niet — kies een redelijke optie en ga door. De uitvoer-JSON is
   het controlespoor; een beoordelaar kan altijd terugkomen op een keuze.

## 7. Wat valt buiten de reikwijdte

Buiten dit project (en dus buiten "modernisatie" in deze betekenis)
vallen:

- **Liturgische bewerking.** Voorlees-ritme, kanselversies, lectionarium-
  indelingen.
- **Studie-apparaat.** Inleidingen op bijbelboeken, kruisverwijzingen
  tussen verzen, archeologische / historische verklaringen.
- **Audio / spreekstem.** Modernisatie is een tekstuele operatie.
- **Apocriefen.** De huidige reikwijdte is canonieke boeken. De
  SV-Apocriefen zijn een mogelijke uitbreiding, maar onder een eigen
  set keuzes (ze hadden in de SV1657 al een aparte status — zie
  `research/vertaalprincipes.txt` §5).

## 8. Waar dit document fout kan zitten

Dit document is gemaakt met zorg, maar geen enkel project van deze
aard is bij de start volledig geconsolideerd. Bij elke afwijking
tussen wat hier staat en de praktijk is de juiste reactie:
**document bijwerken of praktijk bijstellen — niet de discrepantie
laten staan.** Dit document is geldend; afwijkingen die de moeite
waard zijn vereisen een expliciete update hier.
