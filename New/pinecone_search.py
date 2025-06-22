from pinecone import Pinecone
from openai import OpenAI
from utils import load_keys
import os

def query_pinecone(question_id: str, top_k: int = 3) -> list:
    """Search Pinecone for chunks relevant to the question ID."""
    keys = load_keys()
    openai_client = OpenAI(api_key=keys["OPENAI_API_KEY"])
    pc = Pinecone(api_key=keys["PINECONE_API_KEY"])
    index = pc.Index(keys["PINECONE_INDEX"])

    # Generate embedding for the search query (e.g., "Q10.1")
    print(f"Generating embedding for query: {question_id}")
    query_response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=question_id
    )
    query_vector = query_response.data[0].embedding

    # Query Pinecone vector DB
    search_result = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    # Extract matching chunks
    matches = search_result.matches
    print(f"Found {len(matches)} matching chunks:\n")
    for i, match in enumerate(matches):
        print(f"Match {i+1} (score={match.score:.4f}):\n{match.metadata['text'][:500]}\n")

    return [match.metadata["text"] for match in matches]

if __name__ == "__main__":
    question_id = "Q10.1"  # Replace with any question label
    query_pinecone(question_id)
