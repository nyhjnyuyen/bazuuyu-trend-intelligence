import math
from typing import Iterable


def normalize(value: float, minimum: float, maximum: float) -> float:
    """
    Normalize a value to a 0-100 scale.
    """

    if maximum <= minimum:
        return 50.0

    value = max(minimum, min(value, maximum))

    return ((value - minimum) / (maximum - minimum)) * 100


def calculate_engagement_score(
    avg_score: float,
    avg_comments: float,
    avg_upvote_ratio: float,
) -> float:
    """
    Calculate an engagement score from Reddit activity.

    The logarithm prevents very large Reddit scores/comments
    from completely dominating the result.
    """

    score_signal = math.log1p(max(avg_score, 0))
    comment_signal = math.log1p(max(avg_comments, 0))
    upvote_signal = max(0.0, min(avg_upvote_ratio, 1.0)) * 100

    raw_score = (
        score_signal * 0.4
        + comment_signal * 0.4
        + upvote_signal * 0.2
    )

    # Approximate conversion to 0-100.
    return max(0.0, min(raw_score * 10, 100.0))


def calculate_frequency_score(
    post_count: int,
    total_posts: int,
) -> float:
    """
    Measure how large a trend is relative to the
    available posts in the period.

    Uses a square-root curve so that very large clusters
    do not immediately dominate the score.
    """

    if total_posts <= 0 or post_count <= 0:
        return 0.0

    ratio = post_count / total_posts

    # Convert the share of conversation into a 0-100 score.
    # 25% of the conversation corresponds to 100.
    score = (ratio / 0.25) ** 0.5 * 100

    return round(min(score, 100.0), 2)

def calculate_growth_score(
    previous_count: int,
    current_count: int,
) -> float:
    """
    Measure trend growth between two periods.

    100 = strong growth
    50 = approximately stable
    0 = strong decline
    """

    if previous_count <= 0:
        if current_count > 0:
            return 100.0
        return 0.0

    growth_rate = (
        current_count - previous_count
    ) / previous_count

    # Convert growth rate into a bounded 0-100 score.
    score = 50 + (growth_rate * 50)

    return max(0.0, min(score, 100.0))


def calculate_persistence_score(
    periods_present: int,
    periods_observed: int,
) -> float:
    """
    Measure how consistently a trend appears over time.
    """

    if periods_observed <= 0:
        return 0.0

    persistence = periods_present / periods_observed

    return max(0.0, min(persistence * 100, 100.0))


def calculate_trend_score(
    engagement_score: float,
    frequency_score: float,
    growth_score: float,
    persistence_score: float,
) -> float:
    """
    Combine measurable signals into a single Trend Score.

    Current weights:
        engagement  = 25%
        frequency   = 20%
        growth      = 35%
        persistence = 20%
    """

    score = (
        engagement_score * 0.25
        + frequency_score * 0.20
        + growth_score * 0.35
        + persistence_score * 0.20
    )

    return round(max(0.0, min(score, 100.0)), 2)
def percentile_score(value: float, reference_values: Iterable[float]) -> float:
    """
    Convert a value into a percentile-based 0-100 score.

    The reference distribution should come from the actual
    dataset being analyzed.
    """

    values = sorted(float(v) for v in reference_values)

    if not values:
        return 0.0

    count_below_or_equal = sum(
        1 for v in values if v <= value
    )

    return round(
        (count_below_or_equal / len(values)) * 100,
        2,
    )


def calculate_calibrated_engagement_score(
    avg_score: float,
    avg_comments: float,
    avg_upvote_ratio: float,
    score_reference: Iterable[float],
    comments_reference: Iterable[float],
) -> float:
    """
    Calculate engagement using the actual Reddit
    dataset distribution.
    """

    score_percentile = percentile_score(
        avg_score,
        score_reference,
    )

    comments_percentile = percentile_score(
        avg_comments,
        comments_reference,
    )

    upvote_score = (
        max(0.0, min(avg_upvote_ratio, 1.0))
        * 100
    )

    engagement = (
        score_percentile * 0.4
        + comments_percentile * 0.4
        + upvote_score * 0.2
    )

    return round(engagement, 2)
def calculate_dataset_engagement_scores(
    cluster_stats: list[dict],
) -> list[dict]:
    """
    Calculate calibrated engagement scores for a collection
    of trend/cluster statistics using the dataset distribution.
    """

    score_reference = [
        float(item.get("avg_score", 0))
        for item in cluster_stats
    ]

    comments_reference = [
        float(item.get("avg_comments", 0))
        for item in cluster_stats
    ]

    results = []

    for item in cluster_stats:
        engagement = calculate_calibrated_engagement_score(
            avg_score=float(item.get("avg_score", 0)),
            avg_comments=float(item.get("avg_comments", 0)),
            avg_upvote_ratio=float(item.get("avg_upvote_ratio", 0)),
            score_reference=score_reference,
            comments_reference=comments_reference,
        )

        result = dict(item)
        result["engagement_score"] = engagement

        results.append(result)

    return results
