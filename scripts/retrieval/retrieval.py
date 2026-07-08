from collections import defaultdict

from scripts.config import (
    SEMANTIC_RESULTS,
    KEYWORD_RESULTS,
    MAX_CONTEXT_CHUNKS,
)

from scripts.retrieval.semantic import semantic_search
from scripts.retrieval.keyword import keyword_search
from scripts.retrieval.reranker import rerank_results
from scripts.retrieval.formatter import format_chunks
from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# SINGLE QUERY
# ==========================================================

def retrieve_context(
    question: str,
    semantic_limit: int = SEMANTIC_RESULTS,
    keyword_limit: int = KEYWORD_RESULTS,
    return_string: bool = True,
):

    semantic_results = semantic_search(
        question,
        limit=semantic_limit,
    )

    keyword_results = keyword_search(
        question,
        limit=keyword_limit,
    )

    merged = rerank_results(
        semantic_results,
        keyword_results,
    )

    merged = merged[:MAX_CONTEXT_CHUNKS]

    if return_string:
        return format_chunks(merged)

    return merged


# ==========================================================
# MULTI QUERY
# ==========================================================

def retrieve_multiple_context(
    queries: list[str],
    semantic_limit: int = SEMANTIC_RESULTS,
    keyword_limit: int = KEYWORD_RESULTS,
):

    print()
    print("=" * 80)
    print("HYBRID RETRIEVAL")
    print("=" * 80)

    weighted_chunks: dict[tuple, RetrievedChunk] = {}

    # Earlier queries are more important than later generic ones
    total_queries = max(len(queries), 1)

    for index, query in enumerate(queries):

        print(f"\n[{index + 1}/{len(queries)}] {query}")

        semantic = semantic_search(
            query,
            limit=semantic_limit,
        )

        keyword = keyword_search(
            query,
            limit=keyword_limit,
        )

        merged = rerank_results(
            semantic,
            keyword,
            limit=max(
                semantic_limit,
                keyword_limit,
            ),
        )

        #
        # Earlier queries receive larger boost
        #

        query_weight = (
            total_queries - index
        ) / total_queries

        for chunk in merged:

            boosted = RetrievedChunk(
                file=chunk.file,
                path=chunk.path,
                chunk_name=chunk.chunk_name,
                chunk_type=chunk.chunk_type,
                document=chunk.document,
                source=chunk.source,
                score=chunk.score + (query_weight * 100),
            )

            key = (
                boosted.path,
                boosted.chunk_name,
            )

            if (
                key not in weighted_chunks
                or boosted.score > weighted_chunks[key].score
            ):
                weighted_chunks[key] = boosted

    #
    # Final rerank
    #

    final_chunks = sorted(
        weighted_chunks.values(),
        key=lambda c: c.score,
        reverse=True,
    )

    #
    # Avoid returning 6 chunks from same file
    #

    file_counts = defaultdict(int)

    filtered: list[RetrievedChunk] = []

    for chunk in final_chunks:

        if file_counts[chunk.file] >= 2:
            continue

        filtered.append(chunk)

        file_counts[chunk.file] += 1

        if len(filtered) >= MAX_CONTEXT_CHUNKS:
            break

    print()

    print("=" * 80)
    print("FINAL RETRIEVAL")
    print("=" * 80)

    print(f"Queries       : {len(queries)}")
    print(f"Unique Chunks : {len(filtered)}")

    print()

    print("Selected")

    print("-" * 80)

    for chunk in filtered:

        print(
            f"[{chunk.source}] "
            f"{chunk.score:7.1f} | "
            f"{chunk.file} | "
            f"{chunk.chunk_name}"
        )

    return format_chunks(filtered)


# ==========================================================
# DEBUG
# ==========================================================

def debug_search(
    query: str,
):

    results = retrieve_context(
        query,
        return_string=False,
    )

    for chunk in results:

        print()

        print("=" * 80)

        print(chunk.file)

        print(chunk.chunk_name)

        print(chunk.source)

        print(chunk.score)

        print("=" * 80)

        print(chunk.document[:700])