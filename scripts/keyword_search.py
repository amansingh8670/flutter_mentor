import os
import re

REPO_PATH = "/Users/amansingh/Desktop/Practice/chef_ai_mobile/lib"


# ==========================================================
# TOKENIZATION
# ==========================================================

def tokenize(text):
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
        text
    )

    text = text.lower()

    return re.findall(
        r"[a-z0-9]+",
        text
    )


# ==========================================================
# CHUNK NAME
# ==========================================================

def extract_chunk_name(content):

    patterns = [

        r"class\s+(\w+)",
        r"enum\s+(\w+)",
        r"extension\s+(\w+)",
        r"mixin\s+(\w+)",
        r"final\s+(\w+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            content
        )

        if match:
            return match.group(1)

    return "file"


# ==========================================================
# WORD BOUNDARY COUNT
# ==========================================================

def count_word_occurrences(
    token,
    text
):

    return len(
        re.findall(
            rf"\b{re.escape(token)}\b",
            text
        )
    )


# ==========================================================
# SCORE
# ==========================================================

def calculate_score(
    query_tokens,
    filename,
    content
):

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
    # class/widget name
    # ------------------------------------------------------

    for token in query_tokens:

        if token in class_tokens:
            score += 50

    # ------------------------------------------------------
    # exact word matches
    # ------------------------------------------------------

    for token in query_tokens:

        occurrences = count_word_occurrences(
            token,
            content_lower
        )

        score += occurrences * 6

    # ------------------------------------------------------
    # token presence
    # ------------------------------------------------------

    overlap = len(
        set(query_tokens) &
        token_set
    )

    score += overlap * 8

    # ------------------------------------------------------
    # comments
    # ------------------------------------------------------

    comments = re.findall(
        r"//.*",
        content
    )

    for comment in comments:

        comment = comment.lower()

        for token in query_tokens:

            if token in comment:
                score += 2

    # ------------------------------------------------------
    # imports
    # ------------------------------------------------------

    imports = re.findall(
        r"import\s+'([^']+)'",
        content
    )

    for imp in imports:

        imp_tokens = tokenize(imp)

        for token in query_tokens:

            if token in imp_tokens:
                score += 8

    return score


# ==========================================================
# SEARCH
# ==========================================================

def search_repo(
    query,
    repo_path=REPO_PATH,
    limit=10
):

    query_tokens = tokenize(query)

    results = []

    for root, _, files in os.walk(repo_path):

        for file in files:

            if not file.endswith(".dart"):
                continue

            full_path = os.path.join(
                root,
                file
            )

            try:

                with open(
                    full_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    content = f.read()

            except Exception:
                continue

            score = calculate_score(
                query_tokens,
                file,
                content
            )

            if score == 0:
                continue

            results.append({

                "file": file,

                "path": full_path,

                "chunk_name": extract_chunk_name(
                    content
                ),

                "document": content,

                "score": score
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:limit]


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    while True:

        query = input(
            "\nKeyword Search (exit): "
        ).strip()

        if query.lower() == "exit":
            break

        results = search_repo(query)

        print()

        if not results:

            print("No matches found.")

            continue

        for result in results:

            print(
                f"{result['score']:4} | "
                f"{result['file']} | "
                f"{result['chunk_name']}"
            )