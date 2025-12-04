"""Build a FAISS index + metadata JSON from raw runbook files.

Usage (CORRECT):

    poetry run python -m inc_tria9.build_runbook_index

Do NOT run this file directly like:

    python src/inc_tria9/build_runbook_index.py

because relative imports will fail.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import faiss  # type: ignore[import]
from sentence_transformers import SentenceTransformer  # type: ignore[import]

# Safety guard for incorrect execution
try:
    from .vector_db.config import INDEX_PATH, METADATA_PATH, EMBEDDING_MODEL_NAME
except ImportError:
    if __name__ == "__main__" and (__package__ is None or __package__ == ""):
        print(
            "\n[build_runbook_index] ERROR: This script must be run as a module in the inc_tria9 package.\n"
            "Use:\n\n"
            "    poetry run python -m inc_tria9.build_runbook_index\n\n"
            "from the project root (where pyproject.toml lives).\n"
        )
        sys.exit(1)
    raise


def _read_runbook_files(source_dir: Path) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    if not source_dir.exists():
        print(f"[build_index] Runbook source dir does not exist: {source_dir}")
        return docs

    exts = {".md", ".txt"}
    for path in sorted(source_dir.rglob("*")):
        if path.suffix.lower() not in exts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[build_index] Skipping {path}: {e}")
            continue
        docs.append(
            {
                "id": path.stem,
                "text": text,
                "metadata": {
                    "filename": path.name,
                    "relative_path": str(path.relative_to(source_dir)),
                },
            }
        )
    return docs


def build_index() -> None:
    env_dir = os.getenv("RUNBOOK_SOURCE_DIR", "./runbooks")
    source_dir = Path(env_dir).resolve()
    print(f"[build_index] Using runbook source dir: {source_dir}")

    docs = _read_runbook_files(source_dir)
    if not docs:
        print("[build_index] No runbook files found. Nothing to index.")
        return

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"[build_index] Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    texts = [d["text"] for d in docs]
    print(f"[build_index] Encoding {len(texts)} runbook documents...")
    embeddings = model.encode(texts, convert_to_numpy=True)

    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)

    print(f"[build_index] Writing FAISS index to: {INDEX_PATH}")
    faiss.write_index(index, str(INDEX_PATH))

    print(f"[build_index] Writing metadata to: {METADATA_PATH}")
    import json

    with METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    print("[build_index] Done.")


if __name__ == "__main__":
    build_index()
