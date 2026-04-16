"""Document ingestion — chunk, embed, and store in ChromaDB."""

import hashlib
import io

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings

_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def _collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    ef = OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key,
        model_name=settings.openai_embedding_model,
    )
    return client.get_or_create_collection("documents", embedding_function=ef)


def ingest_file(filename: str, content: bytes) -> int:
    """Chunk and embed a file. Returns number of chunks stored."""
    text = content.decode("utf-8", errors="ignore")
    chunks = _splitter.split_text(text)
    if not chunks:
        return 0

    collection = _collection()
    ids = [
        hashlib.sha256(f"{filename}::{i}::{chunk}".encode()).hexdigest()
        for i, chunk in enumerate(chunks)
    ]
    metadatas = [{"source": filename, "chunk": i} for i, _ in enumerate(chunks)]
    collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)
