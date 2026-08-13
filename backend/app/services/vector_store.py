import chromadb

#creates a persistent ChromaDB database.
client = chromadb.PersistentClient(path="./chroma_db")
#Give me the documents collection. If it doesn't exist, create it
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
def reset_collection():
    global collection

    client.delete_collection(name="documents")

    collection = client.get_or_create_collection(
        name="documents"
    )