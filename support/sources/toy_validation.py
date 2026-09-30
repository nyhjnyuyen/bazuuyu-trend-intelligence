def validate_toy_candidate(
    toy_summary: dict,
) -> dict:
    """
    Decide whether a CHECK entertainment candidate has enough
    toy-industry evidence to justify deeper analysis.

    This is a routing decision only.
    It is not a final opportunity score.
    """

    article_count = toy_summary.get(
        "article_count",
        0,
    )

    recent_90d = toy_summary.get(
        "recent_90d_count",
        0,
    )

    signal_counts = toy_summary.get(
        "signal_counts",
        {},
    )

    commercial_signals = {
        "PRODUCT_LAUNCH",
        "COLLECTIBLE",
        "PREORDER",
        "COLLABORATION",
        "LIMITED_EXCLUSIVE",
        "BLIND_BOX",
        "BUILDING_TOY",
    }

    matched_signals = {
        signal: count
        for signal, count in signal_counts.items()
        if signal in commercial_signals
        and count > 0
    }

    has_commercial_signal = bool(
        matched_signals
    )

    # Conservative first-pass rule:
    # require actual ToyNewsI coverage plus commercial evidence.
    passed = (
        article_count > 0
        and has_commercial_signal
    )

    return {
        "passed": passed,
        "article_count": article_count,
        "recent_90d_count": recent_90d,
        "commercial_signals": matched_signals,
    }