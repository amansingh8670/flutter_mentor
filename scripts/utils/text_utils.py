import re
from typing import List


# ==========================================================
# TOKENIZATION
# ==========================================================

def tokenize(text: str) -> List[str]:
    """
    Converts:

    AppBottomNav
    app_bottom_nav
    bottomNavigationBar
    Sign In

    into searchable tokens.
    """

    if not text:
        return []

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
# NORMALIZATION
# ==========================================================

def normalize(text: str) -> str:
    """
    Lowercase + collapse whitespace.
    """

    if not text:
        return ""

    return " ".join(text.lower().split())


# ==========================================================
# WORD COUNT
# ==========================================================

def count_word_occurrences(
    word: str,
    text: str,
) -> int:
    """
    Whole-word occurrence count.
    """

    if not word or not text:
        return 0

    return len(
        re.findall(
            rf"\b{re.escape(word.lower())}\b",
            text.lower(),
        )
    )


# ==========================================================
# CLASS / WIDGET NAME EXTRACTION
# ==========================================================

def extract_chunk_name(content: str) -> str:
    """
    Extract primary Dart symbol from a file.
    """

    patterns = [
        r"class\s+(\w+)",
        r"enum\s+(\w+)",
        r"extension\s+(\w+)",
        r"mixin\s+(\w+)",
        r"typedef\s+(\w+)",
        r"final\s+(\w+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            content,
        )

        if match:
            return match.group(1)

    return "file"


# ==========================================================
# IMPORT EXTRACTION
# ==========================================================

def extract_imports(content: str) -> List[str]:

    return re.findall(
        r"import\s+'([^']+)'",
        content,
    )


# ==========================================================
# COMMENT EXTRACTION
# ==========================================================

def extract_comments(content: str) -> List[str]:

    return re.findall(
        r"//.*",
        content,
    )


# ==========================================================
# SPLIT LARGE TEXT
# ==========================================================

def split_text(
    text: str,
    max_chars: int = 1500,
) -> List[str]:
    """
    Generic character splitter used during indexing.
    """

    if len(text) <= max_chars:
        return [text]

    return [
        text[i:i + max_chars]
        for i in range(0, len(text), max_chars)
    ]


# ==========================================================
# CLEAN WHITESPACE
# ==========================================================

def clean_text(text: str) -> str:

    return re.sub(
        r"\n{3,}",
        "\n\n",
        text.strip(),
    )