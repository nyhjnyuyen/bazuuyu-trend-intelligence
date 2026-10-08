from support.sources.toynewsi import summarize_toynewsi_ip
from support.sources.ip_evidence import validate_article_ip
from collections import Counter
from datetime import datetime, timedelta, date

from support.sources.toynewsi_signals import (
    detect_toynewsi_signals,
    classify_toy_evidence,
)

def summarize_validated_toy_ip(
    movie: dict,
    ip_name: str,
    search_query: str,
    limit: int = 10,
) -> dict:
    """
    Retrieve ToyNewsI evidence and keep only articles that
    can be connected to the intended entertainment IP.

    This does not calculate opportunity or trend scores.
    """

    raw_summary = summarize_toynewsi_ip(
        search_query,
        limit=limit,
    )

    validated_articles = []
    rejected_articles = []

    for article in raw_summary.get(
        "articles",
        []
    ):
        evidence = validate_article_ip(
            article,
            movie,
            ip_name,
        )

        item = {
            **article,
            "ip_evidence": evidence,
        }

        item["toy_evidence"] = classify_toy_evidence(item)

        if evidence["matched"]:
            validated_articles.append(item)
        else:
            rejected_articles.append(item)

    evidence_strength_counts = Counter(
        article["ip_evidence"].get(
            "evidence_strength",
            "NONE",
        )
        for article in validated_articles
    )

    dated_articles = []

    for article in validated_articles:
        published_date = article.get(
            "published_date"
        )

        if not published_date:
            continue

        try:
            parsed_date = datetime.fromisoformat(
                published_date
            )
        except ValueError:
            continue

        dated_articles.append(
            (article, parsed_date)
        )

    # Calculate recency only after all dated
    # validated articles have been collected.
    if dated_articles:
        latest_date = max(
            date_value
            for _, date_value in dated_articles
        )

        recent_30d_count = sum(
            1
            for _, date_value in dated_articles
            if date.today() - timedelta(days=30) <= date_value.date() <= date.today()
        )

        recent_90d_count = sum(
            1
            for _, date_value in dated_articles
            if date.today() - timedelta(days=90) <= date_value.date() <= date.today()
        )

        days_since_latest_activity = (
            date.today()
            - latest_date.date()
        ).days

    else:
        latest_date = None
        recent_30d_count = 0
        recent_90d_count = 0
        days_since_latest_activity = None
        
    validated_signal_counts = Counter()
    strong_signal_counts = Counter()
    weak_signal_counts = Counter()

    for article in validated_articles:

        signals = detect_toynewsi_signals(
            article
        )

        validated_signal_counts.update(
            signals
        )

        strength = article[
            "ip_evidence"
        ].get(
            "evidence_strength",
            "NONE",
        )

        if strength == "STRONG":
            strong_signal_counts.update(
                signals
            )

        elif strength == "WEAK":
            weak_signal_counts.update(
                signals
            )
    return {
        "ip": ip_name,
        "search_query": search_query,
        "raw_article_count": raw_summary.get(
            "article_count",
            0,
        ),
        "article_count": len(
            validated_articles
        ),
        "validated_article_count": len(
            validated_articles
        ),
        "rejected_article_count": len(
            rejected_articles
        ),
        "evidence_strength_counts": dict(
            evidence_strength_counts
        ),
        "evidence_category_counts": dict(Counter(
            article["toy_evidence"]["category"]
            for article in validated_articles
        )),
        "commercial_product_article_count": sum(
            article["toy_evidence"]["category"] == "COMMERCIAL_PRODUCT"
            for article in validated_articles
        ),
        "movie_specific_commercial_article_count": sum(
            article["toy_evidence"]["category"] == "COMMERCIAL_PRODUCT"
            and article["toy_evidence"]["movie_specific"]
            for article in validated_articles
        ),
        "signal_counts": dict(
            validated_signal_counts
        ),
        "strong_signal_counts": dict(
            strong_signal_counts
        ),

        "weak_signal_counts": dict(
            weak_signal_counts
        ),
        "signal_type_count": len(
            validated_signal_counts
        ),
        "latest_activity": (
            latest_date.date().isoformat()
            if latest_date
            else None
        ),
        "days_since_latest_activity": (
            days_since_latest_activity
        ),

        "recent_30d_count": (
            recent_30d_count
        ),

        "recent_90d_count": (
            recent_90d_count
        ),
        "validated_articles": validated_articles,
        "rejected_articles": rejected_articles,
    }