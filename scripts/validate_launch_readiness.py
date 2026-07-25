from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


MAX_CONVERSION_RATE = 0.03
MINIMUM_STARS_FLOOR = 30
MINIMUM_QUALIFIED_VISITS = 1_000
MINIMUM_INDEPENDENT_CHANNELS = 3


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _source_label(source: dict[str, Any], index: int) -> str:
    name = source.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return f"source #{index}"


def validate_plan(plan: dict) -> list[str]:
    """Return release-blocking errors for a launch readiness plan."""
    errors: list[str] = []

    if not isinstance(plan, dict):
        plan = {}
        errors.append("Plan must be a JSON object.")

    conversion_rate = plan.get("conversionRate")
    conversion_valid = (
        _is_number(conversion_rate)
        and math.isfinite(conversion_rate)
        and 0 < conversion_rate <= MAX_CONVERSION_RATE
    )
    if not conversion_valid:
        errors.append("conversionRate must be greater than 0 and at most 0.03.")

    minimum_stars = plan.get("minimumStars")
    minimum_stars_valid = (
        _is_integer(minimum_stars) and minimum_stars >= MINIMUM_STARS_FLOOR
    )
    if not minimum_stars_valid:
        errors.append("minimumStars must be an integer of at least 30.")

    raw_sources = plan.get("sources")
    if not isinstance(raw_sources, list):
        errors.append("sources must be a list.")
        raw_sources = []

    included_visits = 0
    independent_channels: set[str] = set()
    seen_names: set[str] = set()

    for index, raw_source in enumerate(raw_sources, start=1):
        if not isinstance(raw_source, dict):
            errors.append(f"Source #{index} is invalid: source must be an object.")
            continue

        label = _source_label(raw_source, index)
        source_errors: list[str] = []

        name = raw_source.get("name")
        normalized_name = name.strip().casefold() if isinstance(name, str) else ""
        if not normalized_name:
            source_errors.append("name must be a non-empty string")
        elif normalized_name in seen_names:
            source_errors.append("name must be unique")
        else:
            seen_names.add(normalized_name)

        if raw_source.get("confirmed") is not True:
            source_errors.append("confirmed must be true")

        paid = raw_source.get("paid")
        if paid is True:
            source_errors.append("paid sources cannot count")
        elif paid is not False:
            source_errors.append("paid must be false")

        artificial = raw_source.get("artificial", False)
        if artificial is True:
            source_errors.append("artificial sources cannot count")
        elif artificial is not False:
            source_errors.append("artificial must be false")

        bilibili_recommendation = raw_source.get("bilibiliRecommendation", False)
        if bilibili_recommendation is True:
            source_errors.append("Bilibili recommendation traffic cannot count")
        elif bilibili_recommendation is not False:
            source_errors.append("bilibiliRecommendation must be false")

        qualified_visits = raw_source.get("qualifiedVisits")
        if not _is_integer(qualified_visits) or qualified_visits < 0:
            source_errors.append(
                "qualifiedVisits must be a non-negative integer"
            )

        channel = raw_source.get("channel")
        normalized_channel = (
            channel.strip().casefold() if isinstance(channel, str) else ""
        )
        if not normalized_channel:
            source_errors.append("channel must be a non-empty string")

        evidence = raw_source.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            source_errors.append("evidence must be a non-empty URL or path")

        if source_errors:
            errors.extend(
                f"Source '{label}' is excluded: {message}."
                for message in source_errors
            )
            continue

        included_visits += qualified_visits
        independent_channels.add(normalized_channel)

    if included_visits < MINIMUM_QUALIFIED_VISITS:
        errors.append(
            f"Included qualified visits: {included_visits:,}; "
            f"at least {MINIMUM_QUALIFIED_VISITS:,} required."
        )

    channel_count = len(independent_channels)
    if channel_count < MINIMUM_INDEPENDENT_CHANNELS:
        errors.append(
            f"Independent channels: {channel_count}; "
            f"at least {MINIMUM_INDEPENDENT_CHANNELS} required."
        )

    effective_rate = conversion_rate if conversion_valid else 0
    forecast_stars = math.floor(included_visits * effective_rate)
    required_stars = minimum_stars if minimum_stars_valid else MINIMUM_STARS_FLOOR
    if forecast_stars < required_stars:
        errors.append(
            f"Forecast Stars: {forecast_stars}; at least {required_stars} required."
        )

    return errors


def _load_plan(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the conservative v0.2.0 launch readiness gate."
    )
    parser.add_argument("plan", type=Path, help="Path to launch-plan.json")
    args = parser.parse_args(argv)

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

    errors = validate_plan(plan)
    if errors:
        print("Launch readiness blocked:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Launch readiness gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
