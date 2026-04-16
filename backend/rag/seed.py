"""One-time script to seed ChromaDB with documents from rag/seed/."""

import os
import sys
from pathlib import Path

# allow running from repo root or backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.ingest import ingest_file

SEED_DIR = Path(__file__).parent / "seed"


def main():
    files = list(SEED_DIR.iterdir())
    if not files:
        print("No files found in rag/seed/")
        return

    for path in files:
        if path.is_file():
            print(f"Ingesting {path.name}...", end=" ")
            n = ingest_file(path.name, path.read_bytes())
            print(f"{n} chunks")

    print("Done.")


if __name__ == "__main__":
    main()
