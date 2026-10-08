from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
from support.sources.news_dedup import deduplicate_news_articles
import requests


GOOGLE_NEWS_RSS = "https://" + "news.google.com/rss/search"


def fetch_google_news(
    query: str,
    limit: int = 20,
) -> list[dict]:
    """
    Fetch and normalize Google News RSS search results.
    """

    url = (
        f"{GOOGLE_NEWS_RSS}"
        f"?q={quote_plus(query)}"
        "&hl=en-US"
        "&gl=US"
        "&ceid=US:en"
    )

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        timeout=20,
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    articles = []

    for item in root.findall(".//item"):

        title = item.findtext("title")
        link = item.findtext("link")
        published = item.findtext("pubDate")

        if not title or not link:
            continue

        published_date = None

        if published:
            try:
                parsed = parsedate_to_datetime(
                    published
                )

                published_date = (
                    parsed.astimezone(timezone.utc)
                    .date()
                    .isoformat()
                )
            except (TypeError, ValueError):
                pass

        # Google News titles normally end with
        # " - Publisher Name".
        publisher = None

        if " - " in title:
            article_title, publisher = title.rsplit(
                " - ",
                1,
            )
        else:
            article_title = title

        articles.append({
            "source": "google_news",
            "query": query,
            "title": article_title.strip(),
            "publisher": (
                publisher.strip()
                if publisher
                else None
            ),
            "published_date": published_date,
            "url": link,
        })

        if len(articles) >= limit:
            break

    return articles

def summarize_google_news(
    query: str,
    limit: int = 20,
) -> dict:
    """
    Summarize Google News activity for an IP/query.
    """

    from support.sources.web_news_signals import (
        detect_web_news_signals,
    )

    articles = fetch_google_news(
        query,
        limit=limit,
    )

    stories = deduplicate_news_articles(
        articles,
        similarity_threshold=0.72,
    )

    signal_counts = {}
    publishers = set()

    for article in articles:

        publisher = article.get("publisher")

        if publisher:
            publishers.add(publisher)

        signals = detect_web_news_signals(article)
        article["signals"] = signals

        for signal in signals:
            signal_counts[signal] = (
                signal_counts.get(signal, 0) + 1
            )

    dates = [
        article["published_date"]
        for article in articles
        if article.get("published_date")
    ]

        # Preserve cluster-level news coverage evidence.
    largest_story = max(
        stories,
        key=lambda story: story.get(
            "article_count",
            0,
        ),
        default=None,
    )

    if largest_story:
        largest_story_article_count = (
            largest_story.get(
                "article_count",
                0,
            )
        )

        largest_story_publisher_count = len(
            largest_story.get(
                "publishers",
                [],
            )
        )

    else:
        largest_story_article_count = 0
        largest_story_publisher_count = 0

    story_concentration = (
        largest_story_article_count
        / len(articles)
        if articles
        else 0.0
    )

    return {
        "query": query,
        "article_count": len(articles),
        "unique_story_count": len(stories),
        "duplicate_article_count": (
            len(articles) - len(stories)
        ),
                "largest_story_article_count": (
            largest_story_article_count
        ),
        "largest_story_publisher_count": (
            largest_story_publisher_count
        ),
        "story_concentration": round(
            story_concentration,
            3,
        ),
        "latest_activity": max(dates) if dates else None,
        "earliest_activity": min(dates) if dates else None,
        "publisher_count": len(publishers),
        "publishers": sorted(publishers),
        "signal_counts": signal_counts,
        "stories": stories,
        "articles": articles,
    }