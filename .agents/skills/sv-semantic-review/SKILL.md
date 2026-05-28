---
name: sv-semantic-review
description: Kritische semantische beoordeling van een gemoderniseerde vers-range — in-context door het agent-model zelf, geen externe LLM. Detecteert false friends, idiomatische mismatches, concordantietwijfel, en spiegelt de modernisatie tegen HSV (Herziene Statenvertaling) om taalfouten / semantische missers / drempel-archaïsmen op te sporen die door bestaande linters niet worden gevangen. Vervangt de oude `scripts/semantic_review.py` (externe embeddings-aanroep). Roep aan binnen `sv-batch-orchestrate` Stap 3 (review-subagent), of zelfstandig voor een ad-hocbeoordeling van een bestaande vers-range.
---

# sv-semantic-review — beoordelingsprotocol

Deze skill draait **in de orchestratorcontext** (het agent-model zelf). Geen
externe LLM-aanroep, geen netwerkronde per vers — het agent-model doet de redenering
zelf op basis van de modernisatietekst, het SV1657-origineel, de Griekse
brontekst, buurverzen, en concordantie-matches uit `sv-memory`.

Werkdirectory: de huidige repo-root (`git rev-parse --show-toplevel`) —
hoofdrepository of actieve worktree, nooit een hardcoded pad.

## Wanneer aanroepen

- **Binnen `sv-batch-orchestrate` Stap 3 (review-subagent)**: na validator +
  alle lints op een nieuwe batch van 3 verzen. De review-subagent voert
  dit protocol uit in zijn eigen geïsoleerde context.
- **Zelfstandig**: gebruiker vraagt om kritische beoordeling van een
  bestaande vers-range — bv. "review LUK 1:11-13".

Niet voor introductie / epiloog (geen brontekst, geen kanttekeningen,
geen concordantie-as).

## Stap 1 — laad de te beoordelen verzen

Lees `output/<BOEK>/<BOEK>.<H>.json` **met de Read-tool** — niet via een
inline Bash-python-dump. De Read-tool houdt de JSON-inhoud uit de
stdout-stroom; een `python3 -c "... print(...)"` echoot het hele bestand
verbatim de orchestratorcontext in.

Pak per batch-vers: `verse_number`, `original`, `modernized`,
`source_text`. Lees daarnaast vers `N-1` en `N+1` voor idiomatische
continuïteit (mag ontbreken aan de randen van het hoofdstuk).

## Stap 2 — concordantie-context per vers

Voor elk vers in de range: query sv-memory met het SV-origineel, top-3
matches, eigen vers uitgesloten:

```bash
uv run python scripts/memory.py query \
    --from-output output/<BOEK>/<BOEK>.<H>.json --verse <V> \
    --k 3 --axis sv --terse > /tmp/svsr_mem_<V>.json
```

`--from-output ... --verse <V>` haalt het SV-origineel uit de output-JSON
en sluit het bevraagde vers zelf uit — **geen inline-python-extractie van
de zoek-tekst, geen shell-quoting** van kanttekeningen / quotes / `$refs$`.
`--terse` drop `source_text` (Griekse brontekst); de concordantie-bewijslast
zit in `sv` + `modern`.

**Redirect naar `/tmp/svsr_mem_<V>.json` en lees met de Read-tool** — zo
blijft de volledige query-JSON (3 volle verspaare per vers) uit de
orchestratorstdout. Uitvoer is JSON met
`{results: [{book, chapter, verse, sv, modern, similarity}, ...], total_in_db}`.
Bewaar de relevante matches in-context per vers — gebruikt in stap 3 als
feitelijke onderbouwing van concordantie-twijfel.

Foutgevallen:

- **Lege database / geen matches** (`total_in_db=0` of `results=[]`): ga door
  zonder concordantie. Concordantiebevindingen worden dan strikt
  overgeslagen — geen evidentie.
- **Query faalt** (bv. `GOOGLE_API_KEY` ontbreekt of API-fout): noteer
  in eindverslag dat concordantie-context niet beschikbaar was; doe
  alleen false-friend / idiomatic.

## Stap 2.1 — decision-memory bij twijfel

Bij concordantie-, idioom- of false-friend-twijfel: raadpleeg de lokale
decision-memory adviserend, vóór je een bevinding formuleert:

```bash
uv run python scripts/query_decisions.py "<woord of patroon>" \
    --book <BOEK> --limit 5
```

Als `output/META/decisions.jsonl` ontbreekt, mag je hem eerst opbouwen:

```bash
uv run python scripts/extract_decisions.py --root output --book <BOEK>
```

Deze hits zijn **geen autoriteit**. Gebruik ze alleen als context voor
eerder vastgelegde fixes/rebuttals; elke nieuwe bevinding of weerlegging
moet nog steeds passen bij dit vers, SV1657, Grieks en de projectregels.

