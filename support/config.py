"""
config.py — Central configuration for the Reddit Trend Finder pipeline.

All tunable parameters live here. Database credentials are loaded from .env.
"""

import os
from dotenv import load_dotenv

# Load .env from the same directory as this file (support/)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ─────────────────────────────────────────────────────────────
# DATABASE (PostgreSQL + pgvector)
# ─────────────────────────────────────────────────────────────
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5442")
DB_NAME     = os.getenv("DB_NAME", "postgres")

# ─────────────────────────────────────────────────────────────
# GEMINI LLM
# ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

# ─────────────────────────────────────────────────────────────
# NICHES
# ─────────────────────────────────────────────────────────────
NICHES = ["technology", "science", "worldnews", "gaming", "smartphones", "movies"]

# ─────────────────────────────────────────────────────────────
# EMBEDDINGS
# ─────────────────────────────────────────────────────────────
EMBEDDING_MODEL   = "all-MiniLM-L6-v2"
EMBEDDING_DIM     = 384
EMBEDDING_BATCH   = 32

# ─────────────────────────────────────────────────────────────
# CLUSTERING (HDBSCAN — weekly)
#
# Rationale:
#   ~250 posts/week in the largest niche (technology).
#   min_cluster_size = 15  →  a cluster needs ≥ 6 % of weekly posts
#   min_samples      = 5   →  lenient core-point definition
#   → Expect 5–10 clusters per week/niche; top 3 selected.
# ─────────────────────────────────────────────────────────────
HDBSCAN_MIN_CLUSTER_SIZE = 10
HDBSCAN_MIN_SAMPLES      = 5
HDBSCAN_METRIC            = "euclidean"

# How many of the best clusters to send to the LLM
TOP_N_CLUSTERS        = 3

# How many posts per cluster are included in the LLM prompt
TOP_POSTS_PER_CLUSTER = 8

# ─────────────────────────────────────────────────────────────
# UMAP (dimensionality reduction before HDBSCAN)
# ─────────────────────────────────────────────────────────────
UMAP_N_COMPONENTS = 10   # 15–30 sweet spot for clustering; 10 is too aggressive
UMAP_N_NEIGHBORS  = 15
UMAP_MIN_DIST     = 0.0
UMAP_METRIC       = "cosine"

# ─────────────────────────────────────────────────────────────
# SCORING WEIGHTS (cluster importance)
#   importance = avg_score*W_SCORE + avg_comments*W_COMMENTS
#                + avg_upvote_ratio*100*W_UPVOTE
# ─────────────────────────────────────────────────────────────
W_SCORE    = 0.5
W_COMMENTS = 0.3
W_UPVOTE   = 0.2

# ─────────────────────────────────────────────────────────────
# OUTPUT (lives inside support/)
# ─────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, "weekly_trends.json")

# ─────────────────────────────────────────────────────────────
# FASTAPI
# ─────────────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8080"
).split(",")

# ─────────────────────────────────────────────────────────────
# CSV PATHS (raw / preprocessed data)
# ─────────────────────────────────────────────────────────────
RAW_CSV_PATH = os.getenv(
    "RAW_CSV_PATH",
    os.path.join(PROJECT_ROOT, "data", "final_trendingtopics_reddit.csv"),
)

# ─────────────────────────────────────────────────────────────
# TMDB (The Movie Database) API
# ─────────────────────────────────────────────────────────────
TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")

# ─────────────────────────────────────────────────────────────
# BAZUUYU RELEVANCE FILTER
# ─────────────────────────────────────────────────────────────

# Strong signals that a trend may be directly relevant to Bazuuyu.
BAZUUYU_STRONG_KEYWORDS = [
    "plush",
    "plushie",
    "stuffed animal",
    "stuffed toy",
    "soft toy",
    "teddy bear",
    "collectible",
    "collectibles",
    "blind box",
    "blindbox",
    "designer toy",
    "vinyl toy",
    "character toy",
    "figurine",
    "figure",
    "toy",
]

