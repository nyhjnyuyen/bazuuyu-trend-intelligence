"""
bazuuyu_relevance.py

Local rule-based relevance engine for Bazuuyu.

Purpose:
- Detect direct product signals
- Detect character/IP signals
- Detect fandom signals
- Detect nostalgia signals
- Detect visual/design signals
- Detect content/marketing signals
- Detect combinations of signals
- Estimate opportunity strength

This runs locally before Gemini so that we only send
useful trends to the LLM.
"""

import re

from support.config import (
    BAZUUYU_STRONG_KEYWORDS,
    BAZUUYU_ADJACENT_KEYWORDS,
    BAZUUYU_EXCLUDE_KEYWORDS,
    BAZUUYU_PRODUCT_KEYWORDS,
    BAZUUYU_COLLECTIBLE_KEYWORDS,
    BAZUUYU_CHARACTER_IP_KEYWORDS,
    BAZUUYU_FANDOM_KEYWORDS,
    BAZUUYU_NOSTALGIA_KEYWORDS,
    BAZUUYU_VISUAL_KEYWORDS,
    BAZUUYU_CONTENT_KEYWORDS,
    BAZUUYU_BEHAVIOR_KEYWORDS,
    BAZUUYU_BEHAVIOR_CONTEXT_KEYWORDS,
    BAZUUYU_ENTERTAINMENT_CONTEXT_KEYWORDS,
)


# ─────────────────────────────────────────────────────────────
# TEXT PROCESSING
# ─────────────────────────────────────────────────────────────


def normalize_text(text: str) -> str:
    """Convert text to lowercase and normalize whitespace."""

    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def build_trend_text(trend: dict) -> str:
    """
    Combine the most useful Trend-Finder fields
    into searchable text.
    """

    entities = trend.get("key_entities", {})

    if isinstance(entities, dict):

        entity_text = " ".join(
            str(value)
            for values in entities.values()
            for value in (
                values if isinstance(values, list) else [values]
            )
        )

    elif isinstance(entities, list):

        entity_text = " ".join(
            str(value)
            for value in entities
        )

    else:

        entity_text = str(entities or "")

    parts = [
        trend.get("title", ""),
        trend.get("description", ""),
        trend.get("importance", ""),
        entity_text,
    ]

    return normalize_text(
        " ".join(parts)
    )


def find_keyword_matches(
    text: str,
    keywords: list[str],
) -> list[str]:
    """
    Find whole-word keyword matches.

    Whole-word matching prevents accidental matches.
    """

    matches = []

    for keyword in keywords:

        pattern = r"\b" + re.escape(
            keyword.lower()
        ) + r"\b"

        if re.search(pattern, text):

            matches.append(keyword)

    return matches

def detect_behavior_signals(text: str) -> dict:
    """
    Detect consumer behavior signals relevant to Bazuuyu.

    Behavior signals are detected separately from product/category
    keywords so they can later be used as an additional intelligence layer.
    """

    text_lower = text.lower()

    behavior_matches = [
        keyword
        for keyword in BAZUUYU_BEHAVIOR_KEYWORDS
    if re.search(rf"\b{re.escape(keyword.lower())}\b", text_lower)
    ]

    # Trading is context-dependent.

    # Customization is context-dependent.
    # Generic software/device customization should not count
    # as a Bazuuyu consumer behavior signal.
    customization_context = [
        "customized toy",
        "customized toys",
        "customized plush",
        "customized plushie",
        "customized figure",
        "customized collectible",
        "customized character",
        "customized product",
        "customized design",
        "customized merchandise",
        "customization options",
        "customization products",
        "customization of toys",
        "customization of plush",
        "customization of figures",
    ]

    if "customized" in behavior_matches:
        if not any(context in text_lower for context in customization_context):
            behavior_matches.remove("customized")

    if "customization" in behavior_matches:
        if not any(context in text_lower for context in customization_context):
            behavior_matches.remove("customization")

    # Financial/prediction-market trading should not count as
    # collectible/toy trading.
    if "trading" in behavior_matches:
        trading_context = [
            "toy trading",
            "collectible trading",
            "collectibles trading",
            "figure trading",
            "figurine trading",
            "blind box trading",
            "trading figures",
            "trading collectibles",
            "trading cards",
        ]

        if not any(context in text_lower for context in trading_context):
            behavior_matches.remove("trading")

    context_matches = [
        keyword
        for keyword in BAZUUYU_BEHAVIOR_CONTEXT_KEYWORDS
        if re.search(rf"\b{re.escape(keyword.lower())}\b", text_lower)

    ]

    return {
        "behavior_matches": behavior_matches,
        "behavior_context_matches": context_matches,
    }

