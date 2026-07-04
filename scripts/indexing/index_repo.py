import os
import re
import uuid

import chromadb

from scripts.config import (
    CHROMA_PATH,
    REPO_COLLECTION,
    REPO_PATH,
)

from scripts.llm.embeddings import get_embedding


# ==========================================================
# CHROMA
# ==========================================================

client = chromadb.PersistentClient(path=CHROMA_PATH)

try:
    client.delete_collection(REPO_COLLECTION)
    print("Old repository collection deleted.")
except Exception:
    pass

collection = client.create_collection(REPO_COLLECTION)


# ==========================================================
# DECLARATIONS
# ==========================================================

DECLARATION_PATTERN = re.compile(
    r"^(class|enum|extension|mixin)\s+(\w+)|^final\s+(\w+)",
    re.MULTILINE,
)


# ==========================================================
# UTILITIES
# ==========================================================

MAX_CHUNK_SIZE = 3500


def split_if_needed(text: str) -> list[str]:
    """
    Only split extremely large chunks.

    Most Flutter classes stay intact.
    """

    if len(text) <= MAX_CHUNK_SIZE:
        return [text]

    parts = []

    start = 0

    while start < len(text):

        end = min(start + MAX_CHUNK_SIZE, len(text))

        newline = text.rfind("\n", start, end)

        if newline > start:
            end = newline

        parts.append(text[start:end])

        start = end

    return parts


# ==========================================================
# SEMANTIC EXTRACTION
# ==========================================================

def extract_semantic_chunks(content: str):

    matches = list(
        DECLARATION_PATTERN.finditer(content)
    )

    if not matches:

        return [
            {
                "name": "file",
                "type": "file",
                "content": content,
            }
        ]

    chunks = []

    for i, match in enumerate(matches):

        start = match.start()

        end = (
            matches[i + 1].start()
            if i < len(matches) - 1
            else len(content)
        )

        code = content[start:end].strip()

        if match.group(1):

            chunk_type = match.group(1)
            chunk_name = match.group(2)

        else:

            chunk_type = "provider"
            chunk_name = match.group(3)

        chunks.append(
            {
                "name": chunk_name,
                "type": chunk_type,
                "content": code,
            }
        )

    return chunks


# ==========================================================
# INDEX FILE
# ==========================================================

def index_file(path: str):

    filename = os.path.basename(path)

    relative_path = os.path.relpath(
        path,
        REPO_PATH,
    )

    print(f"\n📄 {relative_path}")

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        content = f.read()

    semantic_chunks = extract_semantic_chunks(content)

    chunk_count = 0

    for chunk in semantic_chunks:

        for index, piece in enumerate(
            split_if_needed(chunk["content"])
        ):

            embedding_text = f"""
FILE: {filename}

PATH: {relative_path}

TYPE: {chunk["type"]}

NAME: {chunk["name"]}

{piece}
""".strip()

            embedding = get_embedding(
                embedding_text
            )

            collection.add(

                ids=[str(uuid.uuid4())],

                documents=[embedding_text],

                embeddings=[embedding],

                metadatas=[
                    {
                        "source": "repository",
                        "file": filename,
                        "path": relative_path,
                        "chunk_name": chunk["name"],
                        "chunk_type": chunk["type"],
                        "chunk_index": index,
                    }
                ],
            )

            chunk_count += 1

    print(
        f"   Semantic Chunks : {len(semantic_chunks)}"
    )

    print(
        f"   Indexed Pieces  : {chunk_count}"
    )


# ==========================================================
# INDEX REPOSITORY
# ==========================================================

def index_repository():

    total_files = 0

    print("=" * 80)
    print("INDEXING FLUTTER REPOSITORY")
    print("=" * 80)

    for root, dirs, files in os.walk(REPO_PATH):

        dirs[:] = [
            d
            for d in dirs
            if d not in (
                ".git",
                ".dart_tool",
                "build",
            )
        ]

        for file in files:

            if not file.endswith(".dart"):
                continue

            index_file(
                os.path.join(root, file)
            )

            total_files += 1

    print()
    print("=" * 80)
    print("INDEX COMPLETE")
    print("=" * 80)

    print(f"Files Indexed : {total_files}")
    print(f"Total Chunks  : {collection.count()}")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    index_repository()