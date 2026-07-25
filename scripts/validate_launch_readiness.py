from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


MINIMUM_NET_STARS = 30
MINIMUM_WINDOW_DAYS = 30


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _parse_date(value: object, label: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO date (YYYY-MM-DD).")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be an ISO date (YYYY-MM-DD).")
        return None


def validate_plan(plan: object) -> list[str]:
    """Return schema errors for the post-release Star-goal plan."""

    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["Plan must be a JSON object."]

    goal = plan.get("goal")
    if not isinstance(goal, dict):
        return ["goal must be an object."]

    minimum_stars = goal.get("minimumNetStars")
    if not _is_integer(minimum_stars) or minimum_stars < MINIMUM_NET_STARS:
        errors.append(
            "goal.minimumNetStars must be an integer of at least 30."
        )

    window_days = goal.get("windowDays")
    if not _is_integer(window_days) or window_days < MINIMUM_WINDOW_DAYS:
        errors.append("goal.windowDays must be an integer of at least 30.")

    release = plan.get("release")
    if not isinstance(release, dict):
        errors.append("release must be an object.")
        return errors

    status = release.get("status")
    if status not in {"planned", "released"}:
        errors.append("release.status must be 'planned' or 'released'.")
        return errors

    if status == "released":
        _parse_date(release.get("date"), "release.date", errors)
        baseline_stars = release.get("baselineStars")
        if not _is_integer(baseline_stars) or baseline_stars < 0:
            errors.append("release.baselineStars must be a non-negative integer.")
        evidence = release.get("baselineEvidence")
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(
                "release.baselineEvidence must be a non-empty URL or path."
            )

    return errors


def assess_goal(
    plan: object,
    *,
    as_of: date,
    current_stars: int | None,
) -> tuple[list[str], list[str]]:
    """Return goal errors and informational messages for the requested date."""

    errors = validate_plan(plan)
    if errors:
        return errors, []

    assert isinstance(plan, dict)
    goal = plan["goal"]
    release = plan["release"]
    assert isinstance(goal, dict)
    assert isinstance(release, dict)

    if release["status"] == "planned":
        return [], [
            "Post-release Star goal is configured; record the release baseline on launch day."
        ]

    release_errors: list[str] = []
    release_date = _parse_date(release["date"], "release.date", release_errors)
    if release_errors or release_date is None:
        return release_errors, []
    if as_of < release_date:
        return ["as-of date cannot be earlier than release.date."], []

    elapsed_days = (as_of - release_date).days
    window_days = goal["windowDays"]
    minimum_stars = goal["minimumNetStars"]
    assert isinstance(window_days, int)
    assert isinstance(minimum_stars, int)
    if elapsed_days < window_days:
        return [], [
            f"First-month Star goal is in progress: day {elapsed_days} of {window_days}."
        ]

    if not _is_integer(current_stars) or current_stars < 0:
        return [
            "currentStars must be a non-negative integer on or after the goal date."
        ], []

    baseline_stars = release["baselineStars"]
    assert isinstance(baseline_stars, int)
    net_stars = current_stars - baseline_stars
    if net_stars < minimum_stars:
        return [
            f"Net Stars after {window_days} days: {net_stars}; "
            f"at least {minimum_stars} required."
        ], []
    return [], [
        f"First-month Star goal met: {net_stars} net Stars after {window_days} days."
    ]


def _load_plan(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the v0.2.0 post-release Star-goal plan."
    )
    parser.add_argument("plan", type=Path, help="Path to launch-plan.json")
    parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Date to assess in YYYY-MM-DD format (default: today).",
    )
    parser.add_argument(
        "--current-stars",
        type=int,
        help="Current public GitHub Star count, required on or after the goal date.",
    )
    args = parser.parse_args(argv)

    try:
        as_of = date.fromisoformat(args.as_of)
    except ValueError:
        parser.error("--as-of must be an ISO date (YYYY-MM-DD).")

    try:
        plan = _load_plan(args.plan)
    except FileNotFoundError:
        parser.error(f"plan file not found: {args.plan}")
    except json.JSONDecodeError as exc:
        parser.error(
            f"invalid JSON in {args.plan}: line {exc.lineno}, column {exc.colno}"
        )
    except OSError as exc:
        parser.error(f"cannot read {args.plan}: {exc}")

    errors, messages = assess_goal(
        plan,
        as_of=as_of,
        current_stars=args.current_stars,
    )
    if errors:
        print("Launch-goal validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
