from scripts.retrieval.semantic import semantic_search
from scripts.retrieval.keyword import keyword_search
from scripts.retrieval.reranker import rerank_results
from scripts.retrieval.formatter import format_chunks

# Maximum chunks allowed into the final prompt.
MAX_FINAL_CHUNKS = 6


# ==========================================================
# SINGLE QUERY
# ==========================================================

def retrieve_context(
    question: str,
    semantic_limit: int = 5,
    keyword_limit: int = 5,
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

    merged = merged[:MAX_FINAL_CHUNKS]

    if return_string:
        return format_chunks(merged)

    return merged


# ==========================================================
# MULTI QUERY
# ==========================================================

def retrieve_multiple_context(
    queries: list[str],
    semantic_limit: int = 2,
    keyword_limit: int = 2,
):
    all_results = []

    print()
    print("=" * 80)
    print("HYBRID RETRIEVAL")
    print("=" * 80)

    for index, query in enumerate(queries, start=1):

        print(f"\n[{index}/{len(queries)}] {query}")

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
        )

        all_results.extend(merged)

    merged = rerank_results(
        semantic_chunks=all_results,
        keyword_chunks=[],
    )

    merged = merged[:MAX_FINAL_CHUNKS]

    print(f"\nUnique chunks : {len(merged)}")

    return format_chunks(merged)


# ==========================================================
# DEBUG
# ==========================================================

def debug_search(query: str):

    results = retrieve_context(
        query,
        return_string=False,
    )

    for chunk in results:

        print("\n" + "=" * 80)
        print(chunk.file)
        print(chunk.chunk_name)
        print(chunk.source)
        print("=" * 80)

        print(chunk.document[:700])