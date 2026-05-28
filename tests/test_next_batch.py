"""Smoke-tests voor `scripts/next_batch.py`.

Borgt dat de orchestrator een duidelijke fout krijgt i.p.v. een
ongevangen traceback bij ontbrekende invoer.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "next_batch.py"


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_missing_input_returns_exit_2(tmp_path: Path) -> None:
    (tmp_path / "input.sv").mkdir()
    res = _run(["--book", "ZZZ", "--chapter", "1"], cwd=tmp_path)
    assert res.returncode == 2
    assert "ERROR" in res.stderr
    assert res.stdout.strip() == ""


def test_corrupt_input_returns_exit_2(tmp_path: Path) -> None:
    book_dir = tmp_path / "input.sv" / "ZZZ"
    book_dir.mkdir(parents=True)
    (book_dir / "ZZZ.1.json").write_text("not valid json {", encoding="utf-8")
    res = _run(["--book", "ZZZ", "--chapter", "1"], cwd=tmp_path)
    assert res.returncode == 2
    assert "valide JSON" in res.stderr


def test_full_chapter_yields_chapter_complete(tmp_path: Path) -> None:
    book_dir = tmp_path / "input.sv" / "ZZZ"
    out_dir = tmp_path / "output" / "ZZZ"
    book_dir.mkdir(parents=True)
    out_dir.mkdir(parents=True)
    (book_dir / "ZZZ.1.json").write_text(
        json.dumps({"verses": [{"verse_number": i} for i in (1, 2, 3)]}),
        encoding="utf-8",
    )
    (out_dir / "ZZZ.1.json").write_text(
        json.dumps({"verses": [{"verse_number": i} for i in (1, 2, 3)]}),
        encoding="utf-8",
    )
    res = _run(["--book", "ZZZ", "--chapter", "1"], cwd=tmp_path)
    assert res.returncode == 0
    assert res.stdout.strip() == "CHAPTER_COMPLETE"


def test_next_batch_yields_three(tmp_path: Path) -> None:
    book_dir = tmp_path / "input.sv" / "ZZZ"
    book_dir.mkdir(parents=True)
    (book_dir / "ZZZ.1.json").write_text(
        json.dumps({"verses": [{"verse_number": i} for i in range(1, 11)]}),
        encoding="utf-8",
    )
    res = _run(["--book", "ZZZ", "--chapter", "1"], cwd=tmp_path)
    assert res.returncode == 0
    assert res.stdout.strip() == "NEXT=1-3"


def test_ceil_caps_range(tmp_path: Path) -> None:
    book_dir = tmp_path / "input.sv" / "ZZZ"
    book_dir.mkdir(parents=True)
    (book_dir / "ZZZ.1.json").write_text(
        json.dumps({"verses": [{"verse_number": i} for i in range(1, 11)]}),
        encoding="utf-8",
    )
    res = _run(["--book", "ZZZ", "--chapter", "1", "--ceil", "2"], cwd=tmp_path)
    assert res.returncode == 0
    assert res.stdout.strip() == "NEXT=1-2"
