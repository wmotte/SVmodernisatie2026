"""Shared rule configurations for SVmodernisatie2026.

Centralizes lists for blacklists, false friends, participles, genitives, and drempel-archaïsmen to act as a single source of truth across:
- scripts/validate.py
- scripts/lint_false_friends.py
- scripts/adversarial_scan.py
- scripts/meta_diff_aggregate.py
- scripts/lint_carryovers.py
"""

import re
from pathlib import Path

# Paths
SCRIPTS_DIR = Path(__file__).resolve().parent
STOPLIST_PATH = SCRIPTS_DIR / "stoplist.txt"

# 1. Archaïsche Blacklist (from validate.py)
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
    r"\bzijnde\b(?! een)",  # 'zijnde' stand-alone is verdacht; "zijnde een" is OK
    r"\bhebbende\b",        # participle 'gekregen hebbende' etc. → unfold (AGENTS.md)
    r"\bnagetracht\b",      # archaïsch "nagestreefd"
    # 'geschieden'-paradigma → "gebeuren"-vormen (γίνομαι), concordantie.
    # UITZONDERING (gefossiliseerde formule, analoog aan §2.3c genitief-fossielen,
    # SV27-conform): de Lukaanse/Septuaginta-formule καὶ ἐγένετο blijft staan —
    #   narratief  'het geschiedde …' / ''t geschiedde …'  (lookbehind 'het '/''t ')
    #   profetisch 'geschiedde het woord …'                 (lookahead ' het woord')
    # 'geschiede' (Onze Vader, Lk 11:2) en 'geschiedenis' vallen al buiten de \b-groep.
    # Concrete betekenis ('geschiedde een stem' Lk 9:35 → 'kwam') blijft WEL HARD.
    r"(?<!het )(?<!'t )\bgeschied(t|de|den|en)?\b(?!\s+het woord)",
    r"(?<!hieraan )(?<!daaraan )(?<!eraan )(?<!hieraan\] )(?<!daaraan\] )(?<!eraan\] )(?<!aan dit )(?<!aan deze )(?<!aan dat )(?<!aan die )(?<!aan dit\] )(?<!aan deze\] )(?<!aan dat\] )(?<!aan die\] )\bgelijk\b(?! aan)",          # voegwoord → "zoals"; predicatief "[hieraan] gelijk" / "gelijk aan" mag
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
    r"\brantsoen\b",        # → "losprijs" (Gr. λύτρον); modern NL = voedseltoewijzing
    r"\beertijds\b",        # → "vroeger / voorheen" (drempel-archaisme; PHM 1:11)
    r"\bdieverij\b",        # → "diefstal" (PHM 1:18 kt)
    r"\bdaar\s+(?:ik|wij|u|gij)\s+\w+\b",  # causaal 'daar' + 1/2-persoon → "nu / aangezien / omdat" (PHM 1:9)
]

# Allowlist als (artikel, zn)-paar in lowercase.
FOSSIL_GENITIVE_PAIRS: frozenset[tuple[str, str]] = frozenset({
    ("des", "mensen"),         # Zoon des mensen (Gr. ὁ υἱὸς τοῦ ἀνθρώπου)
    ("der", "joden"),          # Koning der Joden
    ("der", "heerlijkheid"),   # Koning der heerlijkheid
    ("der", "heerscharen"),    # Heer der heerscharen
    ("der", "hemelen"),        # Koninkrijk der hemelen
    ("des", "oordeels"),       # dag des oordeels
    ("des", "huizes"),         # heer des huizes
    ("des", "heeren"),         # dag des Heeren
    ("des", "levens"),         # boek des levens
    ("der", "heiligen"),       # Heilige der heiligen
    ("der", "voorbereiding"),  # dag der voorbereiding
    ("der", "verwoesting"),    # gruwel der verwoesting
    ("der", "tanden"),         # knersing der tanden
    ("der", "ongerechtigheid"),# werkers der ongerechtigheid
    ("der", "rechtvaardigen"), # opstanding der rechtvaardigen
    ("der", "doden"),          # opstanding der doden
    ("des", "persoons"),       # aanzien des persoons (Gr. προσωπολημψία)
    ("der", "aarde"),          # einden der aarde
    ("der", "wereld"),         # volken der wereld
})

# 2. Participle Rules (from validate.py)
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
    # Latinaat-participiale doorlopers
    "strekkende",
    "navolgende",
    # Kanttekening-glossen
    "werpende", "aanvangende", "uitberstende", "uitbarstende",
    "kennende", "makende", "vasthoudende",
})

PARTICIPLE_CONTEXT_ENDE: frozenset[str] = frozenset({
    "komende", "zittende", "weidende", "vallende", "varende",
    "liggende", "wandelende", "lopende", "bevende", "wakende",
    "wonende", "rustende", "slapende", "zwijgende",
    "toekomende",
    "neerzittende",
})

ADVERBIAL_TRIGGERS_AFTER_PARTICIPLE = frozenset({
    "op", "in", "tot", "aan", "uit", "van", "met", "naar", "over",
    "onder", "boven", "tussen", "achter", "voor", "bij", "om", "door",
    "wat", "dat", "toen", "terwijl", "omdat", "zodat", "wanneer", "waarom",
    "hoe", "of", "waar",
})

PARTICIPLE_ATTRIBUTIVE_REQUIRES_DETERMINER: frozenset[str] = frozenset({
    "staande",
})

