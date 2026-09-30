from support.sources.entertainment import fetch_movie_details
from support.sources.entertainment_signals import detect_entertainment_signals
from support.sources.toynewsi import summarize_toynewsi_ip
from support.sources.web_news import summarize_google_news
from support.sources.search_trends import summarize_search_interest
from support.sources.ip_extractor import extract_ip_name

def build_future_trend_candidate(
    movie: dict,
    ip_query: str | None = None,
    toynewsi_limit: int = 10,
) -> dict:
    """
    Build a cross-source future trend candidate using
    TMDB entertainment data, ToyNewsI toy-industry data,
    and Google News activity.

    No final trend score is calculated here.
    This function preserves the evidence from each source.
    """

    details = fetch_movie_details(
        movie["tmdb_id"]
    )
    
    if not ip_query:
        ip_query = extract_ip_name(details)

    entertainment_signals = detect_entertainment_signals(
        details
    )

    toy_summary = summarize_toynewsi_ip(
        ip_query,
        limit=toynewsi_limit,
    )

    news_summary = summarize_google_news(
        ip_query,
        limit=20,
    )

    search_summary = summarize_search_interest(
        ip_query,
    )

    return {
        "ip": ip_query,

        "entertainment": {
            "source": "tmdb",
            "title": details.get("title"),
            "tmdb_id": details.get("tmdb_id"),
            "release_date": movie.get("release_date"),
            "tmdb_primary_release_date": details.get("release_date"),
            "status": details.get("status"),
            "collection": details.get("collection"),
            "genres": details.get("genres", []),
            "popularity": details.get("popularity", 0),
            "signals": entertainment_signals,
        },

        "toy_industry": {
            "source": "toynewsi",
            "article_count": toy_summary.get(
                "article_count",
                0,
            ),
            "latest_activity": toy_summary.get(
                "latest_activity"
            ),
            "recent_30d_count": toy_summary.get(
                "recent_30d_count",
                0,
            ),
            "recent_90d_count": toy_summary.get(
                "recent_90d_count",
                0,
            ),
            "categories": toy_summary.get(
                "categories",
                [],
            ),
            "signal_counts": toy_summary.get(
                "signal_counts",
                {},
            ),
        },

        "news": {
            "source": "google_news",
            "status": search_summary.get("status"),
            "article_count": news_summary.get(
                "article_count",
                0,
            ),
            "unique_story_count": news_summary.get(
                "unique_story_count",
                0,
            ),
            "duplicate_article_count": news_summary.get(
                "duplicate_article_count",
                0,
            ),
            "latest_activity": news_summary.get(
                "latest_activity"
            ),
            "earliest_activity": news_summary.get(
                "earliest_activity"
            ),
            "publisher_count": news_summary.get(
                "publisher_count",
                0,
            ),
            "publishers": news_summary.get(
                "publishers",
                [],
            ),
            "signal_counts": news_summary.get(
                "signal_counts",
                {},
            ),
        },

        "search": {
            "source": "google_trends",
            "status": search_summary.get("status"),
            "geo": search_summary.get("geo"),
            "timeframe": search_summary.get("timeframe"),
            "data_points": search_summary.get(
                "data_points",
                0,
            ),
            "average_interest": search_summary.get(
                "average_interest"
            ),
            "recent_average": search_summary.get(
                "recent_average"
            ),
            "previous_average": search_summary.get(
                "previous_average"
            ),
            "change_percent": search_summary.get(
                "change_percent"
            ),
            "direction": search_summary.get(
                "direction"
            ),
            "peak_interest": search_summary.get(
                "peak_interest"
            ),
            "peak_date": search_summary.get(
                "peak_date"
            ),
            "latest_complete_date": search_summary.get(
                "latest_complete_date"
            ),
        },

        "social": None,
    }