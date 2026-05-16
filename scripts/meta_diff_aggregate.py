"""Meta-diff aggregator: mine cross-chapter patterns from
`docs/diff_hsv_<BOEK>_<H>.json` files.

Per verse, extract candidate patterns from the (sv2026 ↔ hsv ↔ original)
triple and aggregate across chapters. Output:
`output/META/candidates.json` — grouped per kind, sorted by frequency desc.

Four pattern kinds:
  - carryover         : tokens in sv2026 ∩ original, not in hsv (modulo stoplists)
  - fossiel-lidwoord  : der/des/den + noun in sv2026 but not in hsv
  - latinaat-window   : 3–5-token windows reused from original, dropped by hsv
  - cap-asym          : capitalized in sv2026, lowercase in hsv (non-sentence-initial)

CLI:
    uv run python scripts/meta_diff_aggregate.py --book LUK --chapters 1-18

Reads existing diff files by default. Use --refresh to regenerate them via
scripts/compare_hsv.py first.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Hergebruik bestaande stoplists.
from lint_carryovers import STOPLIST as CARRYOVER_STOPLIST  # noqa: E402
from validate import CAP_CHECK_STOPLIST  # noqa: E402
from adversarial_scan import (  # noqa: E402
    DREMPEL_ARCHAISMEN,
    ENDE_WHITELIST,
)

# Regex om markup uit verstekst te strippen voordat we tokeniseren.
_KANTT_RE = re.compile(r"<[^>]+>")
_BIBREF_RE = re.compile(r"\$[^$]+\$")
_SQBR_RE = re.compile(r"\[([^\]]+)\]")
_FOSSIL_RE = re.compile(r"\b(der|des|den)\s+([A-Za-zà-ÿ]+)", re.IGNORECASE)
_WORD_RE = re.compile(r"[A-Za-zà-ÿ]+")
_TOKEN_RE = re.compile(r"[A-Za-zà-ÿ]{2,}")

# Bijbeluitdrukkingen waarin der/des/den blijft staan (bucket A fossielen).
BIBLICAL_FOSSIL_PATTERNS = [
    re.compile(r"\bzoon\s+des\s+mensen\b", re.IGNORECASE),
    re.compile(r"\bkoninkrijk\s+der\s+hemelen\b", re.IGNORECASE),
    re.compile(r"\bkoninkrijk\s+der\s+heerlijkheid\b", re.IGNORECASE),
    re.compile(r"\bdag\s+des\s+heren\b", re.IGNORECASE),
    re.compile(r"\bdag\s+des\s+heeren\b", re.IGNORECASE),
    re.compile(r"\bzonen\s+der\s+mensen\b", re.IGNORECASE),
    re.compile(r"\bvrees\s+des\s+heren\b", re.IGNORECASE),
    re.compile(r"\bvrees\s+des\s+heeren\b", re.IGNORECASE),
    re.compile(r"\bwoord\s+des\s+heren\b", re.IGNORECASE),
    re.compile(r"\bwoord\s+des\s+heeren\b", re.IGNORECASE),
    re.compile(r"\bgeest\s+des\s+heren\b", re.IGNORECASE),
    re.compile(r"\bgeest\s+des\s+heeren\b", re.IGNORECASE),
    re.compile(r"\bhuis\s+des\s+heren\b", re.IGNORECASE),
    re.compile(r"\bhuis\s+des\s+heeren\b", re.IGNORECASE),
    re.compile(r"\bglans\s+der\s+heerlijkheid\b", re.IGNORECASE),
    re.compile(r"\bengel\s+des\s+heren\b", re.IGNORECASE),
    re.compile(r"\bengel\s+des\s+heeren\b", re.IGNORECASE),
]

# Functiewoorden die nooit als carryover-signaal tellen (bovenop STOPLIST).
EXTRA_FUNCTION_WORDS: frozenset[str] = frozenset({
    "de", "het", "een", "en", "of", "maar", "want", "dat", "die", "dit",
    "deze", "dezen", "wie", "wat", "welk", "welke", "als", "dan", "toen",
    "ook", "nog", "wel", "niet", "geen", "zo", "zoals", "om", "te", "voor",
    "naar", "van", "in", "op", "met", "bij", "uit", "aan", "door", "over",
    "onder", "tussen", "tegen", "tot", "tussen", "zonder", "binnen",
    "buiten", "ik", "jij", "u", "hij", "zij", "het", "wij", "jullie", "ze",
    "mij", "mijn", "jou", "jouw", "uw", "hem", "haar", "ons", "onze", "hun",
    "is", "was", "zijn", "waren", "wordt", "worden", "werd", "werden",
    "heeft", "had", "hebben", "hadden", "kan", "kon", "kunnen", "konden",
    "zal", "zou", "zouden", "zullen", "moet", "moest", "moeten",
    "ja", "nee", "ook", "weer", "al", "alle", "andere",
    # Genitief-/datief-artikelen (handled door fossiel-lidwoord kind,
    # niet door carryover).
    "der", "des", "den",
})

DEFAULT_KINDS = ("carryover", "fossiel-lidwoord", "latinaat-window", "cap-asym")


def strip_markup(text: str) -> str:
    """Verwijder kanttekeningen / bibref / vierkante haken inhoud-behoud."""
    if not text:
        return ""
    s = _KANTT_RE.sub(" ", text)
    s = _BIBREF_RE.sub(" ", s)
    s = _SQBR_RE.sub(r"\1", s)
    return s


def tokens_lower(text: str, min_len: int = 3) -> set[str]:
    """Lower-case tokens van min_len of langer."""
    return {t.lower() for t in _TOKEN_RE.findall(text) if len(t) >= min_len}


def tokens_lower_seq(text: str, min_len: int = 3) -> list[str]:
    """Lower-case token-volgorde voor n-gram-matching."""
    return [t.lower() for t in _TOKEN_RE.findall(text) if len(t) >= min_len]


def is_biblical_fossil(snippet: str) -> bool:
    return any(p.search(snippet) for p in BIBLICAL_FOSSIL_PATTERNS)


def excerpt_around(text: str, idx: int, span: int = 50) -> str:
    start = max(0, idx - span)
    end = min(len(text), idx + span)
    s = text[start:end].replace("\n", " ")
    return ("…" if start > 0 else "") + s + ("…" if end < len(text) else "")


def mine_carryover(sv2026: str, hsv: str, original: str, stoplist: frozenset[str]) -> list[dict]:
    """Tokens in sv2026 ∩ original, niet in hsv, niet in stoplist."""
    sv_main = strip_markup(sv2026)
    hsv_main = strip_markup(hsv)
    orig_main = strip_markup(original)

    sv_tok = tokens_lower(sv_main)
    hsv_tok = tokens_lower(hsv_main)
    orig_tok = tokens_lower(orig_main)

    candidates = (sv_tok & orig_tok) - hsv_tok - stoplist - EXTRA_FUNCTION_WORDS
    candidates -= {w.lower() for w in CAP_CHECK_STOPLIST}

    out: list[dict] = []
    for word in candidates:
        # HSV alternatieven: tokens in hsv die niet in sv2026 zitten en hetzelfde
        # ruwe semantische slot bezetten — we kennen het slot niet, dus we leveren
        # de symmetrische verschilset (modulo stoplist) als kandidaten.
        alts = (hsv_tok - sv_tok - orig_tok - EXTRA_FUNCTION_WORDS - stoplist)
        alts -= {w.lower() for w in CAP_CHECK_STOPLIST}
        # Beperk tot 'plausibele' alternatieven: max 10, gesorteerd alfabetisch.
        alts_list = sorted(alts)[:10]

        # Vind een excerpt-positie in sv2026.
        m = re.search(r"\b" + re.escape(word) + r"\b", sv_main, flags=re.IGNORECASE)
        sv_excerpt = excerpt_around(sv_main, m.start()) if m else sv_main[:120]
        h_excerpt = hsv_main[:120]
        o_excerpt = orig_main[:120]

        out.append({
            "kind": "carryover",
            "key": word,
            "hsv_alternatives": alts_list,
            "sv2026_excerpt": sv_excerpt,
            "hsv_excerpt": h_excerpt,
            "original_excerpt": o_excerpt,
            "severity_hint": "hard" if word in DREMPEL_ARCHAISMEN else "soft",
        })
    return out


def mine_fossiel_lidwoord(sv2026: str, hsv: str, original: str) -> list[dict]:
    """`\\b(der|des|den)\\s+\\w+` in sv2026, niet als bijbeluitdrukking,
    en niet ook in hsv (HSV koos modern alternatief)."""
    sv_main = strip_markup(sv2026)
    hsv_main = strip_markup(hsv)
    orig_main = strip_markup(original)

    out: list[dict] = []
    seen: set[str] = set()
    for m in _FOSSIL_RE.finditer(sv_main):
        article = m.group(1).lower()
        noun = m.group(2).lower()
        snippet = m.group(0)
        # Skip bijbeluitdrukkingen.
        ctx = excerpt_around(sv_main, m.start(), span=30)
        if is_biblical_fossil(ctx):
            continue
        # HSV moet niet dezelfde fossiel gebruiken.
        hsv_pattern = re.compile(r"\b" + article + r"\s+" + re.escape(noun) + r"\b", re.IGNORECASE)
        if hsv_pattern.search(hsv_main):
            continue
        key = f"{article} {noun}"
        if key in seen:
            continue
        seen.add(key)
        is_bibl_likely = is_biblical_fossil(ctx)
        out.append({
            "kind": "fossiel-lidwoord",
            "key": key,
            "article": article,
            "noun": noun,
            "sv2026_excerpt": excerpt_around(sv_main, m.start()),
            "hsv_excerpt": hsv_main[:160],
            "original_excerpt": orig_main[:160],
            "severity_hint": "soft" if is_bibl_likely else "hard",
        })
    return out


def mine_latinaat_window(sv2026: str, hsv: str, original: str) -> list[dict]:
    """3-5-token windows die in sv2026 én original voorkomen (token-overlap
    ≥3) maar niet in hsv. Pakt rest-Latinaat: SV-syntax die wij behielden
    en HSV herstructureerde."""
    sv_main = strip_markup(sv2026)
    hsv_main = strip_markup(hsv)
    orig_main = strip_markup(original)

    sv_seq = tokens_lower_seq(sv_main, min_len=3)
    orig_seq = tokens_lower_seq(orig_main, min_len=3)
    hsv_tok = set(tokens_lower(hsv_main, min_len=3))

    orig_set = set(orig_seq)
    out: list[dict] = []
    seen_keys: set[str] = set()

    for size in (4, 5):
        for i in range(len(sv_seq) - size + 1):
            window = sv_seq[i:i + size]
            # Filter: ≥3 tokens moeten in original voorkomen.
            overlap_orig = sum(1 for t in window if t in orig_set)
            if overlap_orig < 3:
                continue
            # En ≤1 token mag in HSV voorkomen (anders is HSV niet echt
            # afwijkend).
            overlap_hsv = sum(1 for t in window if t in hsv_tok)
            if overlap_hsv >= size - 1:
                continue
            # Filter te-veel-functiewoord-windows.
            content_tokens = [t for t in window
                              if t not in EXTRA_FUNCTION_WORDS
                              and t not in CARRYOVER_STOPLIST]
            if len(content_tokens) < 2:
                continue
            key = " ".join(window)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            out.append({
                "kind": "latinaat-window",
                "key": key,
                "window_size": size,
                "sv2026_excerpt": key,
                "hsv_excerpt": hsv_main[:140],
                "original_excerpt": orig_main[:140],
                "severity_hint": "soft",
            })
    return out


def mine_cap_asym(sv2026: str, hsv: str) -> list[dict]:
    """Woorden met hoofdletter in sv2026 die in hsv lowercase staan.
    Skip zinsbegin (eerste token) en eigennamen via CAP_CHECK_STOPLIST."""
    sv_main = strip_markup(sv2026)
    hsv_main = strip_markup(hsv)

    out: list[dict] = []
    seen: set[str] = set()

    # Zoek hoofdletter-woorden in sv (niet eerste token).
    matches = list(re.finditer(r"\b([A-ZÀ-Ý][a-zà-ÿ]{2,})\b", sv_main))
    if not matches:
        return out

    first_idx = matches[0].start()
    for m in matches:
        word = m.group(1)
        word_lower = word.lower()
        # Skip first-token van vers (kan zinsbegin zijn).
        if m.start() == first_idx:
            continue
        # Skip zinsbegin-na-punt.
        before = sv_main[max(0, m.start() - 2):m.start()]
        if before.strip().endswith((".", "!", "?")):
            continue
        if word_lower in CAP_CHECK_STOPLIST:
            continue
        if word_lower in EXTRA_FUNCTION_WORDS:
            continue
        # HSV moet ditzelfde woord lowercase hebben.
        hsv_low_pat = re.compile(r"\b" + re.escape(word_lower) + r"\b")
        hsv_cap_pat = re.compile(r"\b" + re.escape(word) + r"\b")
        if hsv_cap_pat.search(hsv_main):
            continue
        if not hsv_low_pat.search(hsv_main):
            continue
        if word_lower in seen:
            continue
        seen.add(word_lower)
        out.append({
            "kind": "cap-asym",
            "key": word_lower,
            "sv2026_excerpt": excerpt_around(sv_main, m.start()),
            "hsv_excerpt": hsv_main[:140],
            "original_excerpt": "",
            "severity_hint": "soft",
        })
    return out


def mine_verse(verse: dict, kinds: tuple[str, ...]) -> list[dict]:
    sv = verse.get("sv2026") or ""
    hsv = verse.get("hsv") or ""
    orig = verse.get("original") or ""
    if not sv or not hsv or not orig:
        return []
    findings: list[dict] = []
    if "carryover" in kinds:
        findings.extend(mine_carryover(sv, hsv, orig, CARRYOVER_STOPLIST))
    if "fossiel-lidwoord" in kinds:
        findings.extend(mine_fossiel_lidwoord(sv, hsv, orig))
    if "latinaat-window" in kinds:
        findings.extend(mine_latinaat_window(sv, hsv, orig))
    if "cap-asym" in kinds:
        findings.extend(mine_cap_asym(sv, hsv))
    return findings


def load_diff(book: str, chapter: int) -> dict | None:
    p = PROJECT_ROOT / "docs" / f"diff_hsv_{book}_{chapter}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def parse_chapter_range(s: str) -> list[int]:
    if "-" in s:
        a, b = s.split("-", 1)
        return list(range(int(a), int(b) + 1))
    if "," in s:
        return [int(x) for x in s.split(",") if x.strip()]
    return [int(s)]


def aggregate(book: str, chapters: list[int], kinds: tuple[str, ...],
              min_freq: int) -> dict:
    # pattern_key (kind, key) → {occurrences: [...], hsv_alts_counter, sev_hints}
    buckets: dict[tuple[str, str], dict] = defaultdict(lambda: {
        "occurrences": [],
        "hsv_alts": Counter(),
        "severity_votes": Counter(),
    })

    for ch in chapters:
        diff = load_diff(book, ch)
        if not diff:
            print(f"[skip] geen diff voor {book} {ch}", file=sys.stderr)
            continue
        for verse in diff.get("verses", []):
            if verse.get("status") != "modernized":
                continue
            findings = mine_verse(verse, kinds)
            v_num = verse.get("verse_number")
            for f in findings:
                key = (f["kind"], f["key"])
                bucket = buckets[key]
                bucket["occurrences"].append({
                    "book": book,
                    "chapter": ch,
                    "verse": v_num,
                    "sv2026_excerpt": f.get("sv2026_excerpt", ""),
                    "hsv_excerpt": f.get("hsv_excerpt", ""),
                    "original_excerpt": f.get("original_excerpt", ""),
                })
                for alt in f.get("hsv_alternatives", []):
                    bucket["hsv_alts"][alt] += 1
                bucket["severity_votes"][f["severity_hint"]] += 1

    # Bouw patterns; filter op min_freq.
    patterns_by_kind: dict[str, list[dict]] = defaultdict(list)
    pid = 0
    for (kind, key), bucket in buckets.items():
        freq = len(bucket["occurrences"])
        if freq < min_freq:
            continue
        # severity-hint: meerderheid.
        sev = "hard" if bucket["severity_votes"]["hard"] >= bucket["severity_votes"]["soft"] else "soft"
        # hsv_alternatives: top-N by frequency.
        alts = [a for a, _ in bucket["hsv_alts"].most_common(8)]
        pid += 1
        patterns_by_kind[kind].append({
            "pattern_id": f"p-{pid:04d}",
            "kind": kind,
            "key": key,
            "frequency": freq,
            "hsv_alternatives": alts,
            "severity_hint": sev,
            "occurrences": bucket["occurrences"],
        })

    # Sort within each kind by frequency desc.
    for kind in patterns_by_kind:
        patterns_by_kind[kind].sort(key=lambda p: (-p["frequency"], p["key"]))

    total = sum(len(v) for v in patterns_by_kind.values())
    return {
        "book": book,
        "chapters": chapters,
        "min_freq": min_freq,
        "kinds": list(kinds),
        "total_patterns": total,
        "patterns_by_kind": dict(patterns_by_kind),
    }


def refresh_diffs(book: str, chapters: list[int]) -> None:
    """Roep compare_hsv.py per hoofdstuk aan om diff_hsv-files te verversen."""
    for ch in chapters:
        cmd = ["uv", "run", "python", "scripts/compare_hsv.py", book, str(ch)]
        print(f"[refresh] {' '.join(cmd)}", file=sys.stderr)
        subprocess.run(cmd, check=False, cwd=PROJECT_ROOT)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--book", default="LUK")
    p.add_argument("--chapters", default="1-18",
                   help="Range '1-18' / komma-lijst '1,3,5' / enkel hoofdstuk '8'")
    p.add_argument("--min-freq", type=int, default=2)
    p.add_argument("--kinds", default=",".join(DEFAULT_KINDS),
                   help="Komma-lijst van pattern-kinds")
    p.add_argument("--refresh", action="store_true",
                   help="Draai compare_hsv.py per hoofdstuk eerst")
    p.add_argument("--output", default="output/META/candidates.json")
    args = p.parse_args()

    chapters = parse_chapter_range(args.chapters)
    kinds_tuple = tuple(k.strip() for k in args.kinds.split(",") if k.strip())
    for k in kinds_tuple:
        if k not in DEFAULT_KINDS:
            print(f"Unknown kind: {k}", file=sys.stderr)
            return 2

    if args.refresh:
        refresh_diffs(args.book, chapters)

    result = aggregate(args.book, chapters, kinds_tuple, args.min_freq)

    out_path = PROJECT_ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"→ {out_path}")
    print(f"  patterns: {result['total_patterns']}")
    for kind, lst in result["patterns_by_kind"].items():
        top = lst[0] if lst else None
        if top:
            print(f"  {kind}: {len(lst)} (top: '{top['key']}' freq={top['frequency']})")
        else:
            print(f"  {kind}: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
