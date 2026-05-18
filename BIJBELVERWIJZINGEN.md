# Bijbelverwijzingen — SVmodernisatie2026

Normalisatieformaat voor bijbelreferenties bij modernisatie van de
Statenvertaling 1657. Aanvulling op `AGENTS.md` (sectie
"Bijbelverwijzingen").

## Formaat

Formaat na normalisatie: `$Boek H:V$`, `$Boek H:V,W$`, `$Boek H:V-W$`, of
samengesteld `$Boek H:V; H:W$` (boeknaam alleen bij wisseling). De
`sv-bibref` skill (wrapper rond `scripts/bibref.py`) doet de conversie.

## Voorbeelden

- `$Iudic. 13.4.$` → `$Ri. 13:4$`
- `$Exod. 30.7. Levit. 16.17.$` → `$Ex. 30:7; Lv. 16:17$`
- `$Iesa. 9.1. ende 42.7. ende 43.8.$` → `$Js. 9:1; 42:7; 43:8$`

## Geen sluitpunt na `$...$`

SV1657 zet de terminator-punt **binnen** het bibref-blok: `Luce 7.27.$ Siet,`.
In de modernisering eindigt `$...$` **zonder** externe punt erbuiten — dus
`$Lk. 7:27$ Zie, ik zend …`, niet `$Lk. 7:27$. Zie, …`. Reden: renderers tonen
`$...$` als superscript-letter (a, b, c…); een spurieus extern punt levert
`, a.` op in de gerenderde tekst — een leesfout in plaats van een
verwijzing. Voorbeelden:

- Origineel `in de Propheten, $Malach. 3.1. Matth. 11.10. Luce 7.27.$ Siet,`
  → modern `in de Profeten, $Ml. 3:1; Mt. 11:10; Lk. 7:27$ Zie,`
- Origineel `$Iesa. 40.3. Matth. 3.3.$ De stemme` → modern
  `$Js. 40:3; Mt. 3:3$ De stem`

`validate.py` check 4c vangt regressies: als het origineel `.$` heeft
(punt-direct-voor-sluit-`$`) en de modernisering `$.` (sluit-`$`-direct-voor-punt)
heeft, faalt de validatie.

## Verwijzingen binnen kanttekeningen

Verwijzingen binnen kanttekeningen volgen hetzelfde formaat **én staan ook tussen
`$...$`**, zodat een regex-gebruiker ze in één ronde kan vinden — ongeacht
of ze in hoofdtekst of kanttekening staan. Voorbeelden:

- `<Siet 1.Ioan. 1.1.>` → `<Zie $1Jh. 1:1$.>`
- `<… 1.Cor. 14. vers 19. Gal. 6.6.>` → `<… $1Kor. 14:19; Gl. 6:6$.>`
- `<Siet Actor. 24.3. ende 26.25.>` → `<Zie $Hd. 24:3; 26:25$.>`

Met de vlag `--include-kanttekeningen` doet `bibref.py` dit automatisch —
geen handwerk meer voor losse verwijzingen. De validator (`sv-validate`) markeert
losse verwijzingen binnen `<…>` als harde fout om regressies te voorkomen.