def detect_entertainment_context(text: str) -> list[str]:
    """
    Detect entertainment context relevant to Bazuuyu.

    This identifies whether a trend is connected to gaming,
    movies, anime, animation, TV, or related entertainment.
    Context is detected separately from relevance scoring.
    """

    text_lower = text.lower()

    return [
        keyword
        for keyword in BAZUUYU_ENTERTAINMENT_CONTEXT_KEYWORDS
        if keyword.lower() in text_lower
    ]

def calculate_entertainment_context_score(entertainment_matches: list[str]) -> float:
    """
    Estimate how strongly a trend is connected to entertainment.

    Stronger signals receive more weight than broader context terms.
    """

    weights = {
        "gaming": 3,
        "video game": 3,
        "video games": 3,
        "movie": 3,
        "movies": 3,
        "anime": 3,
        "manga": 3,
        "film": 3,
        "films": 3,
        "animation": 2,
        "animated": 2,
        "cartoon": 2,
        "television": 2,
    }

    score = sum(
        weights.get(match.lower(), 0)
        for match in entertainment_matches
    )

    return round(min(score, 10), 2)

def detect_entertainment_opportunity_signals(
    entertainment_matches: list[str],
    character_matches: list[str],
    fandom_matches: list[str],
    nostalgia_matches: list[str],
    visual_matches: list[str],
    content_matches: list[str],
    behavior_matches: list[str],
) -> list[str]:
    """
    Detect combinations between entertainment context and
    Bazuuyu-relevant consumer/product signals.
    """

    signals = []

    if entertainment_matches and character_matches:
        signals.append("ENTERTAINMENT_CHARACTER_IP")

    if entertainment_matches and fandom_matches:
        signals.append("ENTERTAINMENT_FANDOM")

    if entertainment_matches and nostalgia_matches:
        signals.append("ENTERTAINMENT_NOSTALGIA")

    if entertainment_matches and visual_matches:
        signals.append("ENTERTAINMENT_VISUAL")

    if entertainment_matches and content_matches:
        signals.append("ENTERTAINMENT_CONTENT")

    if entertainment_matches and behavior_matches:
        signals.append("ENTERTAINMENT_BEHAVIOR")

    return signals

def calculate_entertainment_opportunity_score(
    opportunity_signals: list[str],
) -> float:
    """
    Score the commercial strength of entertainment-related
    Bazuuyu opportunity signals.

    Consumer/fandom/product-oriented signals receive more weight
    than general visual or content signals.
    """

    weights = {
        "ENTERTAINMENT_CHARACTER_IP": 20,
        "ENTERTAINMENT_FANDOM": 20,
        "ENTERTAINMENT_BEHAVIOR": 20,
        "ENTERTAINMENT_NOSTALGIA": 10,
        "ENTERTAINMENT_VISUAL": 5,
        "ENTERTAINMENT_CONTENT": 5,
    }

    score = sum(
        weights.get(signal, 0)
        for signal in opportunity_signals
    )

    return round(min(score, 100), 2)

# ─────────────────────────────────────────────────────────────
# SIGNAL COMBINATIONS
# ─────────────────────────────────────────────────────────────


def detect_strong_combinations(
    product_matches: list[str],
    character_matches: list[str],
    fandom_matches: list[str],
    nostalgia_matches: list[str],
    visual_matches: list[str],
    content_matches: list[str],
) -> list[str]:
    """
    Detect combinations of signals that are more meaningful
    than individual generic keywords.
    """

    combinations = []

    # Product + nostalgia
    if product_matches and nostalgia_matches:

        combinations.append(
            "PRODUCT_NOSTALGIA"
        )

    # Product + fandom
    if product_matches and fandom_matches:

        combinations.append(
            "PRODUCT_FANDOM"
        )

    # Product + character/IP
    if product_matches and character_matches:

        combinations.append(
            "PRODUCT_CHARACTER_IP"
        )

    # Character/IP + fandom
    if character_matches and fandom_matches:

        combinations.append(
            "CHARACTER_IP_FANDOM"
        )

    # Character/IP + nostalgia
    if character_matches and nostalgia_matches:

        combinations.append(
            "CHARACTER_IP_NOSTALGIA"
        )

    # Character/IP + visual
    if character_matches and visual_matches:

        combinations.append(
            "CHARACTER_IP_VISUAL"
        )

    # Character/IP + content
    if character_matches and content_matches:

        combinations.append(
            "CHARACTER_IP_CONTENT"
        )

    # Fandom + visual
    if fandom_matches and visual_matches:

        combinations.append(
            "FANDOM_VISUAL"
        )

    # Fandom + content
    if fandom_matches and content_matches:

        combinations.append(
            "FANDOM_CONTENT"
        )

    # Nostalgia + visual
    if nostalgia_matches and visual_matches:

        combinations.append(
            "NOSTALGIA_VISUAL"
        )

    # Visual + content
    if visual_matches and content_matches:

        combinations.append(
            "VISUAL_CONTENT"
        )

    return combinations


