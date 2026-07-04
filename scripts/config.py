"""
==========================================================
CONFIGURATION
==========================================================

Central configuration for the Flutter Mentor project.

Only modify values in this file.
Other modules should import from here.
"""

import os


# ==========================================================
# ROOT PATHS
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "data"
)

CHROMA_PATH = os.path.join(
    DATA_DIR,
    "chroma"
)

REPO_PATH = "/Users/amansingh/Desktop/Practice/chef_ai_mobile/lib"

FLUTTER_DOCS_PATH = os.path.join(
    DATA_DIR,
    "flutter_docs"
)


# ==========================================================
# OLLAMA
# ==========================================================

OLLAMA_BASE_URL = "http://localhost:11434"

CHAT_URL = f"{OLLAMA_BASE_URL}/api/generate"

EMBED_URL = f"{OLLAMA_BASE_URL}/api/embeddings"


# ==========================================================
# MODELS
# ==========================================================

CHAT_MODEL = "qwen2.5-coder:14b"

VISION_MODEL = "qwen2.5vl:3b"

EMBED_MODEL = "nomic-embed-text"


# ==========================================================
# CHROMA COLLECTIONS
# ==========================================================

REPO_COLLECTION = "flutter_repo"

DOCS_COLLECTION = "flutter_docs"


# ==========================================================
# RETRIEVAL
# ==========================================================

SEMANTIC_RESULTS = 3

KEYWORD_RESULTS = 2

MULTI_QUERY_RESULTS = 2

MAX_CONTEXT_CHUNKS = 20


# ==========================================================
# EMBEDDING
# ==========================================================

EMBED_BATCH_SIZE = 32


# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = 700

CHUNK_OVERLAP = 200


# ==========================================================
# DEBUG
# ==========================================================

PRINT_VISION = True

PRINT_QUERIES = True

PRINT_RETRIEVAL = True

PRINT_PROMPT = False

PRINT_CONTEXT = True