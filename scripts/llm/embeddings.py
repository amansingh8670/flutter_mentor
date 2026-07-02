"""
llm/embeddings.py

Centralized embedding client for Ollama.

All embedding requests should go through this file.
"""

import requests

from scripts.config import (
    OLLAMA_BASE_URL,
    EMBED_MODEL,
)


# ==========================================================
# ENDPOINT
# ==========================================================

EMBEDDING_URL = (
    f"{OLLAMA_BASE_URL}/api/embeddings"
)


# ==========================================================
# GET EMBEDDING
# ==========================================================

def get_embedding(text: str) -> list[float]:
    """
    Generate an embedding for the supplied text.

    Args:
        text: Input text.

    Returns:
        Embedding vector.
    """

    response = requests.post(

        EMBEDDING_URL,

        json={
            "model": EMBED_MODEL,
            "prompt": text
        },

        timeout=120
    )

    response.raise_for_status()

    return response.json()["embedding"]


# ==========================================================
# GET MULTIPLE EMBEDDINGS
# ==========================================================

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts.

    Ollama currently exposes only a single embedding endpoint,
    so we simply batch them here.
    """

    embeddings = []

    for text in texts:

        embeddings.append(
            get_embedding(text)
        )

    return embeddings


# ==========================================================
# HEALTH CHECK
# ==========================================================

def check_embedding_model() -> bool:
    """
    Verify that the embedding model is available.
    """

    try:

        get_embedding("health check")

        return True

    except Exception:

        return False


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("=" * 80)
    print("EMBEDDING TEST")
    print("=" * 80)

    text = "Flutter Login Screen"

    embedding = get_embedding(text)

    print(f"Input      : {text}")
    print(f"Dimensions : {len(embedding)}")
    print(f"First 10   : {embedding[:10]}")