# ─────────────────────────────────────────────────────────────
# SCORE
# ─────────────────────────────────────────────────────────────


def calculate_relevance_score(
    product_matches: list[str],
    collectible_matches: list[str],
    character_matches: list[str],
    fandom_matches: list[str],
    nostalgia_matches: list[str],
    visual_matches: list[str],
    content_matches: list[str],
    exclude_matches: list[str],
    combinations: list[str],
) -> float:
    """
    Calculate Bazuuyu opportunity score.

    Individual signals provide the base score.

    Strong combinations receive additional points because
    combinations are generally more informative than isolated
    generic keywords.
    """

    score = 0.0

    # Direct product signals
    score += len(product_matches) * 25

    score += len(collectible_matches) * 10

    # Character / IP
    score += len(character_matches) * 12

    # Fandom
    score += len(fandom_matches) * 12

    # Nostalgia
    score += len(nostalgia_matches) * 6

    # Visual/design
    score += len(visual_matches) * 3

    # Content/marketing
    score += len(content_matches) * 3

    # Strong combinations
    combination_weights = {
        "PRODUCT_NOSTALGIA": 15,
        "PRODUCT_FANDOM": 15,
        "PRODUCT_CHARACTER_IP": 15,
        "CHARACTER_IP_FANDOM": 12,
        "CHARACTER_IP_NOSTALGIA": 8,
        "CHARACTER_IP_VISUAL": 6,
        "CHARACTER_IP_CONTENT": 6,
        "FANDOM_VISUAL": 6,
        "FANDOM_CONTENT": 6,
        "NOSTALGIA_VISUAL": 3,
        "VISUAL_CONTENT": 3,
    }

    for combination in combinations:

        score += combination_weights.get(
            combination,
            0,
        )

    # Excluded topics reduce relevance.
    score -= len(exclude_matches) * 20

    return round(
        max(0.0, min(score, 100.0)),
        2,
    )


# ─────────────────────────────────────────────────────────────
# SIGNAL STRENGTH
# ─────────────────────────────────────────────────────────────


def determine_signal_strength(
    score: float,
    combinations: list[str],
    product_matches: list[str],
    character_matches: list[str],
    fandom_matches: list[str],
) -> str:
    """
    Estimate how strong the overall commercial signal is.
    """

    # Direct product signals are strong.
    if product_matches:

        if (
            "PRODUCT_FANDOM" in combinations
            or "PRODUCT_CHARACTER_IP" in combinations
            or "PRODUCT_NOSTALGIA" in combinations
        ):

            return "VERY_STRONG"

        return "STRONG"

    # Multiple upstream signals are strong.
    if (
        "CHARACTER_IP_FANDOM" in combinations
        or (
            len(character_matches) >= 1
            and len(fandom_matches) >= 1
        )
    ):

        return "STRONG"

    if score >= 40:

        return "STRONG"

    if score >= 20:

        return "MODERATE"

    return "WEAK"


# ─────────────────────────────────────────────────────────────
# RELEVANCE LEVEL
# ─────────────────────────────────────────────────────────────


def determine_relevance_level(
    score: float,
    signal_strength: str,
    product_matches: list[str],
    character_matches: list[str],
    fandom_matches: list[str],
    nostalgia_matches: list[str],
    behavior_matches: list[str],
) -> str:
    """
    Convert signals into a business-oriented relevance level.

    HIGH:
        Direct product opportunity.

    MEDIUM:
        Potential upstream IP/fandom/nostalgia opportunity.

    LOW:
        Weak or uncertain opportunity.
    """

    # Direct product signals are HIGH.
    if product_matches:

        return "HIGH"

    # Strong signals are MEDIUM only when supported
    # by a consumer or meaningful upstream signal.
    if (
        signal_strength in {
            "STRONG",
            "VERY_STRONG",
        }
        and (
            product_matches
            or behavior_matches
            or fandom_matches
        )
    ):

        return "MEDIUM"

    # Multiple meaningful upstream signals.
    meaningful_categories = sum(
        bool(matches)
        for matches in [
            character_matches,
            fandom_matches,
            nostalgia_matches,
            behavior_matches,
        ]
    )

    if (
        meaningful_categories >= 2
        and (
            fandom_matches
            or behavior_matches
        )
    ):
        return "MEDIUM"

    

    return "LOW"


