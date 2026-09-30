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
    """
    Detect commercial and future-trend signals
    from a ToyNewsI article.
    """

    text = " ".join(
        [
            article.get("title", ""),
            article.get("description", ""),
            article.get("category", ""),
        ]
    ).lower()

    signals = []

    for signal_type, patterns in SIGNAL_PATTERNS.items():
        if any(
            re.search(pattern, text)
            for pattern in patterns
        ):
            signals.append(signal_type)

    return signals