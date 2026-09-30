from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError


def fetch_search_interest(
    query: str,
    timeframe: str = "today 3-m",
    geo: str = "US",
) -> dict:
    """
    Fetch Google Trends search-interest history.

    Google Trends values are normalized from 0-100
    within the requested query and time window.

    This function returns raw evidence only.
    It does not calculate a trend score.
    """

    pytrends = TrendReq(
        hl="en-US",
        tz=420,
    )

    try:
        pytrends.build_payload(
            [query],
            timeframe=timeframe,
            geo=geo,
        )

        df = pytrends.interest_over_time()

    except TooManyRequestsError:
        print(
            f"Google Trends rate limit reached for: {query}"
        )
        return {
            "status": "RATE_LIMITED",
            "data": [],
        }

    if df.empty or query not in df.columns:
        return {
            "status": "NO_DATA",
            "data": [],
        }

    results = []

    for date, row in df.iterrows():
        results.append({
            "date": date.strftime("%Y-%m-%d"),
            "interest": int(row[query]),
            "is_partial": bool(
                row.get("isPartial", False)
            ),
        })

    return {
        "status": "OK",
        "data": results,
    }


def summarize_search_interest(
    query: str,
    timeframe: str = "today 3-m",
    geo: str = "US",
    recent_days: int = 14,
) -> dict:
    """
    Summarize Google Trends search interest.

    Compares the most recent complete period with the
    immediately preceding period of equal length.

    No final cross-source trend score is calculated here.
    """

    result = fetch_search_interest(
        query=query,
        timeframe=timeframe,
        geo=geo,
    )

    status = result["status"]
    data = result["data"]

    # Exclude partial observations.
    complete_data = [
        point
        for point in data
        if not point.get("is_partial", False)
    ]

    if not complete_data:
        return {
            "status": status,
            "query": query,
            "geo": geo,
            "timeframe": timeframe,
            "data_points": 0,
            "average_interest": None,
            "recent_average": None,
            "previous_average": None,
            "change_percent": None,
            "direction": "UNKNOWN",
            "peak_interest": None,
            "peak_date": None,
            "latest_complete_date": None,
        }

    interests = [
        point["interest"]
        for point in complete_data
    ]

    peak_point = max(
        complete_data,
        key=lambda point: point["interest"],
    )

    recent = complete_data[-recent_days:]

    previous = complete_data[
        -(recent_days * 2):-recent_days
    ]

    recent_average = (
        sum(point["interest"] for point in recent)
        / len(recent)
    )

    previous_average = None
    change_percent = None
    direction = "UNKNOWN"

    if previous:
        previous_average = (
            sum(point["interest"] for point in previous)
            / len(previous)
        )

        if previous_average > 0:
            change_percent = (
                (recent_average - previous_average)
                / previous_average
            ) * 100

            if change_percent >= 10:
                direction = "RISING"
            elif change_percent <= -10:
                direction = "FALLING"
            else:
                direction = "STABLE"

    return {
        "status": status,
        "query": query,
        "geo": geo,
        "timeframe": timeframe,
        "data_points": len(complete_data),
        "average_interest": round(
            sum(interests) / len(interests),
            2,
        ),
        "recent_average": round(
            recent_average,
            2,
        ),
        "previous_average": (
            round(previous_average, 2)
            if previous_average is not None
            else None
        ),
        "change_percent": (
            round(change_percent, 2)
            if change_percent is not None
            else None
        ),
        "direction": direction,
        "peak_interest": peak_point["interest"],
        "peak_date": peak_point["date"],
        "latest_complete_date": complete_data[-1]["date"],
    }
def compare_search_interest(
    queries: list[str],
    timeframe: str = "today 3-m",
    geo: str = "US",
    recent_days: int = 14,
) -> dict:
    """
    Compare multiple search terms on the same Google Trends scale.

    This allows relative search interest to be compared across IPs.
    Maximum 5 queries should be supplied per request.
    """

    if not queries:
        return {
            "status": "NO_DATA",
            "queries": [],
            "results": {},
        }

    pytrends = TrendReq(
        hl="en-US",
        tz=420,
    )

    try:
        pytrends.build_payload(
            queries,
            timeframe=timeframe,
            geo=geo,
        )

        df = pytrends.interest_over_time()

    except TooManyRequestsError:
        print(
            "Google Trends rate limit reached "
            "during cross-IP comparison."
        )

        return {
            "status": "RATE_LIMITED",
            "queries": queries,
            "results": {},
        }

    if df.empty:
        return {
            "status": "NO_DATA",
            "queries": queries,
            "results": {},
        }

    if "isPartial" in df.columns:
        df = df[df["isPartial"] == False]

    if df.empty:
        return {
            "status": "NO_DATA",
            "queries": queries,
            "results": {},
        }

    results = {}

    for query in queries:

        if query not in df.columns:
            continue

        series = df[query]

        recent = series.tail(recent_days)

        results[query] = {
            "average_interest": round(
                float(series.mean()),
                2,
            ),
            "recent_average": round(
                float(recent.mean()),
                2,
            ),
            "peak_interest": int(series.max()),
            "peak_date": series.idxmax().strftime(
                "%Y-%m-%d"
            ),
        }

    return {
        "status": "OK",
        "geo": geo,
        "timeframe": timeframe,
        "queries": queries,
        "results": results,
    }