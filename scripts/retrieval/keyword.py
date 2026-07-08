import os
import re

from scripts.config import REPO_PATH
from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# HELPERS
# ==========================================================

DECLARATION_PATTERNS = [
    r"class\s+(\w+)",
    r"enum\s+(\w+)",
    r"extension\s+(\w+)",
    r"mixin\s+(\w+)",
    r"typedef\s+(\w+)",
    r"final\s+(\w+)",
]


def tokenize(text: str) -> list[str]:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text.replace("_", " "))
    return re.findall(r"[a-z0-9]+", text.lower())


def extract_chunk_name(content: str) -> str:
    for pattern in DECLARATION_PATTERNS:
        if match := re.search(pattern, content):
            return match.group(1)
    return "file"


def count(token: str, text: str) -> int:
    return len(re.findall(rf"\b{re.escape(token)}\b", text))


# ==========================================================
# SCORING
# ==========================================================

def calculate_score(
    query_tokens: list[str],
    filename: str,
    content: str,
) -> int:

    score = 0

    filename_tokens = set(tokenize(filename))
    class_tokens = set(tokenize(extract_chunk_name(content)))
    content_tokens = tokenize(content)
    token_set = set(content_tokens)
    content_lower = content.lower()

    imports = " ".join(
        re.findall(r"import\s+'([^']+)'", content)
    ).lower()

    comments = " ".join(
        re.findall(r"//.*", content)
    ).lower()

    for token in query_tokens:

        if token in filename_tokens:
            score += 40

        if token in class_tokens:
            score += 60

        if token in token_set:
            score += 8

        score += count(token, content_lower) * 6

        if token in imports:
            score += 8

        if token in comments:
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

            path = os.path.join(root, file)

            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            score = calculate_score(
                query_tokens,
                file,
                content,
            )

            if score <= 0:
                continue

            results.append(
                RetrievedChunk(
                    file=file,
                    path=path,
                    chunk_name=extract_chunk_name(content),
                    chunk_type="keyword",
                    document=content,
                    source="keyword",
                    score=float(score),
                )
            )

    results.sort(key=lambda x: x.score, reverse=True)

    return results[:limit]


# ==========================================================
# DEBUG
# ==========================================================

if __name__ == "__main__":

    while True:

        query = input("\nKeyword Search (exit): ").strip()

        if query.lower() == "exit":
            break

        results = keyword_search(query)

        if not results:
            print("\nNo matches found.")
            continue

        print()

        for result in results:
            print(
                f"{int(result.score):4} | "
                f"{result.file} | "
                f"{result.chunk_name}"
            )