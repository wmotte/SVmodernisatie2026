#!/usr/bin/env python3
"""Voortgangscijfers voor het achtergrondartikel (resultaten-paragrafen).

Aggregeert in één keer alle getallen die in `achtergrondartikel/`
worden genoemd, met dezelfde definities als `scripts/count_words.py`
(zodat het done-percentage consistent is met het NT-totaal):

  * NT-brontotaal (input.sv/): hoofdtekst-, kanttekening-, introductie-
    en epiloogwoorden + verwijzingen, plus aantal verzen/hoofdstukken.
  * Gemoderniseerd (output/): dezelfde categorieën, geteld over de
    SV-zijde (`original`) zodat het direct vergelijkbaar is met de bron.
  * Per boek: hoeveel hoofdstukken/verzen af zijn en of het boek compleet is.
  * Steigerwerk: aantal scripts, regels, skills, validator-/scanner-omvang.
  * Git: totaal commits + commits die het steigerwerk raken.
  * Kwaliteit: aantal adversariële reviews (review.*.json) + bevindingen.

Een "woord" is een aaneengesloten reeks letters/cijfers (apostrof inbegrepen),
identiek aan count_words.py. Hoofdtekst = versproza zonder kanttekeningen
<…> en zonder bijbelverwijzingen $…$.

Gebruik:  python3 scripts/progress_stats.py
Reproduceerbaar; geen argumenten. Draai vanuit elke map (paden zijn
relatief aan de repo-root, afgeleid van dit script).
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO / "input.sv"
OUTPUT_DIR = REPO / "output"

ANNOTATION_RE = re.compile(r"<[^>]*>")
REFERENCE_RE = re.compile(r"\$[^$]*\$")
WORD_RE = re.compile(r"[0-9A-Za-zÀ-ÿ’']+")

# Canonieke NT-volgorde + volledige Nederlandse boeknaam (zoals count_words.py).
NT_BOOKS: list[tuple[str, str]] = [
    ("MAT", "Mattheüs"), ("MRK", "Markus"), ("LUK", "Lukas"),
    ("JHN", "Johannes"), ("ACT", "Handelingen"), ("ROM", "Romeinen"),
    ("1CO", "1 Korinthe"), ("2CO", "2 Korinthe"), ("GAL", "Galaten"),
    ("EPH", "Efeze"), ("PHP", "Filippenzen"), ("COL", "Kolossenzen"),
    ("1TH", "1 Thessalonicenzen"), ("2TH", "2 Thessalonicenzen"),
    ("1TI", "1 Timotheüs"), ("2TI", "2 Timotheüs"), ("TIT", "Titus"),
    ("PHM", "Filemon"), ("HEB", "Hebreeën"), ("JAS", "Jakobus"),
    ("1PE", "1 Petrus"), ("2PE", "2 Petrus"), ("1JN", "1 Johannes"),
    ("2JN", "2 Johannes"), ("3JN", "3 Johannes"), ("JUD", "Judas"),
    ("REV", "Openbaring"),
]


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def main_words(text: str) -> int:
    """Woorden in de hoofdtekst: zonder <…> en zonder $…$."""
    return words(REFERENCE_RE.sub(" ", ANNOTATION_RE.sub(" ", text)))


def annotation_words(text: str) -> int:
    """Woorden binnen alle <…>-kanttekeningen."""
    return words(" ".join(ANNOTATION_RE.findall(text)))


def fmt(n: int) -> str:
    """Duizendtallen met punt (1.151), zoals in het artikel."""
    return f"{n:,}".replace(",", ".")


def pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.1f}%".replace(".", ",") if whole else "—"


def count_chapter(data: dict, text_field: str) -> tuple[int, int, int, int]:
    """(hoofdtekst, kanttekening, introductie, verzen) voor één hoofdstuk-JSON.

    `text_field` is "text" (input.sv) of "original"/"modernized" (output).
    De introductie-/epiloog-velden zijn in input.sv strings en in output
    dicts met dezelfde tekstvelden.
    """
    def field(obj):
        if isinstance(obj, dict):
            return obj.get(text_field, "") or ""
        return obj or ""

    intro = field(data.get("introduction")) + " " + field(data.get("epilogue"))
    mt = at = 0
    nv = 0
    for verse in data.get("verses", []):
        t = verse.get(text_field, "")
        mt += main_words(t)
        at += annotation_words(t)
        nv += 1
    return mt, at, main_words(intro), nv


def scan_dir(base: Path, book: str, text_field: str) -> tuple[int, int, int, int, int]:
    """Som over alle hoofdstukken van een boek: (hoofdtekst, kant, intro,
    verzen, hoofdstukken)."""
    d = base / book
    mt = at = it = nv = nch = 0
    if not d.is_dir():
        return 0, 0, 0, 0, 0
    for f in sorted(d.glob(f"{book}.*.json")):
        nch += 1
        m, a, i, v = count_chapter(json.loads(f.read_text(encoding="utf-8")), text_field)
        mt += m; at += a; it += i; nv += v
    return mt, at, it, nv, nch


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True, capture_output=True, text=True,
    ).stdout


def line_count(paths: list[Path]) -> int:
    total = 0
    for p in paths:
        if p.is_file():
            total += sum(1 for _ in p.open(encoding="utf-8", errors="ignore"))
    return total


def main() -> None:
    # --- NT-brontotaal (input.sv) ---
    src = {}
    g_main = g_annot = g_intro = g_verses = g_chap = 0
    for book, _ in NT_BOOKS:
        r = scan_dir(INPUT_DIR, book, "text")
        src[book] = r
        g_main += r[0]; g_annot += r[1]; g_intro += r[2]
        g_verses += r[3]; g_chap += r[4]
    nt_total_words = g_main + g_annot + g_intro

    print("== NT-broncorpus (input.sv) ==")
    print(f"  hoofdtekst {fmt(g_main)} · kanttekeningen {fmt(g_annot)} · "
          f"introductie/epiloog {fmt(g_intro)}")
    print(f"  totaal {fmt(nt_total_words)} woorden · {fmt(g_verses)} verzen · "
          f"{fmt(g_chap)} hoofdstukken")

    # --- Gemoderniseerd (output, SV-zijde 'original') ---
    d_main = d_annot = d_intro = d_verses = d_files = 0
    complete = []
    partial = []
    per_book = []
    for book, name in NT_BOOKS:
        r = scan_dir(OUTPUT_DIR, book, "original")
        if r[4] == 0:
            continue
        d_main += r[0]; d_annot += r[1]; d_intro += r[2]
        d_verses += r[3]; d_files += r[4]
        s = src[book]
        done = r[4] == s[4] and r[3] == s[3]
        (complete if done else partial).append((name, book, r[4], s[4], r[3], s[3]))
        per_book.append((name, book, r[4], s[4], r[3], r[0]))
    d_total = d_main + d_annot + d_intro

    # hoofdstukbestanden: hoeveel volledig (verzen >= bron)?
    files_full = 0
    for book, _ in NT_BOOKS:
        od = OUTPUT_DIR / book
        if not od.is_dir():
            continue
        for f in sorted(od.glob(f"{book}.*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            ch = data.get("chapter")
            src_file = INPUT_DIR / book / f"{book}.{ch}.json"
            src_nv = len(json.loads(src_file.read_text(encoding="utf-8")).get("verses", [])) \
                if src_file.is_file() else 10**9
            if len(data.get("verses", [])) >= src_nv:
                files_full += 1

    print("\n== Gemoderniseerd (output) ==")
    print(f"  hoofdstukbestanden {d_files} (waarvan {files_full} volledig afgerond)")
    print(f"  complete boeken: {len(complete)} · deels: {len(partial)}")
    print(f"  verzen {fmt(d_verses)} van {fmt(g_verses)} ({pct(d_verses, g_verses)})")
    print(f"  hoofdtekst {fmt(d_main)} van {fmt(g_main)} ({pct(d_main, g_main)})")
    print(f"  totaal {fmt(d_total)} van {fmt(nt_total_words)} "
          f"({pct(d_total, nt_total_words)})")

    print("\n  Per boek (hoofdstukken af / totaal, verzen):")
    for name, book, nch, tch, nv, _mw in per_book:
        tag = "compleet" if (name, book, nch, tch, nv, src[book][3]) in complete \
            else f"deels {nch}/{tch}"
        print(f"    {name} ({book}): {nch}/{tch} hoofdstukken, {fmt(nv)} verzen — {tag}")

    if partial:
        print("\n  Deels verwerkt: " +
              ", ".join(f"{n}" for n, *_ in partial))

    # --- Steigerwerk ---
    scripts = sorted((REPO / "scripts").glob("*.py"))
    skill_files = sorted((REPO / ".agents" / "skills").glob("*/SKILL.md"))
    rule_files = [REPO / n for n in (
        "ARCHAISMEN.md", "KANTTEKENINGEN.md", "BIJBELVERWIJZINGEN.md",
        "MODERNISATIE.md", "INTRO_EPILOOG.md", "OUTPUT_SCHEMA.md")]
    scaffold_lines = line_count(scripts) + line_count(skill_files) + line_count(rule_files)
    validator = line_count([REPO / "scripts" / "validate.py"])
    scanner = line_count([REPO / "scripts" / "adversarial_scan.py"])

    print("\n== Steigerwerk ==")
    print(f"  {len(scripts)} Python-scripts · {len(skill_files)} skills")
    print(f"  ~{fmt(scaffold_lines)} regels (scripts + skills + kern-regelbestanden)")
    print(f"  validator {fmt(validator)} regels · adversariële scanner {fmt(scanner)} regels")

    # --- Git ---
    total_commits = int(git("rev-list", "--count", "HEAD").strip())
    scaffold_commits = len(git(
        "log", "--oneline", "--",
        "scripts/", ".agents/skills/", "AGENTS.md",
        "ARCHAISMEN.md", "KANTTEKENINGEN.md",
    ).splitlines())
    print("\n== Git ==")
    print(f"  {fmt(total_commits)} commits totaal · "
          f"~{fmt(scaffold_commits)} raken het steigerwerk")

    # --- Kwaliteit ---
    reviews = sorted(OUTPUT_DIR.glob("*/review.*.json"))
    findings = 0
    for r in reviews:
        try:
            data = json.loads(r.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        items = data if isinstance(data, list) else (
            data.get("issues") or data.get("findings") or [])
        findings += len(items)
    print("\n== Kwaliteit ==")
    print(f"  {fmt(len(reviews))} adversariële reviews · {fmt(findings)} bevindingen")


if __name__ == "__main__":
    main()