## Stap 2.5 — HSV-spiegel laden

De HSV (Herziene Statenvertaling) is een externe parallel-modernisatie
van de SV. **Niet normatief** voor dit project (zie `MODERNISATIE.md
§2.7` en §3) — en bovendien **vrijer** dan onze modernisatie: HSV
heeft regelmatig exegese in de hoofdtekst (subject/object invullen,
verklarende bijvoeglijke naamwoorden), eigen kanttekeningen
(`<HSV: …>` / `<HSV-aant: …>`), incidentele eerbiedshoofdletters, en
herstructurering van latinate participia naar finiete werkwoord-
chains. Die keuzes nemen wij *niet* over.

De waarde van de HSV-spiegel is daarom **beperkter** dan een
formeel-equivalente parallel zou zijn: zij dient vooral om
drempel-archaïsmen te bevestigen die wij gemist hebben, en om
aantoonbare lexicale/grammaticale fouten in onze tekst te onthullen.
Stylistische afwijkingen van de HSV zijn standaard "HSV-keuze, geen
bewijs" en mogen geen bevinding opleveren.

### 2.5.1 Diff verversen

Vóór het lezen, regenereer de diff zodat hij de actuele
`output/<BOEK>/<BOEK>.<H>.json` reflecteert (de subagent kan zojuist
verzen geschreven hebben):

```bash
uv run python scripts/compare_hsv.py <BOEK> <H>
```

Schrijft `docs/diff_hsv_<BOEK>_<H>.json` op basis van onze output en
`hsv/<BOEK>/<BOEK>.<H>.json`. **Let op het `diff_hsv_`-prefix** —
verschilt van het SV2027-pad `docs/diff_<BOEK>_<H>.json`, dat (voor
Lucas) bestaat als post-hoc archief en hier *niet* gebruikt wordt.

`compare_hsv.py` past bekende SV1657-broncorrecties uit
`scripts/source_corrections.py` toe op `original` en `sv2026`. Als de
HSV-spiegel een onmogelijke of onwaarschijnlijke SV1657-bijbelverwijzing
blootlegt (bv. een niet-bestaand versnummer) en de correctie onafhankelijk
controleerbaar is, moet die correctie in `scripts/source_corrections.py`
worden toegevoegd zodat toekomstige diff-generatie niet opnieuw de fout
toont.

### 2.5.2 Foutgevallen

- **`hsv/<BOEK>/<BOEK>.<H>.json` ontbreekt**: het script meldt dat
  fetch eerst nodig is. Sla HSV-spiegel volledig over voor deze batch;
  rapporteer in eindverslag dat de spiegel niet beschikbaar was. Géén
  blokker — beoordeling gaat door op false-friend / idiomatische /
  concordantie.
- **`hsv` is leeg-string voor één specifiek vers**: zou bij correct
  gefetchte HSV niet moeten voorkomen (HSV staat 1-op-1 per vers
  zonder bundeling of versnummer-prefix), maar als het toch gebeurt:
  sla dat ene vers over in de spiegel; vermeld in eindverslag.
- **`compare_hsv.py` non-zero exit / crash**: noteer in eindverslag,
  ga door zonder spiegel.
- **Intro / epiloog**: HSV heeft geen apart intro- of epiloog-veld;
  `compare_hsv.py` zet `hsv: null` met status `"no_hsv_equivalent"`.
  Dit is geen foutgeval — gewoon overslaan voor intro/epiloog
  (deze skill draait sowieso niet op intro/epiloog, zie sectie boven).

### 2.5.3 Inlezen

Lees `docs/diff_hsv_<BOEK>_<H>.json` **met de Read-tool** — niet via
`cat` / `python3 -c "... print"` / `jq` naar stdout; dat echoot de hele
diff de orchestratorcontext in. Per batch-vers extract
`{verse_number, sv2026, hsv, original}`. **Strip `<HSV: …>` en
`<HSV-aant: …>` blokken** uit het `hsv`-veld vóór vergelijking — dat zijn
HSV-vertalersaantekeningen (vergelijkbaar met onze
`<kanttekening>`-axis), géén vertaalde hoofdtekst. Findings die over
inhoud uit die blokken gaan, zijn ongeldig. Bewaar het opgeschoonde
HSV-vers in werkgeheugen voor Stap 3 (categorie 4).

## Stap 3 — review, arbitrage en rapportage

Open `references/semantic_protocol.md` zodra Stap 1, Stap 2, Stap 2.1 en Stap 2.5 zijn uitgevoerd. Dat detailprotocol bevat de per-vers checklist, flagarbitrage, actiepad per bevinding en het verplichte eindverslag.
