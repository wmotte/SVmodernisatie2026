---
name: sv-bibref
description: Normaliseer SV1657-bijbelverwijzingen ($...$ blokken) naar moderne notatie. Tweetraps CSV-lookup zet 'Iudic. 13.4.' om naar 'Ri. 13:4'. Idempotent. Roep aan voor elke moderne tekst voordat je hem naar de uitvoer schrijft.
---

# sv-bibref — normalisatie van bijbelverwijzingen

Wrapper rond `scripts/bibref.py`. Werkdirectory:
`/Users/wmotte/Desktop/projects/SVmodernisatie2026/`.

## normalize

```bash
python scripts/bibref.py normalize \
    --current-book LUK [--include-kanttekeningen] \
    "<tekst-met-\$...\$-blokken>"
```

Argumenten:
- `--current-book`: 3-letterige projectcode (`LUK`, `MAT`, ...). Wordt
  gebruikt voor impliciete refs (`$3:1$` zonder boeknaam → `$Lk. 3:1$`
  bij `--current-book LUK`).
- `--include-kanttekeningen`: óók losse verwijzingen binnen `<...>` blokken
  normaliseren **én in `$...$` zetten**, zodat een regex-gebruiker ze
  kan vinden ongeacht of ze in hoofdtekst of kanttekening staan.
  Voorkomt handwerk voor SV1657-kanttekeningen die `1.Cor. 14. vers 19.`
  als platte tekst schrijven. Idempotent. Aanbevolen tijdens modernisatie.
- positioneel argument: de complete moderne tekst (hoofdtekst + kanttekeningen).
  Quote met single-quotes als de tekst dollars of dubbele quotes bevat.

Output: tekst met genormaliseerde refs op stdout.

## Voorbeelden

| Input                                  | Output                              |
|----------------------------------------|-------------------------------------|
| `$Iudic. 13.4.$`                       | `$Ri. 13:4$`                        |
| `$1.Chron. 24.10.$`                    | `$1Kr. 24:10$`                      |
| `$Exod. 30.7. Levit. 16.17.$`          | `$Ex. 30:7; Lv. 16:17$`             |
| `$Iesa. 30.18. ende 41.9. ende 54.5.$` | `$Js. 30:18; 41:9; 54:5$`           |
| `$Hebr. 6.13, 17.$`                    | `$Hb. 6:13,17$`                     |
| `$Psalm 45. vers 7.$`                  | `$Ps. 45:7$`                        |
| `$Malach. cap. 4. vers 6.$`            | `$Ml. 4:6$`                         |
| `$Lk. 3:1$` (al modern)                | `$Lk. 3:1$` (idempotent)            |
| `<Siet 1.Ioan. 1.1.>` (kant)           | `<Zie $1Jh. 1:1$.>`                 |
| `<Actor. 24.3. ende 26.25.>` (kant)    | `<$Hd. 24:3; 26:25$.>`              |

## Werkrichtlijnen

- Draai **vóór** je de moderne tekst naar de uitvoer-JSON schrijft.
- Draai op de **complete moderne tekst** in één aanroep — het script
  vervangt alleen de `$...$` blokken (en met `--include-kanttekeningen`
  ook losse verwijzingen binnen `<...>`) en laat de rest met rust.
- Bij parse-fouten: het script geeft de oorspronkelijke `$...$` terug
  (best-effort, geen crash). Validate signaleert dit later via de
  bijbelref-formaat-check.

## Consistentiecontrole (eenmalig per inrichting)

```bash
python scripts/check_refdata.py
```

Doorloopt alle ketens `oldAbbr → fullName → modAbbr` in de twee CSV's
en de `PROJECT_CODE_TO_FULLNAME` mapping in `bibref.py`. Exit 0 = alles
verbonden, exit 1 = minstens één gat (bv. een typefout in afkortingen.csv).
Draai dit na elke wijziging in `refdata/` of `PROJECT_CODE_TO_FULLNAME`.
