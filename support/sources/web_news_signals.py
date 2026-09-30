import re


WEB_NEWS_SIGNAL_PATTERNS = {
    "ANNIVERSARY": [
        r"\banniversary\b",
        r"\b\d+(?:st|nd|rd|th)\b",
    ],

    "CROSSOVER": [
        r"\bcrossover\b",
        r"\bcross-over\b",
        r"\bx\s+[a-z0-9]",
    ],

    "COLLABORATION": [
        r"\bcollaboration\b",
        r"\bcollab\b",
        r"\bpartners with\b",
        r"\bpartnership\b",
        r"\bteams up with\b",
    ],

    "TRAILER": [
        r"\btrailer\b",
        r"\bteaser\b",
        r"\bfirst look\b",
    ],

    "MOVIE_RELEASE": [
        r"\brelease date\b",
        r"\bhits theaters\b",
        r"\bin theaters\b",
        r"\bpremiere\b",
    ],

    "MERCHANDISE": [
        r"\bmerchandise\b",
        r"\bmerch\b",
        r"\btoy\b",
        r"\btoys\b",
        r"\bfigure\b",
        r"\bfigures\b",
        r"\bcollectible\b",
        r"\bcollectibles\b",
        r"\bplush\b",
    ],

    "LICENSING": [
        r"\blicensing\b",
        r"\blicensed\b",
        r"\blicense agreement\b",
    ],

    "CHARACTER_ACTIVITY": [
        r"\bcharacter\b",
        r"\bmascot\b",
    ],
}


def detect_web_news_signals(article: dict) -> list[str]:
    """
    Detect future-trend signals from a normalized
    web/news article.
    """

    text = " ".join([
        article.get("title", ""),
        article.get("publisher", ""),
    ]).lower()

    signals = []

    for signal_name, patterns in WEB_NEWS_SIGNAL_PATTERNS.items():

        for pattern in patterns:

            if re.search(pattern, text):
                signals.append(signal_name)
                break

    return signals