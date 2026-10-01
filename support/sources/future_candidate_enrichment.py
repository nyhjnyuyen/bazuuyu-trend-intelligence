from support.sources.toy_ip_evidence import (
    summarize_validated_toy_ip,
)
from support.sources.web_news import (
    summarize_google_news,
)
from support.sources.search_trends import (
    summarize_search_interest,
)


def enrich_with_toy_evidence(
    candidates: list[dict],
    toynewsi_limit: int = 10,
) -> list[dict]:
    """
    Attach validated ToyNewsI evidence to candidates
    approved for deeper analysis.

    This stage does not calculate a final trend score.
    """

    enriched = []

    for candidate in candidates:

        # Reuse evidence already collected during the
        # CHECK routing stage when available.
        existing_validation = candidate.get(
            "toy_validation"
        )

        if existing_validation:
            toy_evidence = existing_validation[
                "evidence"
            ]

        else:
            toy_evidence = (
                summarize_validated_toy_ip(
                    movie=candidate["movie_details"],
                    ip_name=candidate["ip"],
                    search_query=candidate[
                        "search_query"
                    ],
                    limit=toynewsi_limit,
                )
            )

        enriched.append({
            **candidate,
            "toy_industry": toy_evidence,
        })

    return enriched

def enrich_with_news(
    candidates: list[dict],
    news_limit: int = 20,
) -> list[dict]:
    """
    Attach Google News evidence to approved
    future-trend candidates.

    This stage does not calculate a final trend score.
    """

    enriched = []

    for candidate in candidates:

        base_query = candidate.get(
            "search_query"
        ) or candidate["ip"]

        # Add entertainment context to reduce ambiguous
        # Google News matches for franchise names such as
        # "Ice Age" or "Dragon".
        query = f'"{base_query}" movie'

        news_summary = summarize_google_news(
            query,
            limit=news_limit,
        )

        enriched.append({
            **candidate,
            "news": news_summary,
        })

    return enriched
def enrich_with_search_momentum(
    candidates: list[dict],
    timeframe: str = "today 3-m",
    geo: str = "US",
) -> list[dict]:
    """
    Attach individual Google Trends momentum evidence.

    Each IP is queried independently, so these values
    measure within-IP momentum over time.

    They must not be used to compare absolute search
    demand between different IPs.
    """

    enriched = []

    for candidate in candidates:

        query = candidate.get(
            "ip"
        ) or candidate.get(
            "search_query"
        )

        search_summary = summarize_search_interest(
            query=query,
            timeframe=timeframe,
            geo=geo,
        )
        
        search_summary["query"] = query

        enriched.append({
            **candidate,
            "search": search_summary,
        })

    return enriched

def enrich_future_candidates(
    candidates: list[dict],
    toynewsi_limit: int = 10,
    news_limit: int = 20,
    search_timeframe: str = "today 3-m",
    search_geo: str = "US",
) -> list[dict]:
    """
    Run the current future-trend evidence enrichment
    pipeline for approved candidates.

    Stages:
        1. Validated ToyNewsI evidence
        2. Google News evidence
        3. Individual Google Trends momentum

    This function does not calculate a final trend score.
    """

    enriched = enrich_with_toy_evidence(
        candidates,
        toynewsi_limit=toynewsi_limit,
    )

    enriched = enrich_with_news(
        enriched,
        news_limit=news_limit,
    )

    enriched = enrich_with_search_momentum(
        enriched,
        timeframe=search_timeframe,
        geo=search_geo,
    )

    return enriched
