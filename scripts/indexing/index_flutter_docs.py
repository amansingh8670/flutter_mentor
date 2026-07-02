import os
import uuid

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from scripts.config import (
    CHROMA_PATH,
    FLUTTER_DOCS_COLLECTION,
    FLUTTER_DOCS_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

from scripts.llm.embeddings import get_embedding


# ==========================================================
# CHROMA
# ==========================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

try:
    client.delete_collection(
        FLUTTER_DOCS_COLLECTION
    )
except Exception:
    pass

collection = client.create_collection(
    FLUTTER_DOCS_COLLECTION
)


# ==========================================================
# TEXT SPLITTER
# ==========================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n# ",
        "\n## ",
        "\n### ",
        "\n#### ",
        "\n\n",
        "\n",
        " ",
        ""
    ]
)


# ==========================================================
# READ FILE
# ==========================================================

def read_file(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ==========================================================
# INDEX SINGLE FILE
# ==========================================================

def index_file(path):

    relative_path = os.path.relpath(
        path,
        FLUTTER_DOCS_PATH
    )

    filename = os.path.basename(path)

    print(f"\n📄 {relative_path}")

    text = read_file(path)

    chunks = splitter.split_text(text)

    for index, chunk in enumerate(chunks):

        embedding = get_embedding(chunk)

        collection.add(

            ids=[
                str(uuid.uuid4())
            ],

            embeddings=[
                embedding
            ],

            documents=[
                chunk
            ],

            metadatas=[
                {
                    "source": "flutter_docs",
                    "file": filename,
                    "path": relative_path,
                    "chunk": index,
                    "type": "documentation"
                }
            ]
        )

    print(
        f"   Indexed {len(chunks)} chunks"
    )


# ==========================================================
# INDEX DIRECTORY
# ==========================================================

def index_flutter_docs():

    total_files = 0

    total_chunks = 0

    print("=" * 80)
    print("INDEXING FLUTTER DOCUMENTATION")
    print("=" * 80)

    for root, _, files in os.walk(
        FLUTTER_DOCS_PATH
    ):

        for file in files:

            if not file.endswith(
                (
                    ".md",
                    ".txt",
                    ".html"
                )
            ):
                continue

            path = os.path.join(
                root,
                file
            )

            before = collection.count()

            index_file(path)

            after = collection.count()

            total_files += 1
            total_chunks += after - before

    print()
    print("=" * 80)
    print("INDEXING COMPLETE")
    print("=" * 80)

    print(f"Files Indexed : {total_files}")
    print(f"Chunks Indexed: {total_chunks}")
    print(f"Collection    : {FLUTTER_DOCS_COLLECTION}")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    index_flutter_docs()