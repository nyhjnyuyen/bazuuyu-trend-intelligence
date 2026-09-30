import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

TOYNEWSI_URL = "https://toynewsi.com/"

def fetch_toynewsi_articles(limit: int = 20) -> list[dict]:
    """
    Fetches the latest articles from ToyNewsi.

    Args:
        limit (int): The maximum number of articles to fetch.
    Returns:
        [
            {
                "source": "toynewsi",
                "title": "...",
                "url": "...",
            }
        ]
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/91.0.4472.124 "
        )
    }

    response = requests.get(TOYNEWSI_URL, headers=headers, timeout=20)

    response.raise_for_status()  # Raise an exception for HTTP errors

    soup = BeautifulSoup(response.content, "html.parser")
    articles = []
    seen_urls = set()

    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        url = link["href"]

        if not title:
            continue  # Skip links without a title

        if len(title) < 20:
            continue

        if url.startswith("/"):
            url = f"https://toynewsi.com{url}"

        if not url.startswith("https://toynewsi.com/"):
            continue  # Skip external links

        if url in seen_urls:
            continue  # Skip duplicate URLs

        seen_urls.add(url)
        articles.append(
            {
                "source": "toynewsi",
                "title": title,
                "url": url,
            }
        )
        if len(articles) >= limit:
            break

    return articles

def search_toynewsi(query: str, limit: int = 50) -> list[dict]:
    """
    Search ToyNewsI and return genuine article results.

    Returns:
        [
            {
                "source": "toynewsi",
                "title": "...",
                "url": "..."
            }
        ]
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(
        "https://toynewsi.com/index.php",
        data={
            "query": query,
            "amount": "0",
            "blogid": "1",
        },
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.content,
        "html.parser",
    )

    articles = []
    seen_urls = set()

    for result in soup.find_all(
        "div",
        class_="ns",
    ):
        title_container = result.find(
            "div",
            class_="nstol",
        )

        if not title_container:
            continue

        link = title_container.find(
            "a",
            href=True,
        )

        if not link:
            continue

        title = link.get_text(
            " ",
            strip=True,
        )

        url = link["href"]

        if url.startswith("/"):
            url = f"https://toynewsi.com{url}"

        if url in seen_urls:
            continue

        seen_urls.add(url)

        articles.append({
            "source": "toynewsi",
            "title": title,
            "url": url,
        })

        if len(articles) >= limit:
            break

    return articles

def fetch_article_details(url: str) -> dict:
    """
    Fetch structured details from a ToyNewsI article page.
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.content,
        "html.parser",
    )

    title_tag = soup.find(
        "meta",
        attrs={"property": "og:title"},
    )

    description_tag = soup.find(
        "meta",
        attrs={"property": "og:description"},
    )

    title = (
        title_tag.get("content", "").strip()
        if title_tag
        else ""
    )

    description = (
        description_tag.get("content", "").strip()
        if description_tag
        else ""
    )

    text = soup.get_text(
        " ",
        strip=True,
    )

    category = ""
    published_date = None

    info = soup.find("div", class_="nsd")

    if info:
        category_tag = info.find(
            "div",
            class_="catlink",
        )

        if category_tag:
            category = category_tag.get_text(
                " ",
                strip=True,
            )

        info_text = info.get_text(
            " ",
            strip=True,
        )

        for text_part in info.stripped_strings:
            try:
                parsed_date = datetime.strptime(
                    text_part,
                    "%B %d, %Y",
                )

                published_date = parsed_date.strftime(
                    "%Y-%m-%d"
                )

                break

            except ValueError:
                continue

    return {
        "source": "toynewsi",
        "title": title,
        "description": description,
        "category": category,
        "published_date": published_date,
        "url": url,
        "text": text,
    }

def analyze_toynewsi_search(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search ToyNewsI, fetch article details,
    and attach detected commercial/future signals.
    """

    from support.sources.toynewsi_signals import (
        detect_toynewsi_signals,
    )

    search_results = search_toynewsi(
        query,
        limit=limit,
    )

    analyzed_articles = []

    for result in search_results:
        details = fetch_article_details(
            result["url"]
        )

        details["signals"] = (
            detect_toynewsi_signals(details)
        )

        analyzed_articles.append(details)

    return analyzed_articles

def summarize_toynewsi_ip(
    query: str,
    limit: int = 10,
) -> dict:
    """
    Build an IP-level summary from analyzed ToyNewsI articles.
    """

    articles = analyze_toynewsi_search(
        query,
        limit=limit,
    )

    signal_counts = {}
    categories = set()

    for article in articles:

        category = article.get("category")

        if category:
            categories.add(category)

        for signal in article.get(
            "signals",
            [],
        ):
            signal_counts[signal] = (
                signal_counts.get(signal, 0) + 1
            )

    dates = [
        article["published_date"]
        for article in articles
        if article.get("published_date")
    ]

    recent_30d_count = 0
    recent_90d_count = 0

    parsed_dates = [
        datetime.strptime(date, "%Y-%m-%d")
        for date in dates
    ]

    if parsed_dates:
        latest_date = max(parsed_dates)

        cutoff_30d = latest_date - timedelta(days=30)
        cutoff_90d = latest_date - timedelta(days=90)

        recent_30d_count = sum(
            date >= cutoff_30d
            for date in parsed_dates
        )

        recent_90d_count = sum(
            date >= cutoff_90d
            for date in parsed_dates
        )

    return {
        "query": query,
        "article_count": len(articles),
        "latest_activity": max(dates) if dates else None,
        "earliest_activity": min(dates) if dates else None,
        "categories": sorted(categories),
        "signal_counts": signal_counts,
        "recent_30d_count": recent_30d_count,
        "recent_90d_count": recent_90d_count,
        "category_count": len(categories),
        "signal_type_count": len(signal_counts),
        "articles": articles,
    }

if __name__ == "__main__":
    articles = fetch_toynewsi_articles(limit=1)

    for article in articles:
        details = fetch_article_details(
            article["url"]
        )

        print("TITLE:")
        print(details["title"])

        print("\nCATEGORY:")
        print(details["category"])

        print("\nPUBLISHED:")
        print(details["published_date"])

        print("\nDESCRIPTION:")
        print(details["description"])

        print("\nURL:")
        print(details["url"])