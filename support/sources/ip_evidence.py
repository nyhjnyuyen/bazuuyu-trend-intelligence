import re


def _normalize(text: str) -> str:
    text = (text or "").lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()

def _contains_phrase(
    text: str,
    phrase: str,
) -> bool:
    """
    Match a normalized phrase using complete word boundaries.

    Prevents false matches such as:
        "Ice Age" matching "Slice Age"
    """

    if not text or not phrase:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(phrase)
        + r"(?![a-z0-9])"
    )

    return bool(
        re.search(pattern, text)
    )


def validate_article_ip(
    article: dict,
    movie: dict,
    ip_name: str,
) -> dict:
    """
    Check whether a retrieved article contains direct textual
    evidence connecting it to the intended movie/franchise.

    This is intentionally conservative.

    It does not determine commercial value.
    """

    # Use high-confidence article metadata for IP identity.    #
    # Do not use the full scraped page text here because it
    # can contain site-wide navigation, social links, related
    # content, and other boilerplate unrelated to the article.
    article_text = " ".join([
        article.get("title", ""),
        article.get("description", ""),
    ])

    article_normalized = _normalize(
        article_text
    )

    ip_normalized = _normalize(
        ip_name
    )

    title_normalized = _normalize(
        movie.get("title", "")
    )

    collection_normalized = _normalize(
        movie.get("collection", "")
    )

    # Remove generic collection wording.
    collection_normalized = re.sub(
        r"\s+collection$",
        "",
        collection_normalized,
    ).strip()

    matches = []

    if _contains_phrase(
        article_normalized,
        ip_normalized,
    ):
        matches.append("IP_NAME")

    if _contains_phrase(
        article_normalized,
        title_normalized,
    ):
        matches.append("MOVIE_TITLE")

    if (
        collection_normalized
        and collection_normalized != ip_normalized
        and _contains_phrase(
            article_normalized,
            collection_normalized,
        )
    ):
        matches.append("COLLECTION")

    ip_word_count = len(
        ip_normalized.split()
    )

    # A single-word IP/title is too ambiguous to establish
    # identity from literal text matching alone.
    #
    # Examples:
    # Dragon -> Dragon Ball / Dungeons & Dragons
    # Cars   -> ordinary uses of "cars"
    #
    # Preserve the textual matches as evidence, but do not
    # automatically accept the article.
    ambiguous_single_word = (
        ip_word_count == 1
        and set(matches).issubset(
            {"IP_NAME", "MOVIE_TITLE"}
        )
    )

    matched = (
        bool(matches)
        and not ambiguous_single_word
    )
    
    if not matched:
        evidence_strength = "NONE"

    elif "MOVIE_TITLE" in matches:
        evidence_strength = "STRONG"

    elif "COLLECTION" in matches:
        evidence_strength = "STRONG"

    elif "IP_NAME" in matches:
        evidence_strength = "WEAK"

    else:
        evidence_strength = "NONE"

    return {
        "matched": matched,
        "matches": matches,
        "ambiguous_single_word": ambiguous_single_word,
        "evidence_strength": evidence_strength,
    }