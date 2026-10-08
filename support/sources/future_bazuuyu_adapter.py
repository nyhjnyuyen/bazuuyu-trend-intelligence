from support.bazuuyu.bazuuyu_relevance import (
    assess_bazuuyu_relevance,
)


def future_candidate_to_bazuuyu_trend(
    candidate: dict,
) -> dict:
    """
    Convert a future-trend candidate into the text-rich
    structure expected by assess_bazuuyu_relevance().
    """

    movie_details = candidate.get(
        "movie_details",
        {},
    )

    title = candidate.get(
        "title",
        "",
    )

    ip = candidate.get(
        "ip",
        "",
    )

    overview = movie_details.get(
        "overview",
        "",
    )

    genres = movie_details.get(
        "genres",
        [],
    )

    keywords = movie_details.get(
        "keywords",
        [],
    )

    characters = movie_details.get(
        "characters",
        [],
    )

    production_companies = (
        movie_details.get(
            "production_companies",
            [],
        )
    )

    collection = movie_details.get(
        "collection",
        "",
    )

    entertainment_signals = (
        candidate.get(
            "entertainment_signals",
            [],
        )
    )

    description_parts = [
        overview,
        f"IP: {ip}",
        f"Genres: {' '.join(genres)}",
        f"Keywords: {' '.join(keywords)}",
        f"Characters: {' '.join(characters)}",
        f"Collection: {collection}",
        (
            "Entertainment signals: "
            + " ".join(entertainment_signals)
        ),
    ]

    description = " ".join(
        part
        for part in description_parts
        if part
    )

    key_entities = {
        "ip": [ip] if ip else [],
        "characters": characters,
        "genres": genres,
        "keywords": keywords,
        "production_companies": (
            production_companies
        ),
        "collection": (
            [collection]
            if collection
            else []
        ),
    }

    return {
        "title": title,
        "description": description,
        "importance": "",
        "key_entities": key_entities,
    }


def assess_future_candidate_bazuuyu_fit(
    candidate: dict,
) -> dict:
    """
    Run the existing Bazuuyu relevance engine
    on a future-trend candidate.
    """

    trend = future_candidate_to_bazuuyu_trend(
        candidate
    )

    return assess_bazuuyu_relevance(
        trend
    )