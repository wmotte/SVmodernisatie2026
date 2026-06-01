# parallelbijbel/

High-quality parallel-bible PDFs generated from the project's
`output/<BOOK>/<BOOK>.<N>.json` files. Two columns per opening:
left the Statenvertaling 1657 with kanttekeningen, right the modernized
version with kanttekeningen. Paired page-bottom note blocks. Trimsize 170 × 249 mm.

## Beschikbare boek-PDFs

Op volgorde van de NT-canon. `build/<BOEK>.pdf` is de volledige uitgave,
`<BOEK>_voorbeeld.pdf` een voorbeeldfragment.

| Code | Titel | Volledig | Voorbeeld |
|---|---|---|---|
| MRK | Het Evangelie naar Marcus | [MRK.pdf](build/MRK.pdf) | [MRK_voorbeeld.pdf](MRK_voorbeeld.pdf) |
| LUK | Het Evangelie naar Lucas | [LUK.pdf](build/LUK.pdf) | [LUK_voorbeeld.pdf](LUK_voorbeeld.pdf) |
| JHN | Het Evangelie naar Johannes² | [JHN.pdf](build/JHN.pdf) | [JHN_voorbeeld.pdf](JHN_voorbeeld.pdf) |
| ROM | De brief van Paulus aan de Romeinen | [ROM.pdf](build/ROM.pdf) | [ROM_voorbeeld.pdf](ROM_voorbeeld.pdf) |
| 1CO | De eerste brief van Paulus aan de Korintiërs | [1CO.pdf](build/1CO.pdf) | [1CO_voorbeeld.pdf](1CO_voorbeeld.pdf) |
| 2CO | De tweede brief van Paulus aan de Korintiërs | [2CO.pdf](build/2CO.pdf) | [2CO_voorbeeld.pdf](2CO_voorbeeld.pdf) |
| GAL | De brief van Paulus aan de Galaten | [GAL.pdf](build/GAL.pdf) | [GAL_voorbeeld.pdf](GAL_voorbeeld.pdf) |
| EPH | De brief van Paulus aan de Efeziërs | [EPH.pdf](build/EPH.pdf) | [EPH_voorbeeld.pdf](EPH_voorbeeld.pdf) |
| PHP | De brief van Paulus aan de Filippenzen | [PHP.pdf](build/PHP.pdf) | [PHP_voorbeeld.pdf](PHP_voorbeeld.pdf) |
| COL | De brief van Paulus aan de Kolossenzen | [COL.pdf](build/COL.pdf) | [COL_voorbeeld.pdf](COL_voorbeeld.pdf) |
| 1TH | De eerste brief van Paulus aan de Tessalonicenzen | [1TH.pdf](build/1TH.pdf) | [1TH_voorbeeld.pdf](1TH_voorbeeld.pdf) |
| 2TH | De tweede brief van Paulus aan de Tessalonicenzen | [2TH.pdf](build/2TH.pdf) | [2TH_voorbeeld.pdf](2TH_voorbeeld.pdf) |
| 1TI | De eerste brief van Paulus aan Timoteüs | [1TI.pdf](build/1TI.pdf) | [1TI_voorbeeld.pdf](1TI_voorbeeld.pdf) |
| 2TI | De tweede brief van Paulus aan Timoteüs | [2TI.pdf](build/2TI.pdf) | [2TI_voorbeeld.pdf](2TI_voorbeeld.pdf) |
| TIT | De brief van Paulus aan Titus | [TIT.pdf](build/TIT.pdf) | [TIT_voorbeeld.pdf](TIT_voorbeeld.pdf) |
| PHM | De brief van Paulus aan Filemon | [PHM.pdf](build/PHM.pdf) | [PHM_voorbeeld.pdf](PHM_voorbeeld.pdf) |
| HEB | De brief aan de Hebreeën | [HEB.pdf](build/HEB.pdf) | [HEB_voorbeeld.pdf](HEB_voorbeeld.pdf) |
| JAS | De brief van Jakobus | [JAS.pdf](build/JAS.pdf) | [JAS_voorbeeld.pdf](JAS_voorbeeld.pdf) |
| 1PE | De eerste brief van Petrus | [1PE.pdf](build/1PE.pdf) | [1PE_voorbeeld.pdf](1PE_voorbeeld.pdf) |
| 2PE | De tweede brief van Petrus | [2PE.pdf](build/2PE.pdf) | [2PE_voorbeeld.pdf](2PE_voorbeeld.pdf) |
| 1JN | De eerste brief van Johannes | [1JN.pdf](build/1JN.pdf) | [1JN_voorbeeld.pdf](1JN_voorbeeld.pdf) |
| 2JN | De tweede brief van Johannes | [2JN.pdf](build/2JN.pdf) | [2JN_voorbeeld.pdf](2JN_voorbeeld.pdf) |
| 3JN | De derde brief van Johannes | [3JN.pdf](build/3JN.pdf) | [3JN_voorbeeld.pdf](3JN_voorbeeld.pdf) |
| JUD | De brief van Judas | [JUD.pdf](build/JUD.pdf) | [JUD_voorbeeld.pdf](JUD_voorbeeld.pdf) |
| REV | De Openbaring van Johannes¹ | [REV.pdf](build/REV.pdf) | [REV_voorbeeld.pdf](REV_voorbeeld.pdf) |

