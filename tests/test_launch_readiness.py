from __future__ import annotations

from datetime import date

import pytest

from scripts.validate_launch_readiness import assess_goal, validate_plan


def planned_goal() -> dict:
    return {
        "goal": {"minimumNetStars": 30, "windowDays": 30},
        "release": {"status": "planned"},
    }


def released_goal() -> dict:
    return {
        "goal": {"minimumNetStars": 30, "windowDays": 30},
        "release": {
            "status": "released",
            "date": "2026-08-01",
            "baselineStars": 4,
            "baselineEvidence": "docs/release/evidence/release-day.md",
        },
    }


def test_planned_goal_is_valid_and_does_not_block_release() -> None:
    errors, messages = assess_goal(
        planned_goal(),
        as_of=date(2026, 7, 25),
        current_stars=None,
    )

    assert errors == []
    assert messages == [
        "Post-release Star goal is configured; record the release baseline on launch day."
    ]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("minimumNetStars", 29, "goal.minimumNetStars must be an integer of at least 30"),
        ("minimumNetStars", True, "goal.minimumNetStars must be an integer of at least 30"),
        ("windowDays", 29, "goal.windowDays must be an integer of at least 30"),
        ("windowDays", 30.0, "goal.windowDays must be an integer of at least 30"),
    ],
)
def test_goal_requires_at_least_thirty_net_stars_in_thirty_days(
    field: str, value: object, message: str
) -> None:
    plan = planned_goal()
    plan["goal"][field] = value

    assert any(message in error for error in validate_plan(plan))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("date", "2026/08/01", "release.date must be an ISO date"),
        ("baselineStars", -1, "release.baselineStars must be a non-negative integer"),
        ("baselineEvidence", " ", "release.baselineEvidence must be a non-empty URL or path"),
    ],
)
def test_released_goal_requires_auditable_baseline(
    field: str, value: object, message: str
) -> None:
    plan = released_goal()
    plan["release"][field] = value

    assert any(message in error for error in validate_plan(plan))


def test_goal_is_in_progress_before_day_thirty() -> None:
    errors, messages = assess_goal(
        released_goal(),
        as_of=date(2026, 8, 15),
        current_stars=None,
    )

    assert errors == []
    assert messages == ["First-month Star goal is in progress: day 14 of 30."]


def test_goal_requires_current_star_count_on_day_thirty() -> None:
    errors, messages = assess_goal(
        released_goal(),
        as_of=date(2026, 8, 31),
        current_stars=None,
    )

    assert messages == []
    assert errors == [
        "currentStars must be a non-negative integer on or after the goal date."
    ]


def test_goal_reports_a_miss_without_retroactively_blocking_release() -> None:
    errors, messages = assess_goal(
        released_goal(),
        as_of=date(2026, 8, 31),
        current_stars=33,
    )

    assert messages == []
    assert errors == ["Net Stars after 30 days: 29; at least 30 required."]


def test_goal_passes_at_thirty_net_stars() -> None:
    errors, messages = assess_goal(
        released_goal(),
        as_of=date(2026, 8, 31),
        current_stars=34,
    )

    assert errors == []
    assert messages == ["First-month Star goal met: 30 net Stars after 30 days."]
