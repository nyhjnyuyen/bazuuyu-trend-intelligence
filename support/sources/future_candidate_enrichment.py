from support.sources.toy_ip_evidence import (
    summarize_validated_toy_ip,
)
from support.sources.web_news import (
    summarize_google_news,
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

        query = candidate.get(
            "search_query"
        ) or candidate["ip"]

        news_summary = summarize_google_news(
            query,
            limit=news_limit,
        )

        enriched.append({
            **candidate,
            "news": news_summary,
        })

    return enriched
