# Kanttekening-conventies — SVmodernisatie2026

Regels voor het verwerken van kanttekeningblokken (`<...>`) bij
modernisatie. Aanvulling op `AGENTS.md` (sectie "Kanttekening-conventies").

## Behoud van blokken

`<…>` blokken **bewaren** (nooit verwijderen, nooit samenvoegen). Aantal
in de modernisatie ≥ aantal in het origineel.

## Standaard-vertalingen voor afkortingen

Standaard-vertalingen voor afkortingen binnen kanttekeningen:

| Origineel            | Modern                |
|----------------------|-----------------------|
| `<D. ...>`           | `<dat is, ...>`       |
| `<Gr. ...>`          | `<Grieks: ...>`       |
| `<Hebr. ...>`        | `<Hebreeuws: ...>`    |
| `<Namelick, ...>`    | `<Namelijk, ...>`     |
| `<Namel. ...>`       | `<Namelijk, ...>`     |
| `<Nam. ...>`         | `<Namelijk, ...>`     |
| `<Ofte, ...>`        | `<Of, ...>`           |
| `<Siet ...>`         | `<Zie ...>`           |
| `<Vergel. ...>`      | `<Vergelijk ...>`     |

## "Hebr." midden in een kanttekening = Hebraïsme-marker

Als `Hebr.` aan het **begin** van een kanttekening of na een term staat
(`<Hebr. דָּבָר>`, `<… Hebr. רוּחַ>`), is het een vertaalglosse en
volgt het de standaard: `<Hebreeuws: …>`.

Maar als `Hebr.` **midden in een kanttekening** staat — los, niet als prefix bij
een Hebreeuws woord — duidt het aan dat de voorgaande Griekse zin een
Hebraïsme is (Hebreeuws idiomatisch denkpatroon achter het Grieks).
Dan **niet** vertalen als "Hebreeuws:" want dat klopt grammaticaal noch
semantisch. Twee opties:

- Vervang door `Hebraïsme,` of `Hebreeuws idiomatisch,`.
- Bij twijfel over interpretatie: laat `Hebr.` letterlijk staan en
  documenteer in `notes` (`type: "twijfel"`).

Voorbeeld uit LUK 1:2 kanttekening 2:

```
Origineel: <Dat is, der sake die hier beschreven wort. Hebr. hoewel
           sommige meenen dat hier door Christus selve verstaen wort,
           gelijck hy alsoo genaemt wort Ioan. 1.1.>
```

Hier is `Hebr.` géén vertaalglosse (er volgt geen Hebreeuws woord);
het signaleert dat "der sake / des woorts" een Hebraïsme reflecteert
(Hebreeuws דָּבָר = woord én zaak). Standaard "Hebreeuws: hoewel
sommige…" levert onzin op. Letterlijk behouden of als "Hebraïsme,"
weergeven.

## Griekse termen in `<Gr. …>`-blokken

Als de Griekse term in een `<Gr. …>`-kanttekening een **modern Nederlands
leenwoord** is met dezelfde wortel, gebruik dan de moderne Nederlandse
spelling. De 1657-Nederlandse spelling van zo'n leenwoord is een
archaïsme zoals elk ander en valt onder AGENTS.md regel 5 (modernisatie
geldt ook in kanttekeningen).

| 1657-spelling      | Modern                |
|--------------------|-----------------------|
| Euangelizeeren     | Evangeliseren         |

De hoofdletter volgt het SV-hoofdletterpatroon (AGENTS.md regel 5): als de
1657-spelling met hoofdletter staat (`Euangelizeeren` na `<Gr. …>`), behoudt de
modernisatie die hoofdletter (`Evangeliseren`). Niet vervlakken naar kleine letter
zoals modern Nederlands soms zou doen voor werkwoord-lemma's.

Als de Griekse term geen modern Nederlands equivalent heeft (vakterm of
pure transliteratie zonder leenwoordstatus), laat de Latijnse
transcriptie staan en plaats die — indien nuttig — in cursief / tussen
aanhalingstekens. Voorbeelden: `Ephemeria` (priesterafdeling, geen
modern Nederlands woord) blijft staan; `Logos` blijft `Logos`.

Vuistregel: zoekt een geletterde lezer dit woord op in een modern
woordenboek en vindt hij het? Dan moderniseer de spelling. Zo niet,
laat staan en geef context in dezelfde of een aansluitende kanttekening.

## Geen redundantie met de hoofdtekst

**Geen redundantie** tussen kanttekening en hoofdtekst. Als een
kanttekening een alternatief geeft (`<Ofte, aanstoot>` bij `ergernisse`),
gebruik dat alternatief NIET in de hoofdtekst — kies een derde modern
synoniem of laat de hoofdtekst-keuze passen bij het bredere woordveld.
