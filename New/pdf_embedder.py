import os
import fitz  # PyMuPDF
import tiktoken
from openai import OpenAI
from pinecone import Pinecone
from utils import load_keys
import re
from typing import Dict, List, Optional, Any, cast, Union

def clean_text(text: str) -> str:
    """Clean up text content from PDF."""
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,?!-]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(filepath: str) -> str:
    """Extract full text from a PDF file."""
    doc = fitz.open(filepath)
    text = ""
    for page_num in range(len(doc)):
        # Use string casting for PyMuPDF compatibility
        text += str(doc[page_num].get_textpage().extractText())
    doc.close()
    return text

def chunk_text(text: str, max_tokens: int = 400, overlap: int = 100) -> list:
    """Split long text into overlapping chunks (~400 tokens with 100-token overlap)."""
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens - overlap):
        chunk = enc.decode(tokens[i:i + max_tokens])
        chunks.append(chunk)

    return chunks

def extract_question_info(text: str) -> Dict[str, str]:
    """Extract question ID and clean text from chunk."""
    # Extract question ID
    qid_match = re.search(r'Q\d+\.?\d*', text)
    qid = qid_match.group(0) if qid_match else "unknown"
    
    # Clean text content
    clean_content = clean_text(text)
    
    return {
        "qid": qid,
        "text": clean_content
    }

def embed_and_store(chunks: List[str], namespace: str = "default") -> None:
    """Embed text chunks and store in Pinecone."""
    keys = load_keys()
    index_name = keys.get("PINECONE_INDEX")
    if not index_name:
        raise ValueError("PINECONE_INDEX is required in environment variables")
        
    openai_client = OpenAI(api_key=keys["OPENAI_API_KEY"])
    pc = Pinecone(api_key=keys["PINECONE_API_KEY"])
    
    index = pc.Index(name=cast(str, index_name))

    for i, chunk in enumerate(chunks):
        # Create embedding
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=chunk
        )
        vector = response.data[0].embedding

        # Extract question info
        info = extract_question_info(chunk)
        
        # Store embedding with metadata
        index.upsert(vectors=[{
            "id": f"{namespace}-chunk-{i}",
            "values": vector,
            "metadata": {
                "text": chunk,
                "qid": info["qid"],
                "clean_text": info["text"]
            }
        }])

        print(f"Chunk {i+1} (qid: {info['qid']}) embedded and stored.")

def embed_pdf_file(filepath: str, namespace: str = "default") -> None:
    print(f"Extracting text from: {filepath}")
    text = extract_text_from_pdf(filepath)
    print(f"Extracted {len(text)} characters")

    chunks = chunk_text(text)
    print(f"Total chunks created: {len(chunks)}")

    embed_and_store(chunks, namespace=namespace)
    print("All chunks embedded and stored in Pinecone.")

def parse_pinecone_response(response: Any) -> Dict[str, Any]:
    """Safely parse Pinecone response into a dictionary."""
    matches = []
    
    try:
        if isinstance(response, dict):
            matches = response.get('matches', [])
        elif hasattr(response, 'matches'):
            matches = list(response.matches)
        elif hasattr(response, '_asdict'):
            matches = response._asdict().get('matches', [])
            
    except Exception as e:
        print(f"Warning: Error parsing response - {str(e)}")
        
    return {
        "matches": matches
    }

def query_pdf_question(question: str, top_k: int = 3) -> Dict[str, Any]:
    """Search Pinecone for the most relevant question chunks."""
    keys = load_keys()
    index_name = keys.get("PINECONE_INDEX")
    if not index_name:
        raise ValueError("PINECONE_INDEX is required in environment variables")

    openai_client = OpenAI(api_key=keys["OPENAI_API_KEY"])
    pc = Pinecone(api_key=keys["PINECONE_API_KEY"])
    
    index = pc.Index(name=cast(str, index_name))

    # Create a more comprehensive query that includes variations
    query_text = f"Survey question about: {question}"
    
    # Embed the query
    embedding = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=query_text
    ).data[0].embedding

    # Query Pinecone with higher top_k to ensure we get good matches
    response = index.query(
        vector=embedding,
        top_k=top_k * 2,  # Get more results to filter
        include_metadata=True
    )
    
    # Parse response into standard format
    result = parse_pinecone_response(response)
    
    print("\nDebug: Examining Pinecone query results")
    print(f"Debug: Found {len(result['matches'])} matches")
    
    return result

if __name__ == "__main__":
    # Test the PDF embedder
    filepath = "Data/raw data/DOC.docx"  # Your file path
    embed_pdf_file(filepath)
    
    # Test query
    test_question = "Which OTT apps are you currently using?"
    result = query_pdf_question(test_question)
    print("\nTest Query Result:", result)
