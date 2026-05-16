---
name: sv-memory
description: Vectordatabase voor gemoderniseerde SV-verzen. Sla per vers twee embeddings op (SV-origineel + modernisatie) via de embeddings-service (nu Gemini, verwisselbaar via scripts/memory.py) zodat de moderniseer-skill eerdere paren als voorbeeld kan ophalen. Gebruik query vóór elke modernisatie en add ná geslaagde validatie. Database start leeg en groeit — een lege query is geen fout.
---

# sv-memory — vectordatabase

Wrapper rond `scripts/memory.py`. Werkdirectory:
`/Users/wmotte/Desktop/projects/SVmodernisatie2026/`.

## query — top-k vergelijkbare verzen

Roep aan **vóór** modernisatie van elk vers:

```bash
python scripts/memory.py query --text "<sv-origineel>" --k 5 --axis sv \
  --exclude-book LUK --exclude-chapter 1 --exclude-verse 1 --terse
```

Argumenten:
- `--text`: de zoektekst. Voor modernisatie: het SV-origineel van het
  vers dat je gaat moderniseren.
- `--k`: aantal resultaten (standaard 5).
- `--axis`: op welke embedding zoeken — `sv` (standaard, zoekt op
  archaïsche vorm), `mod` (zoekt op moderne formulering), of `both`
  (max van beide).
- `--exclude-book` / `--exclude-chapter` / `--exclude-verse`: sluit dit
  exacte tuple `(book, chapter, verse)` uit het resultaat. Alles of niets
  (één weglaten = `sys.exit(2)`). Bij her-modernisatie van een bestaand
  vers verplicht: voorkomt dat het vers zichzelf als voorbeeld terugziet
  (zelf-bevestigend). Bij eerste modernisatie no-op (vers staat nog niet
  in de database).
- `--terse`: drop `source_text`-veld uit elke hit. Bespaart ~33% per
  call. Bij twijfel over een Grieks lemma: laat `--terse` weg.

Output (stdout, JSON):

```json
{
  "results": [
    {
      "book": "LUK",
      "chapter": 1,
      "verse": 1,
      "sv": "...",
      "modern": "...",
      "similarity": 0.87,
      "source_text": "..."
    }
  ],
  "total_in_db": 47,
  "axis": "sv"
}
```

**Lege DB:** als `total_in_db == 0`, komt er `{"results": []}` terug.
Dat is geen fout — de eerste verzen die je moderniseert hebben geen
voorbeelden, en dat is per definitie zo.

## add — voeg gemoderniseerd vers toe

Roep aan **ná** geslaagde validatie voor elk vers dat passeerde. Twee
varianten:

### a) `--from-output` (aanbevolen)

```bash
python scripts/memory.py add --from-output output/LUK/LUK.1.json --verse 1 --terse
# of voor alle verzen in het bestand:
python scripts/memory.py add --from-output output/LUK/LUK.1.json --all --terse
```

`--terse` levert één regel `<BOEK> <H>:<verses> -> <total>` ipv. JSON.
Laat weg voor volledige JSON.

Leest `book`, `chapter`, `original`, `modernized`, `source_text` uit de
output-JSON. Voorkomt shell-quoting voor lange teksten met
kanttekeningen en aanhalingstekens.

### b) Expliciete tekst (legacy / scripted)

```bash
python scripts/memory.py add \
  --book LUK --chapter 1 --verse 1 \
  --sv "<originele tekst incl. kanttekeningen>" \
  --modern "<moderne tekst incl. moderne kanttekeningen>" \
  --source-text "<Textus Receptus>"
```

Upsert op `(book, chapter, verse)` — heraanroep overschrijft de
bestaande entry.

Output (stdout, JSON — zonder `--terse`):

```json
{"ok": true, "book": "LUK", "chapter": 1, "verse": 1, "total": 48}
```

Met `--terse`: `LUK 1:1 -> 48`

## count — aantal verzen in DB

Voor diagnose:

```bash
python scripts/memory.py count
```

Output: `{"count": 47}`.

## Werkrichtlijnen

- Gebruik `--axis sv` voor de standaardstroom ("welke archaïsche
  structuren heb ik eerder gemoderniseerd?"). Schakel naar `mod` of
  `both` alleen als de SV-tekst zo afwijkend is dat sv-axis geen goede
  matches geeft.
- Filter zelf op `similarity` als je zinvolle voorbeelden wilt: onder
  0.5 zit doorgaans ruis. Geen hard cutoff — beoordeel per geval.
- Geen `add` zonder voorafgaande validatie. Slecht gemoderniseerde
  verzen vervuilen de voorbeeldverzameling van toekomstige aanroepen.
- Bij **her-modernisatie** (heraanroep voor een vers dat al in de DB
  zit): gebruik altijd `--exclude-book/chapter/verse` op de query.
  Anders matcht het vers (bijna) maximaal op zichzelf en krijg je
  zelfbevestigende voorbeeldparen in plaats van verbetering. `add` daarna
  doet automatisch upsert via `ON CONFLICT(book, chapter, verse)`.
