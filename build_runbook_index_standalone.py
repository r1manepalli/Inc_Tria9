# build_runbook_index_standalone.py
"""
Standalone runner for the FAISS runbook index builder.

This avoids the "No module named 'inc_tria9'" issues by:
- adding ./src to sys.path
- importing the package module inc_tria9.build_runbook_index
- calling its build_index() function
"""

import sys
from pathlib import Path

# Ensure ./src is on sys.path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from inc_tria9.build_runbook_index import build_index  # type: ignore[import]


if __name__ == "__main__":
    build_index()
