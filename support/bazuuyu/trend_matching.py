import re
from difflib import SequenceMatcher


def normalize_text(text: str) -> str:
    """Normalize text for basic similarity comparison."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def trend_similarity(trend_a: dict, trend_b: dict) -> float:
    """
    Compare two trends using their title and description.

    Returns a score from 0 to 100.
    """

    text_a = normalize_text(
        f"{trend_a.get('title', '')} {trend_a.get('description', '')}"
    )

    text_b = normalize_text(
        f"{trend_b.get('title', '')} {trend_b.get('description', '')}"
    )

    if not text_a or not text_b:
        return 0.0

    similarity = SequenceMatcher(
        None,
        text_a,
        text_b,
    ).ratio()

    return round(similarity * 100, 2)


def find_best_match(
    trend: dict,
    previous_trends: list[dict],
    threshold: float = 55.0,
) -> tuple[dict | None, float]:
    """
    Find the most similar previous trend.

    Returns:
        (matched_trend, similarity_score)
    """

    best_match = None
    best_score = 0.0

    for previous in previous_trends:
        score = trend_similarity(
            trend,
            previous,
        )

        if score > best_score:
            best_score = score
            best_match = previous

    if best_score < threshold:
        return None, best_score

    return best_match, best_score
