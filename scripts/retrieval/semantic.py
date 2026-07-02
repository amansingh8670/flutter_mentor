import chromadb

from scripts.config import CHROMA_PATH
from scripts.llm.embeddings import get_embedding
from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# CHROMA
# ==========================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    "flutter_repo"
)


# ==========================================================
# SEMANTIC SEARCH
# ==========================================================

def semantic_search(
    query: str,
    limit: int = 5,
) -> list[RetrievedChunk]:
    """
    Performs vector search against the indexed Flutter repository.
    """

    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=limit,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks: list[RetrievedChunk] = []

    for index, metadata in enumerate(metadatas):

        if metadata is None:
            continue

        document = (
            documents[index]
            if index < len(documents)
            else ""
        )

        distance = (
            distances[index]
            if index < len(distances)
            else 0.0
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
                score=1.0 - float(distance),
            )
        )

    return chunks


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
                f"{result.score:.3f} | "
                f"{result.file} | "
                f"{result.chunk_name}"
            )