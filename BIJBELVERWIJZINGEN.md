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
