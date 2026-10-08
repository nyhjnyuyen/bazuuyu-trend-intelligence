import json
from pathlib import Path


DEFAULT_SNAPSHOT_DIR = Path(
    "support/output/future_trends"
)


def load_future_trend_history(
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> dict[str, list[dict]]:
    """
    Load all saved future-trend snapshots and group
    candidate observations by IP.

    This function performs no external API calls and
    does not calculate a trend score.
    """

    history = {}

    files = sorted(
        snapshot_dir.glob(
            "future_trends_*.json"
        )
    )

    for path in files:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            snapshot = json.load(file)

        generated_at = snapshot.get(
            "generated_at"
        )

        for candidate in snapshot.get(
            "candidates",
            [],
        ):

            ip = candidate.get("ip")

            if not ip:
                continue

            observation = {
                "generated_at": generated_at,
                "release_date": candidate.get(
                    "release_date"
                ),
                "movie": candidate.get(
                    "title"
                ),
                "routing_priority": candidate.get(
                    "routing",
                    {},
                ).get(
                    "priority"
                ),
                "toy_article_count": (
                    candidate.get(
                        "toy_industry",
                        {},
                    ).get(
                        "validated_article_count"
                    )
                ),
                "toy_latest_activity": (
                    candidate.get(
                        "toy_industry",
                        {},
                    ).get(
                        "latest_activity"
                    )
                ),
                "news_story_count": (
                    candidate.get(
                        "news",
                        {},
                    ).get(
                        "unique_story_count"
                    )
                ),
                "news_publisher_count": (
                    candidate.get(
                        "news",
                        {},
                    ).get(
                        "publisher_count"
                    )
                ),
                "news_concentration": (
                    candidate.get(
                        "news",
                        {},
                    ).get(
                        "story_concentration"
                    )
                ),
                "search_status": (
                    candidate.get(
                        "search",
                        {},
                    ).get(
                        "status"
                    )
                ),
                "search_direction": (
                    candidate.get(
                        "search",
                        {},
                    ).get(
                        "direction"
                    )
                ),
                "search_change_percent": (
                    candidate.get(
                        "search",
                        {},
                    ).get(
                        "change_percent"
                    )
                ),
            }

            history.setdefault(
                ip,
                [],
            ).append(
                observation
            )

    return history

from datetime import datetime


def _safe_number(value):
    """
    Convert None/non-numeric values safely to 0.
    """
    if isinstance(value, (int, float)):
        return value

    return 0


def _percent_change(old_value, new_value):
    """
    Calculate percentage change.

    Returns None when the previous value is zero,
    because percentage growth from zero is undefined.
    """
    old_value = _safe_number(old_value)
    new_value = _safe_number(new_value)

    if old_value == 0:
        if new_value == 0:
            return 0.0

        return None

    return round(
        ((new_value - old_value) / old_value) * 100,
        2,
    )


def _absolute_change(old_value, new_value):
    old_value = _safe_number(old_value)
    new_value = _safe_number(new_value)

    return new_value - old_value

def _normalized_change_score(
    percent_change,
    absolute_change,
):
    """
    Convert growth into a 0-100 momentum component.

    50 = flat
    >50 = growing
    <50 = declining

    Handles growth from zero separately because
    percentage growth from zero is undefined.
    """

    if percent_change is None:
        if absolute_change > 0:
            return min(
                100,
                65 + absolute_change * 5,
            )

        if absolute_change < 0:
            return max(
                0,
                35 + absolute_change * 5,
            )

        return 50

    score = 50 + (
        percent_change * 0.5
    )

    return round(
        max(
            0,
            min(100, score),
        ),
        2,
    )

def _classify_signal_profile(
    toy_score,
    news_score,
    publisher_score,
):
    if (
        toy_score >= 65
        and toy_score > news_score + 10
    ):
        return "TOY_DRIVEN"

    if (
        news_score >= 65
        and news_score > toy_score + 10
    ):
        return "MEDIA_DRIVEN"

    if (
        toy_score >= 55
        and news_score >= 55
    ):
        return "BROAD_GROWTH"

    if (
        toy_score < 45
        and news_score < 45
    ):
        return "BROAD_DECLINE"

    if (
        news_score < 45
        and toy_score >= 50
    ):
        return "MEDIA_COOLING"

    return "MIXED"


def _classify_momentum(score):
    if score >= 75:
        return "SURGING"

    if score >= 55:
        return "RISING"

    if score >= 48:
        return "STABLE"

    if score >= 40:
        return "COOLING"

    return "DECLINING"

def _calculate_action_timing(
    release_date,
    toy_latest_activity,
    generated_at,
):
    """
    Estimate how urgent the opportunity is based on
    release proximity and toy-industry recency.
    """

    try:
        observation_date = datetime.fromisoformat(
            generated_at
        ).date()
    except (TypeError, ValueError):
        observation_date = None

    try:
        release = datetime.fromisoformat(
            release_date
        ).date()
    except (TypeError, ValueError):
        release = None

    try:
        toy_activity = datetime.fromisoformat(
            toy_latest_activity
        ).date()
    except (TypeError, ValueError):
        toy_activity = None

    days_to_release = None

    if observation_date and release:
        days_to_release = (
            release - observation_date
        ).days

    days_since_toy_activity = None

    if observation_date and toy_activity:
        days_since_toy_activity = (
            observation_date - toy_activity
        ).days

    # Release timing score.
    if days_to_release is None:
        release_score = 50

    elif days_to_release < 0:
        release_score = 35

    elif days_to_release <= 30:
        release_score = 95

    elif days_to_release <= 90:
        release_score = 90

    elif days_to_release <= 180:
        release_score = 75

    elif days_to_release <= 270:
        release_score = 60

    else:
        release_score = 45

    # Toy-industry recency score.
    if days_since_toy_activity is None:
        toy_recency_score = 30

    elif days_since_toy_activity <= 7:
        toy_recency_score = 100

    elif days_since_toy_activity <= 30:
        toy_recency_score = 85

    elif days_since_toy_activity <= 90:
        toy_recency_score = 65

    elif days_since_toy_activity <= 180:
        toy_recency_score = 45

    else:
        toy_recency_score = 25

    timing_score = round(
        release_score * 0.55
        + toy_recency_score * 0.45,
        2,
    )

    if timing_score >= 80:
        action_timing = "ACT_NOW"

    elif timing_score >= 65:
        action_timing = "PREPARE"

    elif timing_score >= 50:
        action_timing = "MONITOR"

    else:
        action_timing = "LOW_URGENCY"

    return {
        "action_timing": action_timing,
        "timing_score": timing_score,
        "days_to_release": days_to_release,
        "days_since_toy_activity": (
            days_since_toy_activity
        ),
        "release_score": release_score,
        "toy_recency_score": toy_recency_score,
    }

def _profile_opportunity_score(
    signal_profile,
):
    scores = {
        "TOY_DRIVEN": 90,
        "BROAD_GROWTH": 80,
        "MIXED": 55,
        "MEDIA_DRIVEN": 45,
        "MEDIA_COOLING": 35,
        "BROAD_DECLINE": 20,
    }

    return scores.get(
        signal_profile,
        50,
    )

def _calculate_bazuuyu_opportunity(
    momentum_score,
    momentum_class,
    signal_profile,
    timing_score,
):
    """
    Combine trend momentum, commercial/toy alignment,
    and timing into a Bazuuyu-specific opportunity score.
    """

    if (
        momentum_score is None
        or timing_score is None
    ):
        return {
            "opportunity_score": None,
            "opportunity_class": (
                "INSUFFICIENT_DATA"
            ),
            "profile_score": None,
        }

    profile_score = (
        _profile_opportunity_score(
            signal_profile
        )
    )

    base_score = (
        momentum_score * 0.45
        + timing_score * 0.30
        + profile_score * 0.25
    )

    # Reward accelerating trends and penalize
    # cooling/declining trends.
    momentum_adjustment = {
        "SURGING": 8,
        "RISING": 5,
        "STABLE": 0,
        "COOLING": -10,
        "DECLINING": -20,
    }.get(
        momentum_class,
        0,
    )

    opportunity_score = round(
        max(
            0,
            min(
                100,
                base_score
                + momentum_adjustment,
            ),
        ),
        2,
    )

    if opportunity_score >= 80:
        opportunity_class = (
            "HIGH_PRIORITY"
        )

    elif opportunity_score >= 65:
        opportunity_class = (
            "STRONG_OPPORTUNITY"
        )

    elif opportunity_score >= 50:
        opportunity_class = (
            "WATCH"
        )

    elif opportunity_score >= 35:
        opportunity_class = (
            "LOW_PRIORITY"
        )

    else:
        opportunity_class = (
            "IGNORE_FOR_NOW"
        )

    return {
        "opportunity_score": (
            opportunity_score
        ),
        "opportunity_class": (
            opportunity_class
        ),
        "profile_score": (
            profile_score
        ),
        "momentum_adjustment": (
            momentum_adjustment
        ),
    }

def _generate_recommended_action(
    opportunity_class,
    momentum_class,
    signal_profile,
    action_timing,
):
    """
    Translate scoring signals into an actionable
    Bazuuyu recommendation.
    """

    if opportunity_class == "HIGH_PRIORITY":
        if signal_profile == "TOY_DRIVEN":
            return {
                "action": "PRIORITIZE_PRODUCT_RESEARCH",
                "summary": (
                    "Strong toy-related momentum and favorable timing. "
                    "Investigate characters, plush formats, collectibles, "
                    "licensing activity, and adjacent Bazuuyu concepts now."
                ),
            }

        return {
            "action": "PRIORITIZE",
            "summary": (
                "Strong overall opportunity. Begin deeper product, "
                "content, and commercial research."
            ),
        }

    if opportunity_class == "STRONG_OPPORTUNITY":
        if signal_profile == "TOY_DRIVEN":
            return {
                "action": "INVESTIGATE_NOW",
                "summary": (
                    "Toy-industry activity is rising. Review competing "
                    "products, character demand, plush potential, and "
                    "content opportunities."
                ),
            }

        if signal_profile == "MEDIA_DRIVEN":
            return {
                "action": "TEST_CONTENT_FIRST",
                "summary": (
                    "Media interest is rising, but toy momentum is not yet "
                    "strong enough for aggressive product action. Test "
                    "content and monitor merchandise signals."
                ),
            }

        return {
            "action": "INVESTIGATE",
            "summary": (
                "Opportunity signals are positive. Continue research "
                "before committing significant resources."
            ),
        }

    if opportunity_class == "WATCH":
        if signal_profile == "MEDIA_DRIVEN":
            return {
                "action": "MONITOR_AND_TEST_CONTENT",
                "summary": (
                    "Interest is rising mainly through media coverage. "
                    "Monitor search and toy signals while testing low-cost "
                    "social content."
                ),
            }

        if momentum_class == "STABLE":
            return {
                "action": "MONITOR",
                "summary": (
                    "Awareness remains stable, but there is no strong "
                    "acceleration yet. Continue monitoring."
                ),
            }

        return {
            "action": "WATCH",
            "summary": (
                "Signals are promising but not strong enough for immediate "
                "product investment."
            ),
        }

    if opportunity_class == "LOW_PRIORITY":
        if action_timing == "ACT_NOW":
            return {
                "action": "DO_NOT_CHASE",
                "summary": (
                    "The market window is near, but momentum is weakening. "
                    "Avoid starting major new product development based only "
                    "on release timing."
                ),
            }

        return {
            "action": "LOW_PRIORITY",
            "summary": (
                "Current momentum does not justify significant Bazuuyu "
                "resources. Continue passive monitoring."
            ),
        }

    if opportunity_class == "IGNORE_FOR_NOW":
        return {
            "action": "IGNORE_FOR_NOW",
            "summary": (
                "Current signals are too weak to justify active research "
                "or product development."
            ),
        }

    return {
        "action": "INSUFFICIENT_DATA",
        "summary": (
            "More historical observations are required before making "
            "a recommendation."
        ),
    }

def calculate_ip_momentum(
    observations: list[dict],
) -> dict:
    """
    Compare the two most recent observations
    for one IP.

    Does not generate a momentum score until
    at least two observations exist.
    """ 

    if not observations:
        return {
            "status": "NO_HISTORY",
            "observation_count": 0,
            "direction": None,
            "momentum_score": None,
        }

    ordered = sorted(
        observations,
        key=lambda item: item.get(
            "generated_at"
        ) or "",
    )

    if len(ordered) < 2:
        latest = ordered[-1]

        return {
            "status": "INSUFFICIENT_HISTORY",
            "observation_count": 1,
            "first_seen": latest.get(
                "generated_at"
            ),
            "last_seen": latest.get(
                "generated_at"
            ),
            "direction": None,
            "momentum_score": None,
            "latest": {
                "toy_article_count": (
                    latest.get(
                        "toy_article_count"
                    )
                ),
                "news_story_count": (
                    latest.get(
                        "news_story_count"
                    )
                ),
                "news_publisher_count": (
                    latest.get(
                        "news_publisher_count"
                    )
                ),
                "search_change_percent": (
                    latest.get(
                        "search_change_percent"
                    )
                ),
            },
            "momentum_class": None,
            "signal_profile": None,
            "action_timing": None,
            "timing_score": None,
            "bazuuyu_opportunity_score": None,
            "bazuuyu_opportunity_class": "INSUFFICIENT_DATA",
            "recommended_action": "COLLECT_MORE_DATA",
            "recommendation_summary": (
                "Only one historical observation is available. "
                "Collect another snapshot before evaluating momentum."
            ),
        }

    first = ordered[0]
    previous = ordered[-2]
    latest = ordered[-1]

    toy_old = _safe_number(
        previous.get(
            "toy_article_count"
        )
    )
    toy_new = _safe_number(
        latest.get(
            "toy_article_count"
        )
    )

    news_old = _safe_number(
        previous.get(
            "news_story_count"
        )
    )
    news_new = _safe_number(
        latest.get(
            "news_story_count"
        )
    )

    publishers_old = _safe_number(
        previous.get(
            "news_publisher_count"
        )
    )
    publishers_new = _safe_number(
        latest.get(
            "news_publisher_count"
        )
    )

    toy_delta = _absolute_change(
        toy_old,
        toy_new,
    )

    news_delta = _absolute_change(
        news_old,
        news_new,
    )

    publisher_delta = _absolute_change(
        publishers_old,
        publishers_new,
    )

    toy_percent = _percent_change(
        toy_old,
        toy_new,
    )

    news_percent = _percent_change(
        news_old,
        news_new,
    )

    publisher_percent = _percent_change(
        publishers_old,
        publishers_new,
    )

    toy_score = _normalized_change_score(
        toy_percent,
        toy_delta,
    )

    news_score = _normalized_change_score(
        news_percent,
        news_delta,
    )

    publisher_score = _normalized_change_score(
        publisher_percent,
        publisher_delta,
    )

    momentum_score = round(
        toy_score * 0.45
        + news_score * 0.35
        + publisher_score * 0.20,
        2,
    )

    momentum_class = _classify_momentum(
        momentum_score
    )

    signal_profile = _classify_signal_profile(
        toy_score,
        news_score,
        publisher_score,
    )

    timing = _calculate_action_timing(
        latest.get("release_date"),
        latest.get("toy_latest_activity"),
        latest.get("generated_at"),
    )

    opportunity = (
        _calculate_bazuuyu_opportunity(
            momentum_score,
            momentum_class,
            signal_profile,
            timing["timing_score"],
        )
    )

    recommendation = _generate_recommended_action(
        opportunity["opportunity_class"],
        momentum_class,
        signal_profile,
        timing["action_timing"],
    )

    return {
        "status": "READY",
        "observation_count": len(
            ordered
        ),
        "first_seen": first.get(
            "generated_at"
        ),
        "last_seen": latest.get(
            "generated_at"
        ),
        "comparison_from": previous.get(
            "generated_at"
        ),
        "comparison_to": latest.get(
            "generated_at"
        ),
        "direction": momentum_class,
        "momentum_score": momentum_score,
        "momentum_class": momentum_class,
        "component_scores": {
            "toy": toy_score,
            "news": news_score,
            "publishers": publisher_score,
        },
        "signal_profile": signal_profile,
        "changes": {
            "toy_articles": {
                "previous": toy_old,
                "current": toy_new,
                "absolute_change": (
                    toy_delta
                ),
                "percent_change": toy_percent,
            },
            "news_stories": {
                "previous": news_old,
                "current": news_new,
                "absolute_change": (
                    news_delta
                ),
                "percent_change": news_percent,
            },
            "publishers": {
                "previous": (
                    publishers_old
                ),
                "current": (
                    publishers_new
                ),
                "absolute_change": (
                    publisher_delta
                ),
                "percent_change": publisher_percent
            },
        },
        "action_timing": timing[
            "action_timing"
        ],
        "timing_score": timing[
            "timing_score"
        ],
        "days_to_release": timing[
            "days_to_release"
        ],
        "days_since_toy_activity": timing[
            "days_since_toy_activity"
        ],
        "timing_components": {
            "release": timing[
                "release_score"
            ],
            "toy_recency": timing[
                "toy_recency_score"
            ],
        },
        "bazuuyu_opportunity_score": (
            opportunity[
                "opportunity_score"
            ]
        ),

        "bazuuyu_opportunity_class": (
            opportunity[
                "opportunity_class"
            ]
        ),

        "commercial_profile_score": (
            opportunity[
                "profile_score"
            ]
        ),

        "momentum_adjustment": (
            opportunity[
                "momentum_adjustment"
            ]
        ),
        "recommended_action": recommendation["action"],
        "recommendation_summary": recommendation["summary"],
    }


def calculate_all_ip_momentum(
    history: dict[str, list[dict]],
) -> dict[str, dict]:
    """
    Calculate momentum information for every IP.
    """

    results = {}

    for ip, observations in history.items():
        results[ip] = calculate_ip_momentum(
            observations
        )

    return results

