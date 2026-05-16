"""Valideer een gemoderniseerd vers tegen het origineel.

Checks per vers:
  1. Aantal `<...>` blokken in modern >= aantal in origineel.
  2. Aantal `[...]` blokken identiek (vierkante haken markeren door SV-vertalers
     toegevoegde woorden — theologisch belangrijk om te bewaren).
  3a. Hoofdletter-discipline hoofdtekst: alle hoofdletter-content-woorden uit
     origineel komen in moderne tekst voor (modulo bekende moderne
     spelling-mappings; soft warning).
  3b. Hoofdletter-discipline kanttekeningen: zelfde regel binnen `<...>` blokken,
     zodat case-flips als "Leeraers" → "leraars" niet door de mazen glippen.
  4. Bijbelref-formaat: alle `$...$` matchen modern formaat
     (`Boek H:V` of `Boek H:V-W` of `Boek H:V,W` met optionele `; ...` herhaling).
     Plus: geen loose refs binnen `<kanttekeningen>` — alle refs moeten in
     `$...$` staan zodat regex-consumers ze kunnen onderscheiden.
  5. Archaisme-blacklist: geen `\\bende\\b`, `\\bghy\\b`, `\\baldaer\\b`, etc.
  6. Brontekst (`source_text`) ongewijzigd t.o.v. origineel.

Cross-vers (per hoofdstuk-bestand):
  7. Per-vers loop: geen twee verzen mogen exact dezelfde `generated_at`
     timestamp delen — dat verraadt batch-modernisatie ipv. de één-vers-per-
     cyclus die SKILL.md voorschrijft (memory-query tussen verzen wordt dan
     overgeslagen, concordantie lijdt).

Output: JSON op stdout met per-vers issues + aggregaat. Exit-code 0 = alles ok,
1 = minstens één vers heeft een hard issue (warnings tellen niet als fail).

Naast verzen kunnen ook de hoofdstuk-introductie en de boek-epiloog
gevalideerd worden via `--sections intro,epilogue`. Voor deze secties
worden de checks beperkt: kanttekening- en bijbelref-checks vervallen
(intro/epilogue bevatten die niet), maar `[…]` haken,
archaisme-blacklist en hoofdletter-warnings blijven gelden.

CLI:
    python scripts/validate.py check \\
        --input input.sv/LUK/LUK.1.json \\
        --output output/LUK/LUK.1.json \\
        --verses 1,2,3 \\
        --sections intro,epilogue
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bibref import find_loose_refs  # noqa: E402

# Archaïsmen die NIET in moderne tekst mogen staan. Word-boundaries.
ARCHAISM_BLACKLIST = [
    r"\bende\b",
    r"\bghy\b",
    r"\baldaer\b",
    r"\baldaar\b",
    r"\bsoo\b",
    r"\bdese\b",
    r"\bwelcke\b",
    r"\bvoortijts\b",
    r"\bdaerom\b",
    r"\bvrouwe\b",
    r"\bergernisse\b",
    r"\bsulcks\b",
    r"\bsulks\b",
    r"\bdoch\b",
    r"\bdaer\b",  # 'daer' is altijd fout; 'daar' is OK
    r"\bsy\b",
    r"\bhy\b",
    r"\bhaer\b",
    r"\bonse\b",
    r"\bgesproken hebbende\b",
    r"\bgegaan zijnde\b",
    r"\bzijnde\b(?! een)",  # 'zijnde' staan-alone is verdacht; "zijnde een" is OK
    r"\bhebbende\b",        # participle 'gekregen hebbende' etc. → unfold (AGENTS.md)
    r"\bnagetracht\b",      # archaïsch "nagestreefd"
    r"\bgeschied(t|de|den|en)?\b",  # hele 'geschieden'-paradigma → "gebeuren"-vormen (γίνομαι), concordantie. 'geschiede' (Onze Vader, Lk 11:2) en 'geschiedenis' blijven buiten schot.
    r"\bgelijk\b",          # voegwoord → "zoals"; verbuigingen (gelijke, gelijkenis) niet door \b geraakt
    r"\bvertoefde?\b",      # "vertoeven" is uitstervend literair → "blijven"
    r"\bvertoefden\b",
    r"\bhoedanig\b",        # archaïsch → "wat voor / van welke aard"
    r"\bhoedanige\b",
    r"\baanschouwer\b",     # → "ooggetuige" (Gr. αὐτόπτης)
    r"\baanschouwers\b",
    r"\bnochtans\b",        # → "toch"
    r"\balsdan\b",          # → "dan / vervolgens"
    r"\bterstond\b",        # → "onmiddellijk / meteen" (productiviteits-FAIL)
    r"\bonderwijzing\b",    # → "onderwijs / onderricht"
    r"\bonbillijk(e)?\b",   # → "onrechtvaardig"
    r"\bsmart(en)?\b",      # → "pijn(en) / verdriet"
    r"\bvolkomen\b",        # → "volledig / geheel" (als bijwoord)
    r"\btijding(en)?\b",    # → "boodschap / nieuws"
    r"\bderhalve\b",        # → "daarom / dus"
]

# Bekende spelling-mappings voor hoofdletter-check (origineel-vorm: moderne-vorm).
# Als origineel "Mattheus" heeft en modern "Matteüs", dan is dat OK.
SPELLING_EQUIV = {
    "Mattheus": ["Matteüs", "Mattheüs"],
    "Marcus": ["Marcus", "Markus"],
    "Lucas": ["Lucas"],
    "Bethlehem": ["Betlehem", "Bethlehem"],
    "Iesus": ["Jezus"],
    "Iesum": ["Jezus"],
    "Iesu": ["Jezus"],
    "Iudas": ["Judas"],
    "Iuda": ["Juda"],
    "Iudea": ["Judea"],
    "Iudaeae": ["Judea"],
    "Ioden": ["Joden"],
    "Ioodsche": ["Joodse"],
    "Iohannes": ["Johannes"],
    "Ioannes": ["Johannes"],
    "Ioannem": ["Johannes"],
    "Ioannis": ["Johannes"],
    "Ioannen": ["Johannes"],
    "Ioan": ["Johannes"],
    "Ioseph": ["Jozef"],
    "Iosephs": ["Jozefs", "Jozef"],
    "Iordaen": ["Jordaan"],
    "Iordane": ["Jordaan"],
    "Iordanes": ["Jordaan"],
    "Iacob": ["Jakob"],
    "Iacobus": ["Jakobus"],
    "Iacobum": ["Jakobus"],
    "Iacobi": ["Jakobus"],
    "Ierusalem": ["Jeruzalem"],
    "Israel": ["Israël", "Israel"],
    "Israëls": ["Israëls", "Israels"],
    "Aaron": ["Aäron", "Aaron"],
    "Aarons": ["Aärons", "Aäron", "Aarons"],
    "Cainan": ["Kenan", "Kainan"],
    "Capernaum": ["Kafarnaüm", "Kapernaüm", "Kapernaum"],
    "Keyser": ["Keizer"],
    "Keysers": ["Keizers", "Keizer"],
    "Salighmaker": ["Zaligmaker"],
    "Sone": ["Zoon"],
    "Sones": ["Zoons", "Zoon"],
    "Wort": ["Woord"],
    "Godts": ["Gods", "God"],
    "Godtheyt": ["Godheid"],
    "Godtlick": ["Goddelijk"],
    "Godtlicke": ["Goddelijke", "Goddelijk"],
    "Godtloos": ["Goddeloos"],
    "Leeraer": ["Leraar"],
    "Leeraers": ["Leraren", "Leraars", "Leraar"],
    "Christus": ["Christus"],
    "GODT": ["GOD"],
    "Godt": ["God"],
    "HEERE": ["HEERE", "HEER"],
    "Heere": ["Heere", "Heer"],
    "Christi": ["Christus", "Christi"],
    "JESU": ["Jezus"],
    "CHRISTI": ["Christus"],
}

# §2.3 participium-check — SV-stijl finiete tegenwoordige participia (en hun
# modern-gespelde varianten op `-end,`) moeten ontvouwd zijn naar een finiete
# bijzin. Zie MODERNISATIE.md §2.3 / §2.3b.
#
# Aanpak: expliciete lijst van bekende SV-participia, opgesplitst in
#   ALWAYS-BAD : altijd adverbial in moderne tekst (zeggende, ziende, …);
#                flag waar dan ook
#   CONTEXT    : kunnen attributief zijn (komende eeuw); flag alleen als
#                gevolgd door punctuatie (= adverbial) of niet door een
#                zelfst.nw.
#
# Een regex `\w+ende` is te grof: matched ook past-tense (kende, meende,
# diende, zegende), ordinalen (vijftiende) en adjectieven (verschillende).

# `-ende` participia die in modern Nederlands ALTIJD een SV-carry-over zijn
# (geen productieve attributief gebruik). Lower-cased.
PARTICIPLE_ALWAYS_BAD_ENDE: frozenset[str] = frozenset({
    # Direct-speech intros
    "zeggende", "seggende", "sprekende", "antwoordende", "roepende",
    "vragende", "ondervragende", "smekende",
    # Zien/horen
    "ziende", "horende", "hoorende",
    # Bewegen
    "uitvarende", "ingaande", "uitgaande", "heengaande",
    "neervallende", "neerknielende", "neerbuigende",
    "omkerende", "voortgaande",
    # Activiteiten (adverbial in SV)
    "etende", "drinkende", "wenende", "huilende", "lachende",
    "schreiende", "biddende", "wrijvende",
    "verkondigende", "predikende", "lezende", "schrijvende",
    "denkende", "menende", "wetende", "kennende",
    "begeerende", "begerende",
    "overleggende", "zoekende",
    # Latinaat-participiale doorlopers (toegevoegd na LUK 18:1 / 16:23 / 18:35 gap)
    "strekkende",   # 'daartoe strekkende dat …' — ontvouw naar 'die ertoe strekt dat …'
    "navolgende",   # 'enige navolgende' — modern: 'enkele die hierna volgen'
})

# `-ende` participia die context-afhankelijk zijn: attributief OK
# ('komende eeuw', 'staande orde'), adverbial NIET ('komende uit').
# Flag wanneer gevolgd door punctuatie of niet-zelfst.naamwoord.
# Met name: gevolgd door `[,:;]` of door een voorzetsel (`op`, `in`,
# `tot`, `aan`, `uit`, `van`, …) is een sterk adverbial-signaal.
PARTICIPLE_CONTEXT_ENDE: frozenset[str] = frozenset({
    "komende", "staande", "zittende", "weidende", "vallende", "varende",
    "liggende", "wandelende", "lopende", "bevende", "wakende",
    "wonende", "rustende", "slapende", "zwijgende",
    "toekomende",  # 'toekomende eeuw' attributief; adverbial flag
    "neerzittende",
})

# Adverbial-trigger woorden direct na een CONTEXT participium: voorzetsels
# en interpunctie. Als context-participium hierdoor wordt gevolgd, flag.
ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE = frozenset({
    "op", "in", "tot", "aan", "uit", "van", "met", "naar", "over",
    "onder", "boven", "tussen", "achter", "voor", "bij", "om", "door",
    "wat",  # "ziende wat ..." (zelfs al in always-bad, maar context handhaaft)
    # Subordinators direct na participium = altijd participium-clause, geen attributief gebruik
    # ('daartoe strekkende dat …', 'menende dat …', 'wetende waarom …').
    "dat", "toen", "terwijl", "omdat", "zodat", "wanneer", "waarom",
    "hoe", "of",
})

# Specifieke werkwoordstammen waarvan de modern-gespelde participium-vorm
# (`-end[,]`) als adverbiale clause-intro een §2.3-overtreding is. Catch
# bv. "Dit zeggend, riep hij" / "Bevende, viel zij neer". Voeg toe wanneer
# een nieuwe stam in review opduikt.
PARTICIPLE_BAD_END_STEMS: tuple[str, ...] = (
    "zegg", "sprek", "roep", "zien", "ziend", "horend", "hoorend",
    "gaand", "staand", "komend", "vallend", "brengend", "wandelend",
    "neervallend", "neerknielend", "neerbuigend", "antwoord",
    "doend", "lezend", "schrijvend", "etend", "drinkend", "weidend",
    "varend", "uitvarend", "ingaand", "uitgaand", "heengaand",
    "verkondigend", "predikend", "biddend", "smekend", "vragend",
    "denkend", "menend", "wetend", "kennend", "begeerd",
    "wenend", "huilend", "lachend", "schreiend",
)

REF_RE = re.compile(r"\$([^$]+)\$")
# Een geldige moderne ref: optionele afk + H:V[,W][-X][; ...]
# Voorbeelden: "Lk. 3:1", "Mt. 1:18,21", "Js. 30:18; 41:9", "Hb. 6:13,17"
MODERN_REF_PART = re.compile(
    r"^\s*(?:[1-3]?\s?[A-ZÀ-ÿ][a-zà-ÿ]*\.?\s+)?\d+:\d+(?:,\d+)*(?:-\d+)?\s*$"
)

# Loose bibref-abbreviation tokens in de SV-tekst (binnen kanttekeningen):
# `Matth. 1.18`, `1 Cor. 5:3`, `Ioan. 3.16`. Na bibref-normalisatie zit dit in
# `$Mt. 1:18$` etc., maar de validator extraheert caps op de rauwe tekst en
# zou dan `Matth`/`Cor`/`Ioan` als "ontbrekend" flaggen. Maskeren we de
# abbrev-tokens voordat we caps extraheren.
BIBREF_ABBREV_TOKEN_RE = re.compile(r"\b[A-Z][a-zà-ÿ]{1,9}\.(?=\s*\d)")

# SV-functiewoorden / typografische sentence-starters die SYSTEMATISCH naar
# een lowercase modern equivalent worden vertaald. Cap-check zou anders bij
# elke voorkomen warning genereren ("Ende" → "En" is verwacht; geen signaal).
# Filter case-insensitief in `_capitalized_words`.
CAP_CHECK_STOPLIST = {
    # Sentence-starters / voegwoorden / aanwijzingen (modernisering: lowercase).
    "ende", "doch", "soo", "dese", "desen", "deser", "daer", "daerom",
    "siet", "ofte", "gelijck", "ghy", "gy", "des", "nademael", "aangezien",
    "aengaende", "aengezien", "voortijts", "sulcks", "alsoo", "alsdan",
    "terstondt", "want", "maer", "ook", "overmits", "wijl", "alsoo",
    "doe", "alhoewel", "hoewel", "het",
    # Drop-cap-equivalents: leading-cap variants gevangen door .lower().
    "ende.", "ende,",
}


def _run_participle_checks(text: str, location: str) -> list[str]:
    """Pure checker — scant gegeven tekst op finiete tgw. participia.
    Caller bepaalt of `<…>`-stripping al gebeurd is.
    """
    issues: list[str] = []

    # A) Always-bad -ende participia: altijd flag.
    for m in re.finditer(r"\b(\w+ende)\b", text, flags=re.IGNORECASE):
        word = m.group(1).lower()
        if word in PARTICIPLE_ALWAYS_BAD_ENDE:
            issues.append(
                f"{location}: §2.3-participium '{m.group(1)}' — finiet tgw. participium "
                f"moet ontvouwd naar finiete bijzin (zie MODERNISATIE.md §2.3)"
            )

    # B) Context-dependent -ende participia: flag alleen als adverbial
    #    (gevolgd door interpunctie of een voorzetsel).
    for m in re.finditer(r"\b(\w+ende)\b(\s*[,:;.]|\s+(\w+))?",
                         text, flags=re.IGNORECASE):
        word = m.group(1).lower()
        if word not in PARTICIPLE_CONTEXT_ENDE:
            continue
        trailing = m.group(2) or ""
        next_word = (m.group(3) or "").lower()
        is_adverbial = bool(re.match(r"\s*[,:;.]", trailing)) or \
                       next_word in ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE
        if is_adverbial:
            issues.append(
                f"{location}: §2.3-participium '{m.group(1)}' (adverbial) — "
                f"ontvouw naar finiete bijzin (zie MODERNISATIE.md §2.3)"
            )

    # C) Modern-gespeld -end, adverbial clause-intro voor specifieke stammen.
    for m in re.finditer(r"\b(\w+end)\b\s*,", text, flags=re.IGNORECASE):
        word = m.group(1).lower()
        if any(word == stem + "end" or word.endswith(stem + "end")
               for stem in PARTICIPLE_BAD_END_STEMS):
            issues.append(
                f"{location}: §2.3-participium '{m.group()}' — modern-gespeld "
                f"adverbiaal participium; ontvouw naar 'terwijl X …' of 'en …' "
                f"(zie MODERNISATIE.md §2.3)"
            )

    return issues


def _check_participles(mod_text: str, location: str) -> list[str]:
    """Detecteer finiete tegenwoordige participia in moderne hoofdtekst /
    intro / epilogue / sectie. Zie MODERNISATIE.md §2.3 / §2.3b.

    Twee klassen overtredingen:
      A) `-ende` woorden — SV-spelling van het tegenwoordig participium.
         In modern Nederlands is `-ende` vrijwel altijd attributief
         (`de volgende dag`); adverbiale `-ende[,:;]` of niet-attributieve
         `-ende` is een carry-over uit SV-syntaxis.
      B) `-end,` clause-intros — modern-gespelde adverbiale participia
         (`Dit zeggend, riep hij`). Beperkt tot stammen waarvan de
         participium-clause een §2.3-overtreding is.

    Strippen van `<…>` kanttekeningen vóór de check, zodat citaten/oude
    vormen binnen kanttekeningen niet als overtreding tellen — §2.3
    geldt voor de hoofdtekst. Vierkante haken behouden (inhoud telt mee).

    Returns: lijst hard issues.
    """
    hoofdtekst = re.sub(r"<[^>]+>", " ", mod_text)
    hoofdtekst = re.sub(r"\$[^$]+\$", " ", hoofdtekst)
    hoofdtekst = re.sub(r"\[([^\]]+)\]", r"\1", hoofdtekst)
    return _run_participle_checks(hoofdtekst, location)


def _check_participles_in_kanttekening(
    mod_text: str, location: str
) -> tuple[list[str], list[str]]:
    """Pass over kanttekening-inhoud `<…>` voor §2.3-participia.

    Kanttekeningen zijn uitlegregister, maar Latinate participia
    (`navolgende`, `strekkende`, `ziende gemaakt`) moeten óók daar
    ontvouwd zijn. Splitsing:
      - ALWAYS_BAD hits → hard issue (zelfde register als hoofdtekst)
      - CONTEXT/onbekend hits → soft warning (mogelijk citaat)

    Returns (issues, warnings).
    """
    kanttekening_text = " ".join(_bracket_contents(mod_text, "<", ">"))
    kanttekening_text = re.sub(r"\$[^$]+\$", " ", kanttekening_text)
    raw = _run_participle_checks(kanttekening_text, f"{location} <kant>")
    issues: list[str] = []
    warnings: list[str] = []
    for msg in raw:
        # Onderscheid op woord uit msg: '... §2.3-participium 'XXX' ...'
        m = re.search(r"§2\.3-participium '(\w+)'", msg)
        word = m.group(1).lower() if m else ""
        if word in PARTICIPLE_ALWAYS_BAD_ENDE:
            issues.append(msg)
        else:
            warnings.append(msg + " (soft)")
    return issues, warnings


def _count_blocks(text: str, open_ch: str, close_ch: str) -> int:
    """Tel het aantal `<...>` of `[...]` blokken (niet-genest, simpel)."""
    pattern = re.escape(open_ch) + r"[^" + re.escape(close_ch) + r"]+" + re.escape(close_ch)
    return len(re.findall(pattern, text))


def _bracket_contents(text: str, open_ch: str, close_ch: str) -> list[str]:
    pattern = re.escape(open_ch) + r"([^" + re.escape(close_ch) + r"]+)" + re.escape(close_ch)
    return re.findall(pattern, text)


def _kanttekening_text(text: str) -> str:
    """Concatenateer alle `<…>` kanttekening-inhoud tot één string.

    Gebruikt voor caps-discipline binnen kanttekeningen: we vergelijken de
    set hoofdlettrige woorden in originele kanttekeningen (gestript van
    bibrefs en geneste haken via `_capitalized_words`) tegen de moderne
    kanttekening-inhoud, zodat case-flips als "Leeraers" → "leraars" gevangen
    worden.
    """
    return " ".join(_bracket_contents(text, "<", ">"))


def _capitalized_words(text: str) -> set[str]:
    """Geef alle woorden met hoofdletter (buiten begin van zin) als set."""
    # Strip kanttekeningen en bibrefs eerst — die hebben hun eigen patroon.
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\$[^$]+\$", " ", cleaned)
    cleaned = re.sub(r"\[[^\]]+\]", " ", cleaned)
    # Loose bibref-abbrev tokens (`Matth.`, `Cor.`, `Ioan.` voor cijfers) maskeren —
    # die worden door bibref.py naar `$Mt. ...$` etc. genormaliseerd en zijn dus
    # geen kandidaten voor cap-discipline.
    cleaned = BIBREF_ABBREV_TOKEN_RE.sub(" ", cleaned)
    # Tokenize op witruimte + interpunctie.
    tokens = re.findall(r"[A-ZÀ-Ÿa-zà-ÿ']+", cleaned)
    # Filter SV-functiewoorden die altijd naar lowercase modern transformeren —
    # die genereren anders ~50× per hoofdstuk een warning (`Ende`, `Siet`, `Doch`,
    # ...) die het signaal verdrinken. Stoplist case-insensitief.
    return {
        t for t in tokens
        if t and (t[0].isupper() and not t.isupper() or t.isupper())
        and t.lower() not in CAP_CHECK_STOPLIST
    }


def _is_acceptable_modern_form(orig_word: str, modern_text: str) -> bool:
    """Is de moderne tekst acceptabel als `orig_word` daarin niet letterlijk staat?"""
    if orig_word in modern_text:
        return True
    for variant in SPELLING_EQUIV.get(orig_word, []):
        if variant in modern_text:
            return True
    # Algemene moderne spelling-substituties. Eerst zonder 'y'-conversie,
    # daarna twee varianten: y→ij (voor 'hy' → 'hij') en y→i (voor 'Eynde'
    # → 'Einde'). De SV gebruikt 'y' voor beide moderne klanken.
    # Soft spelling-substituties. Beide hoofdletter- én onderkast-vormen, anders
    # mist een woord met capital leading letter (bv. "Aen") zijn moderne vorm
    # ("Aan") en wordt het later vals als caseflip geflagd.
    base = (
        orig_word.replace("ck", "k")
        .replace("Ae", "Aa")
        .replace("ae", "aa")
        .replace("Ph", "F")
        .replace("ph", "f")
        .replace("Eu", "Ev")  # Euangeli → Evangeli
        .replace("eu", "ev")  # idem onderkast
    )
    # `oo→o` reductie alleen optioneel: SV spelt vaak open lettergrepen met
    # dubbele klinker (Dooper→Doper, Hoogepriester→Hogepriester) terwijl andere
    # woorden hun `oo` houden (boom, groot, dood). We proberen beide vormen,
    # zodat de match-set strikt groter wordt en de validator niet op spelling
    # struikelt — concordantie-validatie blijft de woord-keuze bewaken.
    bases = [base]
    if "oo" in base:
        bases.append(base.replace("oo", "o"))
    for b in bases:
        for soft in (b, b.replace("y", "ij"), b.replace("y", "i")):
            if soft in modern_text:
                return True
    # Laatste poging: prefix-match op de eerste 4 letters na soft-substitutie.
    # Vangt vormvarianten zoals 'Heyligen' (origineel) → 'Heilige' (modern,
    # buigvorm verschilt) of 'Euangeliums' → 'Evangelie' (genitief weg).
    for b in bases:
        for soft in (b, b.replace("y", "ij"), b.replace("y", "i")):
            if len(soft) >= 4 and soft[:4] in modern_text:
                return True
    return False


def _check_cap_form(orig_word: str, modern_text: str) -> str:
    """Drie-staps check voor hoofdletter-discipline.

    Returns:
      'acceptable' — modern bevat herkenbare vorm met juiste case
      'caseflip'   — modern bevat de woordvorm maar met andere case (HARD issue,
                     SV-cap-pattern moet bewaard blijven per AGENTS.md)
      'missing'    — modern bevat de woordvorm helemaal niet (SOFT warning,
                     waarschijnlijk geherformuleerd)
    """
    if _is_acceptable_modern_form(orig_word, modern_text):
        return "acceptable"
    # Case-insensitive whole-word match met soft-substituties. Als het woord wel
    # ergens lowercase voorkomt, is dat een cap-discipline-fout, niet een
    # 'woord ontbreekt'. Whole-word check voorkomt false-positives bij short
    # SV-cap-woorden als 'Ende' die als substring in moderne werkwoorden
    # ('zegende', 'hangende') voorkomen.
    orig_lower = orig_word.lower()
    mod_lower = modern_text.lower()
    if re.search(r"\b" + re.escape(orig_lower) + r"\b", mod_lower):
        return "caseflip"
    base = (
        orig_lower.replace("ck", "k")
        .replace("ae", "aa")
        .replace("ph", "f")
        .replace("eu", "ev")
    )
    for soft in (base, base.replace("y", "ij"), base.replace("y", "i")):
        if re.search(r"\b" + re.escape(soft) + r"\b", mod_lower):
            return "caseflip"
        if len(soft) >= 4 and re.search(r"\b" + re.escape(soft[:4]), mod_lower):
            return "caseflip"
    return "missing"


def _check_caps(orig_text: str, mod_text: str, location: str) -> tuple[list[str], list[str]]:
    """Hoofdletter-discipline check, herbruikbaar voor hoofdtekst, kanttekening
    of meta-secties (intro/epilogue).

    `location` is een label dat in de issue/warning-tekst verschijnt
    (bv. 'hoofdtekst', 'kanttekening', 'introduction', 'epilogue').

    Returns (issues, warnings).
    """
    issues: list[str] = []
    warnings: list[str] = []
    orig_caps = _capitalized_words(orig_text)
    for word in orig_caps:
        if len(word) < 3:
            continue
        status = _check_cap_form(word, mod_text)
        if status == "caseflip":
            issues.append(
                f"hoofdletter-discipline ({location}): '{word}' staat met andere "
                f"case in modernisatie (SV-cap-patroon moet bewaard blijven)"
            )
        elif status == "missing":
            warnings.append(
                f"hoofdletter ({location}): '{word}' uit origineel niet gevonden "
                f"in modernisatie (check spelling-equivalent of bewuste herformulering)"
            )
    return issues, warnings


_NOTES_ALLOWED_TYPES = {"twijfel", "afwijking", "context"}


def _check_notes_shape(notes: object, location: str) -> list[str]:
    """Valideer dat `notes` voldoet aan OUTPUT_SCHEMA.md.

    Per schema: `notes` is optioneel; áls aanwezig is het een lijst van
    objecten met `type` ∈ {twijfel, afwijking, context}. Een losse string,
    `null`-items, of onbekende `type`-waarden zijn HARD issues — ze breken
    de docs-renderer (`notes.map is not a function`) en/of badge-rendering.
    """
    if notes is None:
        return []
    issues: list[str] = []
    if isinstance(notes, str):
        issues.append(
            f"notes ({location}): is een losse string — moet lijst van objecten "
            f"zijn (zie OUTPUT_SCHEMA.md), bv. [{{'type':'afwijking','reason':...}}]"
        )
        return issues
    if not isinstance(notes, list):
        issues.append(
            f"notes ({location}): type {type(notes).__name__} — moet lijst van objecten zijn"
        )
        return issues
    for i, item in enumerate(notes):
        if not isinstance(item, dict):
            issues.append(
                f"notes[{i}] ({location}): type {type(item).__name__} — elk item moet object zijn"
            )
            continue
        t = item.get("type")
        if t is None:
            issues.append(f"notes[{i}] ({location}): 'type' ontbreekt")
        elif t not in _NOTES_ALLOWED_TYPES:
            issues.append(
                f"notes[{i}] ({location}): type={t!r} — toegestaan: "
                f"{sorted(_NOTES_ALLOWED_TYPES)}"
            )
    return issues


def _validate_verse(orig: dict, mod: dict) -> dict:
    """Valideer één vers. Retourneert dict met issues en warnings."""
    issues: list[str] = []
    warnings: list[str] = []

    orig_text = orig.get("text", "")
    mod_text = mod.get("modernized", "")
    orig_source = orig.get("source_text", "")
    mod_source = mod.get("source_text", "")

    # 0. notes-shape — per OUTPUT_SCHEMA.md is `notes` optioneel maar áls
    # aanwezig: lijst-van-objecten met type ∈ {twijfel, afwijking, context}.
    # Een losse string of array-van-strings breekt de docs-renderer
    # (`notes.map is not a function`); dat is een HARD issue.
    issues.extend(_check_notes_shape(mod.get("notes"), "verse"))

    # 1. Kanttekening-aantal
    n_orig_kant = _count_blocks(orig_text, "<", ">")
    n_mod_kant = _count_blocks(mod_text, "<", ">")
    if n_mod_kant < n_orig_kant:
        issues.append(
            f"kanttekeningen: origineel heeft {n_orig_kant}, modern heeft {n_mod_kant} "
            f"(moet >= origineel)"
        )

    # 2. Vierkante haken
    n_orig_haken = _count_blocks(orig_text, "[", "]")
    n_mod_haken = _count_blocks(mod_text, "[", "]")
    if n_orig_haken != n_mod_haken:
        issues.append(
            f"vierkante haken: origineel heeft {n_orig_haken}, modern heeft "
            f"{n_mod_haken} (moet identiek; markeert SV-toevoegingen)"
        )

    # 3a. Hoofdletter-discipline hoofdtekst. AGENTS.md: "Patroon van het origineel
    # volgen". Caseflip = HARD issue; missing = SOFT warning. SV-typografische
    # drop-caps aan vers- of zinsbegin (bv. 'NAdemael' / 'IN') tellen niet als
    # SV-caps — die volgen sentence-case in modern, en `_capitalized_words` filtert
    # ze impliciet via de `len(word) < 3`-grens en de y→ij/i soft-substituties.
    caps_i, caps_w = _check_caps(orig_text, mod_text, "hoofdtekst")
    issues.extend(caps_i)
    warnings.extend(caps_w)

    # 3b. Hoofdletter-discipline binnen kanttekeningen. `_capitalized_words` strijkt
    # `<...>` weg, dus voor deze check vergelijken we de geconcateneerde
    # kanttekening-inhoud van origineel en modern. Vangt o.a. "Leeraers" → "leraars".
    orig_kant = _kanttekening_text(orig_text)
    mod_kant = _kanttekening_text(mod_text)
    if orig_kant.strip():
        kc_i, kc_w = _check_caps(orig_kant, mod_kant, "kanttekening")
        issues.extend(kc_i)
        warnings.extend(kc_w)

    # 4. Bijbelref-formaat
    for ref in REF_RE.findall(mod_text):
        # Splitsen op `;` en elk deel moet matchen.
        parts = [p.strip() for p in ref.split(";") if p.strip()]
        for i, part in enumerate(parts):
            # Eerste deel moet boeknaam bevatten; vervolgdelen mogen alleen H:V.
            if i == 0:
                if not MODERN_REF_PART.match(part):
                    issues.append(f"bijbelref: '${ref}$' onderdeel '{part}' niet in modern formaat")
            else:
                if not (MODERN_REF_PART.match(part) or re.match(r"^\s*\d+:\d+(?:,\d+)*(?:-\d+)?\s*$", part)):
                    issues.append(f"bijbelref: '${ref}$' onderdeel '{part}' niet in modern formaat")

    # 4b. Loose bibrefs binnen kanttekeningen — moeten in $...$ staan zodat
    # regex-consumers ze kunnen onderscheiden. bibref.py --include-kanttekeningen
    # doet dit automatisch; deze check vangt regressies.
    for kant_inner in _bracket_contents(mod_text, "<", ">"):
        for snippet in find_loose_refs(kant_inner):
            issues.append(
                f"loose bibref in kanttekening: '{snippet}' — wrap in $...$ "
                f"via bibref.py --include-kanttekeningen"
            )

    # 5. Archaïsme-blacklist
    for pattern in ARCHAISM_BLACKLIST:
        # Alleen in de hoofdtekst (buiten kanttekeningen) checken — kanttekeningen
        # mogen citaten/oude vormen bevatten.
        hoofdtekst = re.sub(r"<[^>]+>", "", mod_text)
        m = re.search(pattern, hoofdtekst, flags=re.IGNORECASE)
        if m:
            issues.append(f"archaïsme: '{m.group(0)}' (regex={pattern}) in moderne hoofdtekst")

    # 5b. §2.3 participium-check — finiete tgw. participia moeten ontvouwd zijn.
    issues.extend(_check_participles(mod_text, "hoofdtekst"))
    # 5c. Kanttekening-pass: ALWAYS_BAD = hard, anders soft.
    kant_issues, kant_warnings = _check_participles_in_kanttekening(mod_text, "hoofdtekst")
    issues.extend(kant_issues)
    warnings.extend(kant_warnings)

    # 6. Brontekst ongewijzigd. NFC-normaliseren vóór vergelijking — bytewise
    # gelijk is ideaal, maar Greek-polytonic vs -monotonic codepoints (U+1F75
    # vs U+03AE) leveren NFC-equivalente strings op die we niet als wijziging
    # mogen rapporteren. Bytewise-anders maar NFC-equivalent → soft warning
    # (impliceert: input rechtstreeks kopiëren ipv hertypen).
    if orig_source and mod_source:
        a = orig_source.strip()
        b = mod_source.strip()
        if a != b:
            if unicodedata.normalize("NFC", a) != unicodedata.normalize("NFC", b):
                issues.append(
                    "source_text gewijzigd t.o.v. origineel (moet ongewijzigd blijven)"
                )
            else:
                warnings.append(
                    "source_text byte-anders maar NFC-equivalent — kopieer rechtstreeks "
                    "uit input ipv. hertypen"
                )

    return {
        "verse": orig.get("verse_number"),
        "passes": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


def _validate_section(name: str, orig_text: str, mod_text: str) -> dict:
    """Valideer een meta-sectie (introduction/epilogue).

    Beperkte checks: vierkante haken, archaisme-blacklist, hoofdletter
    warnings. Geen kanttekeningen-check (intro/epilogue bevatten ze niet),
    geen bijbelref-check (idem), geen source_text-check.
    """
    issues: list[str] = []
    warnings: list[str] = []

    # Vierkante haken — aantal moet identiek zijn (bv. "[de beschrijvinge]"
    # in LUK 24 epiloog moet "[de beschrijving]" worden — haken bewaard).
    n_orig_haken = _count_blocks(orig_text, "[", "]")
    n_mod_haken = _count_blocks(mod_text, "[", "]")
    if n_orig_haken != n_mod_haken:
        issues.append(
            f"vierkante haken: origineel heeft {n_orig_haken}, modern heeft "
            f"{n_mod_haken} (moet identiek)"
        )

    # Archaïsme-blacklist op de hele moderne tekst (geen kanttekeningen om
    # eruit te strippen — die bestaan niet in intro/epilogue).
    for pattern in ARCHAISM_BLACKLIST:
        m = re.search(pattern, mod_text, flags=re.IGNORECASE)
        if m:
            issues.append(f"archaïsme: '{m.group(0)}' (regex={pattern}) in moderne {name}")

    # §2.3 participium-check
    issues.extend(_check_participles(mod_text, name))

    # Hoofdletter-discipline (zoals bij verzen): caseflip = hard, missing = soft.
    # Intro en epilogue bevatten geen kanttekeningen, dus één call volstaat.
    caps_i, caps_w = _check_caps(orig_text, mod_text, name)
    issues.extend(caps_i)
    warnings.extend(caps_w)

    return {
        "section": name,
        "passes": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


def _validate_chapter(modernized: dict) -> dict:
    """Cross-vers consistentie binnen één hoofdstuk-bestand.

    Per-vers loop: SKILL.md eist één-vers-per-cyclus zodat vers N+1 vers N
    als few-shot uit memory kan ophalen (concordantie). Twee verzen die
    exact dezelfde `generated_at`-timestamp delen verraden dat de
    modernisatie als batch is uitgevoerd — memory-query tussen verzen is
    dan overgeslagen. Hard issue.
    """
    issues: list[str] = []
    warnings: list[str] = []

    timestamps: dict[str, list[int]] = {}
    for v in modernized.get("verses", []):
        ts = v.get("generated_at")
        vn = v.get("verse_number")
        if ts and vn is not None:
            timestamps.setdefault(ts, []).append(vn)

    for ts, vns in sorted(timestamps.items()):
        if len(vns) > 1:
            issues.append(
                f"per-vers loop: verzen {sorted(vns)} delen generated_at='{ts}' "
                f"— modernisatie was waarschijnlijk een batch ipv. één-vers-per-"
                f"cyclus (SKILL.md). Memory-query tussen verzen is gemist; "
                f"concordantie kan eronder lijden."
            )

    return {
        "check": "per-vers loop",
        "passes": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


def cmd_check(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(json.dumps({"error": f"input niet gevonden: {input_path}"}))
        return 2
    if not output_path.exists():
        print(json.dumps({"error": f"output niet gevonden: {output_path}"}))
        return 2

    with input_path.open(encoding="utf-8") as f:
        original = json.load(f)
    with output_path.open(encoding="utf-8") as f:
        modernized = json.load(f)

    orig_by_num = {v["verse_number"]: v for v in original.get("verses", [])}
    mod_by_num = {v["verse_number"]: v for v in modernized.get("verses", [])}

    if args.verses:
        target = [int(x) for x in args.verses.split(",")]
    else:
        target = sorted(mod_by_num.keys())

    per_verse: list[dict] = []
    any_fail = False
    for vn in target:
        if vn not in orig_by_num:
            per_verse.append(
                {"verse": vn, "passes": False, "issues": [f"vers {vn} niet in input"], "warnings": []}
            )
            any_fail = True
            continue
        if vn not in mod_by_num:
            per_verse.append(
                {"verse": vn, "passes": False, "issues": [f"vers {vn} niet in output"], "warnings": []}
            )
            any_fail = True
            continue
        result = _validate_verse(orig_by_num[vn], mod_by_num[vn])
        per_verse.append(result)
        if not result["passes"]:
            any_fail = True

    sections_checked: list[dict] = []
    requested_sections = (
        [s.strip() for s in args.sections.split(",") if s.strip()]
        if args.sections
        else []
    )
    section_keys = {"intro": "introduction", "introduction": "introduction",
                    "epilogue": "epilogue", "epiloog": "epilogue"}
    for raw in requested_sections:
        key = section_keys.get(raw.lower())
        if key is None:
            sections_checked.append(
                {"section": raw, "passes": False,
                 "issues": [f"onbekende sectie: {raw!r} (gebruik intro of epilogue)"],
                 "warnings": []}
            )
            any_fail = True
            continue
        orig_section = original.get(key)
        mod_section = modernized.get(key)
        if orig_section is None:
            sections_checked.append(
                {"section": key, "passes": False,
                 "issues": [f"{key} niet aanwezig in input"], "warnings": []}
            )
            any_fail = True
            continue
        if not isinstance(mod_section, dict) or "modernized" not in mod_section:
            sections_checked.append(
                {"section": key, "passes": False,
                 "issues": [f"{key} niet (correct) gemoderniseerd in output"],
                 "warnings": []}
            )
            any_fail = True
            continue
        result = _validate_section(key, orig_section, mod_section["modernized"])
        sections_checked.append(result)
        if not result["passes"]:
            any_fail = True

    # Cross-vers (per hoofdstuk): timestamp-uniciteit. Loopt altijd, ongeacht
    # welke verzen geselecteerd zijn — batch-fouten elders in het bestand horen
    # gerapporteerd te worden zodra je het bestand sowieso opent.
    chapter_checks = [_validate_chapter(modernized)]
    if any(not r["passes"] for r in chapter_checks):
        any_fail = True

    checked = len(per_verse) + len(sections_checked) + len(chapter_checks)
    passed = (
        sum(1 for r in per_verse if r["passes"])
        + sum(1 for r in sections_checked if r["passes"])
        + sum(1 for r in chapter_checks if r["passes"])
    )
    failed = checked - passed
    warnings_total = (
        sum(len(r["warnings"]) for r in per_verse)
        + sum(len(r["warnings"]) for r in sections_checked)
        + sum(len(r["warnings"]) for r in chapter_checks)
    )

    if args.terse:
        status = "PASS" if not any_fail else "FAIL"
        lines = [f"{status} {passed}/{checked} {failed}F {warnings_total}W"]
        for r in per_verse:
            if not r["passes"]:
                for iss in r["issues"]:
                    lines.append(f"v{r['verse']}: {iss}")
        for r in sections_checked:
            if not r["passes"]:
                for iss in r["issues"]:
                    lines.append(f"{r['section']}: {iss}")
        for r in chapter_checks:
            if not r["passes"]:
                for iss in r["issues"]:
                    lines.append(f"chapter: {iss}")
        print("\n".join(lines))
        return 1 if any_fail else 0

    summary = {
        "checked": checked,
        "passed": passed,
        "failed": failed,
        "warnings_total": warnings_total,
        "verses": per_verse,
        "sections": sections_checked,
        "chapter_checks": chapter_checks,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if any_fail else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("check", help="Valideer modernisatie tegen origineel.")
    sp.add_argument("--input", required=True, help="Pad naar input.sv/<BOEK>/<BOEK>.<H>.json")
    sp.add_argument("--output", required=True, help="Pad naar output/<BOEK>/<BOEK>.<H>.json")
    sp.add_argument("--verses", default=None, help="Komma-gescheiden vers-nummers (default: alle)")
    sp.add_argument(
        "--sections",
        default=None,
        help="Komma-gescheiden sectie-namen om te valideren: intro, epilogue (default: geen).",
    )
    sp.add_argument(
        "--terse",
        action="store_true",
        help="Compacte tekstuele output ipv. JSON: 1 statusregel + 1 regel per fail.",
    )
    sp.set_defaults(func=cmd_check)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
