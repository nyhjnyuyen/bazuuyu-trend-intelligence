from support.sources.toy_ip_evidence import (
    summarize_validated_toy_ip,
)
from support.sources.toy_validation import (
    validate_toy_candidate,
)


def route_future_candidates(
    candidates: list[dict],
    toynewsi_limit: int = 10,
) -> list[dict]:
    """
    Route discovered entertainment candidates.

    PRIORITY and POSSIBLE candidates move forward directly.

    CHECK candidates must pass validated ToyNewsI commercial
    evidence before moving forward.

    LOW_FIT candidates are held.

    This is a routing stage only.
    It does not calculate a final trend score.
    """

    results = []

    for candidate in candidates:

        priority = candidate["routing"]["priority"]

        routed = {
            **candidate,
            "toy_validation": None,
            "decision": None,
        }

        if priority in {
            "PRIORITY",
            "POSSIBLE",
        }:
            routed["decision"] = "KEEP"
            results.append(routed)
            continue

        if priority == "CHECK":

            toy_evidence = summarize_validated_toy_ip(
                movie=candidate["movie_details"],
                ip_name=candidate["ip"],
                search_query=candidate["search_query"],
                limit=toynewsi_limit,
            )

            validation = validate_toy_candidate(
                toy_evidence
            )

            routed["toy_validation"] = {
                "evidence": toy_evidence,
                "validation": validation,
            }

            routed["decision"] = (
                "KEEP"
                if validation["passed"]
                else "HOLD"
            )

            results.append(routed)
            continue

        routed["decision"] = "HOLD"
        results.append(routed)

    return results

def get_kept_candidates(
    routed_candidates: list[dict],
) -> list[dict]:
    """
    Return only candidates approved for deeper
    cross-source analysis.
    """

    return [
        candidate
        for candidate in routed_candidates
        if candidate.get("decision") == "KEEP"
    ]