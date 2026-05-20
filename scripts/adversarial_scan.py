"""Adversarial chapter scan — vind §2.3 / §2.3b / §2.7 / kanttekening-
luiheid op hoofdstuk-niveau. Schrijft een issue-tracker waarop de
orchestrator MOET reageren (fixen of inhoudelijk weerleggen).

Anders dan `validate.py` (per vers, smalle whitelist) werkt deze scan
**adversarial**: default-stand is overtreding. Een participium-
kandidaat staat als issue tenzij we expliciet bewijs hebben dat het
acceptabel is (attributief gevolgd door zelfst.nw. dat niet op de
adverbial-trigger-lijst staat). False positives zijn welkom — de
in-context skill of orchestrator filtert ze.

Categorieën:
  A) §2.3 finiet participium (`\\w+ende\\b`, `\\w+end[,:;]`) — ruimer
     dan validate.py: alle `-ende`-vormen die niet attributief zijn,
     niet op WHITELIST staan, en niet evident-modern (ordinal,
     past-tense-met-d, etc.).
  B) §2.3b Latinaat-syntax: passief van zien, vocatief-u, bijwoord-
     coda, infinitief met nageschoven object.
  C) §2.7 drempel-archaïsmen: woorden die niet op de validator-blacklist
     staan maar de productiviteits/verwarringtest zakken.
  D) Concordantie-drift binnen het hoofdstuk: zelfde origineel-woord
     ≥2× → flag als modernized verschillende rendering geeft.
  E) Kanttekening-luiheid: -ende binnen <…>, of redundantie tussen
     kanttekening en hoofdtekst.

Output: `output/<BOEK>/review.<H>.json` met issue-list. Statussen:
`open`, `fixed`, `rebutted`, `verified`, `reopened`.

CLI:
    python scripts/adversarial_scan.py scan --book LUK --chapter 8
    python scripts/adversarial_scan.py verify --book LUK --chapter 8
"""

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Hergebruik bestaande lijsten uit de centrale rules_data module.
from rules_data import (  # noqa: E402
    PARTICIPLE_ALWAYS_BAD_ENDE,
    PARTICIPLE_CONTEXT_ENDE,
    ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE,
    PARTICIPLE_BAD_END_STEMS,
    ARCHAISM_BLACKLIST,
    ENDE_WHITELIST,
    DREMPEL_ARCHAISMEN,
    DREMPEL_FOSSIELEN,
    KANTTEKENING_ARCHAISMEN,
)

PARTICIPLE_RE = re.compile(r"\b(\w+ende)\b", re.IGNORECASE)
# -end clause-final: interpunctie OF adverbial-trigger-woord. PHM 1:4 gap —
# 'denkend in mijn gebeden' werd gemist toen alleen `[,:;]` werd gematcht.
END_CLAUSE_RE = re.compile(
    r"\b(\w+end)\b(\s*[,:;.]|\s+(\w+))?",
    re.IGNORECASE,
)
KANTT_RE = re.compile(r"<([^>]+)>")
SQB_RE = re.compile(r"\[([^\]]+)\]")
BIBREF_RE = re.compile(r"\$[^$]+\$")


def strip_markup_keep_text(text: str) -> tuple[str, str]:
    """Splits in (hoofdtekst zonder markup, kanttekening-tekst zonder
    omhulsel). Vierkante haken: inhoud blijft als hoofdtekst staan."""
    kanttekeningen = " ".join(KANTT_RE.findall(text))
    main = KANTT_RE.sub(" ", text)
    main = BIBREF_RE.sub(" ", main)
    main = SQB_RE.sub(r"\1", main)
    return main, kanttekeningen


def context_around(text: str, idx: int, span: int = 40) -> str:
    start = max(0, idx - span)
    end = min(len(text), idx + span)
    snippet = text[start:end].replace("\n", " ")
    return ("…" if start > 0 else "") + snippet + ("…" if end < len(text) else "")


def scan_participles_main(verse_num: int, mod_text: str) -> list[dict]:
    """A) §2.3 finiet participium in hoofdtekst (incl. vierkante-haken-
    inhoud). Default = overtreding voor elk -ende-woord dat niet op
    WHITELIST staat én niet attributief gevolgd wordt door een zelfst.
    naamwoord."""
    issues: list[dict] = []
    main, _ = strip_markup_keep_text(mod_text)

    seen_spans: set[tuple[int, int]] = set()

    for m in PARTICIPLE_RE.finditer(main):
        span = m.span()
        if span in seen_spans:
            continue
        seen_spans.add(span)
        word = m.group(1).lower()
        if word in ENDE_WHITELIST:
            continue

        rest = main[m.end():]
        trailing = rest[:30]
        is_adverbial_punct = bool(re.match(r"\s*[,:;.]", trailing))
        next_word_match = re.match(r"\s+(\w+)", trailing)
        next_word = next_word_match.group(1).lower() if next_word_match else ""
        is_adverbial_prep = next_word in ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE
        is_attributive_likely = (
            not is_adverbial_punct
            and not is_adverbial_prep
            and bool(next_word_match)
        )

        # Adversarial criterium: flag tenzij echt attributief én niet
        # in always-bad-list.
        if word in PARTICIPLE_ALWAYS_BAD_ENDE:
            severity = "hard"
            reason = "always-adverbial -ende uit SV-syntaxis"
        elif word in PARTICIPLE_CONTEXT_ENDE and (is_adverbial_punct or is_adverbial_prep):
            severity = "hard"
            reason = "context-participium in adverbial positie"
        elif is_attributive_likely:
            # Niet-blacklist, attributief gevolgd door woord — meestal OK
            # (bv. 'volgende dag', 'komende eeuw'). Skip.
            continue
        else:
            # Onbekende stam in adverbial / clause-final positie:
            # opzettelijk flaggen. Default = overtreding.
            severity = "soft"
            reason = "verdacht -ende-woord in adverbial / clause-final positie"

        issues.append({
            "category": "§2.3 finiet participium",
            "verse": verse_num,
            "severity": severity,
            "quote_modernized": context_around(main, m.start()),
            "rule_reference": "MODERNISATIE.md §2.3",
            "explanation": (
                f"'{m.group(1)}' — {reason}. Ontvouw naar finiete bijzin "
                f"('en X', 'terwijl X', 'toen X')."
            ),
            "proposed_fix": None,
            "location": "hoofdtekst",
        })

    for m in END_CLAUSE_RE.finditer(main):
        word = m.group(1).lower()
        # Alleen flaggen als de stam matcht een SV-participium-stam:
        # voorkomt false positives op gewone -end-vormen ('eind',
        # 'vriend', 'bekend' — die hebben geen \b...\b match op stem).
        if not any(word == stem + "end" or word.endswith(stem + "end")
                   for stem in PARTICIPLE_BAD_END_STEMS):
            continue
        trailing = m.group(2) or ""
        next_word = (m.group(3) or "").lower()
        is_adverbial = bool(re.match(r"\s*[,:;.]", trailing)) or \
                       next_word in ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE
        if not is_adverbial:
            continue
        issues.append({
            "category": "§2.3 finiet participium (-end clause)",
            "verse": verse_num,
            "severity": "hard",
            "quote_modernized": context_around(main, m.start()),
            "rule_reference": "MODERNISATIE.md §2.3",
            "explanation": (
                f"'{m.group(1)}' — modern-gespeld adverbiaal "
                f"participium; ontvouw naar 'terwijl X …' of 'en …'."
            ),
            "proposed_fix": None,
            "location": "hoofdtekst",
        })

    return issues


PASSIVE_GEZIEN_RE = re.compile(
    r"\b(werd|wordt|is|zijn|werden)\s+\w*gezien\b", re.IGNORECASE
)
VOCATIVE_U_RE = re.compile(
    r'(?:^|[„"\'(\s,;:!?])\s*u\s+(\w+(?:de|te|gde))\b', re.IGNORECASE
)
ADVERB_CODA_RE = re.compile(
    r"\b(\w{4,}lijk)\s*[.,;:!?]", re.IGNORECASE
)
INFINITIVE_OBJECT_RE = re.compile(
    r"\bom\b\s+([^.,;:!?]{0,40}?)\bte\s+(\w+)\b\s+(\w+(?:\s+\w+){0,3})",
    re.IGNORECASE,
)


