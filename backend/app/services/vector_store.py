import chromadb

# Persistent ChromaDB database
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def add_documents(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
):
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search_documents(
    query_embedding: list[float],
    n_results: int = 3,
):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results


def get_all_documents():
    """
    Return all stored document chunks and metadata.
    """
    return collection.get(
        include=["metadatas"]
    )


def delete_document(filename: str):
    """
    Delete all chunks belonging to a specific PDF.
    """

    results = collection.get(
        where={
            "filename": filename
        },
        include=["metadatas"]
    )

    ids = results["ids"]

    if ids:
        collection.delete(ids=ids)

    return len(ids)


def reset_collection():
    global collection

    client.delete_collection(
        name="documents"
    )

    collection = client.get_or_create_collection(
        name="documents"
    )