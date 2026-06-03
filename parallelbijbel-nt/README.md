# parallelbijbel-nt/

Eén enkele parallelbijbel-PDF voor het **hele Nieuwe Testament** (voor zover
beschikbaar in `output/`), in plaats van één PDF per bijbelboek.

Hergebruikt de per-vers-renderers en de gedeelde preamble van
`../parallelbijbel/` en rijgt alle beschikbare
`output/<BOEK>/<BOEK>.<N>.json` aan elkaar in NT-canonvolgorde tot één
document: een NT-titelpagina, daarna per boek een titelpagina (rechts
beginnend) gevolgd door de hoofdstukken. Twee kolommen per opening — links
de Statenvertaling 1657 met kanttekeningen, rechts de gemoderniseerde versie
met kanttekeningen, gepaarde voetnootblokken onderaan. Trimsize 170 × 249 mm.

De lopende kop wisselt automatisch per boek (`\bookname`) en per hoofdstuk
(`\hoofdstuknr`).

## Resultaat

`NT.pdf` (gepubliceerd in deze map) — de volledige uitgave.
`build/NT.{tex,pdf,aux,log,...}` — bouw-artefacten (niet getrackt).

Boeken zonder output (bv. **ACT**) worden stilzwijgend overgeslagen;
gedeeltelijk afgewerkte boeken (bv. **MAT** = 8 hoofdstukken) worden
opgenomen voor zover de hoofdstukken bestaan.

## Bouwen

```bash
cd parallelbijbel-nt
python build_nt.py                  # hele NT -> build/NT.pdf, publiceert NT.pdf
python build_nt.py --books LUK JHN  # alleen deze boeken, in die volgorde
python build_nt.py --no-pdf         # alleen build/NT.tex genereren
python build_nt.py --no-publish     # build/NT.pdf niet naar NT.pdf kopiëren
```

## Vereisten

Identiek aan `../parallelbijbel/`: **TeX Live 2023+ / MacTeX**, **LuaLaTeX** +
**latexmk** op PATH, font **EB Garamond** (OTF), Python 3.11+ (alleen stdlib).
De preamble valt terug op Garamond Premier Pro → Latin Modern Roman als
EB Garamond ontbreekt.

## Verschil met `../parallelbijbel/`

| | `parallelbijbel/` | `parallelbijbel-nt/` |
|---|---|---|
| Eenheid | één PDF per boek | één PDF voor het hele NT |
| Script | `build_book.py LUK` | `build_nt.py` |
| Titelpagina's | één per boek | NT-cover + per-boek |
| Renderers | eigen | hergebruikt `build_book.py` |
