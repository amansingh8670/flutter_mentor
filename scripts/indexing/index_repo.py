import os
import re
import uuid

import chromadb

from scripts.config import (
    CHROMA_PATH,
    REPO_COLLECTION,
    REPO_PATH,
    CHUNK_SIZE,
)

from scripts.llm.embeddings import get_embedding


# ==========================================================
# CHROMA
# ==========================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

try:
    client.delete_collection(REPO_COLLECTION)
    print("Old repository collection deleted.")
except Exception:
    pass

collection = client.create_collection(
    REPO_COLLECTION
)


# ==========================================================
# CLASS / PROVIDER EXTRACTION
# ==========================================================

DECLARATION_PATTERN = re.compile(
    r"^(class|enum|extension)\s+(\w+)|^final\s+(\w+)",
    re.MULTILINE
)


# ==========================================================
# SPLIT LARGE CHUNKS
# ==========================================================

def split_large_chunk(text):

    chunks = []

    for i in range(0, len(text), CHUNK_SIZE):

        chunks.append(
            text[i:i + CHUNK_SIZE]
        )

    return chunks


# ==========================================================
# EXTRACT SEMANTIC CHUNKS
# ==========================================================

def extract_semantic_chunks(content):

    matches = list(
        DECLARATION_PATTERN.finditer(content)
    )

    if not matches:

        return [
            {
                "name": "file",
                "type": "file",
                "content": content
            }
        ]

    chunks = []

    for index, match in enumerate(matches):

        start = match.start()

        end = (
            matches[index + 1].start()
            if index < len(matches) - 1
            else len(content)
        )

        chunk_content = content[start:end].strip()

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
                "content": chunk_content
            }
        )

    return chunks


# ==========================================================
# INDEX SINGLE FILE
# ==========================================================

def index_file(path):

    filename = os.path.basename(path)

    relative_path = os.path.relpath(
        path,
        REPO_PATH
    )

    print(f"\n📄 {relative_path}")

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()

    semantic_chunks = extract_semantic_chunks(
        content
    )

    print(
        f"   Semantic Chunks : {len(semantic_chunks)}"
    )

    for chunk in semantic_chunks:

        sub_chunks = split_large_chunk(
            chunk["content"]
        )

        for index, code in enumerate(sub_chunks):

            enriched = f"""
FILE: {filename}

PATH: {relative_path}

TYPE: {chunk["type"]}

NAME: {chunk["name"]}

CODE:

{code}
"""

            embedding = get_embedding(
                enriched
            )

            collection.add(

                ids=[
                    str(uuid.uuid4())
                ],

                documents=[
                    enriched
                ],

                embeddings=[
                    embedding
                ],

                metadatas=[
                    {
                        "source": "repository",
                        "file": filename,
                        "path": relative_path,
                        "chunk_name": chunk["name"],
                        "chunk_type": chunk["type"],
                        "chunk_index": index
                    }
                ]
            )

    print(
        f"   Indexed {len(semantic_chunks)} semantic chunks"
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
            d for d in dirs
            if d not in (
                ".dart_tool",
                "build",
                ".git"
            )
        ]

        for file in files:

            if not file.endswith(".dart"):
                continue

            path = os.path.join(
                root,
                file
            )

            index_file(path)

            total_files += 1

    print()
    print("=" * 80)
    print("INDEXING COMPLETE")
    print("=" * 80)

    print(f"Files Indexed : {total_files}")
    print(
        f"Total Chunks  : {collection.count()}"
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    index_repository()