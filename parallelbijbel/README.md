# parallelbijbel/

High-quality parallel-bible PDFs generated from the project's
`output/<BOOK>/<BOOK>.<N>.json` files. Two columns per opening:
left the Statenvertaling 1657 with kanttekeningen, right the modernized
version with kanttekeningen. Paired page-bottom note blocks. Trimsize 170 × 249 mm.

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
