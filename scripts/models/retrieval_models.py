"""
models/retrieval_models.py

Shared models used throughout the retrieval pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, List


# ==========================================================
# RETRIEVED CHUNK
# ==========================================================

@dataclass(slots=True)
class RetrievedChunk:
    """
    Represents a single retrieved chunk from the repository
    or Flutter documentation.
    """

    file: str

    path: str

    chunk_name: str

    chunk_type: str

    document: str

    source: str

    score: float = 0.0

    metadata: Dict = field(default_factory=dict)


# ==========================================================
# SEARCH RESULT
# ==========================================================

@dataclass(slots=True)
class SearchResult:
    """
    Result returned by semantic/keyword search.
    """

    query: str

    chunks: List[RetrievedChunk]


# ==========================================================
# MERGED RESULT
# ==========================================================

@dataclass(slots=True)
class RetrievalResult:
    """
    Final merged retrieval result after semantic,
    keyword search and reranking.
    """

    queries: List[str]

    chunks: List[RetrievedChunk]

    semantic_chunks: int = 0

    keyword_chunks: int = 0

    duplicate_chunks: int = 0

    reranked: bool = False


# ==========================================================
# INDEXED CHUNK
# ==========================================================

@dataclass(slots=True)
class IndexedChunk:
    """
    Represents a chunk before it is indexed into Chroma.
    """

    file: str

    path: str

    chunk_name: str

    chunk_type: str

    content: str

    index: int = 0


# ==========================================================
# RETRIEVAL CONFIG
# ==========================================================

@dataclass(slots=True)
class RetrievalConfig:
    """
    Runtime retrieval configuration.
    """

    semantic_results: int = 3

    keyword_results: int = 2

    max_chunks: int = 20

    rerank: bool = True

    include_flutter_docs: bool = True

    deduplicate: bool = True