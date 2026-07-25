from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.validate_launch_readiness import validate_plan


def valid_plan() -> dict:
    return {
        "conversionRate": 0.03,
        "minimumStars": 30,
        "sources": [
            {
                "name": "github-native",
                "channel": "github",
                "qualifiedVisits": 350,
                "confirmed": True,
                "paid": False,
                "artificial": False,
                "bilibiliRecommendation": False,
                "evidence": "docs/release/evidence/github.md",
            },
            {
                "name": "ecosystem",
                "channel": "directories",
                "qualifiedVisits": 350,
                "confirmed": True,
                "paid": False,
                "artificial": False,
                "bilibiliRecommendation": False,
                "evidence": "https://example.com/directory-listing",
            },
            {
                "name": "communities",
                "channel": "community",
                "qualifiedVisits": 300,
                "confirmed": True,
                "paid": False,
                "artificial": False,
                "bilibiliRecommendation": False,
                "evidence": "docs/release/evidence/communities.md",
            },
        ],
    }


def source_errors(plan: dict, source_name: str) -> list[str]:
    return [error for error in validate_plan(plan) if source_name in error]


def test_valid_conservative_plan_passes() -> None:
    assert validate_plan(valid_plan()) == []


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("confirmed", False, "confirmed must be true"),
        ("paid", True, "paid sources cannot count"),
        ("artificial", True, "artificial sources cannot count"),
        (
            "bilibiliRecommendation",
            True,
            "Bilibili recommendation traffic cannot count",
        ),
    ],
)
def test_excluded_sources_are_reported_and_do_not_count(
    field: str, value: object, message: str
) -> None:
    plan = valid_plan()
    plan["sources"][0][field] = value

    errors = validate_plan(plan)

    assert any(message in error for error in source_errors(plan, "github-native"))
    assert any("Included qualified visits: 650; at least 1,000 required" in error for error in errors)
    assert any("Independent channels: 2; at least 3 required" in error for error in errors)
    assert any("Forecast Stars: 19; at least 30 required" in error for error in errors)


@pytest.mark.parametrize("conversion_rate", [0, -0.01, 0.031, True, "0.03", None])
def test_conversion_rate_must_be_positive_and_no_more_than_three_percent(
    conversion_rate: object,
) -> None:
    plan = valid_plan()
    plan["conversionRate"] = conversion_rate

    assert any("conversionRate must be greater than 0 and at most 0.03" in error for error in validate_plan(plan))


@pytest.mark.parametrize("minimum_stars", [29, -1, 30.5, True, "30", None])
def test_minimum_stars_must_be_an_integer_floor_of_at_least_thirty(
    minimum_stars: object,
) -> None:
    plan = valid_plan()
    plan["minimumStars"] = minimum_stars

    assert any("minimumStars must be an integer of at least 30" in error for error in validate_plan(plan))


def test_forecast_uses_floor_and_must_meet_configured_minimum() -> None:
    plan = valid_plan()
    plan["conversionRate"] = 0.029999

    errors = validate_plan(plan)

    assert any("Forecast Stars: 29; at least 30 required" in error for error in errors)


def test_duplicate_channel_names_are_not_independent() -> None:
    plan = valid_plan()
    plan["sources"][1]["channel"] = "github"

    errors = validate_plan(plan)

    assert any("Independent channels: 2; at least 3 required" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("qualifiedVisits", -1, "qualifiedVisits must be a non-negative integer"),
        ("qualifiedVisits", 350.0, "qualifiedVisits must be a non-negative integer"),
        ("qualifiedVisits", True, "qualifiedVisits must be a non-negative integer"),
        ("channel", "  ", "channel must be a non-empty string"),
        ("evidence", "  ", "evidence must be a non-empty URL or path"),
    ],
)
def test_invalid_included_source_is_reported_and_not_counted(
    field: str, value: object, message: str
) -> None:
    plan = valid_plan()
    plan["sources"][0][field] = value

    errors = validate_plan(plan)

    assert any(message in error for error in source_errors(plan, "github-native"))
    assert any("Included qualified visits: 650; at least 1,000 required" in error for error in errors)


def test_source_names_must_be_nonempty_and_unique() -> None:
    unnamed = valid_plan()
    unnamed["sources"][0]["name"] = " "
    duplicate = deepcopy(valid_plan())
    duplicate["sources"][1]["name"] = "github-native"

    assert any("source #1" in error and "name must be a non-empty string" in error for error in validate_plan(unnamed))
    assert any("github-native" in error and "name must be unique" in error for error in validate_plan(duplicate))


def test_malformed_sources_list_blocks_with_aggregate_errors() -> None:
    plan = valid_plan()
    plan["sources"] = "not-a-list"

    errors = validate_plan(plan)

    assert any("sources must be a list" in error for error in errors)
    assert any("Included qualified visits: 0; at least 1,000 required" in error for error in errors)
    assert any("Independent channels: 0; at least 3 required" in error for error in errors)
    assert any("Forecast Stars: 0; at least 30 required" in error for error in errors)
