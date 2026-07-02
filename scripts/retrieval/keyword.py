import os
import re

from scripts.config import REPO_PATH
from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# TOKENIZATION
# ==========================================================

def tokenize(text: str) -> list[str]:
    """
    Converts:

    AppBottomNav
    bottomNavigationBar
    app_bottom_nav
    Sign In

    into searchable tokens.
    """

    text = text.replace("_", " ")

    text = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        text,
    )

    text = text.lower()

    return re.findall(
        r"[a-z0-9]+",
        text,
    )


# ==========================================================
# CHUNK NAME
# ==========================================================

def extract_chunk_name(content: str) -> str:

    patterns = [

        r"class\s+(\w+)",
        r"enum\s+(\w+)",
        r"extension\s+(\w+)",
        r"mixin\s+(\w+)",
        r"typedef\s+(\w+)",
        r"final\s+(\w+)",

    ]

    for pattern in patterns:

        match = re.search(pattern, content)

        if match:
            return match.group(1)

    return "file"


# ==========================================================
# WORD COUNT
# ==========================================================

def count_occurrences(
    token: str,
    text: str,
) -> int:

    return len(

        re.findall(

            rf"\b{re.escape(token)}\b",

            text,

        )

    )


# ==========================================================
# SCORE FILE
# ==========================================================

def calculate_score(
    query_tokens: list[str],
    filename: str,
    content: str,
) -> int:

    score = 0

    filename_tokens = tokenize(filename)

    chunk_name = extract_chunk_name(content)

    class_tokens = tokenize(chunk_name)

    content_lower = content.lower()

    content_tokens = tokenize(content)

    token_set = set(content_tokens)

    # ------------------------------------------------------
    # filename
    # ------------------------------------------------------

    for token in query_tokens:

        if token in filename_tokens:
            score += 40

    # ------------------------------------------------------
    # widget/class name
    # ------------------------------------------------------

    for token in query_tokens:

        if token in class_tokens:
            score += 60

    # ------------------------------------------------------
    # exact occurrences
    # ------------------------------------------------------

    for token in query_tokens:

        score += (
            count_occurrences(
                token,
                content_lower,
            )
            * 6
        )

    # ------------------------------------------------------
    # token overlap
    # ------------------------------------------------------

    overlap = len(

        set(query_tokens)

        &

        token_set

    )

    score += overlap * 8

    # ------------------------------------------------------
    # imports
    # ------------------------------------------------------

    imports = re.findall(
        r"import\s+'([^']+)'",
        content,
    )

    for imp in imports:

        imp_tokens = tokenize(imp)

        for token in query_tokens:

            if token in imp_tokens:
                score += 8

    # ------------------------------------------------------
    # comments
    # ------------------------------------------------------

    comments = re.findall(
        r"//.*",
        content,
    )

    for comment in comments:

        comment = comment.lower()

        for token in query_tokens:

            if token in comment:
                score += 2

    return score


# ==========================================================
# SEARCH
# ==========================================================

def keyword_search(
    query: str,
    limit: int = 10,
) -> list[RetrievedChunk]:

    query_tokens = tokenize(query)

    results: list[RetrievedChunk] = []

    for root, _, files in os.walk(REPO_PATH):

        for file in files:

            if not file.endswith(".dart"):
                continue

            path = os.path.join(
                root,
                file,
            )

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8",
                ) as f:

                    content = f.read()

            except Exception:

                continue

            score = calculate_score(

                query_tokens,

                file,

                content,

            )

            if score == 0:
                continue

            results.append(

                RetrievedChunk(

                    file=file,

                    path=path,

                    chunk_name=extract_chunk_name(
                        content,
                    ),

                    chunk_type="keyword",

                    document=content,

                    source="keyword",

                    score=float(score),

                )

            )

    results.sort(
        key=lambda x: x.score,
        reverse=True,
    )

    return results[:limit]


# ==========================================================
# DEBUG
# ==========================================================

if __name__ == "__main__":

    while True:

        query = input(
            "\nKeyword Search (exit): "
        ).strip()

        if query.lower() == "exit":
            break

        results = keyword_search(query)

        print()

        if not results:

            print("No matches found.")

            continue

        for result in results:

            print(

                f"{int(result.score):4} | "

                f"{result.file} | "

                f"{result.chunk_name}"

            )