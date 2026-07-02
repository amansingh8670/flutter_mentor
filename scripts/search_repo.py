import chromadb
import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"

client = chromadb.PersistentClient(
    path="./data/chroma"
)

collection = client.get_collection(
    "flutter_repo"
)


def get_embedding(text):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )

    response.raise_for_status()

    return response.json()["embedding"]


query = input("Search: ")

embedding = get_embedding(query)

results = collection.query(
    query_embeddings=[embedding],
    n_results=5
)

print("\nRESULTS\n")

for i, doc in enumerate(results["documents"][0]):
    metadata = results["metadatas"][0][i]

    print("=" * 80)

    print(
        metadata["file"],
        metadata["chunk_name"]
    )

    print()

    print(doc[:500])