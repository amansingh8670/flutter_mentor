from collections import defaultdict

from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# DUPLICATE KEY
# ==========================================================

def chunk_key(chunk: RetrievedChunk) -> tuple:

    return (

        chunk.file,

        chunk.chunk_name,

        chunk.source,

    )


# ==========================================================
# EXTRA BOOSTS
# ==========================================================

def calculate_boost(chunk: RetrievedChunk) -> float:

    score = chunk.score

    name = chunk.chunk_name.lower()

    document = chunk.document.lower()

    # ------------------------------------------------------
    # Flutter reusable widgets
    # ------------------------------------------------------

    if "widget" in document:
        score += 5

    if name.endswith("page"):
        score += 4

    if name.endswith("screen"):
        score += 4

    if name.endswith("section"):
        score += 5

    if name.endswith("card"):
        score += 5

    if name.endswith("tile"):
        score += 5

    if name.endswith("dialog"):
        score += 5

    # ------------------------------------------------------
    # Theme
    # ------------------------------------------------------

    if "apptheme" in document:
        score += 10

    if "appcolors" in document:
        score += 10

    if "themeprovider" in document:
        score += 10

    if "color" in name:
        score += 4

    if "theme" in name:
        score += 4

    # ------------------------------------------------------
    # Flutter documentation
    # ------------------------------------------------------

    if chunk.source == "flutter_docs":
        score += 8

    # ------------------------------------------------------
    # Semantic generally stronger
    # ------------------------------------------------------

    if chunk.source == "semantic":
        score += 3

    return score


# ==========================================================
# RERANK
# ==========================================================

def rerank_results(
    semantic_chunks: list[RetrievedChunk],
    keyword_chunks: list[RetrievedChunk],
    flutter_doc_chunks: list[RetrievedChunk] | None = None,
    limit: int = 30,
) -> list[RetrievedChunk]:

    flutter_doc_chunks = flutter_doc_chunks or []

    merged: dict[tuple, RetrievedChunk] = {}

    duplicates = 0

    # ------------------------------------------------------
    # Merge
    # ------------------------------------------------------

    for chunk in (

        semantic_chunks

        + keyword_chunks

        + flutter_doc_chunks

    ):

        key = chunk_key(chunk)

        chunk.score = calculate_boost(chunk)

        if key not in merged:

            merged[key] = chunk

            continue

        duplicates += 1

        if chunk.score > merged[key].score:

            merged[key] = chunk

    # ------------------------------------------------------
    # Sort
    # ------------------------------------------------------

    ranked = sorted(

        merged.values(),

        key=lambda x: x.score,

        reverse=True,

    )

    # ------------------------------------------------------
    # Debug
    # ------------------------------------------------------

    print()

    print("=" * 80)

    print("RERANK SUMMARY")

    print("=" * 80)

    print(f"Semantic      : {len(semantic_chunks)}")

    print(f"Keyword       : {len(keyword_chunks)}")

    print(f"Flutter Docs  : {len(flutter_doc_chunks)}")

    print(f"Duplicates    : {duplicates}")

    print(f"Final Chunks  : {min(limit, len(ranked))}")

    print()

    print("Top Ranked")

    print("-" * 80)

    for chunk in ranked[:10]:

        print(

            f"[{chunk.source}] "

            f"{chunk.score:6.1f} | "

            f"{chunk.file} | "

            f"{chunk.chunk_name}"

        )

    return ranked[:limit]