def scan_latinaat(verse_num: int, mod_text: str) -> list[dict]:
    """B) §2.3b Latinaat-syntax: passief 'gezien werd', vocatief-u,
    bijwoord-coda achteraf, infinitief met nageschoven object."""
    issues: list[dict] = []
    main, _ = strip_markup_keep_text(mod_text)

    for m in PASSIVE_GEZIEN_RE.finditer(main):
        issues.append({
            "category": "§2.3b passief van zien",
            "verse": verse_num,
            "severity": "hard",
            "quote_modernized": context_around(main, m.start()),
            "rule_reference": "MODERNISATIE.md §2.3b",
            "explanation": (
                f"'{m.group(0)}' — passief van *zien* is een Latinaat-"
                f"constructie; gebruik 'verscheen aan …'."
            ),
            "proposed_fix": None,
            "location": "hoofdtekst",
        })

    for m in VOCATIVE_U_RE.finditer(main):
        following = m.group(1).lower()
        # Heuristiek: 'u zult', 'u hebt', 'u kunt' zijn modern correct.
        if following in {"zult", "zoudt", "hebt", "kunt", "wilt", "moet",
                         "bent", "doet", "weet"}:
            continue
        issues.append({
            "category": "§2.3b vocatief-u",
            "verse": verse_num,
            "severity": "soft",
            "quote_modernized": context_around(main, m.start()),
            "rule_reference": "MODERNISATIE.md §2.3b",
            "explanation": (
                f"'u {m.group(1)}' aan zin-/clause-begin — mogelijke "
                f"vocatief-u-Latinaatconstructie. Verifieer of 'u' "
                f"hier object van aanspreking is en weghaalbaar is."
            ),
            "proposed_fix": None,
            "location": "hoofdtekst",
        })

    for m in ADVERB_CODA_RE.finditer(main):
        # Heuristiek: bijwoord-coda voelt dan Latinaat als de zinsdeel
        # vóór het bijwoord een lange bepaling bevat. We flaggen alle
        # '-lijk[.,;:]' aan zinseind als adversarial kandidaat.
        word = m.group(1).lower()
        if word in {"mogelijk", "waarschijnlijk", "uiteindelijk",
                    "tenslotte", "dagelijks", "wekelijks"}:
            continue
        issues.append({
            "category": "§2.3b bijwoord-coda",
            "verse": verse_num,
            "severity": "soft",
            "quote_modernized": context_around(main, m.start()),
            "rule_reference": "MODERNISATIE.md §2.3b",
            "explanation": (
                f"'{m.group(0)}' aan zinseind — verifieer of dit "
                f"bijwoord niet als coda achteraf is blijven hangen "
                f"('wandelende … onberispelick' → 'wandelden onberispelijk in …')."
            ),
            "proposed_fix": None,
            "location": "hoofdtekst",
        })

    # Interrogatieve / subordinator-bijzinnen achter infinitief blijven in
    # modern Nederlands gewoon na de infinitief staan (`om te zien wat
    # gebeurd was`, `om te weten of …`). §2.3b geldt voor nominaal object,
    # niet voor wat-/dat-/of-/wie-/hoe-/waar-bijzinnen.
    INTERROG_SUB_HEADS = {"wat", "dat", "of", "wie", "hoe", "waar", "waarom",
                          "wanneer", "welke", "hoeveel"}

    for m in INFINITIVE_OBJECT_RE.finditer(main):
        between, verb, after = m.group(1), m.group(2), m.group(3)
        if not after.strip():
            continue
        # Object langer dan 2 woorden achter de infinitief = verdacht.
        words_after = after.split()
        first_after = words_after[0].lower() if words_after else ""
        if first_after in INTERROG_SUB_HEADS:
            continue
        if len(words_after) >= 3 and len(between.split()) <= 2:
            issues.append({
                "category": "§2.3b infinitief met nageschoven object",
                "verse": verse_num,
                "severity": "soft",
                "quote_modernized": context_around(main, m.start()),
                "rule_reference": "MODERNISATIE.md §2.3b",
                "explanation": (
                    f"'om … te {verb} {after.strip()}' — Latinaat-"
                    f"woordvolgorde; in modern NL gaat het object "
                    f"vóór de infinitief: 'om <object> te {verb}'."
                ),
                "proposed_fix": None,
                "location": "hoofdtekst",
            })

    return issues


def scan_drempel(verse_num: int, mod_text: str) -> list[dict]:
    """C) §2.7 drempel-archaïsmen die niet op blacklist staan."""
    issues: list[dict] = []
    main, _ = strip_markup_keep_text(mod_text)
    main_lower = main.lower()

    for word in DREMPEL_ARCHAISMEN:
        for m in re.finditer(rf"\b{re.escape(word)}\b", main_lower):
            issues.append({
                "category": "§2.7 drempel-archaïsme",
                "verse": verse_num,
                "severity": "soft",
                "quote_modernized": context_around(main, m.start()),
                "rule_reference": "MODERNISATIE.md §2.7",
                "explanation": (
                    f"'{word}' faalt productiviteits- of verwarrings-"
                    f"test. Overweeg modern equivalent (bv. 'omdat' / "
                    f"'hoewel' / 'echter' afhankelijk van context)."
                ),
                "proposed_fix": None,
                "location": "hoofdtekst",
            })

    for pattern in DREMPEL_FOSSIELEN:
        for m in re.finditer(pattern, main_lower):
            issues.append({
                "category": "§2.7 drempel-fossiel",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(main, m.start()),
                "rule_reference": "MODERNISATIE.md §2.7",
                "explanation": (
                    f"Idiomatisch fossiel '{m.group(0)}' — oude "
                    f"dativus/genitief. Modern: 'op de N-de dag' / "
                    f"'op het uur / tegen het uur'."
                ),
                "proposed_fix": None,
                "location": "hoofdtekst",
            })

    return issues


# SV-genitief / dativus-lidwoorden die in modern Nederlands vrijwel
# altijd `van de` / `van het` worden. ARCHAISMEN.md geeft het patroon
# in het LUK 1:6-voorbeeld weg: `des Heeren` → `van de Heere`. De
# scanner flagt elke `der|des|den + woord`-combinatie als kandidaat,
# minus de exclusies hieronder.
INFLECTED_ARTICLE_RE = re.compile(
    r"\b(der|des|den)\s+(\w+)",
    re.IGNORECASE,
)

# `des te` is een gradatie-bijwoord ("des te meer / beter / sneller"),
# géén SV-genitief — uitsluiten.
INFLECTED_ARTICLE_DES_TE_RE = re.compile(r"\bdes\s+te\b", re.IGNORECASE)

# Toponiemen die met `Den` beginnen en gewoon modern Nederlands zijn.
INFLECTED_ARTICLE_DEN_PLACENAMES: frozenset[str] = frozenset({
    "haag", "bosch", "helder", "briel", "hoorn", "burg", "ham",
    "dolder",
})