PARTICIPLE_ATTRIBUTIVE_DETERMINERS: frozenset[str] = frozenset({
    "de", "het", "een", "deze", "die", "dit", "dat",
    "mijn", "uw", "zijn", "haar", "onze", "hun",
    "enkele", "enige", "vele", "veel", "alle", "sommige", "geen",
    "elke", "elk", "ieder", "iedere",
})

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

CAP_CHECK_STOPLIST = {
    "ende", "doch", "soo", "dese", "desen", "deser", "daer", "daerom",
    "siet", "ofte", "gelijck", "ghy", "gy", "des", "nademael", "aangezien",
    "aengaende", "aengezien", "voortijts", "sulcks", "alsoo", "alsdan",
    "terstondt", "want", "maer", "ook", "overmits", "wijl", "alsoo",
    "doe", "alhoewel", "hoewel", "het", "welck", "welcke", "wat",
    "ende.", "ende,",
}

# 3. False Friends (from lint_false_friends.py)
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
        "advies": "'gewoon', 'passend'",  # Note: preserved original advies
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
        "sv": "struikelblok, aanstoot (Gr. σκάνδαλον / πρόσκοmma)",
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
        "advies": "'het waagde te ...', 'het durfde ...'; controleer of het idiom hier bedoeld is — anders carry-over OK",
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
        "advies": "'vrijgekocht' / 'losgekocht'; alleen carry-over als context écht 'afladen/oplossen' is",
    },
    {
        "pattern": r"\b(beschadigen|beschadigd|beschadigt|beschadigde)\b",
        "sv": "letsel/schade toebrengen aan persoon (Gr. ἀδικέω / βλάπτω)",
        "modern": "schade toebrengen aan een zaak/object (niet persoon)",
        "advies": "voor persoon: 'letsel toebrengen', 'schade berokkenen'; 'beschadigen' van persoon leest modern absurd-technisch (LUK 4:35, 10:19)",
    },
    {
        "pattern": r"\b(doorbrengen|doorgebracht|doorbracht|doorbrachten)\b",
        "sv": "verkwisten, erdoorheen jagen (geld/goed) — bij object 'geld'/'goed'/'bezit'",
        "modern": "tijd doorbrengen (met iemand, ergens)",
        "advies": "bij geld/bezit-object: 'verkwisten' / 'opmaken' / 'erdoorheen jagen'; bij tijd-object is carry-over OK (LUK 15:13, 15:30)",
    },
    {
        "pattern": r"\b(hof|hove|hoven)\b",
        "sv": "ommuurde woonruimte/erf óf moestuin (context-afhankelijk)",
        "modern": "vorstenhof, rechtbank, formele tuin",
        "advies": "controleer SV-referent in context: 'erf' / 'woning' (LUK 11:21) of 'tuin' (LUK 13:19); 'hof' bewaart de moderne lezer geen van beide",
    },
]

# 4. Adversarial Scan Specific Rules (from adversarial_scan.py)
ENDE_WHITELIST: frozenset[str] = frozenset({
    # Ordinalen
    "tiende", "elfde", "twaalfde", "dertiende", "veertiende",
    "vijftiende", "zestiende", "zeventiende", "achttiende",
    "negentiende", "twintigste", "honderdste",
    # Stof-/registernamen
    "einde", "vriende", "ellende", "leende", "wende",
    "kruimende", "duizende",
    # Stand-alone gestolde adjectieven
    "volgende", "komende", "voorgaande",
    "aanstaande", "afgelopen",
})

DREMPEL_ARCHAISMEN: frozenset[str] = frozenset({
    "alzo", "voorts", "wijl", "overmits", "alhoewel", "zoo",
    "indien", "ofschoon", "alsook",
    "weldra", "weldadig", "weldadigheid",
    "gewis", "voorzeker",
    "wederom", "wederkeren", "wederkeer", "wederkomst",
    "voorwaar",
    "zekerlijk", "geenszins",
    "ootmoed", "ootmoedig", "ootmoediglijk",
    "lankmoedig", "lankmoedigheid",
    "barmhartiglijk", "rechtvaardiglijk",
    "ongeveinsd", "ongeveinsdheid",
    "vermits", "dewijl", "dewelke", "hetwelk", "hetwelke",
    "evenwel",
    "alom", "voorhanden",
    "smadelijk", "smaadlijk",
    "luttel",
    "nochthans",
    "uwe",  # zelfst. gebruikt possessief 'de uwe' / 'het uwe'
    "ure",
})

DREMPEL_FOSSIELEN: tuple[str, ...] = (
    r"\bten\s+\w+den\s+dage\b",
    r"\bter\s+ure\b",
    r"\b(?:[Hh]oort|[Zz]iet|[Zz]ie)\b(?:\s+\w+){0,4}\s+toe\b",
)

KANTTEKENING_ARCHAISMEN: tuple[str, ...] = (
    r"\bLeeraers?\b", r"\bLeeraren\b",
    r"\bAengaende\b", r"\bAengezien\b",
    r"\bDiscipulen\b", r"\bDiscipulinnen\b",
    r"\bMenschen?\b",
    r"\bzeggens?\b\s+(is|wil)\b",
    r"\bSeggens?\b",
)

# 5. Stoplist helper (from lint_carryovers.py)
def _load_stoplist() -> frozenset[str]:
    """Lees stoplist.txt: één woord per regel, '#' = comment, blanks genegeerd."""
    words: set[str] = set()
    if not STOPLIST_PATH.exists():
        return frozenset()
    for raw in STOPLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            words.add(line)
    return frozenset(words)

STOPLIST: frozenset[str] = _load_stoplist()
