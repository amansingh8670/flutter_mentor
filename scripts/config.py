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

# Planner model
PLANNER_MODEL = "deepseek-coder-v2:16b"

# Generator model
GENERATOR_MODEL = "deepseek-coder-v2:16b"

# Backward compatibility
CHAT_MODEL = GENERATOR_MODEL

VISION_MODEL = "qwen2.5vl:3b"

EMBED_MODEL = "nomic-embed-text"


# ==========================================================
# GENERATION
# ==========================================================

LLM_CONTEXT_SIZE = 8192

LLM_MAX_OUTPUT = 768

LLM_TEMPERATURE = 0.1

REQUEST_TIMEOUT = 1800

KEEP_ALIVE = "30m"


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

# Final number of chunks after reranking
MAX_CONTEXT_CHUNKS = 8


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
# PLANNER
# ==========================================================

# Maximum files planner may request
MAX_IMPLEMENTATION_FILES = 12


# ==========================================================
# DEBUG
# ==========================================================

PRINT_VISION = True

PRINT_QUERIES = True

PRINT_RETRIEVAL = True

PRINT_PROMPT = False

PRINT_CONTEXT = True

PRINT_PLAN = True