def calculate_toynewsi_momentum(
    summary: dict,
) -> dict:
    """
    Calculate a preliminary ToyNewsI momentum score.

    This score measures activity inside ToyNewsI only.
    It is NOT the final Bazuuyu Future Trend Score.
    """

    article_count = max(
        summary.get("article_count", 0),
        1,
    )

    recent_30d = summary.get(
        "recent_30d_count",
        0,
    )

    recent_90d = summary.get(
        "recent_90d_count",
        0,
    )

    category_count = summary.get(
        "category_count",
        0,
    )

    signal_type_count = summary.get(
        "signal_type_count",
        0,
    )

    # Recency density
    density_30d = min(
        recent_30d / article_count,
        1.0,
    )

    density_90d = min(
        recent_90d / article_count,
        1.0,
    )

    # Diversity is capped so very large category
    # counts do not dominate the score.
    category_diversity = min(
        category_count / 6,
        1.0,
    )

    signal_diversity = min(
        signal_type_count / 6,
        1.0,
    )

    score = (
        density_30d * 40
        + density_90d * 25
        + category_diversity * 20
        + signal_diversity * 15
    )

    if score >= 80:
        momentum_level = "VERY_HIGH"
    elif score >= 60:
        momentum_level = "HIGH"
    elif score >= 40:
        momentum_level = "MEDIUM"
    else:
        momentum_level = "LOW"

    return {
        "momentum_score": round(score, 2),
        "momentum_level": momentum_level,
        "density_30d": round(
            density_30d,
            3,
        ),
        "density_90d": round(
            density_90d,
            3,
        ),
        "category_diversity": round(
            category_diversity,
            3,
        ),
        "signal_diversity": round(
            signal_diversity,
            3,
        ),
    }