# ─────────────────────────────────────────────────────────────
# OPPORTUNITY TYPES
# ─────────────────────────────────────────────────────────────


def determine_opportunity_types(
    product_matches: list[str],
    character_matches: list[str],
    fandom_matches: list[str],
    nostalgia_matches: list[str],
    visual_matches: list[str],
    content_matches: list[str],
) -> list[str]:
    """Identify the types of Bazuuyu opportunities."""

    opportunity_types = []

    if product_matches:

        opportunity_types.append(
            "DIRECT_PRODUCT"
        )

    if character_matches:

        opportunity_types.append(
            "CHARACTER_IP"
        )

    if fandom_matches:

        opportunity_types.append(
            "FANDOM"
        )

    if nostalgia_matches:

        opportunity_types.append(
            "NOSTALGIA"
        )

    if visual_matches:

        opportunity_types.append(
            "VISUAL_STYLE"
        )

    if content_matches:

        opportunity_types.append(
            "CONTENT"
        )

    return opportunity_types


# ─────────────────────────────────────────────────────────────
# NEXT ACTION
# ─────────────────────────────────────────────────────────────


def determine_next_action(
    opportunity_types: list[str],
    signal_strength: str,
) -> str:
    """
    Suggest what Bazuuyu should investigate next.

    This is a research recommendation, not a claim that
    a licensing or product opportunity actually exists.
    """
    if (
        "DIRECT_PRODUCT" in opportunity_types
        and "CHARACTER_IP" in opportunity_types
        and "FANDOM" in opportunity_types
    ):
        return (
            "Investigate the underlying IP, character demand, "
            "fandom activity, and existing merchandise before "
            "evaluating Bazuuyu product opportunities."
        )

    if "DIRECT_PRODUCT" in opportunity_types:
        return (
            "Evaluate the product trend, audience behavior, "
            "and potential Bazuuyu product formats."
        )

    if (
        "CHARACTER_IP" in opportunity_types
        and "FANDOM" in opportunity_types
    ):

        return (
            "Investigate the underlying IP, characters, "
            "fandom activity, and potential merchandising fit."
        )

    if "CHARACTER_IP" in opportunity_types:

        return (
            "Investigate the underlying characters or "
            "franchises and their merchandising potential."
        )

    if "FANDOM" in opportunity_types:

        return (
            "Investigate the underlying fandom, community "
            "behavior, and products fans are creating or collecting."
        )

    if "NOSTALGIA" in opportunity_types:

        return (
            "Investigate whether the nostalgic theme connects "
            "to recognizable characters, franchises, or collectibles."
        )

    if "VISUAL_STYLE" in opportunity_types:

        return (
            "Monitor the visual style and evaluate whether "
            "it could influence Bazuuyu product or content design."
        )

    if "CONTENT" in opportunity_types:

        return (
            "Monitor the content trend for creative and "
            "marketing opportunities."
        )

    return (
        "Continue monitoring; current Bazuuyu signal is weak."
    )


# ─────────────────────────────────────────────────────────────
# MAIN ANALYZER
# ─────────────────────────────────────────────────────────────


