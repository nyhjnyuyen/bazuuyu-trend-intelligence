from support.sources.search_trends import compare_search_interest


def attach_cross_ip_search(
    candidates: list[dict],
    timeframe: str = "today 3-m",
    geo: str = "US",
) -> list[dict]:
    """
    Attach cross-IP Google Trends evidence to existing
    future-trend candidates.

    This does not calculate a final trend score.
    """

    if not candidates:
        return candidates

    queries = [
        candidate["ip"]
        for candidate in candidates
        if candidate.get("ip")
    ]

    # Google Trends supports at most five terms
    # in this comparison request.
    queries = queries[:5]

    comparison = compare_search_interest(
        queries=queries,
        timeframe=timeframe,
        geo=geo,
    )

    status = comparison.get("status")
    results = comparison.get("results", {})

    for candidate in candidates:

        ip = candidate.get("ip")

        candidate["search_comparison"] = {
            "source": "google_trends",
            "status": status,
            "geo": geo,
            "timeframe": timeframe,
            "average_interest": None,
            "recent_average": None,
            "peak_interest": None,
            "peak_date": None,
        }

        if ip not in results:
            continue

        result = results[ip]

        candidate["search_comparison"].update({
            "average_interest": result.get(
                "average_interest"
            ),
            "recent_average": result.get(
                "recent_average"
            ),
            "peak_interest": result.get(
                "peak_interest"
            ),
            "peak_date": result.get(
                "peak_date"
            ),
        })

    return candidates