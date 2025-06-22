from pdf_embedder import query_pdf_question
from typing import Dict, Any, List, Tuple, Union, Optional
import re

def clean_text(text: str) -> str:
    """Clean and format survey text."""
    # Remove survey artifacts
    text = re.sub(r'SHOW SCREEN TO THE RESPONDENT\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'CONTINUE ONLY IF\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'TERMINATE\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\(MA\)\s*', '', text)
    text = re.sub(r'\s*\(SA\)\s*', '', text)
    
    # Clean formatting
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def score_match(text: str, query: str) -> float:
    """Score how well a text matches the query intent."""
    # Keywords for scoring
    ott_keywords = ['ott', 'video', 'app', 'stream', 'platform', 'netflix', 'prime', 'hotstar']
    usage_keywords = ['using', 'used', 'use', 'usage', 'currently', 'installed']
    
    text = text.lower()
    query = query.lower()
    
    # Count keyword matches
    ott_matches = sum(1 for k in ott_keywords if k in text)
    usage_matches = sum(1 for k in usage_keywords if k in text)
    query_matches = sum(1 for word in query.split() if word in text)
    
    # Calculate score components
    relevance = 0.4 * (ott_matches / len(ott_keywords))
    usage = 0.3 * (usage_matches / len(usage_keywords))
    query_match = 0.3 * (query_matches / len(query.split()))
    
    return relevance + usage + query_match

def extract_best_question(matches: List[Dict[str, Any]], query: str) -> Tuple[str, str]:
    """Extract best matching question based on relevance scoring."""
    best_score = -1
    best_qid = "unknown"
    best_text = ""
    
    for match in matches:
        metadata = match.get('metadata', {})
        embedding_score = float(match.get('score', 0))
        
        # Get clean text from metadata
        text = metadata.get('clean_text', '') or metadata.get('text', '')
        if not text:
            continue
            
        # Clean the text
        clean_content = clean_text(text)
        
        # Get QID from metadata or extract from text
        qid = metadata.get('qid', '')
        if not qid or qid == 'unknown':
            qid_match = re.search(r'Q\d+\.?\d*', text)
            qid = qid_match.group(0) if qid_match else "unknown"
            
        # Calculate relevance score
        relevance_score = score_match(clean_content, query)
        
        # Combine scores
        final_score = 0.7 * embedding_score + 0.3 * relevance_score
        
        # Boost Q10.x and Q11.x questions (OTT related)
        if qid.startswith('Q10') or qid.startswith('Q11'):
            final_score *= 1.5
            
        print(f"\nDebug: {qid}")
        print(f"Embedding score: {embedding_score:.3f}")
        print(f"Relevance score: {relevance_score:.3f}")
        print(f"Final score: {final_score:.3f}")
        print(f"Text: {clean_content[:100]}...")
        
        if final_score > best_score:
            best_score = final_score
            best_qid = qid
            best_text = clean_content
    
    print(f"\nBest match: {best_qid} (score: {best_score:.3f})")
    return best_qid, best_text

def query_pdf_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node to find relevant survey questions."""
    user_question = state.get("question", "")
    if not user_question:
        print("No question provided in state")
        return {
            **state,
            "question_id": "unknown",
            "question_text": "No question provided"
        }

    print(f"\nSearching PDF for question: {user_question}")

    try:
        # Get matches from PDF embeddings
        result = query_pdf_question(user_question, top_k=40)
        
        if not isinstance(result, dict) or 'matches' not in result:
            print("Invalid response from PDF query")
            return {
                **state,
                "question_id": "unknown",
                "question_text": "Error: Invalid response format"
            }
            
        matches = result['matches']
        if not matches:
            print("No matches found in PDF")
            return {
                **state,
                "question_id": "unknown",
                "question_text": "No matches found in survey"
            }
            
        # Extract best matching question
        question_id, question_text = extract_best_question(matches, user_question)
        
        if question_id == "unknown":
            print("No relevant question found in survey")
            return {
                **state,
                "question_id": "unknown",
                "question_text": "No matching question found in survey"
            }
        
        print(f"Found matching question: {question_id}")
        print(f"Question text: {question_text[:100]}...")
        
        return {
            **state,
            "question_id": question_id,
            "question_text": question_text
        }
        
    except Exception as e:
        error_msg = str(e)
        print("PDF query failed:", error_msg)
        return {
            **state,
            "question_id": "unknown",
            "question_text": f"Error: {error_msg}"
        }

# Test the node
if __name__ == "__main__":
    test_state = {
        "question": "Which OTT / video entertainment apps are you currently using?"
    }
    result = query_pdf_question_node(test_state)
    print("\nTest Result:")
    for key, value in result.items():
        print(f"{key}: {value}")
