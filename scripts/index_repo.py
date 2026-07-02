import os
import re

import chromadb
import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"

REPO_PATH = "/Users/amansingh/Desktop/Practice/chef_ai_mobile/lib"

client = chromadb.PersistentClient(
    path="./data/chroma"
)

#
# Delete old collection so we don't mix old and new chunks
#
try:
    client.delete_collection("flutter_repo")
    print("Old collection deleted")
except Exception:
    pass

collection = client.get_or_create_collection(
    name="flutter_repo"
)


# =========================================================
# EMBEDDING
# =========================================================

def get_embedding(text):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )

    response.raise_for_status()

    return response.json()["embedding"]


# =========================================================
# SPLIT LARGE CHUNKS
# =========================================================

def split_large_chunk(text, max_chars=1500):

    chunks = []

    for i in range(0, len(text), max_chars):
        chunks.append(
            text[i:i + max_chars]
        )

    return chunks


# =========================================================
# SEMANTIC CHUNK EXTRACTION
# =========================================================

def extract_semantic_chunks(content):

    pattern = re.compile(
        r'^(class|enum|extension)\s+(\w+)|^final\s+(\w+)',
        re.MULTILINE
    )

    matches = list(
        pattern.finditer(content)
    )

    if not matches:
        return [
            {
                "name": "file",
                "content": content,
                "type": "file"
            }
        ]

    chunks = []

    for index, match in enumerate(matches):

        start = match.start()

        if index < len(matches) - 1:
            end = matches[index + 1].start()
        else:
            end = len(content)

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
                "content": chunk_content,
                "type": chunk_type
            }
        )

    return chunks


# =========================================================
# INDEX REPO
# =========================================================

for root, dirs, files in os.walk(REPO_PATH):

    for file in files:

        if not file.endswith(".dart"):
            continue

        full_path = os.path.join(
            root,
            file
        )

        print(f"\nProcessing: {file}")

        with open(
            full_path,
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        print(
            f"Characters: {len(content)}"
        )

        semantic_chunks = (
            extract_semantic_chunks(content)
        )

        print(
            f"Semantic chunks: "
            f"{len(semantic_chunks)}"
        )

        for chunk in semantic_chunks:

            chunk_name = chunk["name"]
            chunk_content = chunk["content"]
            chunk_type = chunk["type"]

            sub_chunks = split_large_chunk(
                chunk_content,
                max_chars=1500
            )

            for idx, sub_chunk in enumerate(
                sub_chunks
            ):

                chunk_id = (
                    f"{full_path}"
                    f"::{chunk_name}"
                    f"::{idx}"
                )

                print(
                    f"  -> {chunk_name}"
                    f" [{idx}] "
                    f"({len(sub_chunk)} chars)"
                )

                #
                # Metadata enrichment
                #
                enriched_text = f"""
FILE: {file}

CLASS: {chunk_name}

TYPE: {chunk_type}

PATH: {full_path}

CODE:

{sub_chunk}
"""

                try:

                    embedding = get_embedding(
                        enriched_text
                    )

                    collection.upsert(
                        ids=[chunk_id],

                        documents=[
                            enriched_text
                        ],

                        embeddings=[
                            embedding
                        ],

                        metadatas=[
                            {
                                "file": file,
                                "path": full_path,
                                "chunk_name": chunk_name,
                                "chunk_type": chunk_type,
                                "chunk_index": idx
                            }
                        ]
                    )

                except Exception as e:

                    print(
                        f"FAILED: {file} "
                        f"{chunk_name} [{idx}]"
                    )

                    print(e)

        print(f"Indexed: {file}")

print("\nDone")