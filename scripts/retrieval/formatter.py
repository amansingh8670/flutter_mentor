# ==========================================================
# FORMATTER
# ==========================================================

from scripts.models.retrieval_models import RetrievedChunk


# ==========================================================
# SINGLE CHUNK
# ==========================================================

def format_chunk(chunk: RetrievedChunk) -> str:
    """
    Formats a single retrieved chunk for prompt injection.
    """

    return f"""
FILE: {chunk.file}
PATH: {chunk.path}
TYPE: {chunk.chunk_type}
CHUNK: {chunk.chunk_name}

{chunk.document}
""".strip()


# ==========================================================
# MULTIPLE CHUNKS
# ==========================================================

def format_chunks(chunks: list[RetrievedChunk]) -> str:
    """
    Formats multiple retrieved chunks.
    """

    if not chunks:
        return ""

    return "\n\n".join(
        format_chunk(chunk)
        for chunk in chunks
    )


# ==========================================================
# DEBUG OUTPUT
# ==========================================================

def print_summary(chunks: list[RetrievedChunk]) -> None:
    """
    Prints retrieved chunk summary.
    """

    print()
    print("=" * 80)
    print("RETRIEVED FILES")
    print("=" * 80)

    for chunk in chunks:

        print(
            f"[{chunk.source}] "
            f"{chunk.file} | "
            f"{chunk.chunk_name}"
        )


# ==========================================================
# PREVIEW
# ==========================================================

def preview_context(
    chunks: list[RetrievedChunk],
    max_chars: int = 3000,
) -> None:
    """
    Prints first few thousand characters of context.
    """

    context = format_chunks(chunks)

    print()
    print("=" * 80)
    print("RETRIEVED CONTEXT")
    print("=" * 80)

    print(context[:max_chars])


# ==========================================================
# GROUP BY FILE
# ==========================================================

def group_by_file(
    chunks: list[RetrievedChunk],
) -> dict[str, list[RetrievedChunk]]:
    """
    Groups retrieved chunks by filename.
    """

    grouped: dict[str, list[RetrievedChunk]] = {}

    for chunk in chunks:

        grouped.setdefault(
            chunk.file,
            [],
        ).append(chunk)

    return grouped