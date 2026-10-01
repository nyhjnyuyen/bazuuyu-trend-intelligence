from support.sources.future_candidate_discovery import (
    discover_future_candidates,
)
from support.sources.future_candidate_routing import (
    route_future_candidates,
    get_kept_candidates,
)
from support.sources.future_candidate_enrichment import (
    enrich_with_toy_evidence,
    enrich_with_news,
)
import json
from datetime import datetime
from pathlib import Path

def main():

    candidates = discover_future_candidates(
        region="US",
        days_ahead=365,
        pages=10,
        limit=30,
    )

    routed = route_future_candidates(
        candidates,
        toynewsi_limit=10,
    )

    kept = get_kept_candidates(
        routed
    )

    print(
        f"Discovered: {len(candidates)}"
    )
    print(
        f"Kept: {len(kept)}"
    )

    # Enrich with ToyNewsI evidence.
    enriched = enrich_with_toy_evidence(
        kept,
        toynewsi_limit=10,
    )

    # Enrich with Google News evidence.
    enriched = enrich_with_news(
        enriched,
        news_limit=20,
    )

    output_dir = Path("support/output/future_trends")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        output_dir
        / f"future_trends_{run_timestamp}.json"
    )

    output_data = {
        "generated_at": datetime.now().isoformat(),
        "discovered_count": len(candidates),
        "kept_count": len(kept),
        "candidates": enriched,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output_data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved: {output_path}"
    )

    print("\nFUTURE TREND CANDIDATES")
    print("=" * 80)

    for candidate in enriched:

        toy = candidate.get(
            "toy_industry",
            {},
        )

        news = candidate.get(
            "news",
            {},
        )

        search = candidate.get(
            "search",
            {},
        )

        print(
            "\nIP:",
            candidate["ip"],
        )

        print(
            "MOVIE:",
            candidate["title"],
        )

        print(
            "RELEASE:",
            candidate["release_date"],
        )

        print(
            "TOY ARTICLES:",
            toy.get(
                "validated_article_count"
            ),
        )

        print(
            "TOY LATEST:",
            toy.get(
                "latest_activity"
            ),
        )

        print(
            "NEWS STORIES:",
            news.get(
                "unique_story_count"
            ),
        )

        print(
            "NEWS PUBLISHERS:",
            news.get(
                "publisher_count"
            ),
        )

        print(
            "NEWS CONCENTRATION:",
            news.get(
                "story_concentration"
            ),
        )

        print(
            "SEARCH STATUS:",
            search.get(
                "status"
            ),
        )

        print(
            "SEARCH DIRECTION:",
            search.get(
                "direction"
            ),
        )

        print(
            "SEARCH CHANGE:",
            search.get(
                "change_percent"
            ),
        )


if __name__ == "__main__":
    main()