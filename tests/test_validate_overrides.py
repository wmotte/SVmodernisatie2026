"""Smoke-tests voor `scripts/validate.py --overrides`.

Test alleen het overrides-mechanisme zelf (schema-validatie, suppressie
van issues, herberekening van passes). De validator-checks daaronder
hebben hun eigen dekking via productie-gebruik.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _import_validate():
    """Lazy-import van validate.py — vermijdt module-level cost."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("validate_mod", SCRIPTS / "validate.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def overrides_file(tmp_path: Path) -> Path:
    payload = {
        "version": 1,
        "overrides": [
            {
                "scope": "verse",
                "verse": 3,
                "issue_match": "hoofdletter-discipline",
                "justification": "SV-cap 'Engel' bewust hervormd in mv. context; §2.3 staat dit toe bij collectief.",
            }
        ],
    }
    p = tmp_path / "overrides.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_load_overrides_accepts_valid_schema(overrides_file: Path) -> None:
    mod = _import_validate()
    items = mod._load_overrides(overrides_file)
    assert len(items) == 1
    assert items[0]["scope"] == "verse"


def test_load_overrides_rejects_short_justification(tmp_path: Path) -> None:
    mod = _import_validate()
    p = tmp_path / "bad.json"
    p.write_text(
        json.dumps(
            {
                "version": 1,
                "overrides": [
                    {"scope": "chapter", "issue_match": "x", "justification": "kort"}
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as exc:
        mod._load_overrides(p)
    assert exc.value.code == 2


def test_load_overrides_rejects_bad_version(tmp_path: Path) -> None:
    mod = _import_validate()
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"version": 999, "overrides": []}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        mod._load_overrides(p)
    assert exc.value.code == 2


def test_apply_overrides_moves_matching_issue() -> None:
    mod = _import_validate()
    per_verse = [
        {
            "verse": 3,
            "passes": False,
            "issues": [
                "hoofdletter-discipline (hoofdtekst): 'Engel' -> 'engelen' (case wijziging)",
                "kanttekeningen: origineel heeft 2, modern heeft 1 (moet >= origineel)",
            ],
            "warnings": [],
        }
    ]
    matchers = [
        {
            "scope": "verse",
            "verse": 3,
            "issue_match": "hoofdletter-discipline",
            "justification": "Bewuste hervorming naar meervoud; collectief 'engelen' is moderne equivalent van SV 'Engel'.",
        }
    ]
    total = mod._apply_all_overrides(per_verse, [], [], matchers)
    assert total == 1
    assert len(per_verse[0]["issues"]) == 1
    assert per_verse[0]["issues"][0].startswith("kanttekeningen:")
    assert len(per_verse[0]["overruled"]) == 1
    assert per_verse[0]["passes"] is False  # andere issue blijft hard


def test_apply_overrides_recomputes_passes_to_true() -> None:
    mod = _import_validate()
    per_verse = [
        {
            "verse": 5,
            "passes": False,
            "issues": ["§2.3-participium: 'zeggende' niet ontvouwd"],
            "warnings": [],
        }
    ]
    matchers = [
        {
            "scope": "verse",
            "verse": 5,
            "issue_match": "§2.3-participium",
            "justification": "Attributief gebruik op zelfstandig naamwoord; §2.3 staat participium toe in attributieve positie.",
        }
    ]
    mod._apply_all_overrides(per_verse, [], [], matchers)
    assert per_verse[0]["passes"] is True
    assert per_verse[0]["issues"] == []


def test_validate_cli_overrides_pass_through(tmp_path: Path, overrides_file: Path) -> None:
    """End-to-end: CLI accepteert --overrides en exit-codes blijven kloppen."""
    luk1_input = PROJECT_ROOT / "input.sv" / "LUK" / "LUK.1.json"
    luk1_output = PROJECT_ROOT / "output" / "LUK" / "LUK.1.json"
    if not luk1_input.exists() or not luk1_output.exists():
        pytest.skip("LUK/1 fixtures niet aanwezig")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "validate.py"),
            "check",
            "--input",
            str(luk1_input),
            "--output",
            str(luk1_output),
            "--verses",
            "1",
            "--overrides",
            str(overrides_file),
            "--terse",
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode in (0, 1), f"unexpected exit: {result.returncode}\n{result.stderr}"
    assert result.stdout.startswith(("PASS", "FAIL"))
