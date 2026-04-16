"""Semantic retrieval from ChromaDB."""

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from config import settings


def _collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    ef = OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key,
        model_name=settings.openai_embedding_model,
    )
    return client.get_or_create_collection("documents", embedding_function=ef)


def retrieve(query: str, n_results: int = 5) -> list[dict]:
    """Return the top n_results chunks most relevant to query."""
    collection = _collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[query], n_results=n_results)
    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({"text": doc, "source": meta.get("source"), "chunk": meta.get("chunk")})
    return chunks
