import json

from support.bazuuyu.bazuuyu_relevance import detect_behavior_signals


# Load the current weekly trend data
with open("support/output/weekly_trends.json", "r") as f:
    data = json.load(f)


# Collect all individual trends
all_trends = []

for niche, weekly_results in data.get("results", {}).items():
    for weekly_result in weekly_results:
        for trend in weekly_result.get("trends", []):
            all_trends.append(trend)


print(f"Total trends: {len(all_trends)}")
print()

matched_count = 0


for i, trend in enumerate(all_trends, 1):

    title = trend.get("title", "")
    description = trend.get("description", "")

    text = f"{title} {description}".lower()

    behavior_result = detect_behavior_signals(text)

    behavior_matches = behavior_result["behavior_matches"]
    context_matches = behavior_result["behavior_context_matches"]

    if behavior_matches:
        matched_count += 1

        print(f"{i}. {title}")
        print(f"   Behavior: {behavior_matches}")
        print(f"   Context:  {context_matches}")
        print()


print(f"Trends with behavior signals: {matched_count}/{len(all_trends)}")