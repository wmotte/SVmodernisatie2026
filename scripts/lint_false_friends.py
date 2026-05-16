"""Lint output op false friends — woorden die in modern NL bestaan maar
met andere betekenis dan in de SV1657. Deterministisch, lijst-based.

Synchroniseer FALSE_FRIENDS hieronder met de "False friends"-tabel in
ARCHAISMEN.md. Bij toevoeging in dat document: spiegel hier ook.

False-friend matches zijn **warnings**, geen hard issues — sommige
gevallen zijn in context wel correct (bv. 'menen' kan in modernisatie
prima zijn als de SV-betekenis óók 'denken' was). De lint is bedoeld
als review-prompt, niet als blokker.

CLI:
    uv run python scripts/lint_false_friends.py lint --output output/LUK/LUK.1.json
    uv run python scripts/lint_false_friends.py lint --root output/

Exit-code 0 = geen matches, 1 = minstens één match (zodat CI optioneel
kan halten — handmatig review blijft voor warnings nodig).
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Synchroniseer met ARCHAISMEN.md sectie "False friends".
FALSE_FRIENDS: list[dict] = [
    {
        "pattern": r"\bvervolgens\b",
        "sv": "in volgorde, op rij (Gr. καθεξῆς)",
        "modern": "daarna, subsequently",
        "advies": "'op volgorde', 'achtereenvolgens'",
    },
    {
        "pattern": r"\b(gemeen|gemene)\b",
        "sv": "gewoon, alledaags, algemeen",
        "modern": "vulgair, slecht",
        "advies": "'gewoon', 'algemeen'",
    },
    {
        "pattern": r"\baanstonds\b",
        "sv": "dadelijk, direct, onmiddellijk",
        "modern": "(zelden gebruikt; vaag)",
        "advies": "'dadelijk', 'direct'",
    },
    {
        "pattern": r"\b(bekwaam|bekwame)\b",
        "sv": "geschikt, passend",
        "modern": "vaardig, kundig",
        "advies": "'geschikt', 'passend'",
    },
    {
        "pattern": r"\b(menen|meent|meende|meenden|gemeend)\b",
        "sv": "denken, van mening zijn",
        "modern": "menen ≈ vaag denken, lichtere lading",
        "advies": "'menen' of 'van mening zijn' (controleer lading)",
    },
    {
        "pattern": r"\b(wijf|wijven)\b",
        "sv": "echtgenote, vrouw (neutraal)",
        "modern": "denigrerend",
        "advies": "'vrouw' of 'echtgenote'",
    },
    {
        "pattern": r"\b(ontroeren|ontroerd|ontroerde|ontroert)\b",
        "sv": "ontstellen, verontrusten, schrikken (Gr. ταράσσω)",
        "modern": "geraakt door emotie, gerührt",
        "advies": "'ontstellen', 'verontrusten', 'schrikken'",
    },
    {
        "pattern": r"\brechten\b",
        "sv": "verordeningen, statuten (Gr. δικαιώματα — Gods inzettingen)",
        "modern": "rights, juridische rechten, rechtsstudie",
        "advies": "'voorschriften', 'verordeningen', 'inzettingen' (controleer context — soms is 'recht doen' o.i.d. wel correct)",
    },
    {
        "pattern": r"\bdagorde(n)?\b",
        "sv": "priesterafdeling die op zijn beurt tempeldienst deed (Gr. ἐφημερία)",
        "modern": "agenda, vergaderpunten",
        "advies": "behoud van 'dagorde' alleen als de kanttekening de SV-betekenis uitlegt; anders 'dienstbeurt' / 'priesterafdeling'",
    },
    {
        "pattern": r"\bergernis(sen)?\b",
        "sv": "struikelblok, aanstoot (Gr. σκάνδαλον / πρόσκομμα)",
        "modern": "irritatie, vervelend gevoel",
        "advies": "'aanstoot', 'struikelblok' — 'ergernis te geven' leest modern als 'vervelend doen'",
    },
    {
        "pattern": r"\bsmadelijk(e)?\b",
        "sv": "schandelijk, een schande zijnd (predikaat van toestand)",
        "modern": "smadelijk = van handelingen ('smadelijke nederlaag'), niet van toestanden",
        "advies": "voor toestand: 'als schande gold', 'een schande was'; niet 'smadelijk was'",
    },
    {
        "pattern": r"\b(leerde|leerden|leert)\b",
        "sv": "doceren, onderwijzen (Gr. διδάσκω) — werkwoord van leraar/Christus",
        "modern": "primair: zelf opnemen, studeren ('ik leer Frans')",
        "advies": "'onderwees' / 'onderwijst' wanneer subject de leraar/Christus/Apostel is; 'leerde' alleen als de subject-rol echt 'leerling' is",
    },
    {
        "pattern": r"\b(bestaan|bestond|bestonden|bestaat)\b(?=.*\bte\b)",
        "sv": "wagen, durven (idiom: 'het had bestaan te ...')",
        "modern": "existeren, er zijn",
        "advies": "'het waagde te ...', 'het durfde ...'; controleer of"
                  " het idiom hier bedoeld is — anders carry-over OK",
    },
    {
        "pattern": r"\b(verstaan|verstaat|verstond|verstonden)\s+worden\b",
        "sv": "bedoeld worden (passieve uitleg-formule in kanttekening)",
        "modern": "begrepen worden, gehoord worden",
        "advies": "'bedoeld worden' / 'aangeduid worden'",
    },
    {
        "pattern": r"\b(gelost|loste|lossen)\b",
        "sv": "vrijgekocht / loskopen (Lev. 27, Num. 18 — losgelden)",
        "modern": "afladen, oplossen, afvuren, ontkoppelen",
        "advies": "'vrijgekocht' / 'losgekocht'; alleen carry-over als"
                  " context écht 'afladen/oplossen' is",
    },
    {
        "pattern": r"\b(beschadigen|beschadigd|beschadigt|beschadigde)\b",
        "sv": "letsel/schade toebrengen aan persoon (Gr. ἀδικέω / βλάπτω)",
        "modern": "schade toebrengen aan een zaak/object (niet persoon)",
        "advies": "voor persoon: 'letsel toebrengen', 'schade berokkenen';"
                  " 'beschadigen' van persoon leest modern absurd-technisch"
                  " (LUK 4:35, 10:19)",
    },
    {
        "pattern": r"\b(doorbrengen|doorgebracht|doorbracht|doorbrachten)\b",
        "sv": "verkwisten, erdoorheen jagen (geld/goed) — bij object 'geld'/'goed'/'bezit'",
        "modern": "tijd doorbrengen (met iemand, ergens)",
        "advies": "bij geld/bezit-object: 'verkwisten' / 'opmaken' /"
                  " 'erdoorheen jagen'; bij tijd-object is carry-over OK"
                  " (LUK 15:13, 15:30)",
    },
    {
        "pattern": r"\b(hof|hove|hoven)\b",
        "sv": "ommuurde woonruimte/erf óf moestuin (context-afhankelijk)",
        "modern": "vorstenhof, rechtbank, formele tuin",
        "advies": "controleer SV-referent in context: 'erf' / 'woning'"
                  " (LUK 11:21) of 'tuin' (LUK 13:19); 'hof' bewaart de"
                  " moderne lezer geen van beide",
    },
]


def _scan(text: str) -> list[dict]:
    """Geef alle false-friend matches in deze tekst."""
    matches: list[dict] = []
    for entry in FALSE_FRIENDS:
        for m in re.finditer(entry["pattern"], text, flags=re.IGNORECASE):
            matches.append(
                {
                    "match": m.group(0),
                    "pattern": entry["pattern"],
                    "sv_betekenis": entry["sv"],
                    "modern_betekenis": entry["modern"],
                    "advies": entry["advies"],
                }
            )
    return matches


def _split_hoofdtekst_kanttekeningen(text: str) -> tuple[str, str]:
    kant_inner = " ".join(re.findall(r"<([^>]+)>", text))
    hoofdtekst = re.sub(r"<[^>]+>", " ", text)
    return hoofdtekst, kant_inner


def _scan_verse(verse: dict) -> dict:
    mod = verse.get("modernized", "")
    hoofd, kant = _split_hoofdtekst_kanttekeningen(mod)
    return {
        "verse_number": verse.get("verse_number"),
        "hoofdtekst": _scan(hoofd),
        "kanttekeningen": _scan(kant),
    }


def _scan_section(name: str, section: object) -> dict:
    if isinstance(section, dict):
        text = section.get("modernized", "") or ""
    elif isinstance(section, str):
        text = section
    else:
        text = ""
    return {"section": name, "matches": _scan(text)}


def _scan_file(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    verse_results = []
    for v in data.get("verses", []):
        r = _scan_verse(v)
        if r["hoofdtekst"] or r["kanttekeningen"]:
            verse_results.append(r)

    section_results = []
    for sec_name in ("introduction", "epilogue"):
        if data.get(sec_name):
            sr = _scan_section(sec_name, data[sec_name])
            if sr["matches"]:
                section_results.append(sr)

    return {
        "file": str(path),
        "book": data.get("book"),
        "chapter": data.get("chapter"),
        "verses_with_matches": verse_results,
        "sections_with_matches": section_results,
    }


def cmd_lint(args: argparse.Namespace) -> int:
    if args.output:
        files = [Path(args.output)]
    elif args.root:
        files = sorted(Path(args.root).rglob("*.json"))
    else:
        print(json.dumps({"error": "geef --output of --root"}), file=sys.stderr)
        return 2

    results = []
    n_matches = 0
    n_scanned = 0
    for fp in files:
        if not fp.exists():
            continue
        n_scanned += 1
        r = _scan_file(fp)
        if r["verses_with_matches"] or r["sections_with_matches"]:
            n_matches += sum(
                len(v["hoofdtekst"]) + len(v["kanttekeningen"])
                for v in r["verses_with_matches"]
            )
            n_matches += sum(
                len(s["matches"]) for s in r["sections_with_matches"]
            )
            results.append(r)

    if args.terse:
        if n_matches == 0:
            print(f"false_friends 0 (scanned {n_scanned} files)")
        else:
            lines = [f"false_friends {n_matches} in {len(results)}/{n_scanned} files"]
            for r in results:
                book = r["book"]
                chapter = r["chapter"]
                parts = []
                for v in r["verses_with_matches"]:
                    words = sorted({m["match"] for m in v["hoofdtekst"] + v["kanttekeningen"]})
                    parts.append(f"v{v['verse_number']}:[{','.join(words)}]")
                for s in r["sections_with_matches"]:
                    words = sorted({m["match"] for m in s["matches"]})
                    parts.append(f"{s['section']}:[{','.join(words)}]")
                lines.append(f"{book} {chapter}: " + " ".join(parts))
            print("\n".join(lines))
        return 0 if n_matches == 0 else 1

    summary = {
        "false_friends_size": len(FALSE_FRIENDS),
        "files_scanned": n_scanned,
        "files_with_matches": len(results),
        "total_matches": n_matches,
        "details": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if n_matches == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser(
        "lint",
        help="Scan output op false friends tegen de FALSE_FRIENDS-lijst.",
    )
    sp.add_argument("--output", default=None, help="Pad naar één output JSON.")
    sp.add_argument("--root", default=None, help="Directory recursief scannen.")
    sp.add_argument("--terse", action="store_true",
                    help="Compacte tekstuele output ipv. JSON.")
    sp.set_defaults(func=cmd_lint)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
