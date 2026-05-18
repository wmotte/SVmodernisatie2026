# Scaffolding-deltas — meta-review LUK hoofdstukken 1-18

Gegenereerd: 2026-05-18
Aggregator: `scripts/meta_diff_aggregate.py --book LUK --chapters 1-18 --min-freq 2`
Totaal patterns: 17 (cap-asym 14, carryover 2, latinaat-window 1)

## Auto-toegepaste deltas (bucket C)

Geen. Geen pattern haalde de productiviteits/constructie/verwarringtest §2.7
voor auto-regelaanscherping. Twee carryover-patronen leverden wel per-vers
fixes op (zie bucket B), maar niet de drempel-N voor scaffolding-uitbreiding
(`hoe` 4× — slechts 2 problematisch; `toe` 2× — slechts 1 problematisch).

## Afgewezen deltas (rejected, §2.7-toets niet gehaald)

| Pattern | Kind | Reden afwijzing |
|---|---|---|
| `lijkt een mens die een` | latinaat-window | Geen Latinaat. Verkorte 'is gelijk aan'-constructie binnen één hoofdstuk (LUK 6:48,49). Beide moderne syntaxis, geen recurrent patroon over hoofdstukken. |
| `hoe` (LUK 8:47, 9:41) | carryover | Modern functioneel ('hoe zij genezen was', 'hoe lang'). Geen drempel-archaïsme; HSV-alternatieven zijn herschikking, geen lexicale eis. |
| `toe` (LUK 15:20) | carryover | 'Hij liep toe en viel hem om de hals' — modern leesbaar in context. HSV herschikt volledig; geen lexicale eis. |

## Noise (bucket A — HSV-keuze, geen actie)

| Kind | Aantal | Voorbeelden |
|---|---|---|
| cap-asym (eerbiedshoofdletter / titulaire functie) | 14 keys / 76 occurrences | Profeten (11×), Sabbat (9×), Profeet (8×), Synagoge (7×), Engel (5×), Engelen (5×), Wetgeleerden (4×), Mammon (3×), Schriftgeleerden (3×), Viervorst (3×), Heidenen (2×), Koning (2×), Stadhouder (2×), Synagogen (2×) |
| latinaat-window (HSV-herschikking) | 1 key / 2 occurrences | 'lijkt een mens die een' (LUK 6:48,49) |
| carryover (modern functioneel) | 3 occurrences | LUK 8:47, 9:41, 15:20 |

Cap-asym is SV1657-conventie: eerbiedshoofdletter (Engel, Profeet/Profeten,
Heidenen) en titulaire posities (Sabbat, Synagoge, Wetgeleerden,
Schriftgeleerden, Mammon, Viervorst, Koning, Stadhouder). HSV kiest
consistent lowercase. SV2026 mag SV-conventie behouden — geen
modernisatie-tekortkoming.

## Bucket-overzicht

- B (per-vers fixes): 3 issues over 3 hoofdstukken (LUK 10, 12, 16) — zie `findings.json`
- C (scaffolding-deltas): 0 toegepast, 3 afgewezen
- A (noise): 76 occurrences over 14 cap-asym keys + 2 latinaat-window + 3 carryover

## Bevindingen-detail (bucket B)

1. **LUK 10:26** — 'Hoe leest u?' → 'Wat leest u daar?' (drempel: dubbelzinnig in modern NL).
2. **LUK 12:15** — 'Zie toe en wacht u voor de hebzucht' → 'Pas op en wees op uw hoede voor de hebzucht' (twee drempel-archaïsmen in één imperatief).
3. **LUK 16:2** — 'Hoe hoor ik dit van u?' → 'Wat hoor ik daar over u?' (verouderd vraagregister).

Alle drie soft severity — semantisch correct in SV2026, maar drempel-laag
voor moderne lezer. Apply-modus vereist expliciete trigger
(`meta-review LUK apply content`).
