from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


_model = None


def get_embedding_model():
    """
    Load the sentence-transformer model only when needed.
    """

    global _model

    if _model is None:
        _model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return _model


def deduplicate_news_articles(
    articles: list[dict],
    similarity_threshold: float = 0.72,
) -> list[dict]:
    """
    Group semantically similar news headlines.

    Returns one representative article per detected story,
    together with the articles that belong to that story.
    """

    if not articles:
        return []

    model = get_embedding_model()

    titles = [
        article.get("title", "")
        for article in articles
    ]

    embeddings = model.encode(
        titles,
        normalize_embeddings=True,
    )

    similarity_matrix = cosine_similarity(
        embeddings
    )

    used = set()
    stories = []

    for i, article in enumerate(articles):

        if i in used:
            continue

        used.add(i)

        related_articles = [article]

        for j in range(i + 1, len(articles)):

            if j in used:
                continue

            similarity = similarity_matrix[i][j]

            if similarity >= similarity_threshold:
                used.add(j)
                related_articles.append(
                    articles[j]
                )

        stories.append({
            "representative_title": article.get(
                "title"
            ),
            "article_count": len(
                related_articles
            ),
            "publishers": sorted({
                item.get("publisher")
                for item in related_articles
                if item.get("publisher")
            }),
            "articles": related_articles,
        })

    return stories