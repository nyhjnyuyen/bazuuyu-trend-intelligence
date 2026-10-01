import json
from pathlib import Path


DEFAULT_SNAPSHOT_DIR = Path(
    "support/output/future_trends"
)


def load_future_trend_history(
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> dict[str, list[dict]]:
    """
    Load all saved future-trend snapshots and group
    candidate observations by IP.

    This function performs no external API calls and
    does not calculate a trend score.
    """

    history = {}

    files = sorted(
        snapshot_dir.glob(
            "future_trends_*.json"
        )
    )

    for path in files:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            snapshot = json.load(file)

        generated_at = snapshot.get(
            "generated_at"
        )

        for candidate in snapshot.get(
            "candidates",
            [],
        ):

            ip = candidate.get("ip")

            if not ip:
                continue

            observation = {
                "generated_at": generated_at,
                "release_date": candidate.get(
                    "release_date"
                ),
                "movie": candidate.get(
                    "title"
                ),
                "routing_priority": candidate.get(
                    "routing",
                    {},
                ).get(
                    "priority"
                ),
                "toy_article_count": (
                    candidate.get(
                        "toy_industry",
                        {},
                    ).get(
                        "validated_article_count"
                    )
                ),
                "toy_latest_activity": (
                    candidate.get(
                        "toy_industry",
                        {},
                    ).get(
                        "latest_activity"
                    )
                ),
                "news_story_count": (
                    candidate.get(
                        "news",
                        {},
                    ).get(
                        "unique_story_count"
                    )
                ),
                "news_publisher_count": (
                    candidate.get(
                        "news",
                        {},
                    ).get(
                        "publisher_count"
                    )
                ),
                "news_concentration": (
                    candidate.get(
                        "news",
                        {},
                    ).get(
                        "story_concentration"
                    )
                ),
                "search_status": (
                    candidate.get(
                        "search",
                        {},
                    ).get(
                        "status"
                    )
                ),
                "search_direction": (
                    candidate.get(
                        "search",
                        {},
                    ).get(
                        "direction"
                    )
                ),
                "search_change_percent": (
                    candidate.get(
                        "search",
                        {},
                    ).get(
                        "change_percent"
                    )
                ),
            }

            history.setdefault(
                ip,
                [],
            ).append(
                observation
            )

    return history