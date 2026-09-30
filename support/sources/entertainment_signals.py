import re
from unittest import signals


ENTERTAINMENT_SIGNAL_PATTERNS = {
    "VIDEO_GAME_IP": [
        r"\bbased on video game\b",
        r"\bvideo game\b",
    ],

    "COMIC_IP": [
        r"\bbased on comic\b",
        r"\bcomic book\b",
        r"\bsuperhero\b",
    ],

    "BOOK_IP": [
        r"\bbased on novel\b",
        r"\bbased on book\b",
        r"\byoung adult novel\b",
    ],

}


def detect_entertainment_signals(movie: dict) -> list[str]:
    """
    Detect merchandising/IP-related signals from
    enriched TMDB movie metadata.
    """

    searchable_parts = [
        movie.get("title", ""),
        movie.get("tagline", ""),
        movie.get("overview", ""),
        " ".join(movie.get("genres", [])),
        " ".join(movie.get("keywords", [])),
        " ".join(movie.get("production_companies", [])),
    ]

    searchable_text = " ".join(searchable_parts).lower()

    signals = []

    genres = set(movie.get("genres", []))

    if "Animation" in genres:
        signals.append("ANIMATION")

    if "Family" in genres:
        signals.append("FAMILY")

    if "Fantasy" in genres:
        signals.append("FANTASY")

    for signal_name, patterns in ENTERTAINMENT_SIGNAL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, searchable_text):
                signals.append(signal_name)
                break

    if movie.get("collection"):
        signals.append("FRANCHISE_IP")

    return signals