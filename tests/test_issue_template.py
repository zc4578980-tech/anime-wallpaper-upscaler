from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
BUG_REPORT = ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"


def test_bug_report_issue_form_collects_actionable_safe_details() -> None:
    text = BUG_REPORT.read_text(encoding="utf-8")

    assert "name: Bug report" in text
    assert "title: \"[Bug]: \"" in text
    assert "labels:\n  - bug" in text

    ids = re.findall(r"^  id: ([a-z0-9_-]+)$", text, flags=re.MULTILINE)
    assert len(ids) == len(set(ids))
    assert {
        "area",
        "version",
        "launch_method",
        "environment",
        "steps",
        "expected",
        "actual",
        "logs",
        "additional_context",
        "checks",
    } <= set(ids)

    assert "Do not include passwords, tokens, private paths, or personal information." in text
    assert "Do not upload source artwork unless it is necessary" in text
    assert "I searched existing issues for the same problem." in text
    assert "I removed credentials and personal information from logs and screenshots." in text
