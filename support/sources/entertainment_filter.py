def classify_entertainment_candidate(
    movie: dict,
    signals: list[str],
) -> dict:
    """
    Classify whether an entertainment candidate deserves
    deeper cross-source investigation for Bazuuyu.

    This is a pre-filter only.
    It is NOT a final trend or opportunity score.
    """

    genres = set(movie.get("genres", []))
    signals = set(signals)

    strong_fit_signals = {
        "ANIMATION",
        "FAMILY",
        "FANTASY",
        "VIDEO_GAME_IP",
        "COMIC_IP",
    }

    supporting_signals = {
        "BOOK_IP",
        "FRANCHISE_IP",
    }

    strong_matches = sorted(
        signals & strong_fit_signals
    )

    supporting_matches = sorted(
        signals & supporting_signals
    )

    # Strong character/toy-friendly entertainment evidence.
    if strong_matches:
        priority = "PRIORITY"

    elif "BOOK_IP" in signals:
        priority = "POSSIBLE"

    elif "FRANCHISE_IP" in signals:
        priority = "CHECK"

    else:
        priority = "LOW_FIT"

    return {
        "priority": priority,
        "strong_matches": strong_matches,
        "supporting_matches": supporting_matches,
        "genres": sorted(genres),
    }