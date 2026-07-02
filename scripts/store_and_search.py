import chromadb
import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"

client = chromadb.PersistentClient(
    path="./data/chroma"
)

collection = client.get_or_create_collection(
    name="flutter_repo"
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

documents = [
    "Flutter login screen",
    "Riverpod state management",
    "Nutrition meal card"
]

for i, doc in enumerate(documents):
    collection.upsert(
        ids=[str(i)],
        documents=[doc],
        embeddings=[get_embedding(doc)]
    )

print("Documents stored")

query_embedding = get_embedding("redux")

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print(results["documents"])