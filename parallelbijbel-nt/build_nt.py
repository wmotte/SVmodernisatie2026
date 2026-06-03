#!/usr/bin/env python3
"""Build ONE combined parallel-bible PDF for the whole NT (available books).

Reuses the per-verse renderers from ../parallelbijbel/build_book.py and the
shared preamble. Concatenates every available output/<BOOK>/<BOOK>.<N>.json
in NT-canon order into a single LuaLaTeX document, with an overall NT cover
page and a per-book title page. Books without an output dir (or with no
chapter files) are silently skipped — "voor zover beschikbaar".

Usage:
    python build_nt.py                 # full NT -> build/NT.pdf, publish NT.pdf
    python build_nt.py --books LUK JHN # only these books, in given order
    python build_nt.py --no-pdf        # emit build/NT.tex only
    python build_nt.py --no-publish    # don't copy build/NT.pdf -> NT.pdf
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # parallelbijbel-nt/
REPO_ROOT = ROOT.parent
PB_DIR = REPO_ROOT / "parallelbijbel"

# Reuse the battle-tested renderers + BOOK_TITLES from the per-book builder.
sys.path.insert(0, str(PB_DIR))
import build_book as bb  # noqa: E402

TEMPLATE_DIR = ROOT / "template"
BUILD_DIR = ROOT / "build"
PREAMBLE = PB_DIR / "template" / "preamble.tex"

# NT canon order (Protestant ordering, matching the project's book codes).
NT_ORDER = [
    "MAT", "MRK", "LUK", "JHN", "ACT",
    "ROM", "1CO", "2CO", "GAL", "EPH", "PHP", "COL",
    "1TH", "2TH", "1TI", "2TI", "TIT", "PHM",
    "HEB", "JAS", "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
]


def available_books(books: list[str]) -> list[str]:
    """Filter to books that actually have chapter JSON in output/<BOOK>/."""
    out: list[str] = []
    for b in books:
        book_dir = bb.OUTPUT_DIR / b
        if not book_dir.is_dir():
            print(f"skip {b}: no output dir", file=sys.stderr)
            continue
        chapters = [
            p for p in book_dir.glob(f"{b}.*.json")
            if len(p.stem.split(".")) == 2 and p.stem.split(".")[0] == b
            and p.stem.split(".")[1].isdigit()
        ]
        if not chapters:
            print(f"skip {b}: no chapter files", file=sys.stderr)
            continue
        out.append(b)
    return out


def book_titlepage(book: str) -> str:
    """A recto-starting title page that also (re)sets the running header."""
    title = bb.BOOK_TITLES.get(book, book)
    return "\n".join([
        r"\cleardoublepage",
        r"\phantomsection",
        r"\addcontentsline{toc}{section}{" + title + "}",
        r"\renewcommand{\bookname}{" + title + "}",
        r"\renewcommand{\hoofdstuknr}{}",
        r"\thispagestyle{empty}",
        r"\vspace*{0.30\textheight}",
        r"\begin{center}",
        r"  {\fontsize{22}{26}\selectfont\textbf{\textcolor{accent}{" + title + r"}}}",
        r"\end{center}",
        r"\clearpage",
    ])


def build_tex(books: list[str]) -> str:
    tpl = (TEMPLATE_DIR / "nt.tex.tpl").read_text()
    sections: list[str] = []
    for b in books:
        chapters = bb.load_chapters(b, None)
        rendered: list[str] = []
        for ch in chapters:
            n = ch["chapter"]
            # Nested chapter bookmark (subsection => PDF-outline level 2).
            # Kept out of the printed TOC via tocdepth=1 around \tableofcontents.
            rendered.append(r"\phantomsection")
            rendered.append(r"\addcontentsline{toc}{subsection}{Hoofdstuk " + str(n) + "}")
            rendered.append(bb.render_chapter(ch))
        body = "\n\n".join(rendered)
        sections.append(book_titlepage(b) + "\n\n" + body)
        n_ch = len(chapters)
        print(f"  + {b}: {n_ch} chapter(s)")
    out = tpl.replace("%%PREAMBLE_PATH%%", str(PREAMBLE))
    out = out.replace("%%BODY%%", "\n\n".join(sections))
    return out


def run_latex(tex_path: Path) -> int:
    if shutil.which("latexmk") is None:
        print("warning: latexmk not on PATH; skipping PDF build", file=sys.stderr)
        return 0
    cmd = [
        "latexmk",
        "-lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={tex_path.parent}",
        str(tex_path),
    ]
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--books", nargs="+", default=None,
                    help="Explicit book list/order (default: full NT canon)")
    ap.add_argument("--no-pdf", action="store_true", help="Emit .tex without latexmk")
    ap.add_argument("--no-publish", action="store_true",
                    help="Skip copying build/NT.pdf -> NT.pdf")
    args = ap.parse_args()

    requested = [b.upper() for b in (args.books or NT_ORDER)]
    books = available_books(requested)
    if not books:
        sys.exit("error: no available books to build")

    print(f"building combined NT from {len(books)} book(s): {', '.join(books)}")
    tex = build_tex(books)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    tex_path = BUILD_DIR / "NT.tex"
    tex_path.write_text(tex)
    print(f"wrote {tex_path}")

    if args.no_pdf:
        return 0
    rc = run_latex(tex_path)
    if rc == 0 and not args.no_publish:
        src = BUILD_DIR / "NT.pdf"
        dst = ROOT / "NT.pdf"
        if src.exists():
            shutil.copy2(src, dst)
            print(f"published {dst}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
