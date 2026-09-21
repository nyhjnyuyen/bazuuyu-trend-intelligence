import json
from pathlib import Path

from support.bazuuyu.analyzer import analyze_trend
from support.config import OUTPUT_FILE


# Output file for Bazuuyu-specific analysis
BAZUUYU_OUTPUT_FILE = (
    Path(OUTPUT_FILE).parent / "bazuuyu_trends.json"
)


def run_analysis():
    """Analyze existing Trend-Finder results for Bazuuyu."""

    print("Loading Trend-Finder results...")

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    output = {
        "generated_at": data.get("generated_at"),
        "source_model": data.get("model"),
        "niches_processed": data.get("niches_processed", []),
        "results": {},
    }

    total_trends = 0

    for niche, weekly_results in data.get("results", {}).items():

        print(f"\nProcessing niche: {niche}")

        output["results"][niche] = []

        for week_result in weekly_results:

            analyzed_trends = []

            for trend in week_result.get("trends", []):

                total_trends += 1

                print(
                    f"  Analyzing: {trend.get('title', 'Unknown trend')}"
                )

                bazuuyu_analysis = analyze_trend(trend)

                combined = {
                    "original_trend": trend,
                    "bazuuyu_analysis": bazuuyu_analysis,
                }

                analyzed_trends.append(combined)

            output["results"][niche].append(
                {
                    "niche": week_result.get("niche"),
                    "week_number": week_result.get("week_number"),
                    "week_label": week_result.get("week_label"),
                    "post_count": week_result.get("post_count"),
                    "trends": analyzed_trends,
                }
            )

    with open(
        BAZUUYU_OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\n----------------------------------------")
    print("Bazuuyu analysis complete.")
    print(f"Trends analyzed: {total_trends}")
    print(f"Output: {BAZUUYU_OUTPUT_FILE}")
    print("----------------------------------------")


if __name__ == "__main__":
    run_analysis()