def scan_inflected_articles(verse_num: int, mod_text: str) -> list[dict]:
    """F) SV-genitief/dativus-lidwoorden `der`, `des`, `den` in moderne
    tekst. ARCHAISMEN.md (LUK 1:6) verlangt `der/des Boek` → `van de(t)
    Boek`. Default = overtreding. Excludeert `des te`-gradatieve
    bijwoorden en `Den X`-toponiemen.

    Hits in zowel hoofdtekst als binnen kanttekeningen — twee location-
    waardes. Fossiele bijbel-frasen (`Zoon des mensen`, `Koninkrijk der
    hemelen`) worden NIET hard-coded gewhitelist; orchestrator kan ze
    per geval rebutten met §2.7-achtig argument (vaste term in modern
    bijbels register).
    """
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        # Maskeer 'des te' zodat de algemene regex die hits niet pakt.
        masked = INFLECTED_ARTICLE_DES_TE_RE.sub(
            lambda m: " " * len(m.group(0)), text,
        )
        for m in INFLECTED_ARTICLE_RE.finditer(masked):
            article = m.group(1)
            following = m.group(2)
            # Toponiem-uitzondering: `Den Haag`, `Den Bosch`, etc.
            if article.lower() == "den" and following.lower() in \
                    INFLECTED_ARTICLE_DEN_PLACENAMES:
                continue
            issues.append({
                "category": "verbogen lidwoord (der/des/den)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (LUK 1:6 'des Heeren' → 'van de Heere')",
                "explanation": (
                    f"'{article} {following}' — SV-verbogen lidwoord. "
                    f"Modern Nederlands gebruikt 'van de' / 'van het' "
                    f"i.p.v. genitiefconstructies. Vervang door 'van de "
                    f"{following}' of 'van het {following}', tenzij dit "
                    f"een gefossiliseerde bijbel-uitdrukking is (bv. "
                    f"'Koninkrijk der hemelen', 'Zoon des mensen') — dan "
                    f"rebutten met fossiel-argument + regel-referentie."
                ),
                "proposed_fix": f"van de {following}",
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# === Verdere SV-verbuigings- en archaïsme-scanners ===
#
# Onderstaande scanners volgen het patroon van scan_inflected_articles:
# regex → exclusies/whitelist → issue dict per hit, in zowel hoofdtekst
# als kanttekening. Ze worden opgeroepen vanuit cmd_scan en gedispatcht
# door cmd_verify via SCANNER_REGISTRY (zie onderaan dit bestand).


# B. Verbogen onbep. lidwoord 'eenen', 'eener', 'eenes' (SV
# accusatief/genitief) → modern 'een'.
INDEFINITE_ARTICLE_RE = re.compile(
    r"\b(eenen|eener|eenes)\s+(\w+)", re.IGNORECASE,
)


def scan_inflected_indefinite(verse_num: int, mod_text: str) -> list[dict]:
    """B) Verbogen onbep. lidwoord 'eenen/eener/eenes' → 'een'.
    SV-accusatief/genitief op het onbepaald lidwoord, in modern
    Nederlands volledig dood. Default = overtreding."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in INDEFINITE_ARTICLE_RE.finditer(text):
            article, following = m.group(1), m.group(2)
            issues.append({
                "category": "SV-verbuiging (eenen/eener)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-verbuigingen)",
                "explanation": (
                    f"'{article} {following}' — verbogen onbep. lidwoord "
                    f"(SV-accusatief/genitief). Modern Nederlands "
                    f"verbuigt 'een' niet; vervang door 'een {following}'."
                ),
                "proposed_fix": f"een {following}",
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# C. Verbogen demonstratief 'dezer/dezes/dezen/dien/dier/gener/genen'.
# Matcht zowel 'dezen man' als 'dezen, die...' (anaforisch met
# interpunctie). Volgwoord optioneel zodat ook standalone gebruik wordt
# gevangen ('zijn dezen.').
INFLECTED_DEMONSTRATIVE_RE = re.compile(
    r"\b(dezer|dezes|dezen|dien|dier|gener|genen)\b"
    r"(?:[\s,;:]+(\w+))?",
    re.IGNORECASE,
)

# Gefossiliseerde modern-formele combinaties die GEEN SV-overtreding zijn:
# 'dezer dagen' = "in deze dagen" (formeel maar productief), 'te dien einde',
# 'op dien grondslag' (juridisch). Whitelist-tuples (article, noun).
DEMONSTRATIVE_FOSSIL_PAIRS: frozenset[tuple[str, str]] = frozenset({
    ("dezer", "dagen"),
    ("dien", "einde"),
    ("dien", "verstande"),
    ("dier", "voege"),
})


def scan_inflected_demonstrative(verse_num: int, mod_text: str) -> list[dict]:
    """C) SV-verbogen demonstratief 'dezer/dien/dier/gener'. Whitelist
    voor enkele moderne juridisch-formele fossielen ('dezer dagen',
    'te dien einde'). Skip homonymen die andere woordsoort zijn:
    'dien' = 1sg pres. van 'dienen', 'dier' = zelfst. nw. (animal)."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    # Pre-context-patronen die een homoniem-interpretatie aanduiden:
    # subject-pronomen voor `dien` → werkwoord, niet demonstratief.
    # Lidwoord/demonstratief voor `dier` → zelfst. nw., niet demonstratief.
    SUBJECT_PRON_BEFORE_RE = re.compile(
        r"\b(ik|jij|je|hij|zij|wij|gij|u|jullie|men|niemand|iemand|"
        r"iedereen)\s+$",
        re.IGNORECASE,
    )
    NOUN_DET_BEFORE_DIER_RE = re.compile(
        r"\b(de|het|dat|dit|een|eens|elk|ieder|geen|wild|tam|groot|klein)\s+$",
        re.IGNORECASE,
    )

    def _scan(text: str, location: str) -> None:
        for m in INFLECTED_DEMONSTRATIVE_RE.finditer(text):
            article = m.group(1).lower()
            following = (m.group(2) or "").lower()
            if following and (article, following) in DEMONSTRATIVE_FOSSIL_PAIRS:
                continue
            # Pre-context-check voor homonymie.
            pre = text[:m.start()]
            if article == "dien" and SUBJECT_PRON_BEFORE_RE.search(pre):
                continue
            if article == "dier" and NOUN_DET_BEFORE_DIER_RE.search(pre):
                continue
            issues.append({
                "category": "SV-verbuiging (demonstratief dezer/dien/...)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-verbuigingen)",
                "explanation": (
                    f"'{m.group(1)} {m.group(2)}' — verbogen demonstratief "
                    f"(SV-genitief/datief). Modern Nederlands: 'deze' / "
                    f"'die' / 'in deze ...' / 'op die ...'. "
                    f"Gefossiliseerde uitdrukkingen ('dezer dagen', 'te "
                    f"dien einde') zijn whitelist; rebut zo nodig met "
                    f"register-argument."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# D. Archaïsch anaforisch pronomen 'dezelve/dezelven/denzelven'.
# LET OP: 'dezelfde' (modern OK in vergelijking) heeft 'd' i.p.v. 'v'
# en valt buiten deze regex.
DEZELVE_RE = re.compile(r"\bden?zelve[nrs]?\b", re.IGNORECASE)


def scan_archaic_pronoun_dezelve(verse_num: int, mod_text: str) -> list[dict]:
    """D) 'dezelve/denzelven' anaforisch — modern: ze/die/het/hem.
    Niet te verwarren met 'dezelfde' (modern OK in vergelijkende rol;
    andere regex-tak)."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in DEZELVE_RE.finditer(text):
            issues.append({
                "category": "archaïsch pronomen (dezelve/denzelven)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-pronomina)",
                "explanation": (
                    f"'{m.group(0)}' — archaïsch anaforisch pronomen "
                    f"(SV-vorm voor 'dezelve(n)' = 'die/het/ze'). Modern "
                    f"Nederlands gebruikt 'die', 'ze', 'het', 'hem' "
                    f"afhankelijk van geslacht/getal/casus. Niet te "
                    f"verwarren met 'dezelfde' (modern OK in vergelijking)."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# A. Reflexief 'hem/haar' bij reflexief werkwoord — modern 'zich'.
# We gebruiken een whitelist van werkwoordsvormen die in modern
# Nederlands ALTIJD reflexief zijn (`zich bekeren`, niet `*hem bekeren`).
# Met deze beperking blijven we weg van false positives bij ditransitief
# gebruik ('zij gaf hem het boek').
REFLEXIVE_VERB_FORMS: frozenset[str] = frozenset({
    # bekeren
    "bekeer", "bekeert", "bekeerde", "bekeerden", "bekeerd",
    # verheugen
    "verheug", "verheugt", "verheugde", "verheugden", "verheugd",
    # voorzien (van X)
    "voorzie", "voorziet", "voorzag", "voorzagen", "voorzien",
    # schamen
    "schaam", "schaamt", "schaamde", "schaamden", "geschaamd",
    # beraden
    "beraad", "beraadt", "beraadde", "beraadden", "beraden",
    # haasten
    "haast", "haastte", "haastten", "gehaast",
    # verwonderen
    "verwonder", "verwondert", "verwonderde", "verwonderden",
    # buigen (refl.)
    "buig", "buigt", "boog", "bogen", "gebogen",
    # voornemen — alleen flaggen als 'voor' particle in context. De
    # generieke vormen (neemt/nam/namen/genomen) staan niet op deze
    # lijst want ze leveren te veel false positives op (van hem genomen,
    # tot zich nemen, etc.).
    # vermaken
    "vermaak", "vermaakt", "vermaakte", "vermaakten",
    # wenden
    "wend", "wendt", "wendde", "wendden", "gewend",
    # wenden / keren / scharen
    "scharen", "schaart", "schaarde",
    # zetten (refl. = neerzetten/installeren)
    # 'zich zetten' is archaïsch; modern 'gaan zitten'. Skip.
})


def scan_reflexive_hem_haar(verse_num: int, mod_text: str) -> list[dict]:
    """A) 'hem/haar' bij reflexief werkwoord (SV) → modern 'zich'.
    Whitelist van werkwoordsvormen die in modern NL altijd reflexief
    zijn — beperkt scope om ditransitieve constructies niet te flaggen."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)
    pat = re.compile(r"\b(hem|haar)\s+(\w+)", re.IGNORECASE)

    def _scan(text: str, location: str) -> None:
        for m in pat.finditer(text):
            pron = m.group(1).lower()
            verb = m.group(2).lower()
            if verb not in REFLEXIVE_VERB_FORMS:
                continue
            issues.append({
                "category": "reflexief hem/haar (→ zich)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-pronomina)",
                "explanation": (
                    f"'{pron} {verb}' — SV-reflexief met 'hem/haar' bij "
                    f"een werkwoord dat in modern Nederlands met 'zich' "
                    f"gaat. Vervang door 'zich {verb}'."
                ),
                "proposed_fix": f"zich {verb}",
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# E. Aanvoegende wijs als gebod: 'die neme', 'die verkope'.
# Subjunctief op -e na voornaamwoord/relativum. Severity: soft (false-
# positive-risico bij past simple op -e van zwakke stammen, hoewel die
# meestal in -de eindigen).
SUBJUNCTIVE_VERB_FORMS: frozenset[str] = frozenset({
    "neme", "geve", "kome", "zegene", "hebbe", "leve", "werde",
    "verkope", "kope", "behoeve", "ontvange", "doe", "zoeke",
    "scheide", "kere", "wijke", "zwijge", "spreke", "denke",
    "blijve", "drinke", "ete", "ga", "sla", "vinde", "wete",
    "houde", "drage", "geloove", "geloove",
})

SUBJUNCTIVE_TRIGGER_RE = re.compile(
    r"\b(die|wie|hij|zij|men|niemand)\s+(\w+e)\b", re.IGNORECASE,
)


def scan_subjunctive_imperative(verse_num: int, mod_text: str) -> list[dict]:
    """E) SV-aanvoegende wijs als gebod ('die neme', 'die verkope').
    Soft severity vanwege false-positive-risico (past simple op -e bij
    sommige zwakke stammen). Whitelist-vormen alleen."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in SUBJUNCTIVE_TRIGGER_RE.finditer(text):
            verb = m.group(2).lower()
            if verb not in SUBJUNCTIVE_VERB_FORMS:
                continue
            issues.append({
                "category": "aanvoegende wijs (gebod)",
                "verse": verse_num,
                "severity": "soft",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-werkwoordsvormen)",
                "explanation": (
                    f"'{m.group(0)}' — SV-aanvoegende wijs als gebod/wens. "
                    f"Modern Nederlands: 'laat {m.group(1)} {verb}n' of "
                    f"'{m.group(1)} moet ...'. Soft: subjunctief in "
                    f"plechtig modern register komt nog voor."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# F. Dubbele negatie met clitisch 'en' — SV-syntax 'niet en hebben',
# 'geen ... en heeft'. Modern Nederlands gebruikt enkele negatie.
# We zoeken negatie + (korte gap) + 'en' + finiet werkwoord. Het 'en' is
# clitisch (vlak vóór finiet werkwoord, geen subject ertussen).
DOUBLE_NEG_RE = re.compile(
    r"\b(niet|geen|nooit|nimmer|niemand|niets|nergens)\b"
    r"(?:\s+\w+){0,5}"
    r"\s+en\s+"
    r"(\w+(?:t|de|den|en|st|ft|n))\b",
    re.IGNORECASE,
)

# Werkwoordsvormen die voor 'en + V' in clitisch SV-patroon typisch zijn.
# Daadwerkelijk modern conjunctief 'en' tussen objecten ("appels en peren")
# komt nooit direct vóór een finiet werkwoord; we accepteren elke `\w+`
# eindigend op een werkwoorduitgang.
SV_CLITIC_VERB_HINTS: frozenset[str] = frozenset({
    "hebben", "heeft", "had", "hadden",
    "is", "zijn", "was", "waren",
    "kan", "kunt", "kunnen", "kon", "konden",
    "wil", "wilt", "willen", "wou", "wilden",
    "moet", "moeten", "moest", "moesten",
    "weet", "weten", "wist", "wisten",
    "verstaan", "verstaat", "verstond", "verstonden",
    "behoef", "behoeft", "behoeven", "behoefde", "behoefden",
    "doe", "doet", "doen", "deed", "deden",
    "ga", "gaat", "gaan", "ging", "gingen",
})


def scan_double_negation_en(verse_num: int, mod_text: str) -> list[dict]:
    """F) SV-dubbele negatie met clitisch 'en': 'niet en hebben',
    'geen ... en heeft'. Modern Nederlands kent dit niet meer; ouder
    modernisator-werk kan het laten staan."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in DOUBLE_NEG_RE.finditer(text):
            negation = m.group(1).lower()
            verb = m.group(2).lower()
            # Strengere check: alleen als verb in SV_CLITIC_VERB_HINTS staat,
            # of als 'niet en' / 'geen ... en' direct opeen volgen (meest
            # diagnostisch voor SV-clitisch en).
            window = m.group(0).lower()
            direct_clitic = bool(re.search(rf"\b{negation}\s+en\s+", window))
            if not (direct_clitic or verb in SV_CLITIC_VERB_HINTS):
                continue
            issues.append({
                "category": "dubbele negatie met clitisch en",
                "verse": verse_num,
                "severity": "hard" if direct_clitic else "soft",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-syntax)",
                "explanation": (
                    f"'{m.group(0)}' — SV-clitisch 'en' tussen negatie en "
                    f"finiet werkwoord. Modern Nederlands gebruikt enkele "
                    f"negatie; verwijder het 'en'."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# G. Voornaamwoordelijk bijwoord gesplitst: 'daar in', 'waar mede',
# 'hier op', 'er aan'. Modern: samengevoegd ('daarin', 'waarmee').
# We flaggen alleen als het tweede element een echt SV-bijwoord-deel is
# (mede/nevens/toe/etc.) en niet gevolgd door een NP (dan zou het een
# losse plaatsbepaling kunnen zijn).
SPLIT_PRONADV_PARTICLES: frozenset[str] = frozenset({
    "mede", "nevens", "toe", "van", "af", "aan", "in", "op", "over",
    "onder", "door", "tegen", "bij", "uit", "boven", "achter", "voor",
})

SPLIT_PRONADV_RE = re.compile(
    r"\b(daar|waar|hier|er)\s+(\w+)\b", re.IGNORECASE,
)


def scan_split_pronominal_adverb(verse_num: int, mod_text: str) -> list[dict]:
    """G) SV-syntax: 'daar in', 'waar mede', 'hier op' als gesplitst
    voornaamwoordelijk bijwoord. Modern: samengevoegd. False-positive-
    risico bij plaatsbepalingen ('daar in dat huis') — daarom flaggen we
    alleen als het tweede deel direct gevolgd wordt door interpunctie of
    een werkwoord, niet door een NP."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in SPLIT_PRONADV_RE.finditer(text):
            base = m.group(1).lower()
            particle = m.group(2).lower()
            if particle not in SPLIT_PRONADV_PARTICLES:
                continue
            # Check what follows: punctuation or finite-verb-form = SV-stranding;
            # NP (article + noun) = plaatsbepaling, skip.
            rest = text[m.end():]
            trailing = rest[:30]
            # Skip als direct na particle een lidwoord, demonstratief,
            # bezittelijk voornaamwoord of persoonlijk voornaamwoord komt
            # (= losse PP, geen stranded voornaamwoordelijk bijwoord).
            if re.match(
                r"\s+("
                r"de|het|een|der|des|den|deze|die|dit|dat|"
                r"ditzelfde|datzelfde|dezelfde|dezelfd|"
                r"mijn|jouw|uw|zijn|haar|onze|hun|"
                r"hen|hem|haar|u|mij|me|jou|je|ons|ze|hij|zij|"
                r"\d+"  # numeriek (bv. 'in 1657')
                r")\b",
                trailing, re.IGNORECASE,
            ):
                continue
            issues.append({
                "category": "voornaamwoordelijk bijwoord gesplitst",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-syntax)",
                "explanation": (
                    f"'{base} {particle}' — SV-gesplitst voornaamwoordelijk "
                    f"bijwoord. Modern Nederlands voegt samen: "
                    f"'{base}{particle}' (bv. daarin, waarmee, hierop)."
                ),
                "proposed_fix": f"{base}{particle}",
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# H. SV-spelling-residu: zelfst. nw. eindigend op '-inge', '-isse',
# '-erye'. Modern: '-ing', '-is', '-erij'. Geen modern Nederlands woord
# eindigt zo, dus trefzeker.
SV_SPELLING_RE = re.compile(
    r"\b\w+(?:inge|isse|erye)\b", re.IGNORECASE,
)

SV_SPELLING_WHITELIST: frozenset[str] = frozenset({
    # Modern Nederlands met -inge als adjectief-flexie (gering+e):
    "geringe", "enige", "eenige", "dwingende",  # 'eenige' wordt elders gevangen
    # 'dwingende' is participium-attributief, modern OK (al door
    # ENDE_WHITELIST/PARTICIPLE-scan gedekt).
})


def scan_sv_spelling_residu(verse_num: int, mod_text: str) -> list[dict]:
    """H) SV-spelling-residu '-inge/-isse/-erye'. Lui modernisator
    vergeet finale -e. Trefzeker patroon, default = overtreding."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in SV_SPELLING_RE.finditer(text):
            word = m.group(0).lower()
            if word in SV_SPELLING_WHITELIST:
                continue
            issues.append({
                "category": "SV-spelling-residu (-inge/-isse/-erye)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (spelling)",
                "explanation": (
                    f"'{m.group(0)}' — SV-spelling met finale -e. "
                    f"Modern: -ing / -is / -erij (bekeering→bekering, "
                    f"getuigenisse→getuigenis, slaverye→slavernij)."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# I. Archaïsch demonstratief 'de gene' / 'dengenen'. Modern: 'degene'
# (één woord, formeel) of liever 'wie/zij die'.
DEGENE_RE = re.compile(
    r"\b(de\s+gene[nr]?|den\s*genen|dengenen?|de\s+gene)\b",
    re.IGNORECASE,
)


def scan_archaic_degene(verse_num: int, mod_text: str) -> list[dict]:
    """I) 'de gene' / 'dengenen' archaïsch demonstratief. Modern:
    'degene', 'wie', 'zij die'. Soft severity — modern 'degene' bestaat
    in formeel register."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in DEGENE_RE.finditer(text):
            issues.append({
                "category": "archaïsch demonstratief (de gene)",
                "verse": verse_num,
                "severity": "soft",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-pronomina)",
                "explanation": (
                    f"'{m.group(0)}' — archaïsche schrijfwijze. Modern: "
                    f"'degene' (één woord, formeel), of leesbaarder "
                    f"'wie ...' / 'zij die ...'."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# J. Diminutieven op '-ken / -kens' (SV-zuidelijk, dood in modern
# Nederlands). Modern: '-tje / -tjes'. Een regex op `\w+kens?` matcht
# massaal werkwoorden (spreken, drinken) en bnw-mv (goddelijke,
# koninklijke); we werken daarom met een literal-match-lijst van échte
# SV-diminutieven die we als carry-over willen vangen. In LUK-input
# komen voor: kindeken, kinderkens, tafelken(s), schrijftafelken,
# mannekens, vrouwken, engelken e.a. Lijst groeit in PR's.
SV_DIMINUTIVES: frozenset[str] = frozenset({
    "kindeken", "kinderken", "kinderkens", "kindekens",
    "tafelken", "tafelkens", "schrijftafelken",
    "manneken", "mannekens",
    "vrouwken", "vrouwkens", "vrouken", "vroukens",
    "engelken", "engelkens",
    "vogelken", "vogelkens",
    "voetken", "voetkens",
    "doosken", "dooskens",
    "boomken", "boomkens",
    "broederken", "broederkens",
    "vingerkens", "vingerken",
})


def scan_diminutive_kens(verse_num: int, mod_text: str) -> list[dict]:
    """J) SV-diminutief-suffix '-ken/-kens' als literal carry-over in de
    moderne tekst. We gebruiken geen breed regex-patroon (massieve
    false positives op werkwoorden en bnw-mv) maar een gericht lemma-
    lijst SV_DIMINUTIVES."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for word in SV_DIMINUTIVES:
            for m in re.finditer(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
                issues.append({
                    "category": "diminutief op -ken/-kens",
                    "verse": verse_num,
                    "severity": "hard",
                    "quote_modernized": context_around(text, m.start()),
                    "rule_reference": "ARCHAISMEN.md (SV-morfologie)",
                    "explanation": (
                        f"'{m.group(0)}' — SV-diminutief op -ken/-kens "
                        f"(zuidelijk) als carry-over in moderne tekst. "
                        f"Modern Nederlands: -tje/-tjes ('kindertjes' "
                        f"i.p.v. 'kinderkens')."
                    ),
                    "proposed_fix": None,
                    "location": location,
                })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# K. 'welke / welken / hetwelk' als relatief pronomen (SV-formeel) →
# modern 'die/dat'. Context-gevoelig: in vraagzinnen ('welke man?') is
# 'welke' modern OK. Heuristiek: 'welke' direct na komma of voorzetsel
# is meestal SV-relatief.
WELKE_RELATIVE_RE = re.compile(
    r"(?:[,;]\s+|\b(?:met|in|op|aan|tot|van|over|door|onder|naar|bij|voor)\s+)"
    r"(welke[nr]?|hetwelke?|hetwelk)\b",
    re.IGNORECASE,
)


def scan_relative_welke(verse_num: int, mod_text: str) -> list[dict]:
    """K) 'welke/welken/hetwelk' als relatief pronomen (SV-formeel) →
    modern 'die/dat'. We flaggen alleen na komma of voorzetsel
    (relatieve context); niet in vraagzinnen ('welke man?')."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in WELKE_RELATIVE_RE.finditer(text):
            word = m.group(1)
            issues.append({
                "category": "relativum welke/welken/hetwelk",
                "verse": verse_num,
                "severity": "soft",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-syntax)",
                "explanation": (
                    f"'{word}' als relatief pronomen — SV-formeel, in "
                    f"modern Nederlands vrijwel altijd 'die' (de-woord) of "
                    f"'dat' (het-woord). 'welke' modern alleen in "
                    f"vraagzinnen of zeer formeel-juridisch."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


# L. Genitief-pronomen 'wiens / wier' — modern formeel-archaïsch.
# Modern Nederlands neigt naar 'van wie' of de zinsherbouw met
# bezittelijk voornaamwoord. NBV21 vermijdt 'wiens' grotendeels.
WIENS_RE = re.compile(r"\b(wiens|wier)\s+(\w+)", re.IGNORECASE)

# 'wier' kan ook zelfstandig naamwoord zijn (zeewier). Whitelist op
# context: alleen als gevolgd door (lid)woord-achtig vervolg dat
# beslag gemaakt zou kunnen worden door een bezitsrelatie.
WIER_NOUN_CONTEXT_RE = re.compile(
    r"\b(zee|stuk|bos|drijf|water)wier\b", re.IGNORECASE,
)


def scan_wiens_wier(verse_num: int, mod_text: str) -> list[dict]:
    """L) Genitief-pronomen 'wiens/wier' (SV-formeel) → modern 'van wie'
    of zinsherbouw met bezittelijk voornaamwoord. 'wier' als zelfst.
    nw. (zeewier) wordt gewhitelist op compositum-context."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)

    def _scan(text: str, location: str) -> None:
        for m in WIENS_RE.finditer(text):
            pron = m.group(1).lower()
            following = m.group(2)
            # 'wier' als compositum-deel ('zeewier') uitsluiten via context.
            if pron == "wier":
                start = max(0, m.start() - 10)
                pre = text[start:m.start() + len("wier")]
                if WIER_NOUN_CONTEXT_RE.search(pre):
                    continue
            issues.append({
                "category": "genitief pronomen wiens/wier",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(text, m.start()),
                "rule_reference": "ARCHAISMEN.md (SV-pronomina)",
                "explanation": (
                    f"'{pron} {following}' — formeel-archaïsch genitief-"
                    f"pronomen. Modern Nederlands: 'van wie {following}' "
                    f"of zinsherbouw met bezittelijk voornaamwoord ('die "
                    f"zijn {following}', 'die haar {following}'). NBV21 "
                    f"vermijdt 'wiens' grotendeels."
                ),
                "proposed_fix": None,
                "location": location,
            })

    _scan(main, "hoofdtekst")
    if kantt:
        _scan(kantt, "kanttekening")
    return issues


def scan_kanttekening_luiheid(verse_num: int, mod_text: str) -> list[dict]:
    """E) -ende binnen kanttekeningen + SV-caps niet gemoderniseerd +
    redundantie kanttekening↔hoofdtekst (woordelijke herhaling)."""
    issues: list[dict] = []
    main, kantt = strip_markup_keep_text(mod_text)
    if not kantt:
        return issues

    # E1: -ende binnen kanttekening — adversarial default-stand. Mirror
    # `scan_participles_main`: élk -ende-woord dat niet op ENDE_WHITELIST
    # staat én niet attributief gevolgd wordt door een woord telt als
    # issue. Voorheen sloegen we onbekende stammen over (bv.
    # `gebruikende` in LUK 7:33 glipte zo door); §2.3 geldt ook in <…>.
    seen_kantt_spans: set[tuple[int, int]] = set()
    for m in PARTICIPLE_RE.finditer(kantt):
        span = m.span()
        if span in seen_kantt_spans:
            continue
        seen_kantt_spans.add(span)
        word = m.group(1).lower()
        if word in ENDE_WHITELIST:
            continue

        rest = kantt[m.end():]
        trailing = rest[:30]
        is_adverbial_punct = bool(re.match(r"\s*[,:;.]", trailing))
        next_word_match = re.match(r"\s+(\w+)", trailing)
        next_word = next_word_match.group(1).lower() if next_word_match else ""
        is_adverbial_prep = next_word in ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE
        is_attributive_likely = (
            not is_adverbial_punct
            and not is_adverbial_prep
            and bool(next_word_match)
        )

        if word in PARTICIPLE_ALWAYS_BAD_ENDE:
            severity = "hard"
            reason = "always-adverbial -ende uit SV-syntaxis"
        elif word in PARTICIPLE_CONTEXT_ENDE and (is_adverbial_punct or is_adverbial_prep):
            severity = "hard"
            reason = "context-participium in adverbial positie"
        elif is_attributive_likely:
            # Attributief gevolgd door zelfstandig woord — meestal OK.
            continue
        else:
            # Onbekende stam in adverbial / clause-final positie binnen
            # kanttekening: opzettelijk flaggen. Default = overtreding.
            severity = "hard"
            reason = "verdacht -ende-woord in adverbial / clause-final positie"

        issues.append({
            "category": "kanttekening-luiheid (§2.3 in <…>)",
            "verse": verse_num,
            "severity": severity,
            "quote_modernized": context_around(kantt, m.start()),
            "rule_reference": "KANTTEKENINGEN.md + §2.3",
            "explanation": (
                f"'{m.group(1)}' binnen kanttekening — {reason}. §2.3 geldt "
                f"ook in <…>; ontvouw naar finiete bijzin."
            ),
            "proposed_fix": None,
            "location": "kanttekening",
        })

    # E2: SV-caps in kanttekening
    for pattern in KANTTEKENING_ARCHAISMEN:
        for m in re.finditer(pattern, kantt):
            issues.append({
                "category": "kanttekening-luiheid (SV-archaisme in <…>)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": context_around(kantt, m.start()),
                "rule_reference": "KANTTEKENINGEN.md",
                "explanation": (
                    f"'{m.group(0)}' in kanttekening — SV-vorm niet "
                    f"gemoderniseerd. Pas zelfde modernisatie toe als "
                    f"in hoofdtekst (caps en spelling)."
                ),
                "proposed_fix": None,
                "location": "kanttekening",
            })

    # E3: redundantie hoofdtekst ↔ kanttekening — de kanttekening
    # herhaalt een fragment van de hoofdtekst woordelijk (>=4 tokens).
    main_tokens = re.findall(r"\w+", main.lower())
    kantt_tokens = re.findall(r"\w+", kantt.lower())
    if len(main_tokens) >= 4 and len(kantt_tokens) >= 4:
        # Schuif een venster van 4 tokens over de kanttekening en kijk of
        # die 4 tokens ergens als sub-list in de hoofdtekst staan.
        joined_main = " " + " ".join(main_tokens) + " "
        for i in range(len(kantt_tokens) - 3):
            window = " ".join(kantt_tokens[i:i + 4])
            if f" {window} " in joined_main:
                issues.append({
                    "category": "kanttekening-redundantie",
                    "verse": verse_num,
                    "severity": "soft",
                    "quote_modernized": window,
                    "rule_reference": "KANTTEKENINGEN.md (redundantie-regel)",
                    "explanation": (
                        f"Kanttekening herhaalt '{window}' woordelijk "
                        f"uit de hoofdtekst — schendt redundantie-regel."
                    ),
                    "proposed_fix": None,
                    "location": "kanttekening",
                })
                break  # één hit per vers volstaat

    return issues


def scan_concordantie(verses: list[dict]) -> list[dict]:
    """D) Concordantie-drift binnen het hoofdstuk: voor elk inhoudswoord
    dat in ≥3 verzen voorkomt, kijk of *geen enkel* moderne-token de
    eerste 3 letters van het origineel-stam deelt. Geen lemmatisering;
    we werken met prefix-overlap als zwakke proxy.

    Beperkingen: false positives bij synoniem-verschuiving binnen één
    woordfamilie (geschied → gebeurde). Daarom: severity = soft, en de
    drempels zijn streng (min 3 verzen + min 7 chars). Voor strakke
    concordantie-detectie hoort de in-context skill `sv-memory`-query
    te draaien per kandidaat."""
    issues: list[dict] = []

    def long_stem(w: str) -> str:
        return w.lower()[:7]

    def short_prefix(w: str) -> str:
        return w.lower()[:3]

    def content_words(text: str, min_len: int = 7) -> list[str]:
        text, _ = strip_markup_keep_text(text)
        return [w for w in re.findall(r"[A-Za-zëéüïöäÀ-ÿ']{%d,}" % min_len, text)]

    orig_stem_to_verses: dict[str, list[int]] = defaultdict(list)
    verse_mod_prefixes: dict[int, set[str]] = {}

    for v in verses:
        vn = v["verse_number"]
        ows = content_words(v.get("original", ""), min_len=7)
        mws = content_words(v.get("modernized", ""), min_len=4)
        verse_mod_prefixes[vn] = {short_prefix(w) for w in mws}
        for w in set(ows):
            orig_stem_to_verses[long_stem(w)].append(vn)

    for ostem, vlist in orig_stem_to_verses.items():
        unique_verses = sorted(set(vlist))
        if len(unique_verses) < 3:
            continue
        ostem_prefix = ostem[:3]
        # Voor elk vers: heeft de moderne tekst een token met dezelfde
        # 3-letter prefix? Zo niet, vers draagt bij aan drift-evidence.
        verses_without_match = [
            vn for vn in unique_verses
            if ostem_prefix not in verse_mod_prefixes[vn]
        ]
        # Drift = sommige verzen matchen wél, andere niet (split).
        # Of: geen enkel vers matcht (alle verzen renderen anders).
        if not verses_without_match:
            continue
        if len(verses_without_match) == len(unique_verses):
            note = "geen enkel vers heeft een moderne rendering met dezelfde prefix"
        else:
            note = (
                f"verzen {verses_without_match} renderen het stam anders "
                f"dan {sorted(set(unique_verses) - set(verses_without_match))}"
            )
        issues.append({
            "category": "concordantie-drift",
            "verse": unique_verses[0],
            "severity": "soft",
            "quote_modernized": (
                f"origineel-stam '{ostem}' in {len(unique_verses)} verzen — {note}"
            ),
            "rule_reference": "AGENTS.md vertaalprincipes (concordantie)",
            "explanation": (
                f"Origineel-stam komt in {len(unique_verses)} verzen voor; "
                f"moderne rendering is inconsistent. Verifieer met sv-memory "
                f"of dit bewust is (false-friend-correctie / contextverschil); "
                f"zo niet, harmoniseer naar één keuze."
            ),
            "proposed_fix": None,
            "location": "cross-vers",
            "verses_involved": unique_verses,
        })
    return issues


def already_blacklisted_warning(verse_num: int, mod_text: str) -> list[dict]:
    """Sanity-check: als de validator-blacklist nog matcht in moderne
    tekst, is dat een validator-bug, geen adversarial issue. Markeer
    het apart zodat orchestrator weet dat hier eerst de validator
    moet draaien."""
    main, _ = strip_markup_keep_text(mod_text)
    issues: list[dict] = []
    for pat in ARCHAISM_BLACKLIST:
        if re.search(pat, main):
            issues.append({
                "category": "validator-leak (blacklist match)",
                "verse": verse_num,
                "severity": "hard",
                "quote_modernized": pat,
                "rule_reference": "scripts/validate.py ARCHAISM_BLACKLIST",
                "explanation": (
                    f"Validator-blacklist '{pat}' matcht moderne "
                    f"hoofdtekst — los eerst via sv-validate op."
                ),
                "proposed_fix": None,
                "location": "hoofdtekst",
            })
    return issues


# Registry voor cmd_verify dispatch. Key = category-prefix; value =
# scan-functie met dezelfde signature (verse_num, mod_text) → list[dict].
# Verifier matcht via startswith(prefix); langere prefixes komen eerst om
# overlap te voorkomen ('SV-verbuiging (eenen' vóór 'SV-verbuiging').
# `scan_concordantie` werkt op hoofdstuk-niveau en zit niet in registry.
SCANNER_REGISTRY: tuple[tuple[str, callable], ...] = (
    ("§2.3 finiet participium", scan_participles_main),
    ("§2.3b", scan_latinaat),
    ("§2.7", scan_drempel),
    ("verbogen lidwoord", scan_inflected_articles),
    ("SV-verbuiging (eenen", scan_inflected_indefinite),
    ("SV-verbuiging (demonstratief", scan_inflected_demonstrative),
    ("archaïsch pronomen", scan_archaic_pronoun_dezelve),
    ("archaïsch demonstratief", scan_archaic_degene),
    ("reflexief hem/haar", scan_reflexive_hem_haar),
    ("aanvoegende wijs", scan_subjunctive_imperative),
    ("dubbele negatie", scan_double_negation_en),
    ("voornaamwoordelijk bijwoord", scan_split_pronominal_adverb),
    ("SV-spelling-residu", scan_sv_spelling_residu),
    ("diminutief op -ken", scan_diminutive_kens),
    ("relativum welke", scan_relative_welke),
    ("genitief pronomen", scan_wiens_wier),
    ("kanttekening", scan_kanttekening_luiheid),
    ("validator-leak", already_blacklisted_warning),
)


def _clean_quote(quote: str) -> str:
    return quote.strip("…").strip().lower()


def _extract_match_phrase(issue: dict) -> str:
    explanation = issue.get("explanation", "")
    m = re.match(r"^'([^']+)'", explanation)
    if m:
        return m.group(1).lower().strip()
    return _clean_quote(issue.get("quote_modernized", ""))


def _load_historical_rebuttals() -> dict[tuple[str, str], str]:
    """Walkt door de output/ map om alle review.*.json bestanden te vinden en
    laadt geverifieerde/weerlegde issues, waarbij we (category, cleaned_phrase) -> rebuttal mapping maken.
    """
    rebuttals = {}
    output_dir = PROJECT_ROOT / "output"
    if not output_dir.exists():
        return rebuttals
    
    # Sorteer om determinisme te garanderen
    for review_path in sorted(output_dir.glob("**/review.*.json")):
        try:
            with review_path.open(encoding="utf-8") as f:
                data = json.load(f)
            for issue in data.get("issues", []):
                status = issue.get("status")
                rebuttal_text = issue.get("rebuttal", "").strip()
                if status in ("rebutted", "verified") and rebuttal_text:
                    cat = issue.get("category")
                    if cat:
                        phrase = _extract_match_phrase(issue)
                        
                        # Heuristiek: voorkom dat een rebuttal voor een andere term per ongeluk matcht.
                        # Als de phrase kort is (meestal een specifiek woord/frase), moet tenminste één
                        # van de betekenisvolle woorden (>=3 tekens) in de rebuttal-tekst voorkomen.
                        if len(phrase) < 30:
                            words = [w for w in re.findall(r"[a-zëéüïöäÀ-ÿ']{3,}", phrase)]
                            if words and not any(w in rebuttal_text.lower() for w in words):
                                continue
                                
                        rebuttals[(cat, phrase)] = rebuttal_text
        except Exception:
            continue
    return rebuttals


def assign_ids(book: str, chapter: int, issues: list[dict]) -> None:
    counters: Counter = Counter()
    for issue in issues:
        verse = issue["verse"]
        counters[verse] += 1
        issue["id"] = f"{book}-{chapter}-{verse}-{counters[verse]:03d}"
        issue.setdefault("status", "open")


def cmd_scan(args: argparse.Namespace) -> int:
    book = args.book.upper()
    chapter = int(args.chapter)
    output_path = PROJECT_ROOT / "output" / book / f"{book}.{chapter}.json"
    review_path = PROJECT_ROOT / "output" / book / f"review.{chapter}.json"

    if not output_path.exists():
        print(json.dumps({
            "error": f"output JSON niet gevonden: {output_path.relative_to(PROJECT_ROOT)}",
        }))
        return 2

    with output_path.open(encoding="utf-8") as f:
        data = json.load(f)

    verses = data.get("verses", [])
    all_issues: list[dict] = []

    for v in verses:
        vn = v["verse_number"]
        mod = v.get("modernized", "")
        all_issues.extend(already_blacklisted_warning(vn, mod))
        all_issues.extend(scan_participles_main(vn, mod))
        all_issues.extend(scan_latinaat(vn, mod))
        all_issues.extend(scan_drempel(vn, mod))
        all_issues.extend(scan_inflected_articles(vn, mod))
        all_issues.extend(scan_inflected_indefinite(vn, mod))
        all_issues.extend(scan_inflected_demonstrative(vn, mod))
        all_issues.extend(scan_archaic_pronoun_dezelve(vn, mod))
        all_issues.extend(scan_archaic_degene(vn, mod))
        all_issues.extend(scan_reflexive_hem_haar(vn, mod))
        all_issues.extend(scan_subjunctive_imperative(vn, mod))
        all_issues.extend(scan_double_negation_en(vn, mod))
        all_issues.extend(scan_split_pronominal_adverb(vn, mod))
        all_issues.extend(scan_sv_spelling_residu(vn, mod))
        all_issues.extend(scan_diminutive_kens(vn, mod))
        all_issues.extend(scan_relative_welke(vn, mod))
        all_issues.extend(scan_wiens_wier(vn, mod))
        all_issues.extend(scan_kanttekening_luiheid(vn, mod))

    all_issues.extend(scan_concordantie(verses))

    assign_ids(book, chapter, all_issues)

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    # Merge met bestaande review-tracker als die bestaat: behoud
    # `status`/`fix_commit`/`rebuttal` van issues die nog actueel zijn
    # (matchen op category+verse+quote).
    existing: dict = {}
    if review_path.exists() and not args.fresh:
        with review_path.open(encoding="utf-8") as f:
            existing = json.load(f)
    existing_by_key: dict[tuple, dict] = {}
    for issue in existing.get("issues", []):
        key = (issue.get("category"), issue.get("verse"),
               issue.get("quote_modernized"))
        existing_by_key[key] = issue

    historical_rebuttals = _load_historical_rebuttals()

    merged: list[dict] = []
    for issue in all_issues:
        key = (issue["category"], issue["verse"], issue["quote_modernized"])
        prior = existing_by_key.get(key)
        if prior:
            for keep in ("status", "fix_commit", "rebuttal", "verified_at"):
                if keep in prior:
                    issue[keep] = prior[keep]
        else:
            # Check of we een historische verified/rebutted issue hebben met dezelfde categorie en phrase
            phrase = _extract_match_phrase(issue)
            hist_rebuttal = historical_rebuttals.get((issue["category"], phrase))
            if hist_rebuttal:
                issue["status"] = "rebutted"
                issue["rebuttal"] = f"[Automated Propagation] {hist_rebuttal}"
        merged.append(issue)

    passes = list(existing.get("passes", []))
    pass_num = (passes[-1]["pass"] + 1) if passes else 1
    passes.append({
        "pass": pass_num,
        "ran_at": now,
        "mode": "scan",
        "issues_total": len(merged),
    })

    result = {
        "book": book,
        "chapter": chapter,
        "reviewed_at": now,
        "passes": passes,
        "issues": merged,
    }
    review_path.parent.mkdir(parents=True, exist_ok=True)
    with review_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")

    by_sev = dict(Counter(i["severity"] for i in merged))
    by_cat = dict(Counter(i["category"] for i in merged))
    open_n = sum(1 for i in merged if i.get("status") == "open")

    if args.terse:
        sev_str = " ".join(f"{k}:{v}" for k, v in sorted(by_sev.items()))
        print(
            f"scan {book} {chapter}: {len(merged)} issues ({open_n} open) "
            f"sev=[{sev_str}] -> {review_path.relative_to(PROJECT_ROOT)}"
        )
        return 0 if not merged else 1

    summary = {
        "book": book,
        "chapter": chapter,
        "review_path": str(review_path.relative_to(PROJECT_ROOT)),
        "issues_total": len(merged),
        "by_severity": by_sev,
        "by_category": by_cat,
        "open": open_n,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not merged else 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Pass 2: lees review.<H>.json + output JSON; controleer dat
    `fixed`-issues niet meer matchen, en dat `rebutted`-issues een
    substantief argument bevatten."""
    book = args.book.upper()
    chapter = int(args.chapter)
    output_path = PROJECT_ROOT / "output" / book / f"{book}.{chapter}.json"
    review_path = PROJECT_ROOT / "output" / book / f"review.{chapter}.json"

    if not review_path.exists():
        print(json.dumps({"error": f"review tracker niet gevonden: {review_path}"}))
        return 2
    if not output_path.exists():
        print(json.dumps({"error": f"output JSON niet gevonden: {output_path}"}))
        return 2

    with review_path.open(encoding="utf-8") as f:
        review = json.load(f)
    with output_path.open(encoding="utf-8") as f:
        data = json.load(f)

    verses_by_num = {v["verse_number"]: v for v in data.get("verses", [])}
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    rebuttal_lazy_phrases = (
        "formele equivalentie",
        "behoud van sv-stijl",
        "behoud van de sv",
        "sv-eigenheid",
        "sv stijl",
        "geen actie",
        "ok",
        "niet nodig",
        "klopt",
        "akkoord",
    )

    actions: list[str] = []
    for issue in review.get("issues", []):
        status = issue.get("status", "open")

        if status == "fixed":
            verse = verses_by_num.get(issue["verse"])
            if not verse:
                issue["status"] = "reopened"
                issue["verify_note"] = "vers niet meer aanwezig in output"
                actions.append(f"{issue['id']}: reopened (vers verdwenen)")
                continue
            mod = verse.get("modernized", "")
            # Re-scan dit vers op categorie van issue: matcht het patroon nog?
            still_bad = False
            cat = issue["category"]
            verse_issues: list[dict] = []
            for prefix, scan_fn in SCANNER_REGISTRY:
                if cat.startswith(prefix):
                    verse_issues = scan_fn(issue["verse"], mod)
                    break

            for vi in verse_issues:
                if vi["category"] == cat:
                    still_bad = True
                    break

            if still_bad:
                issue["status"] = "reopened"
                issue["verify_note"] = "fix loste het patroon niet op"
                actions.append(f"{issue['id']}: reopened (patroon nog aanwezig)")
            else:
                issue["status"] = "verified"
                issue["verified_at"] = now
                actions.append(f"{issue['id']}: verified")

        elif status == "rebutted":
            rebuttal = (issue.get("rebuttal") or "").strip()
            lower = rebuttal.lower()
            length_ok = len(rebuttal) >= 60
            cites_rule = bool(re.search(r"§\d|MODERNISATIE\.md|ARCHAISMEN\.md|"
                                        r"KANTTEKENINGEN\.md|Grieks|γ|attributief|"
                                        r"vaste uitdrukking|idioom",
                                        rebuttal))
            is_lazy = any(p in lower for p in rebuttal_lazy_phrases) and not cites_rule
            specific = (str(issue["verse"]) in rebuttal) or cites_rule

            if not rebuttal:
                issue["status"] = "reopened"
                issue["verify_note"] = "rebuttal ontbreekt"
                actions.append(f"{issue['id']}: reopened (geen rebuttal)")
            elif not length_ok:
                issue["status"] = "reopened"
                issue["verify_note"] = "rebuttal te kort (<60 tekens) — geef een inhoudelijk argument"
                actions.append(f"{issue['id']}: reopened (rebuttal te kort)")
            elif is_lazy:
                issue["status"] = "reopened"
                issue["verify_note"] = (
                    "rebuttal valt terug op generieke 'SV-stijl'-formule "
                    "zonder regel- of Grieks-referentie"
                )
                actions.append(f"{issue['id']}: reopened (luie rebuttal)")
            elif not (cites_rule or specific):
                issue["status"] = "reopened"
                issue["verify_note"] = (
                    "rebuttal noemt geen regel (§), geen Griekse term en geen "
                    "vers-specifiek argument — voeg referentie toe"
                )
                actions.append(f"{issue['id']}: reopened (te generiek)")
            else:
                issue["status"] = "verified"
                issue["verified_at"] = now
                actions.append(f"{issue['id']}: rebuttal verified")

    passes = list(review.get("passes", []))
    pass_num = (passes[-1]["pass"] + 1) if passes else 1
    passes.append({
        "pass": pass_num,
        "ran_at": now,
        "mode": "verify",
        "actions": actions,
    })
    review["passes"] = passes
    review["reviewed_at"] = now

    with review_path.open("w", encoding="utf-8") as f:
        json.dump(review, f, ensure_ascii=False, indent=2)
        f.write("\n")

    by_status = dict(Counter(i.get("status", "open") for i in review["issues"]))

    if args.terse:
        st_str = " ".join(f"{k}:{v}" for k, v in sorted(by_status.items()))
        print(
            f"verify {book} {chapter}: status=[{st_str}] "
            f"{len(actions)} actions -> {review_path.relative_to(PROJECT_ROOT)}"
        )
        open_or_reopened = sum(
            1 for i in review["issues"] if i.get("status") in ("open", "reopened")
        )
        return 0 if open_or_reopened == 0 else 1

    summary = {
        "book": book,
        "chapter": chapter,
        "review_path": str(review_path.relative_to(PROJECT_ROOT)),
        "by_status": by_status,
        "actions": actions,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    open_or_reopened = sum(
        1 for i in review["issues"] if i.get("status") in ("open", "reopened")
    )
    return 0 if open_or_reopened == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("scan", help="Adversarial scan van een hoofdstuk.")
    sp.add_argument("--book", required=True, help="3-letterige boekcode (bv. LUK)")
    sp.add_argument("--chapter", required=True, help="Hoofdstuknummer")
    sp.add_argument("--fresh", action="store_true",
                    help="Negeer bestaande review.<H>.json (geen status-merge)")
    sp.add_argument("--terse", action="store_true",
                    help="Compacte tekstuele summary ipv. JSON.")
    sp.set_defaults(func=cmd_scan)

    vp = sub.add_parser("verify", help="Pass 2: verifieer fixes en rebuttals.")
    vp.add_argument("--book", required=True)
    vp.add_argument("--chapter", required=True)
    vp.add_argument("--terse", action="store_true",
                    help="Compacte tekstuele summary ipv. JSON.")
    vp.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
