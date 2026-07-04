# ==========================================================
# FORMATTER
# ==========================================================

import re

from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# CONFIG
# ==========================================================

MAX_CHUNK_CHARS = 700


# ==========================================================
# CLEAN CODE
# ==========================================================

def clean_document(document: str) -> str:
    """
    Removes noise that rarely helps the LLM.
    """

    lines = []

    previous_blank = False

    for line in document.splitlines():

        stripped = line.strip()

        # Remove imports
        if stripped.startswith("import "):
            continue

        if stripped.startswith("export "):
            continue

        # Compress blank lines
        if stripped == "":

            if previous_blank:
                continue

            previous_blank = True

        else:

            previous_blank = False

        lines.append(line)

    cleaned = "\n".join(lines)

    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned,
    )

    return cleaned.strip()


# ==========================================================
# TRUNCATE
# ==========================================================

def truncate_document(
    document: str,
    limit: int = MAX_CHUNK_CHARS,
) -> str:
    """
    Limits the amount of code sent to the LLM.
    """

    if len(document) <= limit:
        return document

    return (
        document[:limit]
        + "\n\n"
        + "... [TRUNCATED]"
    )


# ==========================================================
# SINGLE CHUNK
# ==========================================================

def format_chunk(
    chunk: RetrievedChunk,
) -> str:
    """
    Formats one retrieved chunk.
    """

    document = clean_document(
        chunk.document
    )

    document = truncate_document(
        document
    )

    return f"""
FILE: {chunk.file}
CHUNK: {chunk.chunk_name}
TYPE: {chunk.chunk_type}
SOURCE: {chunk.source}
SCORE: {chunk.score:.1f}

{document}
""".strip()


# ==========================================================
# MULTIPLE CHUNKS
# ==========================================================

def format_chunks(
    chunks: list[RetrievedChunk],
) -> str:
    """
    Formats all retrieved chunks.
    """

    if not chunks:
        return ""

    formatted = "\n\n" + ("=" * 80) + "\n\n"

    formatted += ("\n\n" + ("=" * 80) + "\n\n").join(

        format_chunk(chunk)

        for chunk in chunks

    )

    return formatted


# ==========================================================
# DEBUG OUTPUT
# ==========================================================

def print_summary(
    chunks: list[RetrievedChunk],
) -> None:
    """
    Prints retrieved chunk summary.
    """

    print()
    print("=" * 80)
    print("RETRIEVED FILES")
    print("=" * 80)

    total_chars = 0

    for chunk in chunks:

        chars = min(
            len(chunk.document),
            MAX_CHUNK_CHARS,
        )

        total_chars += chars

        print(
            f"[{chunk.source:<9}] "
            f"{chunk.file:<35} "
            f"{chars:>5} chars"
        )

    print("-" * 80)
    print(f"Chunks      : {len(chunks)}")
    print(f"Context Size: {total_chars:,} chars")
    print(
        f"Approx Tokens: {total_chars // 4:,}"
    )


# ==========================================================
# PREVIEW
# ==========================================================

def preview_context(
    chunks: list[RetrievedChunk],
    max_chars: int = 3000,
) -> None:
    """
    Preview context before sending to the LLM.
    """

    context = format_chunks(
        chunks
    )

    print()
    print("=" * 80)
    print("RETRIEVED CONTEXT")
    print("=" * 80)

    print(
        context[:max_chars]
    )


# ==========================================================
# GROUP BY FILE
# ==========================================================

def group_by_file(
    chunks: list[RetrievedChunk],
) -> dict[str, list[RetrievedChunk]]:
    """
    Groups chunks by filename.
    """

    grouped: dict[
        str,
        list[RetrievedChunk],
    ] = {}

    for chunk in chunks:

        grouped.setdefault(
            chunk.file,
            [],
        ).append(chunk)

    return grouped