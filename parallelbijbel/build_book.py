#!/usr/bin/env python3
"""Build a parallel-bible PDF for one biblical book.

Reads output/<BOOK>/<BOOK>.<N>.json (SV1657-original + modernized text
with inline <kanttekeningen> and $bibrefs$) and emits build/<BOOK>.pdf
via LuaLaTeX (two-column verse rows with paired page-bottom notes).

Usage:
    python build_book.py LUK
    python build_book.py LUK --only 24
    python build_book.py LUK --no-pdf       # only emit .tex
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
OUTPUT_DIR = REPO_ROOT / "output"
TEMPLATE_DIR = ROOT / "template"
BUILD_DIR = ROOT / "build"

BOOK_TITLES = {
    "LUK": "Het Evangelie naar Lukas",
    "MRK": "Het Evangelie naar Markus",
    "MAT": "Het Evangelie naar Mattheus",
    "JHN": "Het Evangelie naar Johannes",
}

# Token-grammar — segments of free text, <kanttekening>, $bibref$, [insertion].
# Greedy match within each delimiter; delimiters do not nest in this project.
TOKEN_RE = re.compile(
    r"<(?P<kt>[^<>]+)>"
    r"|\$(?P<ref>[^$]+)\$"
    r"|\[(?P<br>[^\[\]]+)\]"
    r"|(?P<plain>[^<$\[]+)"
)

# Words rendered in small caps in body text.
SMC_RE = re.compile(r"\b(HEEREN|HEERE|HEER|GOD|IESUS|JEZUS)\b")


def latex_escape(s: str) -> str:
    """Escape LaTeX special characters in user text."""
    s = s.replace("\\", r"\textbackslash{}")
    s = s.replace("&", r"\&")
    s = s.replace("%", r"\%")
    s = s.replace("#", r"\#")
    s = s.replace("_", r"\_")
    s = s.replace("{", r"\{")
    s = s.replace("}", r"\}")
    s = s.replace("~", r"\textasciitilde{}")
    s = s.replace("^", r"\textasciicircum{}")
    # Curly quotes / apostrophe: keep as-is (Unicode), EB Garamond renders.
    return s


def smc_replace(plain_text: str) -> str:
    """Wrap HEERE/HEEREN/HEER/GOD/IESUS in \\smc{...} in already-escaped text."""
    # Tokens are pre-escape-safe (no LaTeX specials), so do replacement
    # on raw text BEFORE latex_escape. This helper assumes plain_text is
    # raw (pre-escape). Caller must escape afterwards.
    return SMC_RE.sub(lambda m: f"\x00SMC\x01{m.group(0)}\x02", plain_text)


def render_text(text: str) -> str:
    """Convert string to LaTeX, keeping $refs$ inline (for intro/epilog)."""
    parts: list[str] = []
    strip_next = False
    for m in TOKEN_RE.finditer(text):
        kt, ref, br, plain = m.group("kt"), m.group("ref"), m.group("br"), m.group("plain")
        if kt is not None:
            parts.append(r"\kt{" + _render_inline(kt) + "}")
            strip_next = True
        elif ref is not None:
            parts.append(r"\bref{" + latex_escape(ref) + "}")
            strip_next = False
        elif br is not None:
            parts.append(r"\svins{" + _render_inline(br) + "}")
            strip_next = False
        else:
            if strip_next:
                plain = plain.lstrip()
                strip_next = False
            parts.append(_render_inline(plain))
    return "".join(parts)


REF_LABELS = "abcdefghijklmnopqrstuvwxyz"


def render_verse(
    text: str,
    note_prefix: str,
    note_mark_macro: str,
) -> tuple[str, list[tuple[str, str]], list[tuple[str, str]]]:
    """Render a verse: extract top-level $refs$, leave a labeled marker
    (\\refmark{a}) in the body so the cross-ref-line stays anchored.

    Markers (\\refmark, kanttekening-markers) attach to the FOLLOWING word: leading space
    on the next plain segment is stripped.

    Refs inside <kanttekeningen> stay inline via _render_inline.
    Returns (body_latex, [(label, ref_text), ...], [(note_id, note_text), ...]).
    """
    parts: list[str] = []
    refs: list[tuple[str, str]] = []
    notes: list[tuple[str, str]] = []
    idx = 0
    strip_next = False
    for m in TOKEN_RE.finditer(text):
        kt, ref, br, plain = m.group("kt"), m.group("ref"), m.group("br"), m.group("plain")
        if kt is not None:
            note_id = f"{note_prefix}{len(notes) + 1}"
            notes.append((note_id, _render_inline(kt)))
            parts.append("\\" + note_mark_macro + "{" + note_id + "}")
            strip_next = True
        elif ref is not None:
            label = REF_LABELS[idx % len(REF_LABELS)]
            idx += 1
            refs.append((label, latex_escape(ref)))
            parts.append(r"\refmark{" + label + "}")
            strip_next = True
        elif br is not None:
            parts.append(r"\svins{" + _render_inline(br) + "}")
            strip_next = False
        else:
            if strip_next:
                plain = plain.lstrip()
                strip_next = False
            parts.append(_render_inline(plain))
    body = "".join(parts)
    body = re.sub(r" {2,}", " ", body)
    body = body.lstrip()
    return body, refs, notes


def format_refs(refs: list[tuple[str, str]]) -> str:
    """Format a label-annotated ref list as a single LaTeX line."""
    parts = [r"\reflabel{" + lbl + "}\\,\\textit{" + txt + "}" for lbl, txt in refs]
    return r"\quad ".join(parts)


def format_notes(notes: list[tuple[str, str]]) -> str:
    """Format extracted kanttekeningen for the page-bottom note block."""
    return "".join(r"\ktitem{" + note_id + "}{" + text + "}" for note_id, text in notes)


def _render_inline(text: str) -> str:
    """Plain-segment renderer: smc-wrap then escape, then expand sentinels.

    Kanttekening-text may itself contain $bibrefs$ — handle those inline.
    """
    # First: detect nested $refs$ inside kanttekening text.
    out: list[str] = []
    pos = 0
    for m in re.finditer(r"\$([^$]+)\$", text):
        if m.start() > pos:
            out.append(_smc_escape(text[pos : m.start()]))
        out.append(r"\bref{" + latex_escape(m.group(1)) + "}")
        pos = m.end()
    if pos < len(text):
        out.append(_smc_escape(text[pos:]))
    return "".join(out)


def _smc_escape(text: str) -> str:
    """Small-caps wrap (sentinel-based) then escape."""
    marked = smc_replace(text)
    escaped = latex_escape(marked)
    # Restore sentinels: \x00SMC\x01WORD\x02 -> \smc{WORD}
    escaped = re.sub(
        r"\x00SMC\x01([A-Z]+)\x02",
        lambda m: r"\smc{" + m.group(1) + "}",
        escaped,
    )
    return escaped


def load_chapters(book: str, only: int | None) -> list[dict]:
    book_dir = OUTPUT_DIR / book
    if not book_dir.is_dir():
        sys.exit(f"error: no output dir for book {book!r}: {book_dir}")
    chapters: list[dict] = []
    for p in book_dir.glob(f"{book}.*.json"):
        # Skip review.*.json and other non-chapter files.
        stem_parts = p.stem.split(".")
        if len(stem_parts) != 2 or stem_parts[0] != book:
            continue
        try:
            ch_num = int(stem_parts[1])
        except ValueError:
            continue
        if only is not None and ch_num != only:
            continue
        with p.open() as f:
            chapters.append(json.load(f))
    chapters.sort(key=lambda c: c["chapter"])
    if not chapters:
        sys.exit(f"error: no chapters found for {book} (only={only})")
    return chapters


def render_chapter(ch: dict) -> str:
    n = ch["chapter"]
    lines: list[str] = []
    lines.append(r"\renewcommand{\hoofdstuknr}{" + f"Hoofdstuk {n}" + "}")
    lines.append(r"\hoofdstuktitel{" + str(n) + "}")

    intro = ch.get("introduction")
    if intro:
        lines.append(
            r"\introblok{"
            + render_text(intro.get("original", ""))
            + "}{"
            + render_text(intro.get("modernized", ""))
            + "}"
        )

    # Two-column parallel verses via unbreakable rows (strict page sync).
    lines.append(r"\headerpair{Statenvertaling 1657}{Gemoderniseerde versie}")

    for v in ch["verses"]:
        vn = v["verse_number"]
        orig_body, orig_refs, orig_notes = render_verse(
            v.get("original", ""), f"kt{n}v{vn}o", "ktmarksv"
        )
        modr_body, modr_refs, modr_notes = render_verse(
            v.get("modernized", ""), f"kt{n}v{vn}m", "ktmarkmod"
        )
        orig_refs_tex = r"\vrsrefs{" + format_refs(orig_refs) + "}" if orig_refs else ""
        modr_refs_tex = r"\vrsrefs{" + format_refs(modr_refs) + "}" if modr_refs else ""
        lines.append(
            r"\verspair{" + str(vn) + "}"
            + "{" + orig_body + "}"
            + "{" + orig_refs_tex + "}"
            + "{" + modr_body + "}"
            + "{" + modr_refs_tex + "}"
        )
        if orig_notes or modr_notes:
            lines.append(
                r"\ktpairnotes{"
                + format_notes(orig_notes)
                + "}{"
                + format_notes(modr_notes)
                + "}"
            )

    epi = ch.get("epilogue")
    if epi:
        lines.append(
            r"\epilogblok{"
            + render_text(epi.get("original", ""))
            + "}{"
            + render_text(epi.get("modernized", ""))
            + "}"
        )

    # Reset footnote-counter at chapter boundary — perpage already does
    # this per page; this is belt+suspenders for clean numbering.
    lines.append(r"\clearpage")
    return "\n".join(lines)


def build_tex(book: str, chapters: list[dict]) -> str:
    tpl = (TEMPLATE_DIR / "book.tex.tpl").read_text()
    body = "\n\n".join(render_chapter(ch) for ch in chapters)
    title = BOOK_TITLES.get(book, book)
    out = tpl.replace("%%PREAMBLE_PATH%%", str(TEMPLATE_DIR / "preamble.tex"))
    out = out.replace("%%BOOK_TITLE%%", title)
    out = out.replace("%%BODY%%", body)
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
    ap.add_argument("book", help="Book code, e.g. LUK")
    ap.add_argument("--only", type=int, default=None, help="Build only chapter N")
    ap.add_argument("--no-pdf", action="store_true", help="Emit .tex without running latexmk")
    args = ap.parse_args()

    book = args.book.upper()
    chapters = load_chapters(book, args.only)
    tex = build_tex(book, chapters)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f".only{args.only}" if args.only is not None else ""
    tex_path = BUILD_DIR / f"{book}{suffix}.tex"
    tex_path.write_text(tex)
    print(f"wrote {tex_path} ({len(chapters)} chapter(s))")

    if args.no_pdf:
        return 0
    return run_latex(tex_path)


if __name__ == "__main__":
    sys.exit(main())
