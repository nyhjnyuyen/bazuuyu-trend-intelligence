import re


def extract_ip_name(movie: dict) -> str:
    """
    Derive a likely franchise/IP search name from TMDB metadata.

    This is deterministic and does not use an LLM.
    """

    title = movie.get("title") or ""
    collection = movie.get("collection")
    keywords = [
        keyword.lower()
        for keyword in movie.get("keywords", [])
    ]

    # Prefer franchise collection metadata.
    if collection:

        ip = collection

        # Remove generic collection wording.
        ip = re.sub(
            r"\s+collection$",
            "",
            ip,
            flags=re.IGNORECASE,
        )

        # Remove leading article.
        ip = re.sub(
            r"^the\s+",
            "",
            ip,
            flags=re.IGNORECASE,
        )

        # Remove TMDB trilogy descriptors.
        ip = re.sub(
            r"\s*[–—-]\s*new trilogy$",
            "",
            ip,
            flags=re.IGNORECASE,
        )

        ip = ip.strip()

        return ip

    # Fall back to the movie title.
    return title.strip()
def build_ip_search_query(
    movie: dict,
    ip_name: str,
) -> str:
    """
    Build a more specific search query for external sources
    when the extracted IP name is ambiguous.

    Keeps the canonical IP identity separate from the
    source-search query.
    """

    title = (
        movie.get("title")
        or ""
    ).strip()

    if not ip_name:
        return title

    # Multi-word franchise names are generally specific
    # enough to search directly.
    if len(ip_name.split()) >= 2:
        return ip_name

    # Single-word IP names can be highly ambiguous:
    # Dragon, Cars, Alien, etc.
    #
    # Preserve the IP identity but use the movie title
    # as the external search query.
    if title:
        return title

    return ip_name