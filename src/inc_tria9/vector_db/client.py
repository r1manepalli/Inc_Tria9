from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
import json

import faiss  # type: ignore[import]
from sentence_transformers import SentenceTransformer  # type: ignore[import]

from .config import INDEX_PATH, METADATA_PATH, EMBEDDING_MODEL_NAME


@dataclass
class RunbookChunk:
    id: str
    text: str
    metadata: Dict[str, Any]


@dataclass
class FAISSRunbookClient:
    index: Any
    chunks: List[RunbookChunk]
    model: SentenceTransformer

    @classmethod
    def from_files(
        cls,
        index_path: Path = INDEX_PATH,
        metadata_path: Path = METADATA_PATH,
        model_name: str = EMBEDDING_MODEL_NAME,
    ) -> "FAISSRunbookClient":
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"Missing FAISS index or metadata. "
                f"Expected index at {index_path} and metadata at {metadata_path}"
            )

        index = faiss.read_index(str(index_path))

        with metadata_path.open("r", encoding="utf-8") as f:
            raw_meta = json.load(f)

        chunks: List[RunbookChunk] = [
            RunbookChunk(id=str(item.get("id", i)), text=item["text"], metadata=item.get("metadata", {}))
            for i, item in enumerate(raw_meta)
        ]

        model = SentenceTransformer(model_name)
        return cls(index=index, chunks=chunks, model=model)

    def embed(self, text: str):
        vec = self.model.encode([text], convert_to_numpy=True)
        return vec

    def search(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Dict[str, Any] | None = None,
    ) -> List[Tuple[RunbookChunk, float]]:
        q = self.embed(query)
        scores, indices = self.index.search(q, top_k)
        indices = indices[0]
        scores = scores[0]

        results: List[Tuple[RunbookChunk, float]] = []
        for idx, score in zip(indices, scores):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            if metadata_filter:
                keep = True
                for k, v in metadata_filter.items():
                    if chunk.metadata.get(k) != v:
                        keep = False
                        break
                if not keep:
                    continue
            results.append((chunk, float(score)))
        return results