def assess_bazuuyu_relevance(
    trend: dict,
) -> dict:
    """
    Assess Bazuuyu relevance for one Trend-Finder trend.
    """

    text = build_trend_text(trend)

    behavior_signals = detect_behavior_signals(text)

    behavior_matches = behavior_signals["behavior_matches"]
    behavior_context_matches = behavior_signals["behavior_context_matches"]

    # Broad signal groups
    strong_matches = find_keyword_matches(
        text,
        BAZUUYU_STRONG_KEYWORDS,
    )

    adjacent_matches = find_keyword_matches(
        text,
        BAZUUYU_ADJACENT_KEYWORDS,
    )

    exclude_matches = find_keyword_matches(
        text,
        BAZUUYU_EXCLUDE_KEYWORDS,
    )

    # Opportunity categories
    product_matches = find_keyword_matches(
        text,
        BAZUUYU_PRODUCT_KEYWORDS,
    )

    collectible_matches = find_keyword_matches(
        text,
        BAZUUYU_COLLECTIBLE_KEYWORDS,
    )

    character_matches = find_keyword_matches(
        text,
        BAZUUYU_CHARACTER_IP_KEYWORDS,
    )

    fandom_matches = find_keyword_matches(
        text,
        BAZUUYU_FANDOM_KEYWORDS,
    )

    nostalgia_matches = find_keyword_matches(
        text,
        BAZUUYU_NOSTALGIA_KEYWORDS,
    )

    visual_matches = find_keyword_matches(
        text,
        BAZUUYU_VISUAL_KEYWORDS,
    )

    content_matches = find_keyword_matches(
        text,
        BAZUUYU_CONTENT_KEYWORDS,
    )

    # Combination signals
    combinations = detect_strong_combinations(
        product_matches=product_matches,
        character_matches=character_matches,
        fandom_matches=fandom_matches,
        nostalgia_matches=nostalgia_matches,
        visual_matches=visual_matches,
        content_matches=content_matches,
    )

    # Score
    relevance_score = calculate_relevance_score(
        product_matches=product_matches,
        collectible_matches=collectible_matches,
        character_matches=character_matches,
        fandom_matches=fandom_matches,
        nostalgia_matches=nostalgia_matches,
        visual_matches=visual_matches,
        content_matches=content_matches,
        exclude_matches=exclude_matches,
        combinations=combinations,
    )

    # Signal strength
    signal_strength = determine_signal_strength(
        score=relevance_score,
        combinations=combinations,
        product_matches=product_matches,
        character_matches=character_matches,
        fandom_matches=fandom_matches,
    )

    # Opportunity types
    opportunity_types = determine_opportunity_types(
        product_matches=product_matches,
        character_matches=character_matches,
        fandom_matches=fandom_matches,
        nostalgia_matches=nostalgia_matches,
        visual_matches=visual_matches,
        content_matches=content_matches,
    )

    # Relevance level
    relevance_level = determine_relevance_level(
        score=relevance_score,
        signal_strength=signal_strength,
        product_matches=product_matches,
        character_matches=character_matches,
        fandom_matches=fandom_matches,
        nostalgia_matches=nostalgia_matches,
        behavior_matches=behavior_matches,
    )

    # Excluded topics should normally be removed.
    is_relevant = relevance_level in {
        "HIGH",
        "MEDIUM",
    }

    if exclude_matches and not product_matches:

        is_relevant = False

    # Next research action
    next_action = determine_next_action(
        opportunity_types=opportunity_types,
        signal_strength=signal_strength,
    )

    # Explanation
    if product_matches:

        reason = (
            "Direct toy, plush, or collectible signals detected."
        )

    elif (
        character_matches
        and fandom_matches
    ):

        reason = (
            "Character/IP and fandom signals appear together, "
            "suggesting an upstream IP or merchandising signal."
        )

    elif character_matches:

        reason = (
            "Potential character or franchise signal detected; "
            "underlying IP should be investigated."
        )

    elif fandom_matches:

        reason = (
            "Fandom or community-creation signals detected; "
            "underlying products, characters, or franchises "
            "should be investigated."
        )

    elif nostalgia_matches:

        reason = (
            "Nostalgia signals detected; investigate whether "
            "they connect to recognizable characters, franchises, "
            "or collectibles."
        )

    elif visual_matches:

        reason = (
            "Visual/design signals detected; useful primarily "
            "for creative monitoring and content direction."
        )

    elif content_matches:

        reason = (
            "Content/marketing signals detected; useful mainly "
            "for monitoring creative or promotional activity."
        )

    elif exclude_matches:

        reason = (
            "Trend contains topics generally outside "
            "Bazuuyu's commercial focus."
        )

    else:

        reason = (
            "Limited Bazuuyu relevance detected."
        )

    return {
        "is_relevant": is_relevant,
        "relevance_level": relevance_level,
        "relevance_score": relevance_score,
        "signal_strength": signal_strength,
        "opportunity_types": opportunity_types,
        "strong_combinations": combinations,
        "strong_matches": strong_matches,
        "adjacent_matches": adjacent_matches,
        "product_matches": product_matches,
        "collectible_matches": collectible_matches,
        "character_ip_matches": character_matches,
        "fandom_matches": fandom_matches,
        "nostalgia_matches": nostalgia_matches,
        "visual_matches": visual_matches,
        "content_matches": content_matches,
        "behavior_matches": behavior_matches,
        "behavior_context_matches": behavior_context_matches,
        "exclude_matches": exclude_matches,
        "reason": reason,
        "next_action": next_action,
    }