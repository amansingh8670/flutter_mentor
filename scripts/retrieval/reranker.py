from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# DUPLICATE KEY
# ==========================================================

def chunk_key(chunk: RetrievedChunk) -> tuple:

    return (
        chunk.file,
        chunk.chunk_name,
    )


# ==========================================================
# BOOST
# ==========================================================

def calculate_boost(chunk: RetrievedChunk) -> float:

    score = chunk.score

    name = chunk.chunk_name.lower()
    file = chunk.file.lower()
    doc = chunk.document.lower()

    # ------------------------------------------------------
    # Highly reusable UI
    # ------------------------------------------------------

    reusable = [
        "widget",
        "section",
        "card",
        "tile",
        "dialog",
        "bottomsheet",
        "item",
        "button",
        "banner",
        "header",
        "footer",
    ]

    if any(x in name for x in reusable):
        score += 40

    # ------------------------------------------------------
    # Theme
    # ------------------------------------------------------

    if "theme" in file:
        score += 35

    if "color" in file:
        score += 35

    if "provider" in file:
        score += 20

    # ------------------------------------------------------
    # Screens
    # ------------------------------------------------------

    if "page" in name:
        score += 12

    if "screen" in name:
        score += 12

    # ------------------------------------------------------
    # Flutter docs
    # ------------------------------------------------------

    if chunk.source == "flutter_docs":
        score += 15

    # ------------------------------------------------------
    # Semantic slightly preferred
    # ------------------------------------------------------

    if chunk.source == "semantic":
        score += 5

    # ------------------------------------------------------
    # Penalize very large chunks
    # ------------------------------------------------------

    words = len(doc.split())

    if words > 1200:
        score -= 50

    elif words > 900:
        score -= 30

    elif words > 700:
        score -= 15

    return score


# ==========================================================
# RERANK
# ==========================================================

def rerank_results(
    semantic_chunks: list[RetrievedChunk],
    keyword_chunks: list[RetrievedChunk],
    flutter_doc_chunks: list[RetrievedChunk] | None = None,
    limit: int = 8,
) -> list[RetrievedChunk]:

    flutter_doc_chunks = flutter_doc_chunks or []

    merged: dict[tuple, RetrievedChunk] = {}

    duplicates = 0

    for chunk in (
        semantic_chunks
        + keyword_chunks
        + flutter_doc_chunks
    ):

        chunk.score = calculate_boost(chunk)

        key = chunk_key(chunk)

        if key not in merged:

            merged[key] = chunk

            continue

        duplicates += 1

        if chunk.score > merged[key].score:
            merged[key] = chunk

    ranked = sorted(
        merged.values(),
        key=lambda c: c.score,
        reverse=True,
    )

    # ------------------------------------------------------
    # Maximum 1 chunk per file
    # ------------------------------------------------------

    filtered = []

    seen_files = set()

    for chunk in ranked:

        if chunk.file in seen_files:
            continue

        filtered.append(chunk)

        seen_files.add(chunk.file)

        if len(filtered) >= limit:
            break

    print()
    print("=" * 80)
    print("RERANK SUMMARY")
    print("=" * 80)

    print(f"Semantic      : {len(semantic_chunks)}")
    print(f"Keyword       : {len(keyword_chunks)}")
    print(f"Flutter Docs  : {len(flutter_doc_chunks)}")
    print(f"Duplicates    : {duplicates}")
    print(f"Final Chunks  : {len(filtered)}")

    print()
    print("Top Ranked")
    print("-" * 80)

    for chunk in filtered:

        print(
            f"[{chunk.source}] "
            f"{chunk.score:6.1f} | "
            f"{chunk.file} | "
            f"{chunk.chunk_name}"
        )

    return filtered