¹ Nog onvolledig: hoofdstukken 1–11 van 22.

² Nog onvolledig: hoofdstukken 1–16 van 21.

## Vereisten

- **TeX Live 2023+** (of MacTeX). Vereiste packages: `fontspec`,
  `footmisc`, `microtype`, `hyperref`, `geometry`,
  `ragged2e`, `fancyhdr`, `etoolbox`.
- **LuaLaTeX** + **latexmk** op PATH.
- Font **EB Garamond** (OTF). Installeer via:
  - macOS: download van Google Fonts → `~/Library/Fonts/`
  - of `tlmgr install ebgaramond`
- Python 3.11+ (alleen stdlib).

## Bouwen

Eén bijbelboek (volledig):

```bash
cd parallelbijbel
python build_book.py LUK
```

Eén hoofdstuk (smoke-test):

```bash
python build_book.py LUK --only 24
```

Alleen `.tex` genereren (geen PDF-run):

```bash
python build_book.py LUK --no-pdf
```

Uitvoer landt in `build/`:

```
build/LUK.tex
build/LUK.pdf
build/LUK.{aux,log,out,fls,fdb_latexmk}
```

## Layout-keuzes

| Aspect | Waarde |
|---|---|
| Trimsize | 170 × 249 mm |
| Marges | binnen 11 mm, buiten 10 mm, boven 12 mm, onder 13 mm |
| Kolomscheiding | 5 mm |
| Hoofdtekst | EB Garamond 8.4 pt / leading 10.2 pt |
| Kanttekeningblok | 6.4 pt / leading 7.6 pt |
| Versnummers | superscript bold 6.4 pt |
| Bijbelverwijzingen | cursief 7.2 pt inline |
| Kanttekeningen | links SV, rechts gemoderniseerd onderaan de pagina |

## JSON → LaTeX-tokens

Inline syntax uit `OUTPUT_SCHEMA.md`:

| JSON | Render |
|---|---|
| `<noot>` | versnoot in links/rechts-kanttekeningblok |
| `$bibref$` | `\bref{bibref}` → cursief inline |
| `[invoeging]` | `\svins{[invoeging]}` → cursief inline |
| `HEERE` / `HEEREN` / `GOD` / `IESUS` | `\smc{...}` → small caps |

## Nieuwe bijbelboeken

Voeg in `BOOK_TITLES` (`build_book.py`) een titel toe. Geen verdere
wijzigingen nodig — script werkt generiek op `output/<BOOK>/`.