# Adjacent signals that can indicate product, character,
# content, or retail opportunities.
BAZUUYU_ADJACENT_KEYWORDS = [
    "cute",
    "kawaii",
    "character",
    "mascot",
    "cute character",
    "animal character",
    "sanrio",
    "anime",
    "manga",
    "cartoon",
    "fandom",
    "merch",
    "merchandise",
    "gift",
    "gifting",
    "stationery",
    "accessories",
    "fashion",
    "food",
    "snack",
    "dessert",
    "viral",
    "meme",
    "nostalgia",
    "aesthetic",
    "decor",
]

# Trends containing these terms are generally less useful
# for Bazuuyu unless they also contain strong toy/collectible signals.
BAZUUYU_EXCLUDE_KEYWORDS = [
    "war",
    "military",
    "election",
    "politics",
    "geopolitical",
    "stock market",
    "layoff",
    "interest rate",
    "mortgage",
    "crime",
    "earthquake",
    "hurricane",
    "disease",
    "medical",
]
# ─────────────────────────────────────────────────────────────
# BAZUUYU OPPORTUNITY CATEGORIES
# ─────────────────────────────────────────────────────────────

# Direct product signals.
BAZUUYU_PRODUCT_KEYWORDS = [
    "plush",
    "plushie",
    "stuffed animal",
    "stuffed toy",
    "soft toy",
    "teddy bear",
    "blind box",
    "blindbox",
    "designer toy",
    "vinyl toy",
    "character toy",
    "figurine",
    "toy",
]

BAZUUYU_COLLECTIBLE_KEYWORDS = [
    "collectible",
    "collectibles",
]

BAZUUYU_BEHAVIOR_KEYWORDS = [
    "collecting",
    "collection",
    "customization",
    "customized",
    "3d printed",
    "3d print",
    "fan art",
    "fanart",
    "cosplay",
    "costume",
    "displaying",
    "painting",
    "painted",
    "handmade",
    "crafting",
    "diy",
    "unboxing",
    "trading",
]

BAZUUYU_BEHAVIOR_CONTEXT_KEYWORDS = [
    "toy",
    "toys",
    "plush",
    "plushie",
    "stuffed animal",
    "collectible",
    "collectibles",
    "figurine",
    "figurines",
    "blind box",
    "blindbox",
    "merch",
    "merchandise",
    "fan art",
    "fandom",
    "cosplay",
]

BAZUUYU_ENTERTAINMENT_CONTEXT_KEYWORDS = [
    "gaming",
    "video game",
    "video games",
    "movie",
    "movies",
    "film",
    "films",
    "anime",
    "manga",
    "animation",
    "animated",
    "cartoon",
    "television",
]

# Character and intellectual-property signals.
BAZUUYU_CHARACTER_IP_KEYWORDS = [
    "mascot",
    "franchise",
    "animated character",
    "fictional character",
    "iconic character",
    "movie character",
    "game character",
    "character franchise",
    "game release",
    "game releases",
    "upcoming game",
    "upcoming games",
    "movie release",
    "movie releases",
    "film release",
    "film releases",
    "upcoming movie",
    "upcoming movies",
]

# Fandom and community signals.
BAZUUYU_FANDOM_KEYWORDS = [
    "fandom",
    "fan art",
    "fanart",
    "cosplay",
    "costume",
    "fan community",
    "community creativity",
    "creator community",
]

# Nostalgia signals can be valuable for collectible products.
BAZUUYU_NOSTALGIA_KEYWORDS = [
    "nostalgia",
    "nostalgic",
    "retro",
    "throwback",
    "anniversary",
    "re-release",
]

# Visual/aesthetic signals that may help product and character design.
BAZUUYU_VISUAL_KEYWORDS = [
    "visual",
    "aesthetic",
    "poster",
    "artwork",
    "design",
    "color",
    "style",
    "illustration",
    "visual style",
]

# Content/marketing signals.
BAZUUYU_CONTENT_KEYWORDS = [
    "trailer",
    "marketing",
    "viral",
    "meme",
    "social media",
    "content",
    "hype",
]