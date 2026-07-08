import chromadb

from scripts.config import (
    CHROMA_PATH,
    REPO_COLLECTION,
    SEMANTIC_RESULTS,
)

from scripts.llm.embeddings import get_embedding
from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# CHROMA
# ==========================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH,
)

collection = client.get_collection(
    REPO_COLLECTION,
)


# ==========================================================
# HELPERS
# ==========================================================

def _boost_score(
    query: str,
    metadata: dict,
    distance: float,
) -> float:
    """
    Apply simple heuristics to improve semantic ranking.
    """

    query = query.lower()

    file_name = metadata.get("file", "").lower()
    chunk_name = metadata.get("chunk_name", "").lower()
    path = metadata.get("path", "").lower()

    score = -distance

    if query in file_name:
        score += 0.40

    if query in chunk_name:
        score += 0.60

    if query in path:
        score += 0.20

    return score


# ==========================================================
# SEMANTIC SEARCH
# ==========================================================

def semantic_search(
    query: str,
    limit: int = SEMANTIC_RESULTS,
) -> list[RetrievedChunk]:
    """
    Semantic retrieval over the indexed Flutter repository.
    """

    embedding = get_embedding(query)

    # retrieve more candidates than needed
    raw = collection.query(
        query_embeddings=[embedding],
        n_results=max(limit * 4, 10),
    )

    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]

    chunks: list[RetrievedChunk] = []

    seen = set()

    for i, metadata in enumerate(metadatas):

        if not metadata:
            continue

        key = (
            metadata.get("path"),
            metadata.get("chunk_name"),
        )

        if key in seen:
            continue

        seen.add(key)

        document = (
            documents[i]
            if i < len(documents)
            else ""
        )

        distance = (
            distances[i]
            if i < len(distances)
            else 999.0
        )

        score = _boost_score(
            query,
            metadata,
            distance,
        )

        chunks.append(
            RetrievedChunk(
                file=metadata.get("file", ""),
                path=metadata.get("path", ""),
                chunk_name=metadata.get(
                    "chunk_name",
                    "",
                ),
                chunk_type=metadata.get(
                    "chunk_type",
                    "",
                ),
                document=document,
                source="semantic",
                score=score,
            )
        )

    chunks.sort(
        key=lambda x: x.score,
        reverse=True,
    )

    return chunks[:limit]


# ==========================================================
# DEBUG
# ==========================================================

if __name__ == "__main__":

    while True:

        query = input(
            "\nSemantic Search (exit): "
        ).strip()

        if query.lower() == "exit":
            break

        results = semantic_search(query)

        print()

        for result in results:

            print(
                f"{result.score:8.2f} | "
                f"{result.file:35} | "
                f"{result.chunk_name}"
            )