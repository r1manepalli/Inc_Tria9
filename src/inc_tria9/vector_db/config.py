from pathlib import Path

# Default locations for the FAISS index + metadata.

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "runbooks"

INDEX_PATH = DATA_DIR / "runbooks.index.faiss"
METADATA_PATH = DATA_DIR / "runbooks.meta.json"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
