"""Load scraped Reddit JSON into PostgreSQL.

Run from the project root:
    python -m support.load_reddit_data
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from support.config import NICHES
from support.database_util import (
    connect_database,
    insert_posts_from_df,
    table_stats,
)
from support.preprocessing.text_cleaner import (
    clean_text,
    combine_title_body,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reddit_trends_last_30_days.json"),
    )
    args = parser.parse_args()

    with args.input.open(encoding="utf-8") as file:
        posts = json.load(file)

    if not isinstance(posts, list) or not posts:
        raise ValueError("Expected a non-empty JSON list of Reddit posts.")

    df = pd.DataFrame(posts)

    required = {"post_id", "niche", "title", "timestamp_utc"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    canonical = {niche.lower(): niche for niche in NICHES}
    df["niche"] = (
        df["niche"]
        .fillna("")
        .astype(str)
        .str.lower()
        .map(canonical)
    )

    df = df.dropna(subset=["post_id", "niche", "title"]).copy()
    df = df.drop_duplicates(subset=["post_id"])

    if df.empty:
        raise ValueError("No posts match the configured Bazuuyu communities.")

    for column in ["author", "permalink", "url", "selftext"]:
        if column not in df.columns:
            df[column] = ""
        df[column] = df[column].fillna("").astype(str)

    df["title"] = df["title"].astype(str)
    df["post_id"] = df["post_id"].astype(str)

    for column in ["score", "num_comments"]:
        if column not in df.columns:
            df[column] = 0
        df[column] = (
            pd.to_numeric(df[column], errors="coerce")
            .fillna(0)
            .astype(int)
        )

    if "upvote_ratio" not in df.columns:
        df["upvote_ratio"] = float("nan")

    # Missing ratios remain NULL rather than invented measurements.
    ratios = pd.to_numeric(df["upvote_ratio"], errors="coerce")
    df["upvote_ratio"] = ratios.astype(object).where(ratios.notna(), None)

    timestamps = pd.to_datetime(
        df["timestamp_utc"],
        errors="coerce",
        utc=True,
    )
    if timestamps.isna().any():
        raise ValueError("Some posts have invalid timestamps.")

    df["timestamp_utc"] = timestamps.dt.tz_convert(None)

    df["full_text"] = [
        clean_text(combine_title_body(title, body))
        for title, body in zip(df["title"], df["selftext"])
    ]

    # Compatibility field: cleaned original text, not a translation.
    df["text_translated"] = df["full_text"]

    print(f"Prepared {len(df):,} posts")
    print(df.groupby("niche").size().to_string())

    conn = connect_database()
    try:
        insert_posts_from_df(conn, df)
        table_stats(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()