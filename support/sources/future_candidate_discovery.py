from support.sources.entertainment import (
    fetch_popular_future_movies,
    fetch_movie_details,
)
from support.sources.entertainment_signals import (
    detect_entertainment_signals,
)
from support.sources.entertainment_filter import (
    classify_entertainment_candidate,
)
from support.sources.ip_extractor import (
    extract_ip_name,
    build_ip_search_query,
)


def discover_future_candidates(
    region: str = "US",
    days_ahead: int = 365,
    pages: int = 10,
    limit: int = 30,
) -> list[dict]:
    """
    Discover future entertainment candidates from TMDB.

    This stage performs entertainment discovery and routing only.
    It does not query ToyNewsI, Google News, or Google Trends.
    """

    movies = fetch_popular_future_movies(
        region=region,
        days_ahead=days_ahead,
        pages=pages,
        limit=limit,
    )

    candidates = []

    for movie in movies:

        details = fetch_movie_details(
            movie["tmdb_id"]
        )

        # For now, require TMDB franchise/collection evidence.
        if not details.get("collection"):
            continue

        ip_name = extract_ip_name(
            details
        )

        search_query = build_ip_search_query(
            details,
            ip_name,
        )

        signals = detect_entertainment_signals(
            details
        )

        classification = (
            classify_entertainment_candidate(
                details,
                signals,
            )
        )

        candidates.append({
            "ip": ip_name,
            "search_query": search_query,
            "tmdb_id": movie["tmdb_id"],
            "title": details["title"],
            "release_date": movie.get(
                "release_date"
            ),
            "tmdb_primary_release_date":
                details.get("release_date"),
            "popularity": details.get(
                "popularity"
            ),
            "genres": details.get(
                "genres",
                [],
            ),
            "entertainment_signals":
                signals,
            "routing": classification,
            "movie_details": details,
        })

    return candidates