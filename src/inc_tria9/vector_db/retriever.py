from __future__ import annotations

from typing import Any, Dict, List

from .client import FAISSRunbookClient

_client: FAISSRunbookClient | None = None


def get_client() -> FAISSRunbookClient | None:
    global _client
    if _client is not None:
        return _client
    try:
        _client = FAISSRunbookClient.from_files()
        print("[vector_db] Loaded FAISS index + metadata successfully.")
    except FileNotFoundError as e:
        print("[vector_db] WARNING:", e)
        _client = None
    return _client


def retrieve_runbooks(
    query: str,
    top_k: int = 5,
    metadata_filter: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    client = get_client()
    if client is None:
        print("[vector_db] No index found, returning synthetic runbook chunk.")
        return [
            {
                "id": "synthetic-0",
                "text": "Synthetic runbook: investigate recent deployments and roll back if correlated with errors.",
                "metadata": {"source": "synthetic", "service": metadata_filter.get("service") if metadata_filter else None},
                "score": 0.0,
            }
        ]

    results = client.search(query=query, top_k=top_k, metadata_filter=metadata_filter or {})
    chunks: List[Dict[str, Any]] = []
    for chunk, score in results:
        chunks.append(
            {
                "id": chunk.id,
                "text": chunk.text,
                "metadata": chunk.metadata,
                "score": score,
            }
        )
    return chunks
