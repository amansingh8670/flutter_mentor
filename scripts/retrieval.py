import chromadb
import requests

from keyword_search import search_repo

EMBED_URL = "http://localhost:11434/api/embeddings"

client = chromadb.PersistentClient(
    path="./data/chroma"
)

collection = client.get_collection(
    "flutter_repo"
)


# ==========================================================
# EMBEDDINGS
# ==========================================================

def get_embedding(text):

    response = requests.post(
        EMBED_URL,
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )

    response.raise_for_status()

    return response.json()["embedding"]


# ==========================================================
# FORMAT CHUNK
# ==========================================================

def format_chunk(chunk):

    return f"""
FILE: {chunk["file"]}
CHUNK: {chunk["chunk_name"]}

{chunk["document"]}
"""


# ==========================================================
# SEMANTIC SEARCH
# ==========================================================

def semantic_search(
    question,
    n_results=5
):

    embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    retrieved = []

    print()
    print("=" * 80)
    print(f"SEMANTIC RESULTS : {question}")
    print("=" * 80)

    for index, metadata in enumerate(metadatas):

        if metadata is None:
            continue

        if index >= len(documents):
            continue

        chunk = {
            "file": metadata.get("file", "Unknown"),
            "chunk_name": metadata.get("chunk_name", "Unknown"),
            "document": documents[index],
            "source": "semantic"
        }

        retrieved.append(chunk)

        print(
            f"{index+1}. "
            f"{chunk['file']} | "
            f"{chunk['chunk_name']}"
        )

    return retrieved


# ==========================================================
# KEYWORD SEARCH
# ==========================================================

def keyword_retrieval(
    query,
    limit=3
):

    print()
    print("=" * 80)
    print(f"KEYWORD RESULTS : {query}")
    print("=" * 80)

    results = search_repo(
        query,
        limit=limit
    )

    chunks = []

    for result in results:

        print(
            f"{result['score']:3} | "
            f"{result['file']} | "
            f"{result['chunk_name']}"
        )

        chunks.append(
            {
                "file": result["file"],
                "chunk_name": result["chunk_name"],
                "document": result["document"],
                "source": "keyword"
            }
        )

    return chunks


# ==========================================================
# SINGLE QUERY
# ==========================================================

def retrieve_context(
    question,
    n_results=5,
    return_string=False
):

    semantic = semantic_search(
        question,
        n_results
    )

    keyword = keyword_retrieval(
        question,
        limit=3
    )

    seen = set()

    merged = []

    for chunk in semantic + keyword:

        key = (
            chunk["file"],
            chunk["chunk_name"]
        )

        if key in seen:
            continue

        seen.add(key)
        merged.append(chunk)

    if return_string:

        return "\n\n".join(
            format_chunk(chunk)
            for chunk in merged
        )

    return merged


# ==========================================================
# MULTI QUERY (WEIGHTED HYBRID)
# ==========================================================

def retrieve_multiple_context(
    queries,
    n_results_per_query=2
):

    seen = set()

    merged = []

    duplicates = 0

    print()
    print("=" * 80)
    print("WEIGHTED HYBRID RETRIEVAL")
    print("=" * 80)

    for index, query in enumerate(queries):

        query_lower = query.lower()

        # --------------------------------------------------
        # Dynamic weighting
        # --------------------------------------------------

        semantic_limit = 2
        keyword_limit = 2

        # Screen names
        if any(
            word in query_lower
            for word in [
                "login",
                "signup",
                "register",
                "dashboard",
                "home",
                "profile",
                "recipe"
            ]
        ):

            semantic_limit = 5
            keyword_limit = 5

        # Widgets
        elif any(
            word in query_lower
            for word in [
                "button",
                "text field",
                "password",
                "card",
                "navigation",
                "checkbox",
                "logo"
            ]
        ):

            semantic_limit = 3
            keyword_limit = 2

        # Theme
        elif "theme" in query_lower:

            semantic_limit = 1
            keyword_limit = 1

        print()
        print("-" * 80)
        print(
            f"Query {index+1}: {query}"
        )
        print(
            f"Semantic={semantic_limit}  "
            f"Keyword={keyword_limit}"
        )

        semantic = semantic_search(
            query,
            semantic_limit
        )

        keyword = keyword_retrieval(
            query,
            keyword_limit
        )

        for chunk in semantic + keyword:

            key = (
                chunk["file"],
                chunk["chunk_name"]
            )

            if key in seen:
                duplicates += 1
                continue

            seen.add(key)

            merged.append(chunk)

    # --------------------------------------------------
    # Light reranking
    # --------------------------------------------------

    def score(chunk):

        score = 0

        filename = chunk["file"].lower()

        if "widget" in filename:
            score += 30

        if "section" in filename:
            score += 20

        if "component" in filename:
            score += 20

        if "theme" in filename:
            score += 15

        if "color" in filename:
            score += 15

        if "provider" in filename:
            score += 10

        if "page" in filename:
            score -= 10

        return score

    merged.sort(
        key=score,
        reverse=True
    )

    print()
    print("=" * 80)
    print("MERGE SUMMARY")
    print("=" * 80)

    print(f"Queries searched : {len(queries)}")
    print(f"Unique chunks    : {len(merged)}")
    print(f"Duplicates       : {duplicates}")

    semantic_count = sum(
        1
        for chunk in merged
        if chunk["source"] == "semantic"
    )

    keyword_count = sum(
        1
        for chunk in merged
        if chunk["source"] == "keyword"
    )

    print(f"Semantic chunks  : {semantic_count}")
    print(f"Keyword chunks   : {keyword_count}")

    print()
    print("TOP RETRIEVED FILES")

    for chunk in merged[:15]:

        print(
            f"[{chunk['source']}] "
            f"{chunk['file']} | "
            f"{chunk['chunk_name']}"
        )

    return "\n\n".join(
        format_chunk(chunk)
        for chunk in merged[:20]
    )


# ==========================================================
# DEBUG
# ==========================================================

def debug_search(query):

    context = retrieve_context(
        query,
        return_string=False
    )

    for chunk in context:

        print()

        print("=" * 60)

        print(chunk["source"].upper())

        print(chunk["file"])

        print(chunk["chunk_name"])

        print("=" * 60)

        print(chunk["document"][:500])