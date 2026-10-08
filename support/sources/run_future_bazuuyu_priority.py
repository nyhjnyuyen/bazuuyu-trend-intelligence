import json

from datetime import datetime
from pathlib import Path

from support.sources.future_bazuuyu_fit import (
    assess_future_ip_fit,
    calculate_final_future_priority,
)

from support.sources.future_trend_history import (
    load_future_trend_history,
    calculate_all_ip_momentum,
)


SNAPSHOT_DIR = Path(
    "support/output/future_trends"
)

OUTPUT_DIR = Path(
    "support/output/future_bazuuyu"
)


def get_latest_snapshot():
    """
    Return the newest future-trend snapshot.
    """

    files = sorted(
        SNAPSHOT_DIR.glob(
            "future_trends_*.json"
        )
    )

    if not files:
        raise FileNotFoundError(
            "No future trend snapshots found."
        )

    return files[-1]


def build_future_bazuuyu_report():
    """
    Combine:

    - future trend momentum
    - action timing
    - Bazuuyu opportunity score
    - future IP/product fit
    - final Bazuuyu priority
    """

    snapshot_path = (
        get_latest_snapshot()
    )

    snapshot = json.loads(
        snapshot_path.read_text(
            encoding="utf-8"
        )
    )

    history = (
        load_future_trend_history()
    )

    momentum_results = (
        calculate_all_ip_momentum(
            history
        )
    )

    results = []

    for candidate in snapshot.get(
        "candidates",
        [],
    ):
        ip = candidate.get(
            "ip"
        )

        fit = assess_future_ip_fit(
            candidate
        )

        momentum = (
            momentum_results.get(
                ip,
                {},
            )
        )

        final = (
            calculate_final_future_priority(
                momentum.get(
                    "bazuuyu_opportunity_score"
                ),
                fit.get(
                    "future_ip_fit_score"
                ),
            )
        )

        opportunity_score = (
            momentum.get(
                "bazuuyu_opportunity_score"
            )
        )

        final_score = final.get(
            "final_future_score"
        )

        final_priority = final.get(
            "final_future_priority"
        )

        action = momentum.get(
            "recommended_action"
        )

        # Give first-observation IPs a useful
        # watchlist action instead of None.
        if (
            final_priority
            == "INSUFFICIENT_HISTORY"
        ):
            if (
                fit.get(
                    "future_ip_fit_score",
                    0,
                )
                >= 75
            ):
                action = (
                    "HIGH_FIT_WATCHLIST"
                )

            else:
                action = (
                    "COLLECT_MORE_DATA"
                )
        toy = candidate.get("toy_industry") or {}

        toy_evidence = {
            "validated_article_count": toy.get("validated_article_count"),
            "commercial_product_article_count": toy.get(
                "commercial_product_article_count"
            ),
            "movie_specific_commercial_article_count": toy.get(
                "movie_specific_commercial_article_count"
            ),
            "recent_30d_count": toy.get("recent_30d_count"),
            "latest_activity": toy.get("latest_activity"),
            "evidence_category_counts": toy.get("evidence_category_counts"),
        }

        toy = candidate.get("toy_industry") or {}
        result = {
            "ip": ip,
            "toy_evidence": {
                "validated_article_count": toy.get(
                    "validated_article_count"
                ),
                "commercial_product_article_count": toy.get(
                    "commercial_product_article_count"
                ),
                "movie_specific_commercial_article_count": toy.get(
                    "movie_specific_commercial_article_count"
                ),
                "recent_30d_count": toy.get("recent_30d_count"),
                "latest_activity": toy.get("latest_activity"),
                "evidence_category_counts": toy.get(
                    "evidence_category_counts"
                ),
            },
            "title": candidate.get(
                "title"
            ),
            "release_date": (
                candidate.get(
                    "release_date"
                )
            ),

            # Historical trend intelligence
            "momentum_score": (
                momentum.get(
                    "momentum_score"
                )
            ),
            "momentum_class": (
                momentum.get(
                    "momentum_class"
                )
            ),
            "signal_profile": (
                momentum.get(
                    "signal_profile"
                )
            ),

            # Timing
            "timing_score": (
                momentum.get(
                    "timing_score"
                )
            ),
            "action_timing": (
                momentum.get(
                    "action_timing"
                )
            ),
            "days_to_release": (
                momentum.get(
                    "days_to_release"
                )
            ),
            "days_since_toy_activity": (
                momentum.get(
                    "days_since_toy_activity"
                )
            ),

            # Trend opportunity
            "opportunity_score": (
                opportunity_score
            ),
            "opportunity_class": (
                momentum.get(
                    "bazuuyu_opportunity_class"
                )
            ),

            # Bazuuyu IP/product fit
            "fit_score": fit.get(
                "future_ip_fit_score"
            ),
            "fit_level": fit.get(
                "future_ip_fit_level"
            ),
            "fit_signals": fit.get(
                "future_ip_fit_signals"
            ),
            "character_count": fit.get(
                "character_count"
            ),
            "animal_matches": fit.get(
                "animal_matches"
            ),

            # Final ranking
            "final_score": final_score,
            "final_priority": (
                final_priority
            ),

            # Recommended business action
            "recommended_action": (
                action
            ),
            "recommendation_summary": (
                momentum.get(
                    "recommendation_summary"
                )
            ),
        }

        results.append(
            result
        )

    # Ranked items first.
    results.sort(
        key=lambda item: (
            item["final_score"]
            if item["final_score"]
            is not None
            else -1
        ),
        reverse=True,
    )

    return {
        "generated_at": (
            datetime.now().isoformat()
        ),
        "source_snapshot": (
            snapshot_path.name
        ),
        "candidate_count": len(
            results
        ),
        "results": results,
    }


def main():
    report = (
        build_future_bazuuyu_report()
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = (
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    output_path = (
        OUTPUT_DIR
        / (
            "future_bazuuyu_priority_"
            f"{timestamp}.json"
        )
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved: {output_path}"
    )

    print(
        "\nBAZUUYU FUTURE PRIORITIES"
    )

    print("=" * 80)

    for result in report["results"]:

        print(
            "\nIP:",
            result["ip"]
        )

        print(
            "FINAL:",
            result["final_score"],
            result["final_priority"],
        )

        print(
            "OPPORTUNITY:",
            result["opportunity_score"],
        )

        print(
            "FIT:",
            result["fit_score"],
            result["fit_level"],
        )

        print(
            "MOMENTUM:",
            result["momentum_score"],
            result["momentum_class"],
        )

        print(
            "PROFILE:",
            result["signal_profile"],
        )

        print(
            "TIMING:",
            result["timing_score"],
            result["action_timing"],
        )

        print(
            "ACTION:",
            result["recommended_action"],
        )


if __name__ == "__main__":
    main()