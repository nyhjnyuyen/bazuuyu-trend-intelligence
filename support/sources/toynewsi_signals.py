import re


SIGNAL_PATTERNS = {
    "FUTURE_RELEASE": [
        r"\brelease\b",
        r"\breleases\b",
        r"\bcoming\b",
        r"\bcoming soon\b",
        r"\bhit theaters\b",
        r"\bpremiere\b",
        r"\bdebut\b",
    ],

    "PRODUCT_LAUNCH": [
        r"\bnew\b",
        r"\bannounces\b",
        r"\bannounced\b",
        r"\breveals\b",
        r"\brevealed\b",
        r"\blaunch\b",
        r"\blaunches\b",
    ],

    "PREORDER": [
        r"\bpre-order\b",
        r"\bpreorder\b",
        r"\bavailable for pre-order\b",
    ],

    "COLLABORATION": [
        r"\bcollaboration\b",
        r"\bcollab\b",
        r"\bpartners with\b",
        r"\bpartnership\b",
    ],

    "COLLECTIBLE": [
        r"\bcollectible\b",
        r"\bcollectibles\b",
        r"\bfigure\b",
        r"\bfigures\b",
        r"\baction figure\b",
        r"\bvinyl figure\b",
    ],

    "BUILDING_TOY": [
        r"\blego\b",
        r"\bbuilding set\b",
        r"\bbuilding sets\b",
    ],
        "ANNIVERSARY": [
        r"\banniversary\b",
        r"\b\d+(?:st|nd|rd|th)\s+celebration\b",
    ],

    "LIMITED_EXCLUSIVE": [
        r"\blimited edition\b",
        r"\bexclusive\b",
        r"\bsdcc exclusive\b",
    ],

    "BLIND_BOX": [
        r"\bblind box\b",
        r"\bblind boxes\b",
    ],
}


def detect_toynewsi_signals(article: dict) -> list[str]:
    """Detect signals in article metadata with product context."""

    text = " ".join(
        str(article.get(field) or "")
        for field in ("title", "description")
    ).lower()

    product_context = bool(re.search(
        r"\b(?:toys?|plush(?:ies)?|figures?|figurines?|"
        r"playsets?|dolls?|blind[\s-]+(?:boxes|box|bags|bag)|"
        r"building sets?|merchandise|vinyl figures?)\b",
        text,
    ))

    signals = []

    for signal_type, patterns in SIGNAL_PATTERNS.items():
        if not any(re.search(pattern, text) for pattern in patterns):
            continue

        # These terms also occur in movie/news announcements.
        if signal_type in {
            "PRODUCT_LAUNCH",
            "PREORDER",
            "LIMITED_EXCLUSIVE",
            "COLLABORATION",
        } and not product_context:
            continue

        signals.append(signal_type)

    if product_context and re.search(
        r"\b(?:in[\s-]+stock|available now|restock(?:ed|s)?|"
        r"available on|available at)\b",
        text,
    ):
        signals.append("PRODUCT_AVAILABILITY")

    return signals


def classify_toy_evidence(article: dict) -> dict:
    """Separate product evidence from media and fan creations.

    Categories describe article content, not verified sales,
    demand, or licensing rights.
    """

    title = str(article.get("title") or "").lower()
    text = " ".join(
        str(article.get(field) or "")
        for field in ("title", "description")
    ).lower()

    signals = detect_toynewsi_signals(article)

    product_context = bool(re.search(
        r"\b(?:toys?|plush(?:ies)?|figures?|figurines?|"
        r"playsets?|dolls?|blind[\s-]+(?:boxes|box|bags|bag)|"
        r"building sets?|merchandise|vinyl figures?)\b",
        text,
    ))

    fan_creation = bool(re.search(
        r"\b(?:custom of the week|fan[\s-]+made|"
        r"custom figures?|custom toys?|custom plush|"
        r"custom playsets?)\b",
        title,
    ))

    commercial_signals = {
        "PRODUCT_LAUNCH",
        "PREORDER",
        "PRODUCT_AVAILABILITY",
    }

    if fan_creation:
        category = "FAN_CREATION"
    elif product_context and commercial_signals.intersection(signals):
        category = "COMMERCIAL_PRODUCT"
    elif product_context:
        category = "PRODUCT_COVERAGE"
    else:
        category = "MEDIA_COVERAGE"

    matches = (article.get("ip_evidence") or {}).get("matches", [])

    return {
        "category": category,
        "movie_specific": "MOVIE_TITLE" in matches,
        "signals": signals,
    }