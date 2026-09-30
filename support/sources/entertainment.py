from datetime import date, datetime, timedelta

import requests

from support.config import TMDB_API_TOKEN


TMDB_BASE_URL = "https://api.themoviedb.org/3"

MOVIE_GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}



def fetch_upcoming_movies(
    region: str = "US",
    pages: int = 1,
) -> list[dict]:
    """
    Fetch upcoming movies from TMDB and normalize
    them for the Bazuuyu trend intelligence system.
    """

    headers = {
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
        "accept": "application/json",
    }

    movies = []
    seen_ids = set()

    for page in range(1, pages + 1):

        response = requests.get(
            f"{TMDB_BASE_URL}/movie/upcoming",
            headers=headers,
            params={
                "language": "en-US",
                "region": region,
                "page": page,
            },
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        for movie in data.get("results", []):

            tmdb_id = movie.get("id")

            if tmdb_id in seen_ids:
                continue

            release_date = movie.get(
                "release_date"
            )

            if not release_date:
                continue

            try:
                parsed_date = datetime.strptime(
                    release_date,
                    "%Y-%m-%d",
                ).date()
            except ValueError:
                continue

            # TMDB's upcoming endpoint can contain
            # records with historical release dates.
            if parsed_date < date.today():
                continue

            seen_ids.add(tmdb_id)

            movies.append({
                "source": "tmdb",
                "tmdb_id": tmdb_id,
                "title": movie.get("title"),
                "original_title": movie.get(
                    "original_title"
                ),
                "release_date": release_date,
                "genre_ids": movie.get(
                    "genre_ids",
                    [],
                ),
                "genres": [
                    MOVIE_GENRES[genre_id]
                    for genre_id in movie.get("genre_ids", [])
                    if genre_id in MOVIE_GENRES
                ],
                "popularity": movie.get(
                    "popularity",
                    0,
                ),
                "vote_count": movie.get(
                    "vote_count",
                    0,
                ),
                "overview": movie.get(
                    "overview",
                    "",
                ),
                "media_type": "movie",
            })

    movies.sort(
        key=lambda movie: movie["release_date"]
    )

    return movies

def fetch_movie_details(tmdb_id: int) -> dict:
    """
    Fetch richer TMDB metadata for an individual movie.

    Used to enrich promising entertainment signals with
    keywords, characters, production companies, and other
    structured metadata.
    """

    headers = {
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
        "accept": "application/json",
    }

    response = requests.get(
        f"{TMDB_BASE_URL}/movie/{tmdb_id}",
        headers=headers,
        params={
            "language": "en-US",
            "append_to_response": "keywords,credits",
        },
        timeout=20,
    )

    response.raise_for_status()

    movie = response.json()

    return {
        "source": "tmdb",
        "tmdb_id": movie.get("id"),
        "title": movie.get("title"),
        "original_title": movie.get("original_title"),
        "release_date": movie.get("release_date"),
        "status": movie.get("status"),
        "tagline": movie.get("tagline"),
        "overview": movie.get("overview", ""),
        "genres": [
            genre.get("name")
            for genre in movie.get("genres", [])
        ],
        "popularity": movie.get("popularity", 0),
        "vote_count": movie.get("vote_count", 0),
        "keywords": [
            keyword.get("name")
            for keyword in movie.get(
                "keywords",
                {},
            ).get("keywords", [])
        ],
        "production_companies": [
            company.get("name")
            for company in movie.get(
                "production_companies",
                []
            )
        ],
        "collection": (
            movie.get("belongs_to_collection", {}).get("name")
            if movie.get("belongs_to_collection")
            else None
        ),
        "characters": [
            person.get("character")
            for person in movie.get(
                "credits",
                {},
            ).get("cast", [])[:15]
            if person.get("character")
        ],
        "media_type": "movie",
    }

def fetch_popular_upcoming_movies(
    region: str = "US",
    pages: int = 8,
    limit: int = 20,
) -> list[dict]:
    """
    Return the most popular upcoming movies from TMDB.
    """

    movies = fetch_upcoming_movies(
        region=region,
        pages=pages,
    )

    movies.sort(
        key=lambda movie: movie.get("popularity", 0),
        reverse=True,
    )

    return movies[:limit]

def fetch_popular_future_movies(
    region: str = "US",
    days_ahead: int = 365,
    pages: int = 10,
    limit: int = 30,
) -> list[dict]:
    """
    Fetch popular movies scheduled for release within
    the next N days using TMDB Discover.

    Release dates are validated locally because TMDB
    results can contain dates outside the requested window.
    """

    today = date.today()
    end_date = today + timedelta(days=days_ahead)

    headers = {
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
        "accept": "application/json",
    }

    movies = []
    seen_ids = set()

    for page in range(1, pages + 1):

        response = requests.get(
            f"{TMDB_BASE_URL}/discover/movie",
            headers=headers,
            params={
                "language": "en-US",
                "region": region,
                "release_date.gte": today.isoformat(),
                "release_date.lte": end_date.isoformat(),
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "page": page,
            },
            timeout=20,
        )

        response.raise_for_status()

        for movie in response.json().get("results", []):

            tmdb_id = movie.get("id")
            release_date = movie.get("release_date")

            if not tmdb_id or not release_date:
                continue

            try:
                parsed_date = datetime.strptime(
                    release_date,
                    "%Y-%m-%d",
                ).date()
            except ValueError:
                continue

            if not today <= parsed_date <= end_date:
                continue

            if tmdb_id in seen_ids:
                continue

            seen_ids.add(tmdb_id)

            movies.append({
                "source": "tmdb",
                "tmdb_id": tmdb_id,
                "title": movie.get("title"),
                "original_title": movie.get("original_title"),
                "release_date": release_date,
                "genre_ids": movie.get("genre_ids", []),
                "genres": [
                    MOVIE_GENRES[genre_id]
                    for genre_id in movie.get("genre_ids", [])
                    if genre_id in MOVIE_GENRES
                ],
                "popularity": movie.get("popularity", 0),
                "vote_count": movie.get("vote_count", 0),
                "overview": movie.get("overview", ""),
                "media_type": "movie",
            })

    movies.sort(
        key=lambda movie: movie.get("popularity", 0),
        reverse=True,
    )

    return movies[:limit]