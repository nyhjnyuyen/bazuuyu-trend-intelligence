def calculate_final_future_priority(
    opportunity_score,
    fit_score,
):
    """
    Combine future opportunity strength with
    Bazuuyu-specific IP/product fit.
    """

    if opportunity_score is None:
        return {
            "final_future_score": None,
            "final_future_priority": (
                "INSUFFICIENT_HISTORY"
            ),
        }

    final_score = round(
        opportunity_score * 0.60
        + fit_score * 0.40,
        2,
    )

    if final_score >= 80:
        priority = "TOP_PRIORITY"

    elif final_score >= 65:
        priority = "HIGH_PRIORITY"

    elif final_score >= 50:
        priority = "WATCH"

    elif final_score >= 35:
        priority = "LOW_PRIORITY"

    else:
        priority = "IGNORE_FOR_NOW"

    return {
        "final_future_score": final_score,
        "final_future_priority": priority,
    }

def _normalize_list(value):
    if isinstance(value, list):
        return [
            str(item).lower()
            for item in value
            if item
        ]

    if value:
        return [str(value).lower()]

    return []


def assess_future_ip_fit(
    candidate: dict,
) -> dict:
    """
    Evaluate whether a future entertainment IP is structurally
    suitable for Bazuuyu-style plush, collectibles, characters,
    and social content.

    This complements the general Bazuuyu relevance engine.
    """

    details = candidate.get(
        "movie_details",
        {},
    )

    title = (
        candidate.get("title")
        or ""
    ).lower()

    ip = (
        candidate.get("ip")
        or ""
    ).lower()

    overview = (
        details.get("overview")
        or ""
    ).lower()

    genres = _normalize_list(
        details.get("genres")
    )

    keywords = _normalize_list(
        details.get("keywords")
    )

    characters = _normalize_list(
        details.get("characters")
    )

    collection = (
        details.get("collection")
        or ""
    ).lower()

    entertainment_signals = (
        _normalize_list(
            candidate.get(
                "entertainment_signals"
            )
        )
    )

    text = " ".join(
        [
            title,
            ip,
            overview,
            " ".join(genres),
            " ".join(keywords),
            " ".join(characters),
            collection,
            " ".join(
                entertainment_signals
            ),
        ]
    )

    score = 0

    signals = []

    # ─────────────────────────────
    # CHARACTER STRENGTH
    # ─────────────────────────────

    character_count = len(
        characters
    )

    if character_count >= 5:
        score += 20
        signals.append(
            "STRONG_CHARACTER_CAST"
        )

    elif character_count >= 2:
        score += 12
        signals.append(
            "MULTIPLE_CHARACTERS"
        )

    elif character_count == 1:
        score += 6
        signals.append(
            "CHARACTER_PRESENT"
        )

    # ─────────────────────────────
    # FRANCHISE / COLLECTION
    # ─────────────────────────────

    if collection:
        score += 15
        signals.append(
            "FRANCHISE_COLLECTION"
        )

    if any(
        signal in {
            "franchise_ip",
            "comic_ip",
        }
        for signal in entertainment_signals
    ):
        score += 12
        signals.append(
            "ESTABLISHED_IP"
        )

    # ─────────────────────────────
    # ANIMATION / FAMILY
    # ─────────────────────────────

    animation_terms = {
        "animation",
        "animated",
        "cartoon",
    }

    if (
        any(
            term in text
            for term in animation_terms
        )
    ):
        score += 20
        signals.append(
            "ANIMATION"
        )

    family_terms = {
        "family",
        "children",
        "kids",
        "child",
    }

    if any(
        term in text
        for term in family_terms
    ):
        score += 10
        signals.append(
            "FAMILY_AUDIENCE"
        )

    # ─────────────────────────────
    # ANIMAL / CREATURE POTENTIAL
    # ─────────────────────────────

    animal_terms = {
        "animal",
        "animals",
        "hedgehog",
        "donkey",
        "dragon",
        "cat",
        "dog",
        "bear",
        "rabbit",
        "fox",
        "mouse",
        "mammoth",
        "sloth",
        "squirrel",
        "creature",
        "monster",
    }

    animal_matches = sorted(
        {
            term
            for term in animal_terms
            if term in text
        }
    )

    if animal_matches:
        score += min(
            25,
            10
            + len(animal_matches) * 3,
        )

        signals.append(
            "ANIMAL_OR_CREATURE"
        )

    # ─────────────────────────────
    # GAME / COLLECTIBLE CULTURE
    # ─────────────────────────────

    game_terms = {
        "video game",
        "gaming",
        "game franchise",
        "sega",
    }

    if any(
        term in text
        for term in game_terms
    ):
        score += 15
        signals.append(
            "GAME_IP"
        )

    collectible_terms = {
        "collectible",
        "collectibles",
        "figure",
        "figurine",
        "toy",
        "merchandise",
    }

    if any(
        term in text
        for term in collectible_terms
    ):
        score += 15
        signals.append(
            "MERCHANDISE_SIGNAL"
        )

    # ─────────────────────────────
    # LESS NATURAL PLUSH CATEGORIES
    # ─────────────────────────────

    harder_fit_terms = {
        "war",
        "political",
        "crime",
        "biography",
        "historical drama",
    }

    hard_matches = [
        term
        for term in harder_fit_terms
        if term in text
    ]

    if hard_matches:
        score -= (
            len(hard_matches)
            * 8
        )

        signals.append(
            "HARDER_PLUSH_FIT"
        )

    score = round(
        max(
            0,
            min(100, score),
        ),
        2,
    )

    if score >= 75:
        fit_level = "VERY_HIGH"

    elif score >= 55:
        fit_level = "HIGH"

    elif score >= 35:
        fit_level = "MEDIUM"

    elif score >= 20:
        fit_level = "LOW"

    else:
        fit_level = "VERY_LOW"

    return {
        "future_ip_fit_score": score,
        "future_ip_fit_level": (
            fit_level
        ),
        "future_ip_fit_signals": (
            signals
        ),
        "character_count": (
            character_count
        ),
        "animal_matches": (
            animal_matches
        ),
    }